"""Repositorio da Agenda (W4) — visitas, reunioes, follow-ups."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable

from app.db import db_session

TIPOS_VALIDOS = {"visita", "reuniao", "captacao", "followup", "bloqueio", "pessoal", "outro"}
STATUS_VALIDOS = {"agendado", "confirmado", "cancelado", "realizado"}

# Negocio em Vitoria da Conquista/BA -> horario de Brasilia (sem horario de verao).
FUSO_BR = timezone(timedelta(hours=-3))


def _agora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(s: str) -> datetime:
    """Aceita ISO com ou sem timezone; assume horario de BRASILIA (-03:00) se ausente.
    (Antes assumia UTC, o que gravava as visitas 3h adiantadas no painel.)"""
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=FUSO_BR)
    return dt


def criar(
    *,
    titulo: str,
    inicio: str,
    fim: str,
    tipo: str = "visita",
    lead_id: int | None = None,
    imovel_id: int | None = None,
    observacoes: str = "",
) -> int:
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"tipo invalido: {tipo}")
    dt_ini = _parse_iso(inicio)
    dt_fim = _parse_iso(fim)
    if dt_fim <= dt_ini:
        raise ValueError("fim precisa ser depois do inicio")
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO agenda (titulo, inicio, fim, tipo, lead_id, imovel_id, observacoes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (titulo.strip(), dt_ini.isoformat(), dt_fim.isoformat(), tipo,
             lead_id, imovel_id, observacoes),
        )
        novo_id = int(cur.lastrowid)

    # Espelha no Google Calendar (best-effort; no-op se nao configurado, NUNCA quebra a marcacao).
    try:
        from app import gcal
        ev = gcal.criar_evento(titulo=titulo.strip(), inicio_iso=dt_ini.isoformat(),
                               fim_iso=dt_fim.isoformat(), descricao=observacoes or "")
        if ev:
            with db_session() as conn:
                conn.execute("UPDATE agenda SET gcal_event_id = ? WHERE id = ?", (ev, novo_id))
    except Exception:  # pragma: no cover - defensivo
        import logging
        logging.getLogger("agenda").exception("falha ao espelhar evento %s no Google", novo_id)

    return novo_id


def listar(
    *,
    inicio_de: str | None = None,
    inicio_ate: str | None = None,
    status: str | None = None,
    lead_id: int | None = None,
) -> list[dict]:
    sql = "SELECT * FROM agenda WHERE 1=1"
    params: list = []
    if inicio_de:
        sql += " AND inicio >= ?"; params.append(_parse_iso(inicio_de).isoformat())
    if inicio_ate:
        sql += " AND inicio <= ?"; params.append(_parse_iso(inicio_ate).isoformat())
    if status:
        sql += " AND status = ?"; params.append(status)
    if lead_id is not None:
        sql += " AND lead_id = ?"; params.append(lead_id)
    sql += " ORDER BY inicio ASC"
    with db_session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def detalhar(item_id: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM agenda WHERE id = ?", (item_id,)).fetchone()
    return dict(row) if row else None


def atualizar(item_id: int, **campos) -> dict | None:
    permitidos = {"titulo", "inicio", "fim", "tipo", "status", "lead_id",
                  "imovel_id", "observacoes", "lembrete_enviado"}
    sets, params = [], []
    for k, v in campos.items():
        if k not in permitidos or v is None:
            continue
        if k == "tipo" and v not in TIPOS_VALIDOS:
            raise ValueError(f"tipo invalido: {v}")
        if k == "status" and v not in STATUS_VALIDOS:
            raise ValueError(f"status invalido: {v}")
        if k in ("inicio", "fim"):
            v = _parse_iso(str(v)).isoformat()
        sets.append(f"{k} = ?")
        params.append(v)
    if not sets:
        return detalhar(item_id)
    sets.append("atualizado_em = ?"); params.append(_agora_iso())
    params.append(item_id)
    with db_session() as conn:
        cur = conn.execute(f"UPDATE agenda SET {', '.join(sets)} WHERE id = ?", params)
        if cur.rowcount == 0:
            return None
    return detalhar(item_id)


def remover(item_id: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM agenda WHERE id = ?", (item_id,))
        return cur.rowcount > 0


def lembretes_a_enviar(*, janela_horas: int = 24) -> list[dict]:
    """Compromissos que comecam dentro das proximas N horas e ainda nao tiveram lembrete."""
    agora = datetime.now(timezone.utc)
    limite = agora + timedelta(hours=janela_horas)
    with db_session() as conn:
        rows = conn.execute(
            """SELECT * FROM agenda
               WHERE lembrete_enviado = 0
                 AND status IN ('agendado', 'confirmado')
                 AND inicio >= ?
                 AND inicio <= ?
               ORDER BY inicio ASC""",
            (agora.isoformat(), limite.isoformat()),
        ).fetchall()
    return [dict(r) for r in rows]


def marcar_lembrete_enviado(item_id: int) -> None:
    with db_session() as conn:
        conn.execute(
            "UPDATE agenda SET lembrete_enviado = 1, atualizado_em = ? WHERE id = ?",
            (_agora_iso(), item_id),
        )
