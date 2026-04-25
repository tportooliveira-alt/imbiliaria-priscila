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
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.dispatcher import responder

# Carrega .env local (se existir)
load_dotenv()

ROOT = Path(__file__).resolve().parent

app = FastAPI(title="Priscila Vasconcelos Imóveis", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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


class ChatResponse(BaseModel):
    rota: str
    confianca: float
    motivo: str
    modelo: str
    fallback: bool
    resposta: str


# ─────────────────────────────────────────────────────────────────────────────
# API
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
        "anthropic_api_key": bool(os.getenv("ANTHROPIC_API_KEY")),
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    historico = [m.model_dump() for m in req.history]
    out = responder(req.message, historico=historico, tem_imagem=req.has_image)
    return ChatResponse(**out)


# ─────────────────────────────────────────────────────────────────────────────
# Estáticos
# ─────────────────────────────────────────────────────────────────────────────
app.mount("/assets", StaticFiles(directory=ROOT / "assets"), name="assets")
app.mount("/shared", StaticFiles(directory=ROOT / "shared"), name="shared")
app.mount("/v3-editorial", StaticFiles(directory=ROOT / "v3-editorial", html=True), name="v3")


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/v3-editorial/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
