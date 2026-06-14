"""Depoimentos de clientes REAIS (prova social) — pesquisa apontou como maior alavancagem de conversão.

Regra: só depoimentos verdadeiros, com consentimento. A Priscila cadastra pelo admin.
"""
from __future__ import annotations

from typing import Any

from app.db import db_session


def _dict(row) -> dict[str, Any]:
    return dict(row) if row else {}


def listar(*, somente_ativos: bool = True) -> list[dict]:
    sql = "SELECT * FROM depoimentos"
    if somente_ativos:
        sql += " WHERE ativo = 1"
    sql += " ORDER BY ordem ASC, id DESC"
    with db_session() as conn:
        return [_dict(r) for r in conn.execute(sql).fetchall()]


def criar(*, nome: str, texto: str, estrelas: int = 5, contexto: str = "",
          foto_url: str = "", ativo: int = 1, ordem: int = 0) -> int:
    estrelas = max(1, min(5, int(estrelas)))
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO depoimentos (nome, texto, estrelas, contexto, foto_url, ativo, ordem)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nome.strip(), texto.strip(), estrelas, (contexto or "").strip(),
             (foto_url or "").strip(), 1 if ativo else 0, int(ordem)),
        )
        return int(cur.lastrowid)


def atualizar(dep_id: int, dados: dict) -> dict | None:
    campos = [c for c in ("nome", "texto", "estrelas", "contexto", "foto_url", "ativo", "ordem") if c in dados]
    if not campos:
        return detalhar(dep_id)
    sets = ", ".join(f"{c} = ?" for c in campos)
    vals = [dados[c] for c in campos]
    with db_session() as conn:
        conn.execute(f"UPDATE depoimentos SET {sets} WHERE id = ?", (*vals, dep_id))
    return detalhar(dep_id)


def detalhar(dep_id: int) -> dict | None:
    with db_session() as conn:
        r = conn.execute("SELECT * FROM depoimentos WHERE id = ?", (dep_id,)).fetchone()
    return _dict(r) if r else None


def remover(dep_id: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM depoimentos WHERE id = ?", (dep_id,))
    return cur.rowcount > 0
