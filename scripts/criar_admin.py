"""Cria ou redefine um usuario admin local.

Uso:
    python scripts/criar_admin.py --email admin@local.dev
    python scripts/criar_admin.py --email admin@local.dev --senha "senha-forte"
"""
from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import auth
from app.db import db_session, init_db


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="admin@local.dev")
    parser.add_argument("--senha", default="")
    args = parser.parse_args()

    email = args.email.lower().strip()
    senha = args.senha or secrets.token_urlsafe(18)
    init_db()

    existente = auth.buscar_usuario_por_email(email)
    if existente:
        with db_session() as conn:
            conn.execute(
                "UPDATE usuarios SET senha_hash = ?, role = 'admin' WHERE email = ?",
                (auth.hash_senha(senha), email),
            )
        acao = "redefinido"
    else:
        auth.criar_usuario(email, senha, role="admin")
        acao = "criado"

    print(f"admin_{acao}=1")
    print(f"email={email}")
    print(f"senha={senha}")


if __name__ == "__main__":
    main()
