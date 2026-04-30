"""Operacao autonoma das IAs (procuradora, rastreadora e leads).

Objetivo:
- manter uma fila de tarefas por agente;
- executar ciclos automaticos (sem bloquear a operacao manual);
- registrar feedback do mentor para correcao continua.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.conversas import registrar_execucao_ia
from app.db import db_session
from app.dispatcher import responder


AGENTES_PADRAO: tuple[dict[str, Any], ...] = (
    {
        "chave": "procuradora",
        "nome": "IA Procuradora",
        "papel": "prospeccao ativa em canais web e social",
        "canais": ["web", "instagram", "site"],
        "configuracao": {"temperatura_operacao": "alta", "modo": "exploracao"},
    },
    {
        "chave": "rastreadora",
        "nome": "IA Rastreadora",
        "papel": "acompanhar leads, detectar sinais e priorizar follow-up",
        "canais": ["site", "whatsapp", "instagram"],
        "configuracao": {"temperatura_operacao": "media", "modo": "monitoramento"},
    },
    {
        "chave": "leads",
        "nome": "IA Leads",
        "papel": "qualificar, resumir contexto e sugerir proximo passo",
        "canais": ["site", "whatsapp", "web"],
        "configuracao": {"temperatura_operacao": "baixa", "modo": "conversao"},
    },
    {
        "chave": "marketing",
        "nome": "IA Marketing",
        "papel": "estrategia de conteudo e perfil de vendas em redes sociais",
        "canais": ["instagram", "web", "site"],
        "configuracao": {"temperatura_operacao": "media", "modo": "growth"},
    },
    {
        "chave": "orquestrador",
        "nome": "IA Orquestrador",
        "papel": "coordena fila, distribui tarefas e prioriza execucao multiagente",
        "canais": ["interno", "web", "instagram", "site", "whatsapp"],
        "configuracao": {"temperatura_operacao": "baixa", "modo": "coordenação"},
    },
    {
        "chave": "corretor",
        "nome": "IA Corretor de Erros",
        "papel": "revisar falhas e transformar erro em playbook pratico",
        "canais": ["interno"],
        "configuracao": {"temperatura_operacao": "baixa", "modo": "correcao_continua"},
    },
)


SUBAGENTES_PADRAO: dict[str, dict[str, Any]] = {
    "procuradora": {
        "chave": "vigia_prospeccao",
        "nome": "Subagente Vigia da Procuradora",
        "papel": "auditar sinais de oportunidade e evitar ruido",
        "configuracao": {"regra": "priorizar intencao clara", "min_score": 35},
    },
    "rastreadora": {
        "chave": "vigia_followup",
        "nome": "Subagente Vigia da Rastreadora",
        "papel": "validar continuidade e timing de follow-up",
        "configuracao": {"regra": "evitar insistencia", "min_score": 30},
    },
    "leads": {
        "chave": "vigia_qualificacao",
        "nome": "Subagente Vigia de Leads",
        "papel": "garantir qualificacao e proximo passo pratico",
        "configuracao": {"regra": "sempre puxar proxima acao", "min_score": 45},
    },
    "marketing": {
        "chave": "vigia_marketing",
        "nome": "Subagente Vigia do Marketing",
        "papel": "auditar proposta de valor, CTA e consistencia comercial",
        "configuracao": {"regra": "cada peca precisa de CTA", "min_score": 40},
    },
    "orquestrador": {
        "chave": "vigia_orquestra",
        "nome": "Subagente Vigia da Orquestra",
        "papel": "auditar balanceamento entre agentes e cobertura das rotas",
        "configuracao": {"regra": "nao deixar fila parada", "min_score": 35},
    },
    "corretor": {
        "chave": "vigia_corretor",
        "nome": "Subagente Vigia do Corretor",
        "papel": "garantir que toda falha vire acao de melhoria",
        "configuracao": {"regra": "erro sem correcao e proibido", "min_score": 30},
    },
}


def _json_dump(data: Any) -> str:
    return json.dumps(data or {}, ensure_ascii=False)


def _json_load_any(valor: str | None, default: Any) -> Any:
    if not valor:
        return default
    try:
        parsed = json.loads(valor)
        return parsed if isinstance(parsed, type(default)) else default
    except (TypeError, ValueError):
        return default


def _normalizar_chave(chave: str | None) -> str | None:
    if not chave:
        return None
    out = chave.strip().lower()
    return out or None


def bootstrap_agentes_padrao() -> dict:
    with db_session() as conn:
        for ag in AGENTES_PADRAO:
            conn.execute(
                """INSERT OR IGNORE INTO ia_agentes
                     (chave, nome, papel, canais, ativo, configuracao)
                   VALUES (?, ?, ?, ?, 1, ?)""",
                (
                    ag["chave"],
                    ag["nome"],
                    ag["papel"],
                    _json_dump(ag["canais"]),
                    _json_dump(ag["configuracao"]),
                ),
            )
        rows = conn.execute("SELECT id, chave FROM ia_agentes").fetchall()
        por_chave = {str(r["chave"]): int(r["id"]) for r in rows}
        for agente_chave, sub in SUBAGENTES_PADRAO.items():
            agente_id = por_chave.get(agente_chave)
            if not agente_id:
                continue
            conn.execute(
                """INSERT OR IGNORE INTO ia_subagentes
                     (agente_id, chave, nome, papel, ativo, configuracao)
                   VALUES (?, ?, ?, ?, 1, ?)""",
                (
                    agente_id,
                    sub["chave"],
                    sub["nome"],
                    sub["papel"],
                    _json_dump(sub["configuracao"]),
                ),
            )
    return {"agentes": listar_agentes()}


def listar_agentes(*, apenas_ativos: bool = False) -> list[dict]:
    where = "WHERE ativo = 1" if apenas_ativos else ""
    with db_session() as conn:
        rows = conn.execute(
            f"""SELECT id, chave, nome, papel, canais, ativo, configuracao,
                       ultimo_ciclo_em, criado_em, atualizado_em
                  FROM ia_agentes
                  {where}
              ORDER BY id""",
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["canais"] = _json_load_any(item.get("canais"), [])
        item["configuracao"] = _json_load_any(item.get("configuracao"), {})
        item["ativo"] = bool(item.get("ativo"))
        out.append(item)
    return out


def _buscar_agente_por_chave(chave: str | None) -> dict | None:
    c = _normalizar_chave(chave)
    if not c:
        return None
    with db_session() as conn:
        row = conn.execute(
            """SELECT id, chave, nome, papel, canais, ativo, configuracao
                 FROM ia_agentes
                WHERE chave = ?""",
            (c,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    item["canais"] = _json_load_any(item.get("canais"), [])
    item["configuracao"] = _json_load_any(item.get("configuracao"), {})
    item["ativo"] = bool(item.get("ativo"))
    return item


def listar_subagentes(*, agente_chave: str | None = None, apenas_ativos: bool = False) -> list[dict]:
    where = []
    params: list[Any] = []
    if agente_chave:
        where.append("a.chave = ?")
        params.append(agente_chave.strip().lower())
    if apenas_ativos:
        where.append("s.ativo = 1")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""
    with db_session() as conn:
        rows = conn.execute(
            f"""SELECT s.id, s.agente_id, s.chave, s.nome, s.papel, s.ativo,
                       s.configuracao, s.criado_em, s.atualizado_em,
                       a.chave AS agente_chave
                  FROM ia_subagentes s
                  JOIN ia_agentes a ON a.id = s.agente_id
                  {where_sql}
              ORDER BY s.id""",
            params,
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["configuracao"] = _json_load_any(item.get("configuracao"), {})
        item["ativo"] = bool(item.get("ativo"))
        out.append(item)
    return out


def _buscar_subagente_por_agente_id(agente_id: int | None) -> dict | None:
    if not agente_id:
        return None
    with db_session() as conn:
        row = conn.execute(
            """SELECT s.id, s.agente_id, s.chave, s.nome, s.papel, s.ativo, s.configuracao
                 FROM ia_subagentes s
                WHERE s.agente_id = ? AND s.ativo = 1
             ORDER BY s.id
                LIMIT 1""",
            (agente_id,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    item["configuracao"] = _json_load_any(item.get("configuracao"), {})
    item["ativo"] = bool(item.get("ativo"))
    return item


def _listar_conhecimentos_marketing_recentes(*, limite: int = 60) -> list[dict]:
    with db_session() as conn:
        rows = conn.execute(
            """SELECT k.id, k.topico, k.conteudo, k.tags, k.fonte
                 FROM ia_conhecimentos k
                 JOIN ia_agentes a ON a.id = k.agente_id
                WHERE a.chave = 'marketing'
                  AND k.valido = 1
             ORDER BY k.id DESC
                LIMIT ?""",
            (min(max(int(limite), 1), 200),),
        ).fetchall()
    out = []
    for r in rows:
        item = dict(r)
        item["tags"] = _json_load_any(item.get("tags"), [])
        out.append(item)
    return out


def _pegar_conhecimento_por_topico(itens: list[dict], prefixo: str) -> str:
    alvo = prefixo.strip().lower()
    for item in itens:
        topico = str(item.get("topico") or "").strip().lower()
        if topico.startswith(alvo):
            return str(item.get("conteudo") or "").strip()
    return ""


def _pegar_copys_recentes(itens: list[dict], *, max_itens: int = 3) -> list[str]:
    copys: list[str] = []
    for item in itens:
        topico = str(item.get("topico") or "").strip().lower()
        if not topico.startswith("instagram:copy:"):
            continue
        conteudo = str(item.get("conteudo") or "").strip()
        if conteudo:
            copys.append(conteudo)
        if len(copys) >= max_itens:
            break
    return copys


def _pegar_noticias_recentes(itens: list[dict], *, max_itens: int = 3) -> list[str]:
    noticias: list[str] = []
    for item in itens:
        topico = str(item.get("topico") or "").strip().lower()
        if not topico.startswith("noticia:"):
            continue
        conteudo = str(item.get("conteudo") or "").strip()
        if conteudo:
            noticias.append(conteudo)
        if len(noticias) >= max_itens:
            break
    return noticias


def _gerar_resposta_local_marketing(tarefa: dict, payload: dict) -> dict:
    mensagem = str((payload or {}).get("mensagem") or "").strip().lower()
    conhecimentos = _listar_conhecimentos_marketing_recentes(limite=90)
    bio_base = _pegar_conhecimento_por_topico(conhecimentos, "instagram:perfil")
    persona = _pegar_conhecimento_por_topico(conhecimentos, "instagram:persona")
    cta = _pegar_conhecimento_por_topico(conhecimentos, "instagram:cta")
    dm = _pegar_conhecimento_por_topico(conhecimentos, "instagram:interacao:dm")
    copys = _pegar_copys_recentes(conhecimentos, max_itens=3)
    noticias = _pegar_noticias_recentes(conhecimentos, max_itens=3)

    if "bio" in mensagem or "perfil" in mensagem:
        partes = [
            "Nome de perfil: Priscila Vasconcelos | Corretora em VDC",
            "Bio: Priscila Vasconcelos | CRECI/BA 29.231 | Casas e terrenos em Vitoria da Conquista | WhatsApp no link.",
            "Destaques: Imoveis | Terrenos | Clientes | Financiamento | Contato",
        ]
        if bio_base:
            partes.append(f"Base cadastrada: {bio_base}")
        if persona:
            partes.append(f"Tom de voz: {persona}")
        if cta:
            partes.append(f"CTA: {cta}")
        resposta = "\n".join(partes)
        return {
            "rota": "marketing_instagram",
            "modelo": "marketing_local",
            "fallback": False,
            "resposta": resposta,
            "lead_score": 68,
            "lead_stage": "morno",
            "lead_next_question": "Qual bairro priorizar para a primeira semana?",
            "provider_metadata": {"modo": "offline_local", "tarefas_suportadas": ["bio", "perfil"]},
        }

    if "calendario" in mensagem or "cronograma" in mensagem or "7 dias" in mensagem:
        dias = [
            "Dia 1: Reel de apresentacao da corretora + CTA para WhatsApp.",
            "Dia 2: Carrossel 'como escolher bairro em Vitoria da Conquista'.",
            "Dia 3: Story com enquete de faixa de valor e prazo.",
            "Dia 4: Post educativo sobre financiamento e simulacao.",
            "Dia 5: Carrossel com oportunidade de casa/terreno e prova social.",
            "Dia 6: Reel 'erros comuns ao comprar imovel' + caixa de perguntas.",
            "Dia 7: Story com chamada para consultoria rapida no WhatsApp.",
        ]
        if noticias:
            dias.append("Noticias atuais para integrar no roteiro:")
            for idx, n in enumerate(noticias, start=1):
                dias.append(f"Noticia {idx}: {n}")
        if copys:
            dias.append("Copys prontas para reaproveitar:")
            for idx, c in enumerate(copys, start=1):
                dias.append(f"Copy {idx}: {c}")
        resposta = "\n".join(dias)
        return {
            "rota": "marketing_instagram",
            "modelo": "marketing_local",
            "fallback": False,
            "resposta": resposta,
            "lead_score": 70,
            "lead_stage": "morno",
            "lead_next_question": "Quer focar mais em comprador de casa ou terreno?",
            "provider_metadata": {"modo": "offline_local", "tarefas_suportadas": ["calendario"]},
        }

    if "story" in mensagem and ("roteiro" in mensagem or "enquete" in mensagem):
        resposta = "\n".join(
            [
                "Story 1: 'Qual bairro voce quer morar em Vitoria da Conquista?' (caixa de pergunta)",
                "Story 2: 'Voce procura casa pronta ou terreno para construir?' (enquete)",
                "Story 3: 'Faixa de valor: ate 250k / 250k-450k / acima de 450k' (enquete)",
                "Story 4: 'Prazo de compra: imediato / 3 meses / 6+ meses' (enquete)",
                "Story 5: 'Me chama no WhatsApp e eu te envio 3 opcoes filtradas hoje.'",
            ]
        )
        return {
            "rota": "marketing_instagram",
            "modelo": "marketing_local",
            "fallback": False,
            "resposta": resposta,
            "lead_score": 66,
            "lead_stage": "morno",
            "lead_next_question": "Qual faixa de valor teve mais respostas?",
            "provider_metadata": {"modo": "offline_local", "tarefas_suportadas": ["stories"]},
        }

    if "dm" in mensagem or "respostas prontas" in mensagem:
        linhas = [
            "DM 1 (entrada): Oi! Vi seu interesse. Busca casa ou terreno em qual bairro de Vitoria da Conquista?",
            "DM 2 (qualificacao): Qual faixa de valor voce quer trabalhar agora?",
            "DM 3 (prazo): Seu prazo de compra e imediato, em 3 meses ou mais?",
            "DM 4 (acao): Posso te mandar 3 opcoes objetivas no WhatsApp agora.",
            "DM 5 (frio): Sem pressa, te envio oportunidades quando surgir algo no seu perfil.",
            "DM 6 (morno): Tenho opcoes aderentes. Quer priorizar financiamento ou pagamento a vista?",
            "DM 7 (quente): Tenho 2 opcoes com boa liquidez. Te envio ainda hoje.",
        ]
        if dm:
            linhas.append(f"Playbook DM base: {dm}")
        resposta = "\n".join(linhas)
        return {
            "rota": "marketing_instagram",
            "modelo": "marketing_local",
            "fallback": False,
            "resposta": resposta,
            "lead_score": 67,
            "lead_stage": "morno",
            "lead_next_question": "Qual template de DM converteu melhor hoje?",
            "provider_metadata": {"modo": "offline_local", "tarefas_suportadas": ["dm"]},
        }

    if "copom" in mensagem or "abecip" in mensagem or "fipezap" in mensagem or "noticia" in mensagem:
        blocos = ["Pauta de noticias atual para Instagram:"]
        if noticias:
            for idx, n in enumerate(noticias, start=1):
                blocos.append(f"{idx}. {n}")
        else:
            blocos.append("Sem noticia cadastrada no banco para esse tema.")
        if copys:
            blocos.append("Sugestao de copy curta para publicar:")
            for idx, c in enumerate(copys, start=1):
                blocos.append(f"Copy {idx}: {c}")
        resposta = "\n".join(blocos)
        return {
            "rota": "marketing_instagram",
            "modelo": "marketing_local",
            "fallback": False,
            "resposta": resposta,
            "lead_score": 69,
            "lead_stage": "morno",
            "lead_next_question": "Quer transformar uma dessas pautas em carrossel ou reel primeiro?",
            "provider_metadata": {"modo": "offline_local", "tarefas_suportadas": ["noticias"]},
        }

    resposta = (
        "Plano comercial Instagram pronto: ajustar perfil, publicar conteudo educativo local, "
        "usar CTA para WhatsApp e responder DM com 3 perguntas de qualificacao."
    )
    return {
        "rota": "marketing_instagram",
        "modelo": "marketing_local",
        "fallback": False,
        "resposta": resposta,
        "lead_score": 64,
        "lead_stage": "morno",
        "lead_next_question": "Qual publico vai receber foco inicial?",
        "provider_metadata": {"modo": "offline_local", "tarefas_suportadas": ["geral"]},
    }


def criar_conhecimento(
    *,
    conteudo: str,
    topico: str | None = None,
    tipo: str = "playbook",
    agente_chave: str | None = None,
    subagente_chave: str | None = None,
    tarefa_id: int | None = None,
    tags: list[str] | None = None,
    confianca: float = 0.8,
    fonte: str = "mentor",
) -> dict:
    ag = _buscar_agente_por_chave(agente_chave)
    sub_id = None
    if subagente_chave and ag:
        subs = listar_subagentes(agente_chave=ag["chave"], apenas_ativos=False)
        alvo = next((s for s in subs if s.get("chave") == subagente_chave), None)
        if alvo:
            sub_id = int(alvo["id"])
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO ia_conhecimentos
                 (agente_id, subagente_id, tarefa_id, tipo, topico, conteudo, tags, confianca, fonte, valido)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                ag["id"] if ag else None,
                sub_id,
                tarefa_id,
                (tipo or "playbook").strip().lower(),
                (topico or "").strip() or None,
                conteudo.strip(),
                _json_dump(tags or []),
                max(0.0, min(float(confianca), 1.0)),
                (fonte or "mentor").strip().lower(),
            ),
        )
        conhecimento_id = int(cur.lastrowid)
    return {"id": conhecimento_id}


def listar_conhecimentos(
    *,
    agente_chave: str | None = None,
    topico: str | None = None,
    apenas_validos: bool = True,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    where = []
    params: list[Any] = []
    if agente_chave:
        where.append("a.chave = ?")
        params.append(agente_chave.strip().lower())
    if topico:
        where.append("k.topico = ?")
        params.append(topico.strip())
    if apenas_validos:
        where.append("k.valido = 1")
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with db_session() as conn:
        total = conn.execute(
            f"""SELECT COUNT(*) AS n
                  FROM ia_conhecimentos k
             LEFT JOIN ia_agentes a ON a.id = k.agente_id
                  {where_sql}""",
            params,
        ).fetchone()["n"]
        rows = conn.execute(
            f"""SELECT k.id, k.agente_id, k.subagente_id, k.tarefa_id, k.tipo, k.topico,
                       k.conteudo, k.tags, k.confianca, k.fonte, k.valido,
                       k.criado_em, k.atualizado_em, a.chave AS agente_chave, a.nome AS agente_nome
                  FROM ia_conhecimentos k
             LEFT JOIN ia_agentes a ON a.id = k.agente_id
                  {where_sql}
              ORDER BY k.id DESC
                 LIMIT ? OFFSET ?""",
            [*params, min(max(limit, 1), 300), max(offset, 0)],
        ).fetchall()

    items = []
    for r in rows:
        item = dict(r)
        item["tags"] = _json_load_any(item.get("tags"), [])
        item["valido"] = bool(item.get("valido"))
        items.append(item)
    return {"total": int(total), "items": items}


def provisionar_instagram_vendas(*, contato: str | None = None) -> dict:
    """Prepara o perfil comercial no Instagram para operacao assistida por IA.

    Nao realiza login/postagem automatica: organiza playbook + tarefas de execucao.
    """
    bootstrap_agentes_padrao()

    conhecimentos = [
        (
            "instagram:bio",
            "Bio: Priscila Vasconcelos | CRECI/BA 29.231 | Vitoria da Conquista. "
            "Casas, terrenos e apartamentos. Atendimento rapido no WhatsApp.",
            ["instagram", "perfil", "bio", "vendas"],
        ),
        (
            "instagram:linha_editorial",
            "Linha editorial: 40% prova social, 30% ofertas de imoveis, 20% educacao "
            "imobiliaria local, 10% bastidores de atendimento.",
            ["instagram", "conteudo", "editorial", "vendas"],
        ),
        (
            "instagram:cta",
            "CTA padrao: 'Me chama no WhatsApp para receber opcoes filtradas por bairro e faixa.'",
            ["instagram", "cta", "whatsapp", "conversao"],
        ),
    ]
    conhecimento_ids: list[int] = []
    for topico, conteudo, tags in conhecimentos:
        k = criar_conhecimento(
            conteudo=conteudo,
            topico=topico,
            tipo="playbook",
            agente_chave="marketing",
            tags=tags,
            confianca=0.95,
            fonte="setup_instagram",
        )
        conhecimento_ids.append(int(k["id"]))

    payload_extra = {}
    if contato:
        payload_extra = {
            "contato": contato,
            "mensagem_notificacao": (
                "Setup Instagram concluido no sistema IA. "
                "Proximo passo: publicar perfil e iniciar prospeccao guiada."
            ),
        }

    tarefas_base = [
        "Definir proposta de valor da bio para atrair compradores de casas e terrenos em VDC.",
        "Montar 10 ideias de posts com CTA para WhatsApp focadas em captacao de leads quentes.",
        "Criar roteiro de DM inicial para identificar comprador potencial em ate 3 mensagens.",
        "Criar roteiro para identificar proprietarios com terreno para vender sem abordagem agressiva.",
    ]
    tarefa_ids: list[int] = []
    for mensagem in tarefas_base:
        t = criar_tarefa(
            origem="instagram",
            tipo="perfil_vendas",
            mensagem=mensagem,
            agente_chave="marketing",
            prioridade=10,
            payload_extra=payload_extra,
        )
        tarefa_ids.append(int(t["id"]))

    return {
        "ok": True,
        "agente": "marketing",
        "conhecimentos_criados": conhecimento_ids,
        "tarefas_criadas": tarefa_ids,
    }


def criar_tarefa(
    *,
    origem: str,
    tipo: str,
    mensagem: str,
    agente_chave: str | None = None,
    prioridade: int = 50,
    lead_id: int | None = None,
    payload_extra: dict | None = None,
    max_tentativas: int = 3,
) -> dict:
    ag = _buscar_agente_por_chave(agente_chave)
    payload = {
        "mensagem": mensagem.strip(),
        "origem": (origem or "web").strip().lower(),
        "tipo": (tipo or "lead_tracking").strip().lower(),
    }
    if payload_extra:
        payload["extra"] = payload_extra

    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO ia_tarefas
                 (agente_id, origem, tipo, status, prioridade, payload,
                  lead_id, max_tentativas)
               VALUES (?, ?, ?, 'pendente', ?, ?, ?, ?)""",
            (
                ag["id"] if ag else None,
                payload["origem"],
                payload["tipo"],
                min(max(int(prioridade), 1), 100),
                _json_dump(payload),
                lead_id,
                min(max(int(max_tentativas), 1), 10),
            ),
        )
        tarefa_id = int(cur.lastrowid)

    return detalhar_tarefa(tarefa_id) or {"id": tarefa_id}


