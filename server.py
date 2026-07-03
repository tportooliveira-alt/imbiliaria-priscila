"""Servidor FastAPI — Site Priscila Vasconcelos Imóveis.

Endpoints:
    GET  /api/health    — status + chaves configuradas
    POST /api/chat      — recebe mensagem, devolve resposta
    GET  /assets/*      — vídeos e imagens
    GET  /shared/*      — componentes JSX
    GET  /              — redireciona p/ /v3-editorial/
    GET  /v3-editorial/ — site

Uso:
    python -m venv venv
    .\\venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt
    copy .env.exemplo .env  (e edite as chaves)
    uvicorn server:app --reload --port 8000
"""
from __future__ import annotations

import os
import re
import time
from html import escape as html_escape
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from app import auth
from app.conversas import registrar_analise_conversa, registrar_conversa_site, resumir_funil
from app.db import DB_PATH, init_db
from app.dispatcher import analisar_pos_conversa, responder
from app.logging_config import setup_logging
from app.routes_admin import router as admin_router, requer_admin
from app.routes_crm import router as crm_router
from app.routes_publicas import router as publicas_router

# Carrega .env local (se existir)
load_dotenv()
setup_logging()

ROOT = Path(__file__).resolve().parent

app = FastAPI(title="Priscila Vasconcelos Imóveis", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


class HeadersDeSeguranca(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        # HSTS: forca HTTPS por 1 ano (site servido via nginx TLS).
        resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault(
            "Permissions-Policy", "camera=(), microphone=(), geolocation=()"
        )
        # Soft-launch: noindex em TUDO ate o lancamento oficial.
        # (Remover esta linha quando a Priscila aprovar, pra liberar o Google.)
        resp.headers.setdefault("X-Robots-Tag", "noindex, nofollow")
        # CSP — permite React/Babel via unpkg + WhatsApp/Google fonts.
        # 'unsafe-inline' e 'unsafe-eval' continuam necessarios enquanto Babel
        # standalone roda no navegador; ao migrar para build esses some.
        resp.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net https://connect.facebook.net https://www.googletagmanager.com https://www.google-analytics.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: blob: https:; "
            "media-src 'self' blob:; "
            "frame-src 'self' https:; "
            "connect-src 'self' https://wa.me https://pannellum.org https://www.facebook.com https://connect.facebook.net https://www.google-analytics.com https://*.google-analytics.com https://www.googletagmanager.com https://*.analytics.google.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        return resp


app.add_middleware(HeadersDeSeguranca)
app.include_router(admin_router)
app.include_router(crm_router)
app.include_router(publicas_router)


def _base_public_url(request: Request) -> str:
    base = str(request.base_url)
    return base[:-1] if base.endswith("/") else base


@app.on_event("startup")
def _bootstrap() -> None:
    init_db()
    email = os.getenv("ADMIN_BOOTSTRAP_EMAIL")
    senha = os.getenv("ADMIN_BOOTSTRAP_SENHA")
    if email and senha and not auth.buscar_usuario_por_email(email):
        auth.criar_usuario(email, senha, role="admin")


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class MensagemHistorico(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[MensagemHistorico] = Field(default_factory=list)
    has_image: bool = False
    session_id: str | None = Field(None, max_length=120)


class ChatResponse(BaseModel):
    rota: str
    confianca: float
    motivo: str
    modelo: str
    fallback: bool
    resposta: str
    lead_score: int
    lead_stage: str
    lead_next_question: str
    lead_fields: dict[str, bool]
    provider_metadata: dict = Field(default_factory=dict)
    session_id: str | None = None
    conversation_id: int | None = None


class LeadAnalysisRequest(BaseModel):
    history: list[MensagemHistorico] = Field(default_factory=list)
    session_id: str | None = Field(None, max_length=120)


class LeadAnalysisResponse(BaseModel):
    modelo: str
    fallback: bool
    resumo: str
    lead_score: int
    lead_stage: str
    lead_next_question: str
    lead_fields: dict[str, bool]


# ─────────────────────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health() -> dict:
    # Publico = so liveness. Diagnostico (chaves/contagens) fica no /api/admin/health protegido.
    return {"status": "ok"}


@app.get("/robots.txt", include_in_schema=False)
def robots_txt(request: Request) -> PlainTextResponse:
    base = _base_public_url(request)
    texto = "\n".join(
        [
            "User-agent: *",
            "Disallow: /admin/",
            "Disallow: /api/admin/",
            f"Sitemap: {base}/sitemap.xml",
            "",
        ]
    )
    return PlainTextResponse(texto, media_type="text/plain; charset=utf-8")


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml(request: Request) -> PlainTextResponse:
    base = _base_public_url(request)
    urls = [
        f"{base}/",
        f"{base}/v3-editorial/",
        f"{base}/v3-editorial/privacidade.html",
    ]

    linhas = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in urls:
        linhas.append("  <url>")
        linhas.append(f"    <loc>{html_escape(url, quote=True)}</loc>")
        linhas.append("  </url>")
    linhas.append("</urlset>")
    return PlainTextResponse("\n".join(linhas), media_type="application/xml; charset=utf-8")


@app.get("/api/admin/health")
def admin_health(_: dict = Depends(requer_admin)) -> dict:
    """Diagnóstico detalhado — só admin."""
    from app.db import db_session

    info: dict = {
        "status": "ok",
        "versao": app.version,
        "db_path": str(DB_PATH),
        "db_existe": DB_PATH.exists(),
        "db_tamanho_kb": round(DB_PATH.stat().st_size / 1024, 1) if DB_PATH.exists() else 0,
        "chaves": {
            "google": bool(os.getenv("GOOGLE_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "jwt_secret": bool(os.getenv("JWT_SECRET")),
        },
        "flags": {
            "dev_open_admin": os.getenv("DEV_OPEN_ADMIN") == "1",
        },
    }
    try:
        with db_session() as conn:
            for tabela in (
                "usuarios", "imoveis", "imagens", "leads", "simulacoes", "avaliacoes",
                "conversas", "mensagens_conversa", "execucoes_ia", "eventos_funil",
            ):
                try:
                    n = conn.execute(f"SELECT COUNT(*) AS n FROM {tabela}").fetchone()["n"]
                    info[f"n_{tabela}"] = n
                except Exception:
                    info[f"n_{tabela}"] = None
    except Exception as e:
        info["db_erro"] = str(e)
    return info


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    historico = [m.model_dump() for m in req.history]
    inicio = time.perf_counter()
    out = responder(req.message, historico=historico, tem_imagem=req.has_image)
    persistencia = registrar_conversa_site(
        sessao_id=req.session_id,
        historico=historico,
        mensagem=req.message,
        resposta=out,
        tem_imagem=req.has_image,
        duracao_ms=int((time.perf_counter() - inicio) * 1000),
    )
    out.update(persistencia)
    # Avisa Priscila no WhatsApp SÓ quando a conversa do site ESQUENTA (não toda hora).
    # Toda conversa fica no banco e é lida pelo dashboard via MCP.
    score = out.get("lead_score", 0)
    stage = out.get("lead_stage", "frio")
    if score >= 60 or stage in {"quente", "pronto_visita", "pronto_proposta"}:
        import threading as _th, os as _os, logging as _lg
        def _avisar_quente():
            try:
                num = _os.getenv("PRISCILA_WHATSAPP", "").strip()
                if not num: return
                from app import whatsapp as _wn
                if not _wn.disponivel(): return
                resposta_ana = out.get("resposta", "")[:120]
                msg = (
                    f"🔥 Lead QUENTE no SITE! (score {score} / {stage})\n"
                    f"Cliente: *\"{req.message[:120]}\"*\n"
                    f"Ana: \"{resposta_ana}\"\n"
                    f"Veja a conversa: pvscelosimobiliaria.com/admin/"
                )
                r = _wn.enviar_mensagem(num, msg)
                _lg.getLogger("imobiliaria").info("[REPASSE-SITE] quente enviado=%s", getattr(r, "enviado", r))
            except Exception:
                _lg.getLogger("imobiliaria").exception("[REPASSE-SITE] FALHOU")
        _th.Thread(target=_avisar_quente, daemon=True).start()
    return ChatResponse(**out)


@app.post("/api/analisar-lead", response_model=LeadAnalysisResponse)
def analisar_lead(req: LeadAnalysisRequest) -> LeadAnalysisResponse:
    historico = [m.model_dump() for m in req.history]
    inicio = time.perf_counter()
    out = analisar_pos_conversa(historico)
    registrar_analise_conversa(
        sessao_id=req.session_id,
        historico=historico,
        resposta=out,
        duracao_ms=int((time.perf_counter() - inicio) * 1000),
    )
    return LeadAnalysisResponse(**out)


@app.get("/api/funnel")
def funnel() -> dict:
    return resumir_funil()


# ─────────────────────────────────────────────────────────────────────────────
# Estáticos
# ─────────────────────────────────────────────────────────────────────────────
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")
app.mount("/shared", StaticFiles(directory=ROOT / "shared"), name="shared")
app.mount("/v3-editorial", StaticFiles(directory=ROOT / "v3-editorial", html=True), name="v3")
admin_dir = ROOT / "admin"
if admin_dir.exists():
    app.mount("/admin", StaticFiles(directory=admin_dir, html=True), name="admin_ui")


# Site NO AR na RAIZ (URL limpa, sem /v3-editorial/). O mount /v3-editorial continua
# funcionando (links/bookmarks antigos nao quebram). X-Robots-Tag noindex GLOBAL segura
# o Google ate o lancamento oficial — remover aquele noindex quando a Priscila aprovar.
_V3 = ROOT / "v3-editorial"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_V3 / "index.html")


@app.get("/{page}.html", include_in_schema=False)
def pagina_html(page: str) -> FileResponse:
    """Serve as paginas do site na RAIZ (ex.: /imovel.html, /empreendimentos.html, /agendar-visita.html)."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", page):
        raise HTTPException(status_code=404, detail="nao encontrado")
    arq = _V3 / f"{page}.html"
    if not arq.is_file():
        raise HTTPException(status_code=404, detail="nao encontrado")
    return FileResponse(arq)


@app.get("/anunciar")
@app.get("/avaliar")
def anunciar_redirect() -> RedirectResponse:
    """Link curto p/ captacao (placas, Instagram, WhatsApp)."""
    return RedirectResponse(url="/anunciar.html")


@app.get("/mercado")
@app.get("/panorama")
def mercado_redirect() -> RedirectResponse:
    """Link curto p/ a aba de Panorama do Mercado."""
    return RedirectResponse(url="/mercado.html")


@app.get("/i/{slug}")
def compartilhar_imovel(slug: str):
    """Link de compartilhamento p/ WhatsApp: entrega as tags Open Graph com a
    CAPA do imovel (preview) e leva a pessoa ao imovel no site. O robo do
    WhatsApp le a foto; quem clica cai no detalhe normal do SPA."""
    from app import imoveis as _imoveis

    HOST = "https://pvscelosimobiliaria.com"
    item = _imoveis.buscar_por_slug(slug)
    if not item:
        return RedirectResponse(url="/")

    imgs = _imoveis.listar_imagens(item["id"])
    capa = next((i for i in imgs if i.get("tipo") == "capa"), imgs[0] if imgs else None)
    og_img = f"{HOST}/assets/{capa['arquivo']}/original.jpg" if capa else f"{HOST}/selo.png"

    fin = item.get("finalidade") or "venda"
    preco = item.get("preco") or 0
    preco_fmt = (
        "R$ " + f"{preco:,.0f}".replace(",", ".") + ("/mes" if fin == "aluguel" else "")
    ) if preco else "Sob consulta"
    partes = []
    if item.get("bairro"):
        partes.append(str(item["bairro"]))
    if item.get("quartos"):
        partes.append(f"{item['quartos']} quartos")
    if item.get("area_util"):
        partes.append(f"{item['area_util']:.0f}m2")
    detalhe = " · ".join(partes)
    desc = preco_fmt + (f" — {detalhe}" if detalhe else "") + ". Priscila Vasconcelos Imobiliaria."

    t = html_escape(item.get("titulo") or "Imovel")
    d = html_escape(desc)
    img = html_escape(og_img)
    url = html_escape(f"{HOST}/i/{slug}")
    og = (
        '<meta property="og:type" content="website">'
        '<meta property="og:site_name" content="Priscila Vasconcelos Imobiliaria">'
        f'<meta property="og:title" content="{t}">'
        f'<meta property="og:description" content="{d}">'
        f'<meta property="og:image" content="{img}">'
        '<meta property="og:image:width" content="1200">'
        '<meta property="og:image:height" content="900">'
        f'<meta property="og:url" content="{url}">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{t}">'
        f'<meta name="twitter:description" content="{d}">'
        f'<meta name="twitter:image" content="{img}">'
    )

    # Serve o PROPRIO SPA (index.html buildado) com as tags OG injetadas: o robo
    # do WhatsApp le a capa; o humano carrega o site normal e ve o imovel.
    dist_index = ROOT / "design-recebido" / "pvscelos-imobiliaria" / "dist" / "index.html"
    try:
        page = dist_index.read_text(encoding="utf-8")
    except Exception:
        return RedirectResponse(url=f"/?imovel={slug}")
    page = page.replace("<head>", "<head>\n" + og, 1)
    page = re.sub(r"<title>.*?</title>", lambda _m: f"<title>{t}</title>", page, count=1, flags=re.S)
    return HTMLResponse(content=page)


@app.get("/ads")
def ads_redirect() -> RedirectResponse:
    """Ferramenta INTERNA: calculadora de investimento em Ads (noindex)."""
    return RedirectResponse(url="/ads.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
