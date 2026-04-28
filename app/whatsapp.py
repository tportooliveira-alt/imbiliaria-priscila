"""Cliente WhatsApp via Evolution API (self-hosted).

Documentacao: https://doc.evolution-api.com/
Em producao a Priscila roda Evolution na mesma VPS Hostinger; em dev/testes
sem `EVOLUTION_API_URL` configurado o cliente devolve fallback gracioso.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import urllib.request
import urllib.error
import json as _json


@dataclass
class RespostaEnvio:
    """Resultado do envio de mensagem WhatsApp."""

    enviado: bool
    fallback: bool
    mensagem_id: str | None = None
    erro: str | None = None
    detalhes: dict[str, Any] | None = None


def _normalizar_telefone(telefone: str) -> str:
    """Remove tudo que nao e digito e garante DDI 55 (Brasil) na frente."""
    digitos = re.sub(r"\D", "", telefone or "")
    if not digitos:
        return ""
    if digitos.startswith("55") and len(digitos) >= 12:
        return digitos
    if len(digitos) in (10, 11):  # DDD + numero
        return "55" + digitos
    return digitos


def telefone_valido(telefone: str) -> bool:
    n = _normalizar_telefone(telefone)
    return len(n) >= 12  # 55 + DDD(2) + numero(8 ou 9)


def _config() -> tuple[str, str, str] | None:
    base = os.getenv("EVOLUTION_API_URL", "").rstrip("/")
    key = os.getenv("EVOLUTION_API_KEY", "")
    instancia = os.getenv("EVOLUTION_INSTANCIA", "priscila")
    if not base or not key:
        return None
    return base, key, instancia


def disponivel() -> bool:
    return _config() is not None


def enviar_mensagem(telefone: str, texto: str, *, timeout: float = 8.0) -> RespostaEnvio:
    """Envia mensagem de texto para um numero via Evolution API.

    Retorna RespostaEnvio com `fallback=True` quando o servico nao esta
    configurado (sem EVOLUTION_API_URL) ou o numero e invalido.
    """
    if not telefone_valido(telefone):
        return RespostaEnvio(
            enviado=False,
            fallback=False,
            erro="telefone invalido (esperado DDD + numero brasileiro)",
        )
    if not (texto or "").strip():
        return RespostaEnvio(enviado=False, fallback=False, erro="texto vazio")

    cfg = _config()
    if cfg is None:
        return RespostaEnvio(
            enviado=False,
            fallback=True,
            erro="EVOLUTION_API_URL/KEY nao configurados",
        )
    base, key, instancia = cfg
    numero = _normalizar_telefone(telefone)
    url = f"{base}/message/sendText/{instancia}"
    payload = {"number": numero, "text": texto}
    body = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                dados = _json.loads(raw)
            except ValueError:
                dados = {"raw": raw}
        msg_id = (
            dados.get("key", {}).get("id")
            if isinstance(dados, dict)
            else None
        )
        return RespostaEnvio(
            enviado=True, fallback=False, mensagem_id=msg_id, detalhes=dados
        )
    except urllib.error.HTTPError as exc:
        return RespostaEnvio(
            enviado=False,
            fallback=False,
            erro=f"HTTP {exc.code}: {exc.reason}",
        )
    except (urllib.error.URLError, TimeoutError) as exc:
        return RespostaEnvio(
            enviado=False, fallback=False, erro=f"falha de rede: {exc}"
        )
