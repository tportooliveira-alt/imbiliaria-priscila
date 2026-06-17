"""Autenticação — bcrypt + JWT + rate limit por IP.

Lê `JWT_SECRET` do env. Se não houver, gera um na hora (não persiste — só dev).
"""
from __future__ import annotations

import datetime as dt
import os
import secrets
import sqlite3

import bcrypt
import jwt

from app.db import db_session

JWT_ALG = "HS256"
JWT_TTL_HOURS = 8
LOGIN_LIMITE = 5            # tentativas
LOGIN_JANELA_MIN = 15       # janela em minutos


def _secret() -> str:
    s = os.getenv("JWT_SECRET")
    if not s:
        # Em producao, JWT_SECRET e OBRIGATORIO (falha rapido em vez de gerar um fragil).
        if os.getenv("ENV") == "production":
            raise RuntimeError("JWT_SECRET e obrigatorio em producao (defina no .env)")
        # fallback de DEV: gera e seta no processo (some quando reinicia)
        s = secrets.token_urlsafe(64)
        os.environ["JWT_SECRET"] = s
    return s


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verifica_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())
    except Exception:
        return False


def gerar_token(user_id: int, email: str, role: str) -> str:
    agora = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(agora.timestamp()),
        "exp": int((agora + dt.timedelta(hours=JWT_TTL_HOURS)).timestamp()),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALG)


def decodar_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Rate limit (SQLite — janela deslizante simples)
# ─────────────────────────────────────────────────────────────────────────────
def registrar_tentativa(ip: str) -> None:
    with db_session() as conn:
        conn.execute("INSERT INTO login_attempts (ip) VALUES (?)", (ip,))


def excedeu_limite(ip: str) -> bool:
    with db_session() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM login_attempts "
            "WHERE ip = ? AND quando >= datetime('now', ?)",
            (ip, f"-{LOGIN_JANELA_MIN} minutes"),
        ).fetchone()
    return (row["n"] if row else 0) >= LOGIN_LIMITE


def limpar_tentativas_antigas() -> None:
    with db_session() as conn:
        conn.execute(
            "DELETE FROM login_attempts WHERE quando < datetime('now', ?)",
            (f"-{LOGIN_JANELA_MIN * 4} minutes",),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Usuários
# ─────────────────────────────────────────────────────────────────────────────
def criar_usuario(email: str, senha: str, role: str = "admin") -> int:
    with db_session() as conn:
        cur = conn.execute(
            "INSERT INTO usuarios (email, senha_hash, role) VALUES (?, ?, ?)",
            (email.lower().strip(), hash_senha(senha), role),
        )
        return int(cur.lastrowid)


def buscar_usuario_por_email(email: str) -> sqlite3.Row | None:
    with db_session() as conn:
        return conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email.lower().strip(),)
        ).fetchone()


def autenticar(email: str, senha: str) -> sqlite3.Row | None:
    user = buscar_usuario_por_email(email)
    if not user:
        return None
    if not verifica_senha(senha, user["senha_hash"]):
        return None
    return user
