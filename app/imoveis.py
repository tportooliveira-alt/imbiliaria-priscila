"""Repositório CRUD de imóveis e imagens."""
from __future__ import annotations

import json
import re
import sqlite3
import unicodedata
from typing import Any

from app.db import db_session

TIPOS_COMODO = {"capa", "sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"}


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9\s-]", "", texto).lower().strip()
    texto = re.sub(r"[\s-]+", "-", texto)
    return texto[:120] or "imovel"


def slug_unico(base: str) -> str:
    slug = slugify(base)
    with db_session() as conn:
        existentes = {
            row["slug"]
            for row in conn.execute(
                "SELECT slug FROM imoveis WHERE slug = ? OR slug LIKE ?",
                (slug, f"{slug}-%"),
            )
        }
    if slug not in existentes:
        return slug
    n = 2
    while f"{slug}-{n}" in existentes:
        n += 1
    return f"{slug}-{n}"


def linha_para_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    d = dict(row)
    if "caracteristicas" in d and isinstance(d["caracteristicas"], str):
        try:
            d["caracteristicas"] = json.loads(d["caracteristicas"])
        except (TypeError, ValueError):
            d["caracteristicas"] = []
    if "destaque" in d:
        d["destaque"] = bool(d["destaque"])
    if "ativo" in d:
        d["ativo"] = bool(d["ativo"])
    return d


def listar_imoveis(*, somente_ativos: bool = True, bairro: str | None = None) -> list[dict]:
    sql = "SELECT * FROM imoveis WHERE 1=1"
    params: list[Any] = []
    if somente_ativos:
        sql += " AND ativo = 1"
    if bairro:
        sql += " AND lower(bairro) = lower(?)"
        params.append(bairro)
    sql += " ORDER BY destaque DESC, atualizado_em DESC"
    with db_session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [linha_para_dict(r) for r in rows]


def buscar_por_slug(slug: str) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM imoveis WHERE slug = ?", (slug,)).fetchone()
    return linha_para_dict(row)


def buscar_por_id(imovel_id: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM imoveis WHERE id = ?", (imovel_id,)).fetchone()
    return linha_para_dict(row)


def criar_imovel(dados: dict) -> dict:
    slug = slug_unico(f"{dados['titulo']}-{dados.get('bairro', '')}")
    caract = json.dumps(dados.get("caracteristicas", []), ensure_ascii=False)
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO imoveis
                (slug, titulo, bairro, tipo, quartos, suites, vagas,
                 area_util, preco, descricao, caracteristicas, destaque, ativo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                slug,
                dados["titulo"],
                dados["bairro"],
                dados["tipo"],
                int(dados.get("quartos", 0)),
                int(dados.get("suites", 0)),
                int(dados.get("vagas", 0)),
                float(dados.get("area_util", 0)),
                float(dados["preco"]),
                dados.get("descricao", ""),
                caract,
                int(bool(dados.get("destaque", False))),
                int(bool(dados.get("ativo", True))),
            ),
        )
        novo_id = int(cur.lastrowid)
    return buscar_por_id(novo_id)


def atualizar_imovel(imovel_id: int, dados: dict) -> dict | None:
    if not buscar_por_id(imovel_id):
        return None
    campos_permitidos = {
        "titulo", "bairro", "tipo", "quartos", "suites", "vagas",
        "area_util", "preco", "descricao", "destaque", "ativo",
    }
    sets: list[str] = []
    params: list[Any] = []
    for k, v in dados.items():
        if k in campos_permitidos:
            sets.append(f"{k} = ?")
            params.append(int(v) if isinstance(v, bool) else v)
    if "caracteristicas" in dados:
        sets.append("caracteristicas = ?")
        params.append(json.dumps(dados["caracteristicas"], ensure_ascii=False))
    if not sets:
        return buscar_por_id(imovel_id)
    sets.append("atualizado_em = CURRENT_TIMESTAMP")
    params.append(imovel_id)
    with db_session() as conn:
        conn.execute(f"UPDATE imoveis SET {', '.join(sets)} WHERE id = ?", params)
    return buscar_por_id(imovel_id)


def desativar_imovel(imovel_id: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("UPDATE imoveis SET ativo = 0 WHERE id = ?", (imovel_id,))
        return cur.rowcount > 0


# ─────────────────────────────────────────────────────────────────────────────
# Imagens
# ─────────────────────────────────────────────────────────────────────────────
def adicionar_imagem(
    imovel_id: int, *, arquivo: str, tipo: str = "sala", legenda: str = "", ordem: int | None = None
) -> dict:
    if tipo not in {"capa", "sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"}:
        tipo = "sala"
    with db_session() as conn:
        if ordem is None:
            row = conn.execute(
                "SELECT COALESCE(MAX(ordem), -1) + 1 AS prox FROM imagens WHERE imovel_id = ?",
                (imovel_id,),
            ).fetchone()
            ordem = int(row["prox"])
        cur = conn.execute(
            """INSERT INTO imagens (imovel_id, arquivo, legenda, ordem, tipo)
               VALUES (?, ?, ?, ?, ?)""",
            (imovel_id, arquivo, legenda, ordem, tipo),
        )
        novo_id = int(cur.lastrowid)
        row = conn.execute("SELECT * FROM imagens WHERE id = ?", (novo_id,)).fetchone()
    return dict(row)


def listar_imagens(imovel_id: int) -> list[dict]:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM imagens WHERE imovel_id = ? ORDER BY ordem ASC, id ASC",
            (imovel_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def remover_imagem(imagem_id: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM imagens WHERE id = ?", (imagem_id,))
        return cur.rowcount > 0


def atualizar_imagem(imagem_id: int, *, tipo: str | None = None, legenda: str | None = None) -> dict | None:
    """Atualiza tipo/legenda. Se virar 'capa', remove capa anterior do mesmo imovel."""
    tipos_validos = {"capa", "sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"}
    with db_session() as conn:
        row = conn.execute("SELECT * FROM imagens WHERE id = ?", (imagem_id,)).fetchone()
        if not row:
            return None
        sets = []
        params: list = []
        if tipo is not None:
            if tipo not in tipos_validos:
                raise ValueError(f"tipo invalido: {tipo}")
            if tipo == "capa":
                conn.execute(
                    "UPDATE imagens SET tipo = 'sala' WHERE imovel_id = ? AND tipo = 'capa' AND id != ?",
                    (row["imovel_id"], imagem_id),
                )
            sets.append("tipo = ?"); params.append(tipo)
        if legenda is not None:
            sets.append("legenda = ?"); params.append(legenda)
        if not sets:
            return dict(row)
        params.append(imagem_id)
        conn.execute(f"UPDATE imagens SET {', '.join(sets)} WHERE id = ?", params)
        novo = conn.execute("SELECT * FROM imagens WHERE id = ?", (imagem_id,)).fetchone()
    return dict(novo)


def reordenar_imagens(imovel_id: int, ordem_ids: list[int]) -> None:
    with db_session() as conn:
        for posicao, img_id in enumerate(ordem_ids):
            conn.execute(
                "UPDATE imagens SET ordem = ? WHERE id = ? AND imovel_id = ?",
                (posicao, img_id, imovel_id),
            )
