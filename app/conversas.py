"""Persistencia operacional do chat, eventos padronizados e telemetria de IA."""
from __future__ import annotations

import hashlib
import json
import re
import uuid
from threading import Lock

from app import leads as leads_repo
from app import db as app_db
from app.db import db_session
from app.lead import detect_phone


EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
STAGES_FUNIL = ("frio", "morno", "quente", "pronto_visita", "pronto_proposta")

_schema_ok = False
_schema_db_path = ""
_schema_lock = Lock()


def _garantir_schema() -> None:
    global _schema_ok, _schema_db_path
    db_path_atual = str(app_db.DB_PATH)
    if _schema_ok and _schema_db_path == db_path_atual:
        return
    with _schema_lock:
        db_path_atual = str(app_db.DB_PATH)
        if _schema_ok and _schema_db_path == db_path_atual:
            return
        app_db.init_db()
        _schema_ok = True
        _schema_db_path = db_path_atual


def _json(data: dict | None) -> str:
    return json.dumps(data or {}, ensure_ascii=False)


def _json_load(s: str | None) -> dict:
    if not s:
        return {}
    try:
        return json.loads(s)
    except (TypeError, ValueError):
        return {}


def _hash(valor: str) -> str:
    return hashlib.sha1(valor.encode("utf-8")).hexdigest()


def _provider_do_modelo(modelo: str) -> str:
    nome = (modelo or "").lower()
    if nome.startswith("gemini"):
        return "google"
    if nome.startswith("claude"):
        return "anthropic"
    if nome == "fallback":
        return "fallback"
    return "desconhecido"


def _buscar_email(texto: str) -> str | None:
    achou = EMAIL_RE.search(texto or "")
    return achou.group(0).lower() if achou else None


def _perfil_interno(
    *,
    texto_contexto: str,
    lead_stage: str,
    lead_score: int,
    rota: str,
) -> dict:
    texto = (texto_contexto or "").lower()
    quer_vender = any(p in texto for p in (
        "vender", "venda meu", "avaliar meu", "avaliacao do meu", "avaliação do meu",
        "quanto vale", "anunciar meu", "tenho um imovel", "tenho um imóvel",
    ))
    quer_comprar = any(p in texto for p in (
        "comprar", "financiar", "financiamento", "visita", "proposta", "entrada",
        "parcela", "quero uma casa", "quero apartamento", "procuro",
    ))
    urgencia = "alta" if any(p in texto for p in (
        "urgente", "essa semana", "este mes", "esse mes", "logo", "ja quero", "já quero",
    )) else "normal"
    jornada = "descoberta"
    if lead_stage in {"quente", "pronto_visita"}:
        jornada = "interesse_ativo"
    if lead_stage == "pronto_proposta":
        jornada = "proposta"
    return {
        "visivel_cliente": False,
        "origem": "chat",
        "jornada": jornada,
        "intencao": "vender" if quer_vender else "comprar" if quer_comprar else "tirar_duvida",
        "urgencia": urgencia,
        "score_operacional": lead_score,
        "stage_operacional": lead_stage,
        "rota_operacional": rota,
        "proximo_passo": "encaminhar para atendimento humano" if lead_score >= 60 else "continuar qualificacao",
    }


def _upsert_evento(
    nome: str,
    *,
    origem: str,
    lead_id: int | None = None,
    conversa_id: int | None = None,
    payload: dict | None = None,
    idempotency_key: str | None = None,
) -> None:
    _garantir_schema()
    with db_session() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO eventos_funil
                 (nome, origem, lead_id, conversa_id, payload, idempotency_key)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (nome, origem, lead_id, conversa_id, _json(payload), idempotency_key),
        )


def registrar_evento_funil(
    nome: str,
    *,
    origem: str,
    lead_id: int | None = None,
    conversa_id: int | None = None,
    payload: dict | None = None,
    idempotency_key: str | None = None,
) -> None:
    _upsert_evento(
        nome,
        origem=origem,
        lead_id=lead_id,
        conversa_id=conversa_id,
        payload=payload,
        idempotency_key=idempotency_key,
    )


