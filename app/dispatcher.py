"""Despacha mensagem classificada para o LLM apropriado.

Mapa rota → cliente:
    TRIAGEM     → Gemini Flash
    INFO_VDC    → Gemini Pro (com Search ativado no futuro)
    NEGOCIACAO  → Claude Sonnet
    DESCRICAO   → Claude Sonnet
    FOLLOWUP    → Claude Haiku
    VISAO       → Gemini Pro (Vision)
"""
from __future__ import annotations

from app.clients import ClienteClaude, ClienteFallback, ClienteGemini, LLMClient, RespostaLLM
from app.prompts import system_prompt
from app.router import Rota, classificar


# Mapa rota → fábrica de cliente (lazy)
_FABRICAS: dict[Rota, callable] = {
    Rota.TRIAGEM: lambda: ClienteGemini("gemini-2.0-flash"),
    Rota.INFO_VDC: lambda: ClienteGemini("gemini-2.0-flash"),  # Pro+Search depois
    Rota.NEGOCIACAO: lambda: ClienteClaude("claude-sonnet-4-5"),
    Rota.DESCRICAO: lambda: ClienteClaude("claude-sonnet-4-5"),
    Rota.FOLLOWUP: lambda: ClienteClaude("claude-haiku-4-5"),
    Rota.VISAO: lambda: ClienteGemini("gemini-2.0-flash"),
}


def cliente_para(rota: Rota) -> LLMClient:
    cliente = _FABRICAS[rota]()
    if not cliente.available():
        return ClienteFallback()
    return cliente


def responder(mensagem: str, *, historico: list[dict] | None = None, tem_imagem: bool = False) -> dict:
    """Pipeline completo: classifica → escolhe cliente → gera resposta."""
    cls = classificar(mensagem, tem_imagem=tem_imagem)
    cliente = cliente_para(cls.rota)
    resp: RespostaLLM = cliente.gerar(system_prompt(cls.rota), mensagem, historico)
    return {
        "rota": cls.rota.value,
        "confianca": cls.confianca,
        "motivo": cls.motivo,
        "modelo": resp.modelo,
        "fallback": resp.fallback,
        "resposta": resp.texto,
    }
