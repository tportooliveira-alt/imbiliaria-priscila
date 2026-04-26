"""Repositorio de leads (CRM) + classificacao automatica de temperatura.

Regras de temperatura (heuristica simples, ajustavel depois com ML):
- QUENTE: simulou + informou renda + comprometimento <= 30%
        ou: tem >= 5 interacoes em 7 dias
        ou: estagio in (visita, proposta)
- MORNO:  simulou OU avaliou OU tem 2-4 interacoes
- FRIO:   so visitou ou abandonou cedo

Score 0-100: derivado das interacoes (cada interacao vale pontos).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from app.db import db_session


# ─────────────────────────────────────────────────────────────────────────────
# Pontuacao por tipo de interacao
# ─────────────────────────────────────────────────────────────────────────────
PONTOS_INTERACAO = {
    "chat": 5,
    "simulacao": 15,
    "avaliacao": 15,
    "visita": 30,
    "whatsapp": 8,
    "email": 5,
    "nota": 0,
    "proposta": 50,
}

ESTAGIOS_VALIDOS = ("novo", "contatado", "qualificado", "visita", "proposta", "fechado", "perdido")
TEMPERATURAS = ("quente", "morno", "frio")
ORIGENS = ("site", "simulador", "avaliacao", "chat", "whatsapp", "indicacao", "manual", "vendedor")


@dataclass
class LeadResumo:
    id: int
    nome: str | None
    telefone: str | None
    email: str | None
    origem: str
    estagio: str
    temperatura: str
    score: int
    criado_em: str
    atualizado_em: str


# ─────────────────────────────────────────────────────────────────────────────
# Identificacao / criacao
# ─────────────────────────────────────────────────────────────────────────────
def _normalizar_telefone(tel: str | None) -> str | None:
    if not tel:
        return None
    return "".join(c for c in tel if c.isdigit()) or None


def _buscar_existente(conn, telefone: str | None, email: str | None) -> int | None:
    """Procura lead existente por telefone OU email (qualquer um que bater)."""
    if telefone:
        row = conn.execute("SELECT id FROM leads WHERE telefone = ?", (telefone,)).fetchone()
        if row:
            return row["id"]
    if email:
        row = conn.execute("SELECT id FROM leads WHERE email = ?", (email,)).fetchone()
        if row:
            return row["id"]
    return None


def upsert_lead(
    *,
    nome: str | None = None,
    telefone: str | None = None,
    email: str | None = None,
    origem: str = "site",
) -> int:
    """Cria ou atualiza lead. Retorna id."""
    if origem not in ORIGENS:
        origem = "site"
    tel_norm = _normalizar_telefone(telefone)
    email_norm = (email or "").strip().lower() or None

    with db_session() as conn:
        existente = _buscar_existente(conn, tel_norm, email_norm)
        if existente:
            # atualiza nome se ainda estava vazio
            if nome:
                conn.execute(
                    "UPDATE leads SET nome = COALESCE(NULLIF(nome, ''), ?), atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                    (nome, existente),
                )
            return existente
        cur = conn.execute(
            """INSERT INTO leads (nome, telefone, email, origem)
               VALUES (?, ?, ?, ?)""",
            (nome, tel_norm, email_norm, origem),
        )
        return int(cur.lastrowid)


def registrar_interacao(
    lead_id: int,
    *,
    tipo: str,
    descricao: str,
    metadata: dict | None = None,
    referencia_id: int | None = None,
) -> None:
    """Registra interacao + recalcula score/temperatura."""
    with db_session() as conn:
        conn.execute(
            """INSERT INTO lead_interacoes (lead_id, tipo, descricao, metadata, referencia_id)
               VALUES (?, ?, ?, ?, ?)""",
            (lead_id, tipo, descricao, json.dumps(metadata or {}, ensure_ascii=False), referencia_id),
        )
        conn.execute(
            "UPDATE leads SET atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
            (lead_id,),
        )
    _recalcular(lead_id)


# ─────────────────────────────────────────────────────────────────────────────
# Classificacao
# ─────────────────────────────────────────────────────────────────────────────
def _calcular_score(interacoes: list[dict]) -> int:
    score = 0
    for i in interacoes:
        score += PONTOS_INTERACAO.get(i["tipo"], 0)
    return min(100, score)


def _calcular_temperatura(estagio: str, score: int, interacoes: list[dict]) -> str:
    if estagio in ("visita", "proposta", "fechado"):
        return "quente"

    # comprometimento OK em alguma simulacao -> quente
    for i in interacoes:
        if i["tipo"] == "simulacao":
            md = i.get("metadata") or {}
            if md.get("comprometimento_ok") is True:
                return "quente"

    # interacoes recentes (7 dias)
    sete_dias_atras = datetime.utcnow() - timedelta(days=7)
    recentes = [
        i for i in interacoes
        if _parse_dt(i.get("criado_em")) and _parse_dt(i["criado_em"]) >= sete_dias_atras
    ]
    if len(recentes) >= 5:
        return "quente"

    if score >= 30:
        return "morno"
    if score >= 10:
        return "morno"
    return "frio"


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def _recalcular(lead_id: int) -> None:
    """Recalcula score + temperatura a partir das interacoes."""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT tipo, metadata, criado_em FROM lead_interacoes WHERE lead_id = ?",
            (lead_id,),
        ).fetchall()
        interacoes = []
        for r in rows:
            md = {}
            try:
                md = json.loads(r["metadata"] or "{}")
            except (TypeError, ValueError):
                md = {}
            interacoes.append({"tipo": r["tipo"], "metadata": md, "criado_em": r["criado_em"]})

        lead = conn.execute("SELECT estagio FROM leads WHERE id = ?", (lead_id,)).fetchone()
        if not lead:
            return
        score = _calcular_score(interacoes)
        temp = _calcular_temperatura(lead["estagio"], score, interacoes)
        conn.execute(
            "UPDATE leads SET score = ?, temperatura = ? WHERE id = ?",
            (score, temp, lead_id),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Consultas
# ─────────────────────────────────────────────────────────────────────────────
def listar(
    *,
    estagio: str | None = None,
    temperatura: str | None = None,
    origem: str | None = None,
    busca: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    where = []
    params: list = []
    if estagio:
        where.append("estagio = ?"); params.append(estagio)
    if temperatura:
        where.append("temperatura = ?"); params.append(temperatura)
    if origem:
        where.append("origem = ?"); params.append(origem)
    if busca:
        where.append("(nome LIKE ? OR telefone LIKE ? OR email LIKE ?)")
        like = f"%{busca}%"; params += [like, like, like]
    sql = "SELECT * FROM leads"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY atualizado_em DESC LIMIT ? OFFSET ?"
    params += [limit, offset]
    with db_session() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def detalhar(lead_id: int) -> dict | None:
    with db_session() as conn:
        lead = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        if not lead:
            return None
        interacoes = conn.execute(
            "SELECT * FROM lead_interacoes WHERE lead_id = ? ORDER BY criado_em DESC",
            (lead_id,),
        ).fetchall()
        tags = conn.execute(
            "SELECT tag FROM lead_tags WHERE lead_id = ?", (lead_id,),
        ).fetchall()
        out = dict(lead)
        out["interacoes"] = [dict(i) for i in interacoes]
        out["tags"] = [t["tag"] for t in tags]
        return out


def atualizar(lead_id: int, **campos) -> bool:
    permitidos = {"nome", "telefone", "email", "estagio", "observacoes", "responsavel_id"}
    sets = {k: v for k, v in campos.items() if k in permitidos and v is not None}
    if not sets:
        return False
    if "estagio" in sets and sets["estagio"] not in ESTAGIOS_VALIDOS:
        raise ValueError(f"estagio invalido: {sets['estagio']}")
    if "telefone" in sets:
        sets["telefone"] = _normalizar_telefone(sets["telefone"])
    sql = ", ".join(f"{k} = ?" for k in sets)
    params = list(sets.values()) + [lead_id]
    with db_session() as conn:
        conn.execute(
            f"UPDATE leads SET {sql}, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
            params,
        )
    if "estagio" in sets:
        _recalcular(lead_id)
    return True


def adicionar_tag(lead_id: int, tag: str) -> None:
    tag = tag.strip().lower()
    if not tag:
        return
    with db_session() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO lead_tags (lead_id, tag) VALUES (?, ?)",
            (lead_id, tag),
        )


def remover_tag(lead_id: int, tag: str) -> None:
    with db_session() as conn:
        conn.execute(
            "DELETE FROM lead_tags WHERE lead_id = ? AND tag = ?",
            (lead_id, tag.strip().lower()),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard agregados
# ─────────────────────────────────────────────────────────────────────────────
def dashboard() -> dict:
    with db_session() as conn:
        total = conn.execute("SELECT COUNT(*) AS n FROM leads").fetchone()["n"]
        por_estagio = {
            r["estagio"]: r["n"]
            for r in conn.execute(
                "SELECT estagio, COUNT(*) AS n FROM leads GROUP BY estagio"
            ).fetchall()
        }
        por_temperatura = {
            r["temperatura"]: r["n"]
            for r in conn.execute(
                "SELECT temperatura, COUNT(*) AS n FROM leads GROUP BY temperatura"
            ).fetchall()
        }
        por_origem = {
            r["origem"]: r["n"]
            for r in conn.execute(
                "SELECT origem, COUNT(*) AS n FROM leads GROUP BY origem"
            ).fetchall()
        }
        # 7 dias
        sete = (datetime.utcnow() - timedelta(days=7)).isoformat()
        novos_7d = conn.execute(
            "SELECT COUNT(*) AS n FROM leads WHERE criado_em >= ?", (sete,),
        ).fetchone()["n"]
        # simulacoes/avaliacoes totais
        simulacoes = conn.execute("SELECT COUNT(*) AS n FROM simulacoes").fetchone()["n"]
        avaliacoes = conn.execute("SELECT COUNT(*) AS n FROM avaliacoes").fetchone()["n"]
        # imoveis ativos
        imoveis_ativos = conn.execute(
            "SELECT COUNT(*) AS n FROM imoveis WHERE ativo = 1"
        ).fetchone()["n"]

        # ultimos 5 leads
        ultimos = [
            dict(r) for r in conn.execute(
                "SELECT id, nome, telefone, origem, temperatura, estagio, criado_em "
                "FROM leads ORDER BY criado_em DESC LIMIT 5"
            ).fetchall()
        ]

    return {
        "total_leads": total,
        "por_estagio": por_estagio,
        "por_temperatura": por_temperatura,
        "por_origem": por_origem,
        "novos_7d": novos_7d,
        "simulacoes": simulacoes,
        "avaliacoes": avaliacoes,
        "imoveis_ativos": imoveis_ativos,
        "ultimos_leads": ultimos,
    }