def resumir_funil() -> dict:
    _garantir_schema()
    stages = {stage: 0 for stage in STAGES_FUNIL}
    with db_session() as conn:
        total = conn.execute("SELECT COUNT(*) AS n FROM conversas WHERE canal = 'site'").fetchone()["n"]
        rows = conn.execute(
            "SELECT ultimo_stage, COUNT(*) AS n FROM conversas WHERE canal = 'site' GROUP BY ultimo_stage"
        ).fetchall()
    for row in rows:
        stage = row["ultimo_stage"]
        if stage in stages:
            stages[stage] = row["n"]
    return {"total": total, "stages": stages}


def registrar_execucao_ia(
    *,
    agente: str,
    evento: str,
    modelo: str,
    fallback: bool,
    duracao_ms: int | None,
    metadata: dict | None = None,
    conversa_id: int | None = None,
    lead_id: int | None = None,
    erro: str | None = None,
    chave_idempotencia: str | None = None,
) -> None:
    _garantir_schema()
    with db_session() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO execucoes_ia
                 (conversa_id, lead_id, agente, evento, provedor, modelo,
                  fallback, sucesso, duracao_ms, metadata, erro, chave_idempotencia)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                conversa_id,
                lead_id,
                agente,
                evento,
                _provider_do_modelo(modelo),
                modelo,
                int(bool(fallback)),
                int(not erro),
                duracao_ms,
                _json(metadata),
                erro,
                chave_idempotencia,
            ),
        )


def _criar_ou_obter_conversa(sessao_id: str, rota: str, lead_score: int, lead_stage: str) -> tuple[int, bool, int | None]:
    _garantir_schema()
    with db_session() as conn:
        existente = conn.execute(
            "SELECT id, lead_id FROM conversas WHERE sessao_id = ?",
            (sessao_id,),
        ).fetchone()
        if existente:
            conn.execute(
                """UPDATE conversas
                      SET rota_atual = ?, ultimo_score = ?, ultimo_stage = ?, atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?""",
                (rota, lead_score, lead_stage, existente["id"]),
            )
            return int(existente["id"]), False, existente["lead_id"]
        cur = conn.execute(
            """INSERT INTO conversas (sessao_id, canal, rota_atual, ultimo_score, ultimo_stage)
               VALUES (?, 'site', ?, ?, ?)""",
            (sessao_id, rota, lead_score, lead_stage),
        )
        return int(cur.lastrowid), True, None


