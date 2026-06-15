"""Repositório CRUD de empreendimentos (pai), tipologias (filhas) e imagens.

Espelha o padrão de `app/imoveis.py`. Soft-delete via `ativo=0` (nunca hard-delete
no empreendimento). Tipologias são One-to-Many e substituídas em bloco no salvar.
"""
from __future__ import annotations

import sqlite3
from typing import Any

from app.db import db_session
from app.imoveis import linha_para_dict, slugify

STATUS_OBRA = {"na_planta", "em_obras", "pronto"}


def slug_unico(base: str) -> str:
    slug = slugify(base) or "empreendimento"
    with db_session() as conn:
        existentes = {
            row["slug"]
            for row in conn.execute(
                "SELECT slug FROM empreendimentos WHERE slug = ? OR slug LIKE ?",
                (slug, f"{slug}-%"),
            )
        }
    if slug not in existentes:
        return slug
    n = 2
    while f"{slug}-{n}" in existentes:
        n += 1
    return f"{slug}-{n}"


# ─────────────────────────────────────────────────────────────────────────────
# Empreendimento (pai)
# ─────────────────────────────────────────────────────────────────────────────
def listar_empreendimentos(*, somente_ativos: bool = True) -> list[dict]:
    sql = "SELECT * FROM empreendimentos WHERE 1=1"
    if somente_ativos:
        sql += " AND ativo = 1"
    sql += " ORDER BY destaque DESC, atualizado_em DESC"
    with db_session() as conn:
        rows = conn.execute(sql).fetchall()
    return [linha_para_dict(r) for r in rows]


def buscar_por_id(emp_id: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM empreendimentos WHERE id = ?", (emp_id,)).fetchone()
    return linha_para_dict(row)


def buscar_por_slug(slug: str) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM empreendimentos WHERE slug = ?", (slug,)).fetchone()
    return linha_para_dict(row)


def _normalizar_status(valor: Any) -> str:
    v = str(valor or "na_planta").strip().lower()
    return v if v in STATUS_OBRA else "na_planta"


def criar_empreendimento(dados: dict) -> dict:
    slug = slug_unico(f"{dados['nome']}-{dados.get('bairro', '')}")
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO empreendimentos
                (slug, nome, construtora, bairro, descricao, video_url,
                 status_obra, entrega_prevista, destaque, ativo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                slug,
                dados["nome"],
                dados.get("construtora", ""),
                dados.get("bairro", ""),
                dados.get("descricao", ""),
                dados.get("video_url"),
                _normalizar_status(dados.get("status_obra")),
                dados.get("entrega_prevista", ""),
                int(bool(dados.get("destaque", False))),
                int(bool(dados.get("ativo", True))),
            ),
        )
        novo_id = int(cur.lastrowid)
    if "tipologias" in dados:
        salvar_tipologias(novo_id, dados.get("tipologias") or [])
    return buscar_por_id(novo_id)


def atualizar_empreendimento(emp_id: int, dados: dict) -> dict | None:
    if not buscar_por_id(emp_id):
        return None
    campos_permitidos = {
        "nome", "construtora", "bairro", "descricao", "video_url",
        "entrega_prevista", "destaque", "ativo",
    }
    sets: list[str] = []
    params: list[Any] = []
    for k, v in dados.items():
        if k in campos_permitidos:
            sets.append(f"{k} = ?")
            params.append(int(v) if isinstance(v, bool) else v)
    if "status_obra" in dados:
        sets.append("status_obra = ?")
        params.append(_normalizar_status(dados["status_obra"]))
    if sets:
        sets.append("atualizado_em = CURRENT_TIMESTAMP")
        params.append(emp_id)
        with db_session() as conn:
            conn.execute(f"UPDATE empreendimentos SET {', '.join(sets)} WHERE id = ?", params)
    if "tipologias" in dados:
        salvar_tipologias(emp_id, dados.get("tipologias") or [])
    return buscar_por_id(emp_id)


def desativar_empreendimento(emp_id: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("UPDATE empreendimentos SET ativo = 0 WHERE id = ?", (emp_id,))
        return cur.rowcount > 0


# ─────────────────────────────────────────────────────────────────────────────
# Tipologias (filhas) — substituídas em bloco a cada salvar (simples e robusto)
# ─────────────────────────────────────────────────────────────────────────────
def listar_tipologias(emp_id: int) -> list[dict]:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM empreendimento_tipologias WHERE empreendimento_id = ? ORDER BY ordem ASC, id ASC",
            (emp_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def salvar_tipologias(emp_id: int, tipologias: list[dict]) -> list[dict]:
    """Substitui TODAS as tipologias do empreendimento pelas recebidas (na ordem dada)."""
    with db_session() as conn:
        conn.execute("DELETE FROM empreendimento_tipologias WHERE empreendimento_id = ?", (emp_id,))
        for i, t in enumerate(tipologias):
            nome = str(t.get("nome", "")).strip()
            if not nome:
                continue  # ignora linha vazia
            conn.execute(
                """INSERT INTO empreendimento_tipologias
                    (empreendimento_id, nome, area_util, quartos, suites, vagas, preco_a_partir, ordem)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    emp_id,
                    nome,
                    float(t.get("area_util", 0) or 0),
                    int(t.get("quartos", 0) or 0),
                    int(t.get("suites", 0) or 0),
                    int(t.get("vagas", 0) or 0),
                    float(t.get("preco_a_partir", 0) or 0),
                    int(t.get("ordem", i)),
                ),
            )
    return listar_tipologias(emp_id)


# ─────────────────────────────────────────────────────────────────────────────
# Imagens (galeria do empreendimento) — mesma estrutura de `imagens`
# ─────────────────────────────────────────────────────────────────────────────
_TIPOS_IMG = {"capa", "sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"}


def adicionar_imagem(emp_id: int, *, arquivo: str, tipo: str = "sala", legenda: str = "", ordem: int | None = None) -> dict:
    if tipo not in _TIPOS_IMG:
        tipo = "sala"
    with db_session() as conn:
        if ordem is None:
            row = conn.execute(
                "SELECT COALESCE(MAX(ordem), -1) + 1 AS prox FROM empreendimento_imagens WHERE empreendimento_id = ?",
                (emp_id,),
            ).fetchone()
            ordem = int(row["prox"])
        cur = conn.execute(
            """INSERT INTO empreendimento_imagens (empreendimento_id, arquivo, legenda, ordem, tipo)
               VALUES (?, ?, ?, ?, ?)""",
            (emp_id, arquivo, legenda, ordem, tipo),
        )
        novo_id = int(cur.lastrowid)
        row = conn.execute("SELECT * FROM empreendimento_imagens WHERE id = ?", (novo_id,)).fetchone()
    return dict(row)


def listar_imagens(emp_id: int) -> list[dict]:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM empreendimento_imagens WHERE empreendimento_id = ? ORDER BY ordem ASC, id ASC",
            (emp_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def remover_imagem(imagem_id: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM empreendimento_imagens WHERE id = ?", (imagem_id,))
        return cur.rowcount > 0


def detalhar(slug_ou_id: str | int) -> dict | None:
    """Empreendimento completo: dados + tipologias + imagens. Aceita slug ou id."""
    emp = buscar_por_id(int(slug_ou_id)) if str(slug_ou_id).isdigit() else buscar_por_slug(str(slug_ou_id))
    if not emp:
        return None
    emp["tipologias"] = listar_tipologias(emp["id"])
    emp["imagens"] = listar_imagens(emp["id"])
    return emp
