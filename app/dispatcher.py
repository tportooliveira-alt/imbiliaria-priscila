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


def _montar_contexto_carteira() -> str:
    """Monta um snapshot rapido da carteira ativa para injetar no system prompt.
    Retorna string vazia se BD nao estiver acessivel (fallback silencioso).
    """
    try:
        from app.db import db_session

        with db_session() as conn:
            total = conn.execute(
                "SELECT COUNT(*) AS n FROM imoveis WHERE ativo=1"
            ).fetchone()["n"]
            por_bairro = conn.execute(
                """SELECT bairro, COUNT(*) AS n,
                          ROUND(AVG(preco)) AS preco_medio
                   FROM imoveis WHERE ativo=1
                   GROUP BY bairro ORDER BY n DESC LIMIT 6"""
            ).fetchall()
            destaques = conn.execute(
                """SELECT titulo, bairro, preco, quartos, area_util
                   FROM imoveis WHERE ativo=1 AND destaque=1
                   ORDER BY preco DESC LIMIT 5"""
            ).fetchall()

        if not total:
            return ""

        linhas = [
            f"CARTEIRA COMPLETA E REAL — estes sao os UNICOS {total} imovel(is) que EXISTEM. "
            f"Voce SO pode oferecer imoveis desta lista. Se o cliente pedir bairro/tipo que NAO "
            f"esta aqui, diga que no momento nao tem e que vai verificar com a Priscila. NUNCA invente imovel."
        ]
        if por_bairro:
            linhas.append("Distribuicao por bairro:")
            for r in por_bairro:
                preco = r["preco_medio"] or 0
                preco_fmt = f"~R$ {preco/1000:.0f} mil" if preco < 1_000_000 else f"~R$ {preco/1_000_000:.2f} mi"
                linhas.append(f"  - {r['bairro']}: {r['n']} imoveis (ticket {preco_fmt})")
        if destaques:
            linhas.append("Destaques no momento:")
            for r in destaques:
                p = r["preco"] or 0
                p_fmt = f"R$ {p/1_000_000:.2f} mi" if p >= 1_000_000 else f"R$ {p/1000:.0f} mil"
                linhas.append(
                    f"  - {r['titulo']} ({r['bairro']}, {r['quartos']}q, {r['area_util']}m2) - {p_fmt}"
                )
        return "\n".join(linhas)
    except Exception:
        return ""


def _ler_dados_financeiros() -> str:
    """Le a ficha de dados financeiros atualizavel (fonte de verdade)."""
    try:
        import os
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base, "data", "dados_financeiros.md"), encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""
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


def _construir(fabricas: dict[Rota, callable], rota: Rota) -> LLMClient:
    cliente = fabricas[rota]()
    if not cliente.available():
        return ClienteFallback()
    return cliente


def cliente_para(rota: Rota) -> LLMClient:
    return _construir(_FABRICAS, rota)


def cliente_failover_para(rota: Rota) -> LLMClient:
    return _construir(_FABRICAS_FAILOVER, rota)


def _cascata(rota: Rota, system: str, mensagem: str, historico: list[dict] | None) -> RespostaLLM:
    """Tenta primário, depois secundário, depois fallback estático.

    Cada provedor entra automaticamente se o anterior falhar (sem chave,
    erro de rede, cota etc.).
    """
    primario = _construir(_FABRICAS, rota)
    if not isinstance(primario, ClienteFallback):
        resp = primario.gerar(system, mensagem, historico)
        if not resp.fallback:
            return resp

    secundario = _construir(_FABRICAS_FAILOVER, rota)
    if not isinstance(secundario, ClienteFallback):
        resp2 = secundario.gerar(system, mensagem, historico)
        if not resp2.fallback:
            return resp2

    return ClienteFallback().gerar(system, mensagem, historico)


def responder(mensagem: str, *, historico: list[dict] | None = None, tem_imagem: bool = False) -> dict:
    """Pipeline completo: classifica → cascata Gemini → Claude → fallback."""
    cls = classificar(mensagem, tem_imagem=tem_imagem)
    lead = qualify_lead(mensagem, history=historico)
    _partes = [p for p in (_montar_contexto_carteira(), _ler_dados_financeiros()) if p]
    contexto = "\n\n".join(_partes)
    system = system_prompt(cls.rota, contexto=contexto or None)

    resp = _cascata(cls.rota, system, mensagem, historico)

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
    """Resume e qualifica uma conversa finalizada (cascata Gemini → Claude)."""
    joined = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in historico)
    lead = qualify_lead("", history=historico)
    system = analysis_prompt()

    resp: RespostaLLM = ClienteFallback().gerar(system, joined)

    primario = ClienteGemini(MODEL_GEMINI_PRO)
    if primario.available():
        tentativa = primario.gerar(system, joined)
        if not tentativa.fallback:
            resp = tentativa

    if resp.fallback:
        secundario = ClienteClaude(MODEL_CLAUDE_SONNET)
        if secundario.available():
            tentativa2 = secundario.gerar(system, joined)
            if not tentativa2.fallback:
                resp = tentativa2

    return {
        "modelo": resp.modelo,
        "fallback": resp.fallback,
        "resumo": resp.texto,
        "lead_score": lead.score,
        "lead_stage": lead.stage,
        "lead_next_question": lead.next_question,
        "lead_fields": lead.fields,
    }
