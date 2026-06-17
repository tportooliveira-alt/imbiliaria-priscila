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


def baixar_midia_base64(msg: dict) -> tuple[bytes, str] | None:
    """Baixa a midia (imagem/documento) do WhatsApp via Evolution e devolve (bytes, mime).
    None se nao configurado ou erro. Reusa o mesmo getBase64FromMediaMessage do audio."""
    cfg = _config()
    if not cfg:
        return None
    base, key, instancia = cfg
    try:
        import base64 as _b64

        body = _json.dumps({"message": {"key": (msg or {}).get("key", {})}}).encode()
        req = urllib.request.Request(
            f"{base}/chat/getBase64FromMediaMessage/{instancia}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "apikey": key},
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            data = _json.load(r)
        b64 = data.get("base64") or data.get("media") or ""
        if not b64:
            return None
        mime = (data.get("mimetype") or "").split(";")[0].strip() or "image/jpeg"
        return _b64.b64decode(b64), mime
    except Exception:
        return None


def transcrever_audio(msg: dict) -> str | None:
    """Baixa o audio do WhatsApp (Evolution) e transcreve via Groq Whisper.

    Retorna o texto transcrito, ou None se nao houver chave/servico ou der erro
    (o webhook entao trata o audio com jeito, sem quebrar).
    """
    groq = os.getenv("GROQ_API_KEY", "").strip()
    cfg = _config()
    if not groq or not cfg:
        return None
    base, key, instancia = cfg
    try:
        import base64 as _b64
        import requests as _rq

        # 1) baixa o audio em base64 no Evolution
        body = _json.dumps({"message": {"key": (msg or {}).get("key", {})}}).encode()
        req = urllib.request.Request(
            f"{base}/chat/getBase64FromMediaMessage/{instancia}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", "apikey": key},
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            data = _json.load(r)
        b64 = data.get("base64") or data.get("media") or ""
        if not b64:
            return None
        audio = _b64.b64decode(b64)

        # 2) transcreve no Groq Whisper (API compativel com OpenAI)
        resp = _rq.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {groq}"},
            files={"file": ("audio.ogg", audio, "audio/ogg")},
            data={"model": "whisper-large-v3-turbo", "language": "pt",
                  "response_format": "text"},
            timeout=60,
        )
        if resp.status_code == 200:
            txt = (resp.text or "").strip()
            return txt or None
        return None
    except Exception:
        return None


def gerar_voz(texto: str, voice_id: str | None = None, stability: float = 0.6) -> bytes | None:
    """Gera audio a partir do texto, via ElevenLabs. None se falhar.

    voice_id: voz especifica (ex.: a do Joao). Sem isso, usa a voz padrao (Ana).
    stability: 0..1, maior = mais calmo/estavel (Joao usa ~0.85).
    """
    el = os.getenv("ELEVENLABS_API_KEY", "").strip()
    voz = (voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")).strip()
    if not el or not voz or not (texto or "").strip():
        return None
    try:
        import requests as _rq
        modelo = os.getenv("ELEVENLABS_MODEL", "eleven_turbo_v2_5")
        payload = {
            "text": texto.strip()[:1500],
            "model_id": modelo,
            "language_code": "pt",  # trava portugues -> evita misturar ingles
            "voice_settings": {
                "stability": stability,  # maior = mais calmo/estavel (Joao usa 0.85)
                "similarity_boost": 0.85,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }
        r = _rq.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voz}",
            headers={"xi-api-key": el, "Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        return r.content if (r.status_code == 200 and r.content) else None
    except Exception:
        return None


def enviar_audio(telefone: str, audio: bytes, *, timeout: float = 40.0) -> RespostaEnvio:
    """Envia um audio (voz) pelo WhatsApp via Evolution (sendWhatsAppAudio)."""
    cfg = _config()
    if not cfg:
        return RespostaEnvio(enviado=False, fallback=True, erro="evolution nao configurado")
    base, key, instancia = cfg
    numero = _normalizar_telefone(telefone)
    if not telefone_valido(numero):
        return RespostaEnvio(enviado=False, fallback=False, erro="numero invalido")
    try:
        import base64 as _b64
        b64 = _b64.b64encode(audio).decode()
        body = _json.dumps({"number": numero, "audio": b64}).encode()
        req = urllib.request.Request(
            f"{base}/message/sendWhatsAppAudio/{instancia}",
            data=body, method="POST",
            headers={"Content-Type": "application/json", "apikey": key},
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = _json.load(r)
        mid = (d.get("key") or {}).get("id") if isinstance(d, dict) else None
        return RespostaEnvio(enviado=True, fallback=False, mensagem_id=mid)
    except urllib.error.HTTPError as exc:
        return RespostaEnvio(enviado=False, fallback=False,
                             erro=f"HTTP {exc.code}: {exc.read().decode()[:120]}")
    except Exception as exc:
        return RespostaEnvio(enviado=False, fallback=False, erro=str(exc)[:120])
