"""Ponte Instagram — cliente da Graph API oficial da Meta (CUSTO ZERO).

Fala direto com a Graph API da Meta usando o token da Página/Usuário de Sistema da Priscila.
Sem serviços pagos de terceiro. Expõe leitura (perfil, mídias, insights) e publicação
(foto, carrossel, reel) em 2 passos (cria container -> publica), como a Meta exige.

Pré-requisitos (ver docs/ACESSO-INSTAGRAM-PASSO-A-PASSO.md):
- IG da Priscila = conta PROFISSIONAL (Business) vinculada a uma Página do Facebook.
- App na Meta com permissões instagram_business_basic + instagram_business_content_publish.
- Token de longa duração / Usuário de Sistema.

⚠️ A Meta BUSCA a imagem/vídeo por URL: image_url/video_url precisam ser PÚBLICOS.
   Solução grátis: servir os arquivos pelo próprio site da VPS
   (ex.: https://pvscelosimobiliaria.com/ig-media/arquivo.jpg).

Env (.env do site, NUNCA no git):
    IG_BUSINESS_ACCOUNT_ID=...
    META_PAGE_TOKEN=...
    META_GRAPH_VERSION=v23.0
"""
from __future__ import annotations

import json as _json
import ipaddress
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

_GRAPH = "https://graph.facebook.com"


def _ver() -> str:
    return os.getenv("META_GRAPH_VERSION", "v23.0")


def _token() -> str | None:
    return os.getenv("META_PAGE_TOKEN") or None


def _ig_id() -> str | None:
    return os.getenv("IG_BUSINESS_ACCOUNT_ID") or None


def disponivel() -> bool:
    """True se as credenciais mínimas (token + IG id) estão no ambiente."""
    return bool(_token() and _ig_id())


def status_config() -> dict[str, Any]:
    """Diagnóstico seguro da configuração Meta/Instagram, sem expor segredos."""
    token_ok = bool(_token())
    ig_ok = bool(_ig_id())
    graph_version_configurada = bool(os.getenv("META_GRAPH_VERSION"))
    faltando: list[str] = []
    avisos: list[str] = []
    if not token_ok:
        faltando.append("META_PAGE_TOKEN")
    if not ig_ok:
        faltando.append("IG_BUSINESS_ACCOUNT_ID")
    if not graph_version_configurada:
        avisos.append("META_GRAPH_VERSION ausente; usando fallback local. Conferir versao vigente no painel Meta.")

    return {
        "disponivel": token_ok and ig_ok,
        "graph_version": _ver(),
        "graph_version_configurada": graph_version_configurada,
        "credenciais": {
            "META_PAGE_TOKEN": token_ok,
            "IG_BUSINESS_ACCOUNT_ID": ig_ok,
        },
        "faltando": faltando,
        "avisos": avisos,
        "mcp_publicacao_habilitada": os.getenv("MCP_IG_PUBLISH_ENABLED", "0") == "1",
        "auto_outreach_habilitado": os.getenv("META_AUTO_OUTREACH", "0") == "1",
        "media_requer_https_publico": True,
        "segredos_expostos": False,
    }


def _url_publica_https(url: str | None) -> bool:
    """A Meta precisa buscar a mídia por uma URL pública; usamos HTTPS por padrão."""
    if not url:
        return False
    p = urllib.parse.urlparse(url)
    if p.scheme != "https" or not p.netloc:
        return False
    host = p.hostname or ""
    if host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".local"):
        return False
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return True


def validar_url_midia_publica(url: str | None) -> bool:
    """True se a URL atende ao mínimo para a Meta buscar a mídia."""
    return _url_publica_https(url)


@dataclass
class RespostaIG:
    ok: bool
    dados: dict[str, Any] | None = None
    erro: str | None = None


def _req(method: str, path: str, params: dict[str, Any]) -> RespostaIG:
    """Chamada genérica à Graph API. GET manda na query; POST manda no corpo (form-url-encoded)."""
    tok = _token()
    if not tok:
        return RespostaIG(False, erro="META_PAGE_TOKEN ausente no .env")
    params = {k: v for k, v in params.items() if v is not None}
    params["access_token"] = tok
    url = f"{_GRAPH}/{_ver()}/{path.lstrip('/')}"
    data = None
    if method == "GET":
        url = f"{url}?{urllib.parse.urlencode(params)}"
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return RespostaIG(True, dados=_json.loads(resp.read().decode()))
    except urllib.error.HTTPError as e:
        try:
            corpo = _json.loads(e.read().decode())
            msg = corpo.get("error", {}).get("message", str(e))
        except Exception:
            msg = f"HTTP {e.code}"
        return RespostaIG(False, erro=msg)
    except Exception as e:  # noqa: BLE001
        return RespostaIG(False, erro=str(e))