def _registrar_mensagem(conversa_id: int, papel: str, conteudo: str, metadata: dict | None, chave: str) -> None:
    _garantir_schema()
    with db_session() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO mensagens_conversa
                 (conversa_id, papel, conteudo, metadata, chave_mensagem)
               VALUES (?, ?, ?, ?, ?)""",
            (conversa_id, papel, conteudo, _json(metadata), chave),
        )


def _vincular_lead(
    conversa_id: int,
    *,
    texto_contexto: str,
    lead_stage: str,
    lead_score: int,
    rota: str,
    referencia: str,
    lead_existente_id: int | None,
) -> tuple[int | None, bool]:
    _garantir_schema()
    telefone = detect_phone(texto_contexto)
    email = _buscar_email(texto_contexto)
    if not telefone and not email:
        return lead_existente_id, False

    lead_id = leads_repo.upsert_lead(
        telefone=telefone,
        email=email,
        origem="chat",
    )
    with db_session() as conn:
        conn.execute(
            "UPDATE conversas SET lead_id = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
            (lead_id, conversa_id),
        )
    leads_repo.registrar_interacao(
        lead_id,
        tipo="chat",
        descricao="Conversa no site com IA",
        metadata={
            "perfil_interno": _perfil_interno(
                texto_contexto=texto_contexto,
                lead_stage=lead_stage,
                lead_score=lead_score,
                rota=rota,
            ),
            "referencia": referencia,
        },
        referencia_id=conversa_id,
    )
    novo_vinculo = lead_existente_id != lead_id
    return lead_id, novo_vinculo


def registrar_conversa_site(
    *,
    sessao_id: str | None,
    historico: list[dict],
    mensagem: str,
    resposta: dict,
    tem_imagem: bool,
    duracao_ms: int | None,
) -> dict:
    _garantir_schema()
    sessao = sessao_id or uuid.uuid4().hex
    referencia = _hash(f"{sessao}|{len(historico)}|{mensagem}|{resposta['rota']}|{resposta['modelo']}")
    conversa_id, criada, lead_existente_id = _criar_ou_obter_conversa(
        sessao,
        resposta["rota"],
        resposta["lead_score"],
        resposta["lead_stage"],
    )

    if criada and historico:
        for idx, item in enumerate(historico):
            papel = item.get("role")
            if papel not in {"user", "assistant"}:
                continue
            _registrar_mensagem(
                conversa_id,
                papel,
                item.get("content", ""),
                {"bootstrap": True},
                f"{sessao}:bootstrap:{idx}:{_hash(item.get('content', ''))}",
            )

    _registrar_mensagem(
        conversa_id,
        "user",
        mensagem,
        {"tem_imagem": tem_imagem, "rota_prevista": resposta["rota"]},
        f"{referencia}:user",
    )
    _registrar_mensagem(
        conversa_id,
        "assistant",
        resposta["resposta"],
        {"modelo": resposta["modelo"], "fallback": resposta["fallback"]},
        f"{referencia}:assistant",
    )

    texto_contexto = " ".join([m.get("content", "") for m in historico] + [mensagem, resposta["resposta"]])
    lead_id, novo_vinculo = _vincular_lead(
        conversa_id,
        texto_contexto=texto_contexto,
        lead_stage=resposta["lead_stage"],
        lead_score=resposta["lead_score"],
        rota=resposta["rota"],
        referencia=referencia,
        lead_existente_id=lead_existente_id,
    )

    if criada:
        registrar_evento_funil(
            "chat.iniciado",
            origem="site",
            lead_id=lead_id,
            conversa_id=conversa_id,
            payload={"sessao_id": sessao},
            idempotency_key=f"chat.iniciado:{sessao}",
        )

    registrar_evento_funil(
        "chat.mensagem_recebida",
        origem="site",
        lead_id=lead_id,
        conversa_id=conversa_id,
        payload={"rota": resposta["rota"], "tem_imagem": tem_imagem},
        idempotency_key=f"chat.msg:{referencia}",
    )
    registrar_evento_funil(
        "chat.resposta_gerada",
        origem="site",
        lead_id=lead_id,
        conversa_id=conversa_id,
        payload={"modelo": resposta["modelo"], "fallback": resposta["fallback"]},
        idempotency_key=f"chat.resposta:{referencia}",
    )

    if novo_vinculo and lead_id:
        registrar_evento_funil(
            "lead.recebido",
            origem="chat",
            lead_id=lead_id,
            conversa_id=conversa_id,
            payload={"origem": "chat"},
            idempotency_key=f"lead.recebido:{conversa_id}:{lead_id}",
        )

    if lead_id and resposta["lead_stage"] in {"morno", "quente", "pronto_visita", "pronto_proposta"}:
        registrar_evento_funil(
            "lead.qualificado",
            origem="chat",
            lead_id=lead_id,
            conversa_id=conversa_id,
            payload={"score": resposta["lead_score"], "stage": resposta["lead_stage"]},
            idempotency_key=f"lead.qualificado:{referencia}",
        )

    # Handoff: cliente pediu humano -> sinaliza transferencia pra Priscila (painel + tag).
    if resposta.get("rota") == "handoff":
        registrar_evento_funil(
            "handoff.solicitado",
            origem="chat",
            lead_id=lead_id,
            conversa_id=conversa_id,
            payload={"motivo": "pedido_humano", "stage": resposta["lead_stage"]},
            idempotency_key=f"handoff:{referencia}",
        )
        if lead_id:
            try:
                from app import leads as _leads
                _leads.adicionar_tag(lead_id, "handoff")
            except Exception:
                pass

    registrar_execucao_ia(
        agente="chat",
        evento="chat.resposta_gerada",
        modelo=resposta["modelo"],
        fallback=resposta["fallback"],
        duracao_ms=duracao_ms,
        metadata={
            "rota": resposta["rota"],
            "confianca": resposta["confianca"],
            "provider_metadata": resposta.get("provider_metadata") or {},
        },
        conversa_id=conversa_id,
        lead_id=lead_id,
        chave_idempotencia=f"exec.chat:{referencia}",
    )

    return {
        "session_id": sessao,
        "conversation_id": conversa_id,
        "lead_id": lead_id,
    }


def registrar_analise_conversa(*, sessao_id: str | None, historico: list[dict], resposta: dict, duracao_ms: int | None) -> None:
    _garantir_schema()
    sessao = sessao_id or "analise-sem-sessao"
    referencia = _hash(f"analise|{sessao}|{len(historico)}|{resposta['modelo']}|{resposta['lead_stage']}")
    conversa_id = None
    lead_id = None
    if sessao_id:
        with db_session() as conn:
            row = conn.execute("SELECT id, lead_id FROM conversas WHERE sessao_id = ?", (sessao_id,)).fetchone()
        if row:
            conversa_id = row["id"]
            lead_id = row["lead_id"]

    registrar_evento_funil(
        "chat.analise_gerada",
        origem="site",
        lead_id=lead_id,
        conversa_id=conversa_id,
        payload={"modelo": resposta["modelo"], "fallback": resposta["fallback"]},
        idempotency_key=f"chat.analise:{referencia}",
    )
    registrar_execucao_ia(
        agente="analise_lead",
        evento="chat.analise_gerada",
        modelo=resposta["modelo"],
        fallback=resposta["fallback"],
        duracao_ms=duracao_ms,
        metadata={"lead_stage": resposta["lead_stage"], "lead_score": resposta["lead_score"]},
        conversa_id=conversa_id,
        lead_id=lead_id,
        chave_idempotencia=f"exec.analise:{referencia}",
    )


def metricas_operacao_ia(*, horas: int = 24) -> dict:
    _garantir_schema()
    janela = f"-{max(1, min(horas, 720))} hours"
    with db_session() as conn:
        tot = conn.execute(
            "SELECT COUNT(*) AS n FROM execucoes_ia WHERE criado_em >= datetime('now', ?)",
            (janela,),
        ).fetchone()["n"]
        suc = conn.execute(
            "SELECT COUNT(*) AS n FROM execucoes_ia WHERE sucesso = 1 AND criado_em >= datetime('now', ?)",
            (janela,),
        ).fetchone()["n"]
        fb = conn.execute(
            "SELECT COUNT(*) AS n FROM execucoes_ia WHERE fallback = 1 AND criado_em >= datetime('now', ?)",
            (janela,),
        ).fetchone()["n"]
        lat = conn.execute(
            "SELECT AVG(duracao_ms) AS media FROM execucoes_ia WHERE duracao_ms IS NOT NULL AND criado_em >= datetime('now', ?)",
            (janela,),
        ).fetchone()["media"]
        por_modelo = [
            dict(r)
            for r in conn.execute(
                """SELECT modelo, COUNT(*) AS total,
                          SUM(CASE WHEN sucesso = 1 THEN 1 ELSE 0 END) AS sucessos,
                          SUM(CASE WHEN fallback = 1 THEN 1 ELSE 0 END) AS fallbacks
                     FROM execucoes_ia
                    WHERE criado_em >= datetime('now', ?)
                 GROUP BY modelo
                 ORDER BY total DESC""",
                (janela,),
            ).fetchall()
        ]
        por_agente = [
            dict(r)
            for r in conn.execute(
                """SELECT agente, COUNT(*) AS total,
                          SUM(CASE WHEN sucesso = 1 THEN 1 ELSE 0 END) AS sucessos
                     FROM execucoes_ia
                    WHERE criado_em >= datetime('now', ?)
                 GROUP BY agente
                 ORDER BY total DESC""",
                (janela,),
            ).fetchall()
        ]

    pct_sucesso = round((suc / tot) * 100, 1) if tot else 0.0
    pct_fallback = round((fb / tot) * 100, 1) if tot else 0.0
    return {
        "janela_horas": horas,
        "total_execucoes": tot,
        "sucesso_percentual": pct_sucesso,
        "fallback_percentual": pct_fallback,
        "latencia_media_ms": int(lat) if lat else 0,
        "por_modelo": por_modelo,
        "por_agente": por_agente,
    }


def listar_conversas(*, limit: int = 50, offset: int = 0, stage: str | None = None, busca: str | None = None) -> dict:
    _garantir_schema()
    where = []
    params: list = []
    if stage:
        where.append("c.ultimo_stage = ?")
        params.append(stage)
    if busca:
        like = f"%{busca.strip()}%"
        where.append("(c.sessao_id LIKE ? OR l.nome LIKE ? OR l.telefone LIKE ? OR l.email LIKE ?)")
        params.extend([like, like, like, like])

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    with db_session() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS n FROM conversas c LEFT JOIN leads l ON l.id = c.lead_id {where_sql}",
            params,
        ).fetchone()["n"]
        rows = conn.execute(
            f"""SELECT c.id, c.sessao_id, c.rota_atual, c.ultimo_score, c.ultimo_stage, c.status,
                       c.atualizado_em, l.nome AS lead_nome, l.telefone AS lead_telefone,
                       l.email AS lead_email,
                       (SELECT COUNT(*) FROM mensagens_conversa m WHERE m.conversa_id = c.id) AS total_mensagens,
                       (SELECT COUNT(*) FROM execucoes_ia e WHERE e.conversa_id = c.id) AS total_execucoes
                  FROM conversas c
             LEFT JOIN leads l ON l.id = c.lead_id
                 {where_sql}
              ORDER BY c.atualizado_em DESC
                 LIMIT ? OFFSET ?""",
            [*params, max(1, min(limit, 200)), max(0, offset)],
        ).fetchall()
    return {"items": [dict(r) for r in rows], "total": total}


def detalhar_conversa(conversa_id: int) -> dict | None:
    _garantir_schema()
    with db_session() as conn:
        base = conn.execute(
            """SELECT c.*, l.nome AS lead_nome, l.telefone AS lead_telefone, l.email AS lead_email
                   FROM conversas c
              LEFT JOIN leads l ON l.id = c.lead_id
                  WHERE c.id = ?""",
            (conversa_id,),
        ).fetchone()
        if not base:
            return None

        mensagens = [
            {**dict(r), "metadata": _json_load(r["metadata"]) }
            for r in conn.execute(
                "SELECT id, papel, conteudo, metadata, criado_em FROM mensagens_conversa WHERE conversa_id = ? ORDER BY id",
                (conversa_id,),
            ).fetchall()
        ]
        execucoes = [
            {**dict(r), "metadata": _json_load(r["metadata"]) }
            for r in conn.execute(
                """SELECT id, agente, evento, provedor, modelo, fallback, sucesso, duracao_ms, metadata, erro, criado_em
                     FROM execucoes_ia
                    WHERE conversa_id = ?
                 ORDER BY id""",
                (conversa_id,),
            ).fetchall()
        ]
        eventos = [
            {**dict(r), "payload": _json_load(r["payload"]) }
            for r in conn.execute(
                "SELECT id, nome, origem, payload, criado_em FROM eventos_funil WHERE conversa_id = ? ORDER BY id",
                (conversa_id,),
            ).fetchall()
        ]

    return {
        "conversa": dict(base),
        "mensagens": mensagens,
        "execucoes": execucoes,
        "eventos": eventos,
    }
