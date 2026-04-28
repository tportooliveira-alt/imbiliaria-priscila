"""W5 — Documentos do lead/imovel + consentimentos LGPD.

Storage em assets/documentos/{lead_id}/{uuid}_{nome}. Nunca usa nome original
como path. Exclui caminho absoluto da resposta publica.
"""
from __future__ import annotations

import os
import re
import uuid as _uuid
from pathlib import Path
from typing import Iterable

from app.db import db_session

TIPOS_VALIDOS: set[str] = {
    "rg", "cpf", "comprovante_renda", "comprovante_residencia",
    "contrato", "proposta", "outro",
}
TIPOS_CONSENTIMENTO: set[str] = {"contato", "marketing", "cookies", "termos"}

# Limites
TAMANHO_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
MIME_PERMITIDOS: set[str] = {
    "application/pdf",
    "image/jpeg", "image/png", "image/webp", "image/heic",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

_BASE_DIR = Path(os.environ.get("DOCS_DIR", "assets/documentos"))


def _slug_seguro(nome: str) -> str:
    nome = re.sub(r"[^A-Za-z0-9._-]+", "_", nome).strip("_")
    return nome[:80] or "arquivo"


def _base_dir() -> Path:
    base = Path(os.environ.get("DOCS_DIR", str(_BASE_DIR)))
    base.mkdir(parents=True, exist_ok=True)
    return base


# ─── Documentos ──────────────────────────────────────────────────────────────
def salvar(
    *,
    nome_original: str,
    conteudo: bytes,
    mime: str | None = None,
    lead_id: int | None = None,
    imovel_id: int | None = None,
    tipo: str = "outro",
    observacoes: str = "",
) -> dict:
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"tipo invalido: {tipo}")
    if not conteudo:
        raise ValueError("arquivo vazio")
    if len(conteudo) > TAMANHO_MAX_BYTES:
        raise ValueError(f"arquivo excede {TAMANHO_MAX_BYTES // (1024*1024)} MB")
    if mime and mime not in MIME_PERMITIDOS:
        raise ValueError(f"mime nao permitido: {mime}")

    pasta = _base_dir() / (str(lead_id) if lead_id else "_geral")
    pasta.mkdir(parents=True, exist_ok=True)

    nome_safe = _slug_seguro(nome_original)
    nome_disco = f"{_uuid.uuid4().hex}_{nome_safe}"
    caminho_abs = pasta / nome_disco
    caminho_abs.write_bytes(conteudo)
    caminho_rel = str(caminho_abs.relative_to(_base_dir().parent.parent)) \
        if _base_dir().is_absolute() is False else str(caminho_abs)

    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO documentos
               (lead_id, imovel_id, tipo, nome_original, caminho, mime,
                tamanho_bytes, observacoes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (lead_id, imovel_id, tipo, nome_original, str(caminho_abs),
             mime, len(conteudo), observacoes or ""),
        )
        doc_id = cur.lastrowid
    return detalhar(doc_id)  # type: ignore[return-value]


def listar(*, lead_id: int | None = None, imovel_id: int | None = None) -> list[dict]:
    sql = """SELECT id, lead_id, imovel_id, tipo, nome_original, mime,
                    tamanho_bytes, observacoes, criado_em
             FROM documentos WHERE 1=1"""
    params: list = []
    if lead_id is not None:
        sql += " AND lead_id = ?"
        params.append(lead_id)
    if imovel_id is not None:
        sql += " AND imovel_id = ?"
        params.append(imovel_id)
    sql += " ORDER BY criado_em DESC, id DESC"
    with db_session() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def detalhar(doc_id: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute(
            """SELECT id, lead_id, imovel_id, tipo, nome_original, caminho,
                      mime, tamanho_bytes, observacoes, criado_em
               FROM documentos WHERE id = ?""",
            (doc_id,),
        ).fetchone()
    return dict(row) if row else None


def remover(doc_id: int) -> bool:
    info = detalhar(doc_id)
    if not info:
        return False
    try:
        Path(info["caminho"]).unlink(missing_ok=True)
    except OSError:
        pass
    with db_session() as conn:
        conn.execute("DELETE FROM documentos WHERE id = ?", (doc_id,))
    return True


# ─── Consentimentos LGPD ─────────────────────────────────────────────────────
def registrar_consentimento(
    *,
    tipo: str = "contato",
    aceito: bool = True,
    lead_id: int | None = None,
    email: str | None = None,
    telefone: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
    texto_versao: str = "v1",
) -> int:
    if tipo not in TIPOS_CONSENTIMENTO:
        raise ValueError(f"tipo invalido: {tipo}")
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO consentimentos
               (lead_id, email, telefone, tipo, aceito, ip, user_agent, texto_versao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (lead_id, email, telefone, tipo, 1 if aceito else 0,
             ip, user_agent, texto_versao),
        )
        return int(cur.lastrowid)


def listar_consentimentos(
    *, lead_id: int | None = None, email: str | None = None,
) -> list[dict]:
    sql = """SELECT id, lead_id, email, telefone, tipo, aceito, ip,
                    user_agent, texto_versao, criado_em
             FROM consentimentos WHERE 1=1"""
    params: list = []
    if lead_id is not None:
        sql += " AND lead_id = ?"
        params.append(lead_id)
    if email:
        sql += " AND email = ?"
        params.append(email)
    sql += " ORDER BY criado_em DESC, id DESC"
    with db_session() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


__all__ = [
    "TIPOS_VALIDOS", "TIPOS_CONSENTIMENTO",
    "salvar", "listar", "detalhar", "remover",
    "registrar_consentimento", "listar_consentimentos",
]
