"""Login por BIOMETRIA (digital / rosto) via WebAuthn / Passkey.

A Priscila cadastra o aparelho UMA vez (logada). Depois entra so com a biometria do
proprio aparelho (Touch ID / Face ID / Windows Hello / digital do Android) — nada de
senha nem codigo no dia a dia. A biometria NUNCA sai do aparelho; o servidor so guarda
a chave publica e confere a assinatura.

Tabelas (criadas em db.init_db):
- passkeys: credenciais cadastradas (1 por aparelho)
- webauthn_desafios: desafio temporario entre 'inicio' e 'fim' (single-use, expira)
"""
from __future__ import annotations

import base64
import json
import os
import secrets

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import base64url_to_bytes
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from app.db import db_session


def _rp_id() -> str:
    # dominio "puro" (sem https://). Configuravel p/ teste local.
    return os.getenv("WEBAUTHN_RP_ID", "pvscelosimobiliaria.com").strip()


def _origins() -> list[str]:
    """Origens aceitas. Aceita www e sem-www por padrao (a Priscila pode entrar por qualquer um)."""
    env = os.getenv("WEBAUTHN_ORIGIN", "").strip()
    if env:
        return [o.strip() for o in env.split(",") if o.strip()]
    rp = _rp_id()
    return [f"https://{rp}", f"https://www.{rp}"]


def _rp_nome() -> str:
    return "Priscila Vasconcelos Imoveis"


# ─── desafio temporario (single-use) ─────────────────────────────────────────
def _guardar_desafio(chave: str, challenge: bytes, tipo: str) -> None:
    ch_b64 = base64.b64encode(challenge).decode()
    with db_session() as conn:
        conn.execute("DELETE FROM webauthn_desafios WHERE chave = ? AND tipo = ?", (chave, tipo))
        conn.execute(
            "INSERT INTO webauthn_desafios (chave, challenge, tipo) VALUES (?, ?, ?)",
            (chave, ch_b64, tipo),
        )


def _consumir_desafio(chave: str, tipo: str) -> bytes | None:
    with db_session() as conn:
        row = conn.execute(
            "SELECT challenge FROM webauthn_desafios WHERE chave = ? AND tipo = ? "
            "AND criado_em >= datetime('now','-10 minutes')",
            (chave, tipo),
        ).fetchone()
        conn.execute("DELETE FROM webauthn_desafios WHERE chave = ? AND tipo = ?", (chave, tipo))
    return base64.b64decode(row["challenge"]) if row else None


# ─── CADASTRO do aparelho (logada) ───────────────────────────────────────────
def registro_inicio(user_id: int, email: str) -> str:
    """Opcoes pra cadastrar a biometria deste aparelho. Retorna JSON pro navegador."""
    existentes = listar_credenciais(user_id)
    opts = generate_registration_options(
        rp_id=_rp_id(),
        rp_name=_rp_nome(),
        user_id=str(user_id).encode(),
        user_name=email,
        user_display_name=email,
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=base64url_to_bytes(c["credential_id"])) for c in existentes
        ],
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )
    _guardar_desafio(f"reg:{user_id}", opts.challenge, "registro")
    return options_to_json(opts)


def registro_fim(user_id: int, credential_json: dict, apelido: str = "") -> bool:
    challenge = _consumir_desafio(f"reg:{user_id}", "registro")
    if not challenge:
        return False
    verif = verify_registration_response(
        credential=credential_json,
        expected_challenge=challenge,
        expected_rp_id=_rp_id(),
        expected_origin=_origins(),
    )
    cred_id = base64.urlsafe_b64encode(verif.credential_id).decode().rstrip("=")
    pub = base64.b64encode(verif.credential_public_key).decode()
    with db_session() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO passkeys (credential_id, user_id, public_key, sign_count, apelido) "
            "VALUES (?, ?, ?, ?, ?)",
            (cred_id, user_id, pub, verif.sign_count, apelido or "aparelho"),
        )
    return True


# ─── LOGIN por biometria ─────────────────────────────────────────────────────
def login_inicio(email: str | None = None) -> str:
    """Opcoes pro navegador pedir a biometria. Sem email => deixa o aparelho escolher (resident key)."""
    allow = None
    chave = "login:_any_"
    if email:
        from app import auth
        u = auth.buscar_usuario_por_email(email)
        if u:
            creds = listar_credenciais(u["id"])
            allow = [PublicKeyCredentialDescriptor(id=base64url_to_bytes(c["credential_id"])) for c in creds]
            chave = f"login:{u['id']}"
    opts = generate_authentication_options(
        rp_id=_rp_id(),
        allow_credentials=allow,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    _guardar_desafio(chave, opts.challenge, "login")
    return options_to_json(opts)


def login_fim(credential_json: dict, email: str | None = None) -> dict | None:
    """Confere a assinatura da biometria. Retorna o usuario (dict) ou None."""
    cred_id_raw = credential_json.get("id") or credential_json.get("rawId") or ""
    cred_id = cred_id_raw.rstrip("=")
    with db_session() as conn:
        pk = conn.execute("SELECT * FROM passkeys WHERE credential_id = ?", (cred_id,)).fetchone()
        if not pk:
            return None
        user = conn.execute("SELECT * FROM usuarios WHERE id = ?", (pk["user_id"],)).fetchone()
    if not user:
        return None
    chave = f"login:{pk['user_id']}" if email else "login:_any_"
    challenge = _consumir_desafio(chave, "login") or _consumir_desafio("login:_any_", "login")
    if not challenge:
        return None
    try:
        verif = verify_authentication_response(
            credential=credential_json,
            expected_challenge=challenge,
            expected_rp_id=_rp_id(),
            expected_origin=_origins(),
            credential_public_key=base64.b64decode(pk["public_key"]),
            credential_current_sign_count=pk["sign_count"],
        )
    except Exception:
        return None
    with db_session() as conn:
        conn.execute("UPDATE passkeys SET sign_count = ? WHERE credential_id = ?",
                     (verif.new_sign_count, cred_id))
    return dict(user)


def listar_credenciais(user_id: int) -> list[dict]:
    with db_session() as conn:
        rows = conn.execute(
            "SELECT credential_id, apelido, criado_em FROM passkeys WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def tem_passkey(email: str) -> bool:
    from app import auth
    u = auth.buscar_usuario_por_email(email)
    if not u:
        return False
    return len(listar_credenciais(u["id"])) > 0