def listar_tarefas(
    *,
    status: str | None = None,
    origem: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    where = []
    params: list[Any] = []
    if status:
        where.append("t.status = ?")
        params.append(status.strip().lower())
    if origem:
        where.append("t.origem = ?")
        params.append(origem.strip().lower())
    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    with db_session() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS n FROM ia_tarefas t {where_sql}",
            params,
        ).fetchone()["n"]
        rows = conn.execute(
            f"""SELECT t.id, t.agente_id, t.origem, t.tipo, t.status, t.prioridade,
                       t.payload, t.resultado, t.tentativas, t.max_tentativas, t.ultimo_erro,
                       t.lead_id, t.criado_em, t.atualizado_em, t.concluido_em,
                       a.chave AS agente_chave, a.nome AS agente_nome
                  FROM ia_tarefas t
             LEFT JOIN ia_agentes a ON a.id = t.agente_id
                  {where_sql}
              ORDER BY CASE t.status
                           WHEN 'pendente' THEN 0
                           WHEN 'processando' THEN 1
                           WHEN 'erro' THEN 2
                           WHEN 'concluida' THEN 3
                           ELSE 4
                       END,
                       t.prioridade ASC,
                       t.id DESC
                 LIMIT ? OFFSET ?""",
            [*params, min(max(limit, 1), 200), max(offset, 0)],
        ).fetchall()

    items = []
    for r in rows:
        item = dict(r)
        item["payload"] = _json_load_any(item.get("payload"), {})
        item["resultado"] = _json_load_any(item.get("resultado"), {})
        items.append(item)
    return {"total": int(total), "items": items}


