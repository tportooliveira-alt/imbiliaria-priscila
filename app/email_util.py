"""Envio de e-mail por SMTP (ex.: Gmail). Usado pelo 2FA do admin.

Configurar no .env:
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_USER=tportooliveira@gmail.com
    SMTP_PASS=<senha de app do Google (16 chars), NAO a senha normal>
    SMTP_FROM=Priscila Vasconcelos Imoveis <tportooliveira@gmail.com>   # opcional

Enquanto SMTP_USER/SMTP_PASS nao estiverem setados, `disponivel()` retorna False e
nada e enviado (o 2FA fica desligado em vez de travar o login).
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage


def _cfg() -> dict:
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com").strip(),
        "port": int(os.getenv("SMTP_PORT", "587") or 587),
        "user": os.getenv("SMTP_USER", "").strip(),
        "pwd": os.getenv("SMTP_PASS", "").strip(),
        "remetente": os.getenv("SMTP_FROM", "").strip() or os.getenv("SMTP_USER", "").strip(),
    }


def disponivel() -> bool:
    c = _cfg()
    return bool(c["user"] and c["pwd"])


def enviar_email(destino: str, assunto: str, corpo: str) -> bool:
    """Envia um e-mail de texto. Retorna True se enviou, False se desligado/erro."""
    c = _cfg()
    if not (c["user"] and c["pwd"] and destino):
        return False
    try:
        msg = EmailMessage()
        msg["From"] = c["remetente"]
        msg["To"] = destino
        msg["Subject"] = assunto
        msg.set_content(corpo)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(c["host"], c["port"], timeout=15) as s:
            s.starttls(context=ctx)
            s.login(c["user"], c["pwd"])
            s.send_message(msg)
        return True
    except Exception:
        import logging
        logging.getLogger("email_util").exception("falha ao enviar e-mail para %s", destino)
        return False