# ─── LEITURA ─────────────────────────────────────────────────────────────────
def perfil() -> RespostaIG:
    """Dados básicos da conta IG (nome, seguidores, nº de mídias)."""
    if not _ig_id():
        return RespostaIG(False, erro="IG_BUSINESS_ACCOUNT_ID ausente")
    return _req("GET", _ig_id(), {
        "fields": "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url",
    })


def listar_midias(limite: int = 12) -> RespostaIG:
    """Últimas publicações com métricas básicas."""
    if not _ig_id():
        return RespostaIG(False, erro="IG_BUSINESS_ACCOUNT_ID ausente")
    return _req("GET", f"{_ig_id()}/media", {
        "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
        "limit": min(limite, 50),
    })


def insights_conta(periodo: str = "day") -> RespostaIG:
    """Insights da conta (alcance/impressões). periodo: day/week/days_28."""
    if not _ig_id():
        return RespostaIG(False, erro="IG_BUSINESS_ACCOUNT_ID ausente")
    return _req("GET", f"{_ig_id()}/insights", {
        "metric": "reach,impressions,profile_views",
        "period": periodo,
    })


# ─── PUBLICAÇÃO (2 passos: cria container -> publica) ─────────────────────────
def _publicar_container(creation_id: str) -> RespostaIG:
    return _req("POST", f"{_ig_id()}/media_publish", {"creation_id": creation_id})


def publicar_foto(image_url: str, legenda: str = "") -> RespostaIG:
    """Publica 1 foto. image_url PRECISA ser uma URL pública (servir pela VPS)."""
    if not _url_publica_https(image_url):
        return RespostaIG(False, erro="image_url deve ser uma URL pública HTTPS")
    if not _ig_id():
        return RespostaIG(False, erro="IG_BUSINESS_ACCOUNT_ID ausente")
    c = _req("POST", f"{_ig_id()}/media", {"image_url": image_url, "caption": legenda})
    if not c.ok:
        return c
    return _publicar_container(c.dados.get("id"))


def publicar_carrossel(image_urls: list[str], legenda: str = "") -> RespostaIG:
    """Publica carrossel (2 a 10 imagens públicas)."""
    if not 2 <= len(image_urls) <= 10:
        return RespostaIG(False, erro="carrossel aceita de 2 a 10 imagens")
    invalidas = [u for u in image_urls if not _url_publica_https(u)]
    if invalidas:
        return RespostaIG(False, erro="todas as image_urls devem ser URLs públicas HTTPS")
    if not _ig_id():
        return RespostaIG(False, erro="IG_BUSINESS_ACCOUNT_ID ausente")
    filhos: list[str] = []
    for u in image_urls:
        f = _req("POST", f"{_ig_id()}/media", {"image_url": u, "is_carousel_item": "true"})
        if not f.ok:
            return RespostaIG(False, erro=f"falha no item {u}: {f.erro}")
        filhos.append(f.dados.get("id"))
    pai = _req("POST", f"{_ig_id()}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(filhos),
        "caption": legenda,
    })
    if not pai.ok:
        return pai
    return _publicar_container(pai.dados.get("id"))


def publicar_reel(video_url: str, legenda: str = "", capa_url: str | None = None,
                  tentativas: int = 20, intervalo_s: int = 6) -> RespostaIG:
    """Publica um Reel. video_url público. Espera o processamento antes de publicar."""
    if not _url_publica_https(video_url):
        return RespostaIG(False, erro="video_url deve ser uma URL pública HTTPS")
    if capa_url and not _url_publica_https(capa_url):
        return RespostaIG(False, erro="capa_url deve ser uma URL pública HTTPS")
    if not _ig_id():
        return RespostaIG(False, erro="IG_BUSINESS_ACCOUNT_ID ausente")
    c = _req("POST", f"{_ig_id()}/media", {
        "media_type": "REELS", "video_url": video_url,
        "caption": legenda, "cover_url": capa_url,
    })
    if not c.ok:
        return c
    cid = c.dados.get("id")
    # Reel precisa terminar de processar (status_code=FINISHED) antes de publicar.
    for _ in range(tentativas):
        st = _req("GET", cid, {"fields": "status_code"})
        if st.ok and st.dados.get("status_code") == "FINISHED":
            return _publicar_container(cid)
        if st.ok and st.dados.get("status_code") == "ERROR":
            return RespostaIG(False, erro="Meta retornou ERROR no processamento do reel")
        time.sleep(intervalo_s)
    return RespostaIG(False, erro="timeout: reel ainda processando")


def responder_comentario(comment_id: str, mensagem: str) -> RespostaIG:
    """Responde um comentário (requer permissão instagram_business_manage_comments)."""
    return _req("POST", f"{comment_id}/replies", {"message": mensagem})
