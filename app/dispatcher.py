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
                """SELECT titulo, bairro, preco, quartos, suites, vagas, area_util,
                          descricao, caracteristicas
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
                preco_fmt = "~R$ " + f"{preco:,.0f}".replace(",", ".")  # exato, sem "X mil"
                linhas.append(f"  - {r['bairro'].strip()}: {r['n']} imovel(is) (ticket medio {preco_fmt})")
        if destaques:
            linhas.append(
                "IMOVEIS ATIVOS (use EXATAMENTE estes numeros — preco, bairro, metragem — "
                "SEM arredondar; o titulo diz se e venda ou locacao/mes):"
            )
            import json as _json
            import re as _re

            def _limpar(txt: str) -> str:
                t = _re.sub(r"[^\w\sÀ-ÿ.,;:/()%&-]", " ", txt or "")  # tira emoji/simbolos
                return _re.sub(r"\s+", " ", t).strip()

            for r in destaques:
                p = r["preco"] or 0
                p_fmt = "R$ " + f"{p:,.0f}".replace(",", ".")  # EXATO: 6500 -> R$ 6.500
                ficha = []
                if r["quartos"]:
                    ficha.append(f"{r['quartos']} quartos")
                if r["suites"]:
                    ficha.append(f"{r['suites']} suites")
                if r["vagas"]:
                    ficha.append(f"{r['vagas']} vagas")
                if r["area_util"]:
                    ficha.append(f"{r['area_util']:.0f}m2")
                ficha_str = (" · ".join(ficha)) if ficha else ""
                detalhe = f" ({ficha_str})" if ficha_str else ""
                linhas.append(f"  - {r['titulo'].strip()}{detalhe} — {r['bairro'].strip()} — {p_fmt}")
                # Diferenciais cadastrados (ex.: piscina aquecida, energia solar)
                try:
                    carac = _json.loads(r["caracteristicas"] or "[]")
                except Exception:
                    carac = []
                if carac:
                    linhas.append(f"      diferenciais: {', '.join(carac[:8])}")
                # Resumo da descricao real (ex.: 'colado no Shopping Conquista Sul')
                desc = _limpar(r["descricao"] or "")
                if desc:
                    linhas.append(f"      detalhes completos: {desc[:1200]}")
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


def _contexto_momento(nome_cliente: str | None = None) -> str:
    """Injeta o periodo do dia (pro cumprimento certo) e o nome do cliente, se conhecido."""
    import datetime as _dt
    h = (_dt.datetime.utcnow().hour - 3) % 24  # Vitoria da Conquista = UTC-3
    if 5 <= h < 12:
        periodo = "manha — cumprimente com 'Bom dia'"
    elif 12 <= h < 18:
        periodo = "tarde — cumprimente com 'Boa tarde'"
    else:
        periodo = "noite — cumprimente com 'Boa noite'"
    linhas = [f"MOMENTO: agora e de {periodo}."]
    if nome_cliente and str(nome_cliente).strip():
        linhas.append(
            f"NOME DO CLIENTE: '{str(nome_cliente).strip()}' — chame a pessoa pelo nome, com naturalidade."
        )
    return "\n".join(linhas)
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


def _sem_markdown(t: str) -> str:
    """Remove markdown da resposta da Ana (chat estilo WhatsApp nao renderiza ** nem #)."""
    if not t:
        return t
    import re as _re
    t = t.replace("**", "").replace("__", "").replace("`", "")
    t = _re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", t)   # titulos #, ##
    t = _re.sub(r"(?m)^\s{0,3}\*\s+", "• ", t)      # bullets '* ' -> '• '
    return t.strip()


def responder(mensagem: str, *, historico: list[dict] | None = None, tem_imagem: bool = False,
              nome_cliente: str | None = None) -> dict:
    """Pipeline completo: classifica → cascata Gemini → Claude → fallback."""
    cls = classificar(mensagem, tem_imagem=tem_imagem)
    lead = qualify_lead(mensagem, history=historico)
    _partes = [p for p in (_contexto_momento(nome_cliente), _montar_contexto_carteira(), _ler_dados_financeiros()) if p]
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
        "resposta": _sem_markdown(resp.texto),
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