def detalhar_tarefa(tarefa_id: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute(
            """SELECT t.id, t.agente_id, t.origem, t.tipo, t.status, t.prioridade,
                       t.payload, t.resultado, t.tentativas, t.max_tentativas, t.ultimo_erro,
                       t.lead_id, t.criado_em, t.atualizado_em, t.concluido_em,
                       a.chave AS agente_chave, a.nome AS agente_nome
                  FROM ia_tarefas t
             LEFT JOIN ia_agentes a ON a.id = t.agente_id
                 WHERE t.id = ?""",
            (tarefa_id,),
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    item["payload"] = _json_load_any(item.get("payload"), {})
    item["resultado"] = _json_load_any(item.get("resultado"), {})
    return item


def _proxima_tarefa(*, origem: str | None = None, agente_chave: str | None = None) -> dict | None:
    where = ["t.status = 'pendente'"]
    params: list[Any] = []
    if origem:
        where.append("t.origem = ?")
        params.append(origem.strip().lower())
    if agente_chave:
        where.append("a.chave = ?")
        params.append(agente_chave.strip().lower())
    where_sql = " AND ".join(where)

    with db_session() as conn:
        row = conn.execute(
            f"""SELECT t.id, t.agente_id, t.origem, t.tipo, t.status, t.prioridade,
                       t.payload, t.resultado, t.tentativas, t.max_tentativas, t.ultimo_erro,
                       t.lead_id, a.chave AS agente_chave, a.nome AS agente_nome
                  FROM ia_tarefas t
             LEFT JOIN ia_agentes a ON a.id = t.agente_id
                 WHERE {where_sql}
              ORDER BY t.prioridade ASC, t.id ASC
                 LIMIT 1""",
            params,
        ).fetchone()
    if not row:
        return None
    item = dict(row)
    item["payload"] = _json_load_any(item.get("payload"), {})
    item["resultado"] = _json_load_any(item.get("resultado"), {})
    return item


def _marcar_processando(tarefa_id: int, tentativa: int) -> None:
    with db_session() as conn:
        conn.execute(
            """UPDATE ia_tarefas
                  SET status = 'processando',
                      tentativas = ?,
                      atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?""",
            (tentativa, tarefa_id),
        )


def _marcar_concluida(tarefa_id: int, resultado: dict) -> None:
    with db_session() as conn:
        conn.execute(
            """UPDATE ia_tarefas
                  SET status = 'concluida',
                      resultado = ?,
                      ultimo_erro = NULL,
                      atualizado_em = CURRENT_TIMESTAMP,
                      concluido_em = CURRENT_TIMESTAMP
                WHERE id = ?""",
            (_json_dump(resultado), tarefa_id),
        )


def _marcar_erro(tarefa_id: int, *, requeue: bool, erro: str, resultado: dict | None = None) -> None:
    status = "pendente" if requeue else "erro"
    with db_session() as conn:
        conn.execute(
            """UPDATE ia_tarefas
                  SET status = ?,
                      resultado = ?,
                      ultimo_erro = ?,
                      atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?""",
            (status, _json_dump(resultado or {}), erro[:1000], tarefa_id),
        )


def _atualizar_ultimo_ciclo_agente(agente_id: int | None) -> None:
    if not agente_id:
        return
    agora = datetime.utcnow().isoformat()
    with db_session() as conn:
        conn.execute(
            "UPDATE ia_agentes SET ultimo_ciclo_em = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
            (agora, agente_id),
        )


def _auditar_resultado_subagente(subagente: dict | None, resultado: dict) -> dict:
    """Auditoria rapida do subagente: sinaliza risco e sugere correcao."""
    resposta = str(resultado.get("resposta") or "")
    palavras = [p for p in resposta.split() if p]
    flags: list[str] = []
    sugestoes: list[str] = []

    if resultado.get("fallback"):
        flags.append("fallback_ativo")
        sugestoes.append("Configurar chaves de IA para sair do modo offline.")

    if len(palavras) < 12:
        flags.append("resposta_curta")
        sugestoes.append("Expandir com contexto de bairro/faixa e 1 pergunta objetiva.")

    if (resultado.get("rota") or "") == "negociacao" and "?" not in resposta:
        flags.append("sem_pergunta_qualificacao")
        sugestoes.append("Adicionar pergunta de qualificacao (orcamento, prazo ou bairro).")

    score = int(resultado.get("lead_score") or 0)
    min_score = 35
    if subagente:
        cfg = subagente.get("configuracao") or {}
        if isinstance(cfg, dict):
            min_score = int(cfg.get("min_score") or min_score)
    if score < min_score:
        flags.append("lead_score_baixo")
        sugestoes.append("Coletar dado-chave faltante para elevar score do lead.")

    status = "ok" if not flags else "atencao"
    return {
        "subagente": subagente.get("chave") if subagente else None,
        "status": status,
        "flags": flags,
        "sugestoes": sugestoes,
    }


def _registrar_feedback_automatico(tarefa_id: int, agente_id: int | None, supervisao: dict) -> None:
    if not supervisao.get("flags"):
        return
    correcao = " | ".join(supervisao.get("sugestoes") or [])
    if not correcao:
        return
    with db_session() as conn:
        conn.execute(
            """INSERT INTO ia_feedback
                 (tarefa_id, agente_id, mentor_email, nota, correcao, reabrir_tarefa)
               VALUES (?, ?, ?, ?, ?, 0)""",
            (
                tarefa_id,
                agente_id,
                f"subagente:{supervisao.get('subagente') or 'auto'}",
                2,
                correcao[:2000],
            ),
        )


def _gravar_conhecimento_execucao(
    *,
    tarefa: dict,
    subagente: dict | None,
    resultado: dict,
    supervisao: dict,
) -> None:
    rota = str(resultado.get("rota") or "triagem")
    origem = str(tarefa.get("origem") or "web")
    lead_stage = str(resultado.get("lead_stage") or "")
    resumo = str(resultado.get("resposta") or "").strip()
    if not resumo:
        resumo = "sem resposta textual"
    if len(resumo) > 1200:
        resumo = resumo[:1200]
    flags = supervisao.get("flags") or []
    tags = [rota, origem]
    if lead_stage:
        tags.append(lead_stage)
    if resultado.get("fallback"):
        tags.append("fallback")
    tags.extend([f"flag:{f}" for f in flags])
    confianca = 0.9
    if resultado.get("fallback"):
        confianca -= 0.35
    confianca -= 0.08 * len(flags)
    confianca = max(0.1, min(confianca, 1.0))

    with db_session() as conn:
        conn.execute(
            """INSERT INTO ia_conhecimentos
                 (agente_id, subagente_id, tarefa_id, tipo, topico, conteudo,
                  tags, confianca, fonte, valido)
               VALUES (?, ?, ?, 'aprendizado', ?, ?, ?, ?, 'operacao_ia', 1)""",
            (
                tarefa.get("agente_id"),
                subagente.get("id") if subagente else None,
                tarefa.get("id"),
                f"{rota}:{origem}",
                resumo,
                _json_dump(tags),
                confianca,
            ),
        )


def _notificar_contato_se_configurado(payload: dict, resultado: dict) -> dict | None:
    extra = payload.get("extra") if isinstance(payload, dict) else None
    if not isinstance(extra, dict):
        return None
    contato = str(extra.get("contato") or "").strip()
    if not contato:
        return None

    mensagem = str(extra.get("mensagem_notificacao") or "").strip()
    if not mensagem:
        rota = resultado.get("rota") or "triagem"
        stage = resultado.get("lead_stage") or "frio"
        mensagem = (
            "Atualizacao da operacao IA Priscila:\n"
            f"Rota: {rota}\n"
            f"Stage: {stage}\n"
            "Identificamos potencial lead e recomendamos contato rapido."
        )

    try:
        from app import whatsapp

        envio = whatsapp.enviar_mensagem(contato, mensagem)
        return {
            "contato": contato,
            "enviado": bool(envio.enviado),
            "fallback": bool(envio.fallback),
            "mensagem_id": envio.mensagem_id,
            "erro": envio.erro,
        }
    except Exception as exc:
        return {
            "contato": contato,
            "enviado": False,
            "fallback": False,
            "erro": f"{type(exc).__name__}: {exc}",
        }


def _executar_tarefa_orquestrador(tarefa: dict, payload: dict) -> dict:
    """Orquestrador cria subtarefas para os demais agentes."""
    base = str(payload.get("mensagem") or "Coordenar prospeccao e qualificacao de leads.").strip()
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    contato = str((extra or {}).get("contato") or "").strip()
    payload_extra = {"contato": contato} if contato else {}

    plano = [
        ("procuradora", "instagram", "prospeccao_alvo", f"{base} Foco: identificar oportunidade de venda."),
        ("rastreadora", "instagram", "rastreio_followup", f"{base} Foco: separar urgentes e mornos."),
        ("leads", "site", "qualificacao", f"{base} Foco: converter em proxima acao clara."),
        ("marketing", "web", "conteudo_outreach", f"{base} Foco: mensagem de entrada e CTA."),
    ]
    filhos = []
    for agente, origem, tipo, mensagem in plano:
        t = criar_tarefa(
            origem=origem,
            tipo=tipo,
            mensagem=mensagem,
            agente_chave=agente,
            prioridade=max(1, int(tarefa.get("prioridade") or 10)),
            payload_extra=payload_extra,
        )
        filhos.append(int(t["id"]))

    return {
        "rota": "orquestracao",
        "modelo": "orquestrador_local",
        "fallback": False,
        "resposta": f"Orquestrador criou {len(filhos)} subtarefas para execucao paralela.",
        "lead_score": 55,
        "lead_stage": "morno",
        "lead_next_question": "Validar qual canal trouxe maior resposta.",
        "provider_metadata": {"subtarefas": filhos},
    }


def _executar_tarefa_corretor(tarefa: dict, payload: dict) -> dict:
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    tarefa_origem = (extra or {}).get("tarefa_origem_id")
    agente_origem = (extra or {}).get("agente_origem") or "desconhecido"
    sugestoes = (extra or {}).get("sugestoes") or []
    if not isinstance(sugestoes, list):
        sugestoes = [str(sugestoes)]
    conteudo = (
        f"Correcao aplicada para tarefa {tarefa_origem} do agente {agente_origem}: "
        + " | ".join(str(s) for s in sugestoes if s)
    ).strip()
    if conteudo.endswith(":"):
        conteudo += " reforcar coleta de contexto e proxima acao."
    k = criar_conhecimento(
        conteudo=conteudo,
        topico=f"corretor:{agente_origem}",
        tipo="correcao",
        agente_chave="corretor",
        tarefa_id=tarefa_origem if isinstance(tarefa_origem, int) else None,
        tags=["corretor", "erro", "aprendizado"],
        confianca=0.92,
        fonte="corretor_auto",
    )
    return {
        "rota": "correcao",
        "modelo": "corretor_local",
        "fallback": False,
        "resposta": "Corretor registrou melhoria e playbook para o erro detectado.",
        "lead_score": 60,
        "lead_stage": "morno",
        "lead_next_question": "Aplicar melhoria no proximo ciclo para validar ganho.",
        "provider_metadata": {
            "conhecimento_id": k["id"],
            "tarefa_origem_id": tarefa_origem,
            "agente_origem": agente_origem,
        },
    }


def _agendar_tarefa_corretor(*, tarefa_id: int, agente_chave: str, supervisao: dict) -> int | None:
    if agente_chave == "corretor":
        return None
    if not supervisao.get("flags"):
        return None
    msg = (
        f"Revisar erro/alerta da tarefa {tarefa_id} do agente {agente_chave} "
        "e consolidar melhoria objetiva no playbook."
    )
    t = criar_tarefa(
        origem="interno",
        tipo="correcao_continua",
        mensagem=msg,
        agente_chave="corretor",
        prioridade=2,
        payload_extra={
            "tarefa_origem_id": tarefa_id,
            "agente_origem": agente_chave,
            "sugestoes": supervisao.get("sugestoes") or [],
        },
    )
    return int(t["id"])


def executar_ciclo(*, limite: int = 20, origem: str | None = None, agente_chave: str | None = None) -> dict:
    processadas = 0
    concluidas = 0
    erros = 0
    itens: list[dict] = []
    limite_real = min(max(int(limite), 1), 200)

    for _ in range(limite_real):
        tarefa = _proxima_tarefa(origem=origem, agente_chave=agente_chave)
        if not tarefa:
            break
        processadas += 1
        tentativa = int(tarefa.get("tentativas") or 0) + 1
        max_tentativas = int(tarefa.get("max_tentativas") or 3)
        _marcar_processando(int(tarefa["id"]), tentativa)

        payload = tarefa.get("payload") or {}
        mensagem = str(payload.get("mensagem") or "").strip()
        if not mensagem:
            mensagem = "Encontrar e qualificar oportunidade de lead com contexto disponivel."
        historico = payload.get("historico") if isinstance(payload.get("historico"), list) else []
        tem_imagem = bool(payload.get("tem_imagem"))

        try:
            agente_atual = (tarefa.get("agente_chave") or "")
            if agente_atual == "orquestrador":
                out = _executar_tarefa_orquestrador(tarefa, payload)
            elif agente_atual == "corretor":
                out = _executar_tarefa_corretor(tarefa, payload)
            else:
                out = responder(mensagem, historico=historico, tem_imagem=tem_imagem)
                if agente_atual == "marketing" and bool(out.get("fallback")):
                    out = _gerar_resposta_local_marketing(tarefa, payload)
            subagente = _buscar_subagente_por_agente_id(tarefa.get("agente_id"))
            resultado = {
                "rota": out.get("rota"),
                "modelo": out.get("modelo"),
                "fallback": bool(out.get("fallback")),
                "resposta": out.get("resposta"),
                "lead_score": out.get("lead_score"),
                "lead_stage": out.get("lead_stage"),
                "lead_next_question": out.get("lead_next_question"),
                "provider_metadata": out.get("provider_metadata") or {},
            }
            supervisao = _auditar_resultado_subagente(subagente, resultado)
            resultado["supervisao"] = supervisao
            notificacao = _notificar_contato_se_configurado(payload, resultado)
            if notificacao:
                resultado["notificacao"] = notificacao
            _marcar_concluida(int(tarefa["id"]), resultado)
            _atualizar_ultimo_ciclo_agente(tarefa.get("agente_id"))
            _registrar_feedback_automatico(int(tarefa["id"]), tarefa.get("agente_id"), supervisao)
            corretor_task_id = _agendar_tarefa_corretor(
                tarefa_id=int(tarefa["id"]),
                agente_chave=agente_atual,
                supervisao=supervisao,
            )
            _gravar_conhecimento_execucao(
                tarefa={"id": int(tarefa["id"]), "agente_id": tarefa.get("agente_id"), "origem": tarefa.get("origem")},
                subagente=subagente,
                resultado=resultado,
                supervisao=supervisao,
            )
            concluidas += 1
            itens.append(
                {
                    "tarefa_id": int(tarefa["id"]),
                    "status": "concluida",
                    "agente_chave": tarefa.get("agente_chave") or "sem_agente",
                    "modelo": out.get("modelo"),
                    "fallback": bool(out.get("fallback")),
                    "rota": out.get("rota"),
                    "supervisao_status": supervisao.get("status"),
                    "corretor_tarefa_id": corretor_task_id,
                }
            )

            registrar_execucao_ia(
                agente=f"operacao_ia:{tarefa.get('agente_chave') or 'sem_agente'}",
                evento="operacao_ia.ciclo",
                modelo=str(out.get("modelo") or "fallback"),
                fallback=bool(out.get("fallback")),
                duracao_ms=None,
                metadata={
                    "tarefa_id": int(tarefa["id"]),
                    "origem": tarefa.get("origem"),
                    "tipo": tarefa.get("tipo"),
                    "rota": out.get("rota"),
                    "lead_stage": out.get("lead_stage"),
                    "supervisao_status": supervisao.get("status"),
                    "supervisao_flags": supervisao.get("flags"),
                },
                lead_id=tarefa.get("lead_id"),
                chave_idempotencia=f"operacao_ia:{tarefa['id']}:tentativa:{tentativa}",
            )
        except Exception as exc:
            erros += 1
            requeue = tentativa < max_tentativas
            _marcar_erro(
                int(tarefa["id"]),
                requeue=requeue,
                erro=f"{type(exc).__name__}: {exc}",
                resultado={"erro": type(exc).__name__, "mensagem": str(exc)},
            )
            itens.append(
                {
                    "tarefa_id": int(tarefa["id"]),
                    "status": "pendente" if requeue else "erro",
                    "agente_chave": tarefa.get("agente_chave") or "sem_agente",
                    "erro": f"{type(exc).__name__}: {exc}",
                }
            )

    return {
        "processadas": processadas,
        "concluidas": concluidas,
        "erros": erros,
        "itens": itens,
    }


def registrar_feedback(
    *,
    tarefa_id: int,
    correcao: str,
    mentor_email: str | None = None,
    nota: int | None = None,
    reabrir_tarefa: bool = False,
) -> dict:
    tarefa = detalhar_tarefa(tarefa_id)
    if not tarefa:
        raise ValueError("tarefa nao encontrada")
    nota_ok = None
    if nota is not None:
        nota_ok = min(max(int(nota), 1), 5)

    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO ia_feedback
                 (tarefa_id, agente_id, mentor_email, nota, correcao, reabrir_tarefa)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                tarefa_id,
                tarefa.get("agente_id"),
                (mentor_email or "").strip().lower() or None,
                nota_ok,
                correcao.strip(),
                1 if reabrir_tarefa else 0,
            ),
        )
        feedback_id = int(cur.lastrowid)
        if reabrir_tarefa:
            conn.execute(
                """UPDATE ia_tarefas
                      SET status = 'pendente',
                          atualizado_em = CURRENT_TIMESTAMP
                    WHERE id = ?""",
                (tarefa_id,),
            )
        conn.execute(
            """INSERT INTO ia_conhecimentos
                 (agente_id, tarefa_id, tipo, topico, conteudo, tags, confianca, fonte, valido)
               VALUES (?, ?, 'correcao', ?, ?, ?, ?, 'mentor', 1)""",
            (
                tarefa.get("agente_id"),
                tarefa_id,
                f"correcao:{tarefa.get('agente_chave') or 'geral'}",
                correcao.strip(),
                _json_dump(["feedback", "mentor"] + (["reaberta"] if reabrir_tarefa else [])),
                0.95 if nota_ok and nota_ok >= 4 else 0.8,
            ),
        )

    return {
        "id": feedback_id,
        "tarefa_id": tarefa_id,
        "reaberta": bool(reabrir_tarefa),
    }


