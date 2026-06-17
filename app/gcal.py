"""Ponte com o Google Calendar (opcional).

Liga a agenda interna ao Google Agenda da Priscila usando uma SERVICE ACCOUNT:
- a Priscila compartilha o calendario dela com o e-mail da service account
  (permissao "Fazer alteracoes em eventos");
- aqui a gente cria/cancela eventos via API REST do Calendar.

Enquanto NAO houver credencial configurada (`.env`), tudo vira no-op silencioso —
o site e a agenda interna funcionam normalmente, so nao espelham no Google.
NUNCA quebra a marcacao por causa do Google.

.env esperado:
    GOOGLE_CALENDAR_ID=xxxxx@group.calendar.google.com   # ou o e-mail do calendario
    GOOGLE_CALENDAR_SA_JSON=/var/www/imobiliaria/secret/gcal-sa.json   # fora do git
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache

log = logging.getLogger("gcal")

_SCOPES = ["https://www.googleapis.com/auth/calendar"]
_API = "https://www.googleapis.com/calendar/v3"
_TZ = "America/Bahia"  # Brasilia (sem horario de verao)


def _calendar_id() -> str | None:
    return os.getenv("GOOGLE_CALENDAR_ID") or None


def _sa_path() -> str | None:
    return os.getenv("GOOGLE_CALENDAR_SA_JSON") or None


def disponivel() -> bool:
    """True so se tiver calendario + arquivo de credencial existente."""
    p = _sa_path()
    return bool(_calendar_id() and p and os.path.isfile(p))


@lru_cache(maxsize=1)
def _sessao():
    """Sessao autenticada (cacheada). Levanta se a credencial for invalida."""
    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account

    cred = service_account.Credentials.from_service_account_file(_sa_path(), scopes=_SCOPES)
    return AuthorizedSession(cred)


def criar_evento(*, titulo: str, inicio_iso: str, fim_iso: str, descricao: str = "") -> str | None:
    """Cria o evento no Google Calendar e devolve o id dele (ou None se desligado/falhou).
    inicio_iso/fim_iso: ISO com fuso (ex.: 2026-06-17T14:00:00-03:00)."""
    if not disponivel():
        return None
    try:
        corpo = {
            "summary": titulo,
            "description": descricao,
            "start": {"dateTime": inicio_iso, "timeZone": _TZ},
            "end": {"dateTime": fim_iso, "timeZone": _TZ},
        }
        r = _sessao().post(f"{_API}/calendars/{_calendar_id()}/events", json=corpo, timeout=10)
        r.raise_for_status()
        return r.json().get("id")
    except Exception:
        log.exception("gcal.criar_evento falhou (titulo=%s) - seguindo sem espelhar", titulo)
        return None


def cancelar_evento(event_id: str) -> bool:
    """Apaga o evento no Google. Best-effort."""
    if not disponivel() or not event_id:
        return False
    try:
        r = _sessao().delete(f"{_API}/calendars/{_calendar_id()}/events/{event_id}", timeout=10)
        return r.status_code in (200, 204, 404, 410)  # 404/410 = ja nao existe
    except Exception:
        log.exception("gcal.cancelar_evento falhou (id=%s)", event_id)
        return False
