"""Despacha mensagem classificada para o LLM apropriado.

Mapa rota → cliente:
    TRIAGEM     → Gemini 2.5 Flash
    INFO_VDC    → Gemini 2.5 Pro
    NEGOCIACAO  → Claude Sonnet
    DESCRICAO   → Claude Sonnet
    FOLLOWUP    → Claude Haiku
    VISAO       → Gemini 2.5 Pro
"""
from __future__ import annotations

from app.clients import ClienteClaude, ClienteFallback, ClienteGemini, LLMClient, RespostaLLM
from app.lead import qualify_lead, track_stage
from app.prompts import analysis_prompt, system_prompt
from app.router import Rota, classificar


MODEL_GEMINI_FAST = "gemini-2.5-flash"
MODEL_GEMINI_PRO = "gemini-2.5-pro"
MODEL_CLAUDE_SONNET = "claude-sonnet-4-5"
MODEL_CLAUDE_HAIKU = "claude-haiku-4-5"


# Mapa rota → fábrica de cliente (lazy)
_FABRICAS: dict[Rota, callable] = {
    Rota.TRIAGEM: lambda: ClienteGemini(MODEL_GEMINI_FAST),
    Rota.INFO_VDC: lambda: ClienteGemini(MODEL_GEMINI_PRO, use_google_search=True),
    Rota.NEGOCIACAO: lambda: ClienteClaude(MODEL_CLAUDE_SONNET),
    Rota.DESCRICAO: lambda: ClienteClaude(MODEL_CLAUDE_SONNET),
    Rota.FOLLOWUP: lambda: ClienteClaude(MODEL_CLAUDE_HAIKU),
    Rota.VISAO: lambda: ClienteGemini(MODEL_GEMINI_PRO),
}

_FABRICAS_FAILOVER: dict[Rota, callable] = {
    Rota.TRIAGEM: lambda: ClienteClaude(MODEL_CLAUDE_HAIKU),
    Rota.INFO_VDC: lambda: ClienteClaude(MODEL_CLAUDE_HAIKU),
    Rota.NEGOCIACAO: lambda: ClienteGemini(MODEL_GEMINI_FAST),
    Rota.DESCRICAO: lambda: ClienteGemini(MODEL_GEMINI_FAST),
    Rota.FOLLOWUP: lambda: ClienteGemini(MODEL_GEMINI_FAST),
    Rota.VISAO: lambda: ClienteClaude(MODEL_CLAUDE_HAIKU),
}


def cliente_para(rota: Rota) -> LLMClient:
    cliente = _FABRICAS[rota]()
    if not cliente.available():
        return ClienteFallback()
    return cliente


def cliente_failover_para(rota: Rota) -> LLMClient:
    cliente = _FABRICAS_FAILOVER[rota]()
    if not cliente.available():
        return ClienteFallback()
    return cliente


def responder(mensagem: str, *, historico: list[dict] | None = None, tem_imagem: bool = False) -> dict:
    """Pipeline completo: classifica → escolhe cliente → gera resposta."""
    cls = classificar(mensagem, tem_imagem=tem_imagem)
    lead = qualify_lead(mensagem, history=historico)
    system = system_prompt(cls.rota)

    cliente = cliente_para(cls.rota)
    resp: RespostaLLM = cliente.gerar(system, mensagem, historico)

    # Se o provedor primário falhar, tenta o secundário automaticamente.
    if resp.fallback and not isinstance(cliente, ClienteFallback):
        secundario = cliente_failover_para(cls.rota)
        if not isinstance(secundario, ClienteFallback):
            tentativa2 = secundario.gerar(system, mensagem, historico)
            if not tentativa2.fallback:
                resp = tentativa2

    track_stage(lead.stage)

    return {
        "rota": cls.rota.value,
        "confianca": cls.confianca,
        "motivo": cls.motivo,
        "modelo": resp.modelo,
        "fallback": resp.fallback,
        "resposta": resp.texto,
        "lead_score": lead.score,
        "lead_stage": lead.stage,
        "lead_next_question": lead.next_question,
        "lead_fields": lead.fields,
        "provider_metadata": resp.metadata or {},
    }


def analisar_pos_conversa(historico: list[dict]) -> dict:
    """Resume e qualifica uma conversa finalizada para uso da corretora."""
    joined = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in historico)
    lead = qualify_lead("", history=historico)

    primario = ClienteGemini(MODEL_GEMINI_PRO)
    resp = primario.gerar(analysis_prompt(), joined)
    if resp.fallback:
        secundario = ClienteClaude(MODEL_CLAUDE_SONNET)
        resp2 = secundario.gerar(analysis_prompt(), joined)
        if not resp2.fallback:
            resp = resp2

    return {
        "modelo": resp.modelo,
        "fallback": resp.fallback,
        "resumo": resp.texto,
        "lead_score": lead.score,
        "lead_stage": lead.stage,
        "lead_next_question": lead.next_question,
        "lead_fields": lead.fields,
    }