def gerar_relatorio_operacao(*, horas: int = 24, limite_itens: int = 30) -> dict:
    janela_horas = max(1, min(int(horas), 24 * 30))
    limite = max(5, min(int(limite_itens), 200))
    janela = f"-{janela_horas} hours"

    with db_session() as conn:
        tarefas = conn.execute(
            """SELECT t.id, t.origem, t.tipo, t.status, t.prioridade, t.tentativas,
                      t.max_tentativas, t.ultimo_erro, t.resultado, t.criado_em,
                      t.atualizado_em, t.concluido_em, a.chave AS agente_chave, a.nome AS agente_nome
                 FROM ia_tarefas t
            LEFT JOIN ia_agentes a ON a.id = t.agente_id
                WHERE t.criado_em >= datetime('now', ?)
             ORDER BY t.id DESC
                LIMIT ?""",
            (janela, limite),
        ).fetchall()

        feedbacks = conn.execute(
            """SELECT f.id, f.tarefa_id, f.mentor_email, f.nota, f.correcao, f.reabrir_tarefa, f.criado_em,
                      a.chave AS agente_chave
                 FROM ia_feedback f
            LEFT JOIN ia_agentes a ON a.id = f.agente_id
                WHERE f.criado_em >= datetime('now', ?)
             ORDER BY f.id DESC
                LIMIT ?""",
            (janela, limite),
        ).fetchall()

        conhecimentos = conn.execute(
            """SELECT k.id, k.tipo, k.topico, k.tags, k.confianca, k.fonte, k.criado_em,
                      a.chave AS agente_chave
                 FROM ia_conhecimentos k
            LEFT JOIN ia_agentes a ON a.id = k.agente_id
                WHERE k.criado_em >= datetime('now', ?)
             ORDER BY k.id DESC
                LIMIT ?""",
            (janela, limite),
        ).fetchall()

    boas: list[dict] = []
    ruins: list[dict] = []
    por_agente: dict[str, dict[str, int]] = {}
    por_origem: dict[str, int] = {}

    for row in tarefas:
        item = dict(row)
        resultado = _json_load_any(item.get("resultado"), {})
        supervisao = resultado.get("supervisao") if isinstance(resultado, dict) else {}
        agente = item.get("agente_chave") or "sem_agente"
        origem = item.get("origem") or "desconhecida"
        por_origem[origem] = por_origem.get(origem, 0) + 1
        bucket = por_agente.setdefault(
            agente,
            {"total": 0, "concluidas": 0, "erros": 0, "atencao": 0},
        )
        bucket["total"] += 1

        has_flags = bool((supervisao or {}).get("flags"))
        is_fallback = bool((resultado or {}).get("fallback"))

        if item.get("status") == "concluida":
            bucket["concluidas"] += 1
            if not has_flags and not is_fallback:
                boas.append(
                    {
                        "tarefa_id": item["id"],
                        "agente": agente,
                        "origem": origem,
                        "rota": (resultado or {}).get("rota"),
                        "resumo": str((resultado or {}).get("resposta") or "")[:220],
                    }
                )
            else:
                bucket["atencao"] += 1
                ruins.append(
                    {
                        "tarefa_id": item["id"],
                        "agente": agente,
                        "origem": origem,
                        "motivo": "fallback" if is_fallback else "flags_supervisao",
                        "flags": (supervisao or {}).get("flags") or [],
                    }
                )
        elif item.get("status") == "erro":
            bucket["erros"] += 1
            ruins.append(
                {
                    "tarefa_id": item["id"],
                    "agente": agente,
                    "origem": origem,
                    "motivo": "erro_execucao",
                    "erro": item.get("ultimo_erro"),
                }
            )

    feedback_items = []
    for row in feedbacks:
        f = dict(row)
        feedback_items.append(
            {
                "id": f["id"],
                "tarefa_id": f["tarefa_id"],
                "agente": f.get("agente_chave") or "sem_agente",
                "mentor": f.get("mentor_email"),
                "nota": f.get("nota"),
                "correcao": str(f.get("correcao") or "")[:220],
                "reabriu": bool(f.get("reabrir_tarefa")),
                "criado_em": f.get("criado_em"),
            }
        )

    conhecimento_items = []
    for row in conhecimentos:
        k = dict(row)
        conhecimento_items.append(
            {
                "id": k["id"],
                "agente": k.get("agente_chave") or "sem_agente",
                "tipo": k.get("tipo"),
                "topico": k.get("topico"),
                "tags": _json_load_any(k.get("tags"), []),
                "confianca": k.get("confianca"),
                "fonte": k.get("fonte"),
                "criado_em": k.get("criado_em"),
            }
        )

    return {
        "janela_horas": janela_horas,
        "totais": {
            "tarefas": len(tarefas),
            "boas": len(boas),
            "ruins": len(ruins),
            "feedbacks": len(feedback_items),
            "conhecimentos": len(conhecimento_items),
        },
        "por_agente": por_agente,
        "por_origem": por_origem,
        "boas_acoes": boas[:limite],
        "ruins_acoes": ruins[:limite],
        "feedback_recente": feedback_items[:limite],
        "conhecimento_recente": conhecimento_items[:limite],
    }
