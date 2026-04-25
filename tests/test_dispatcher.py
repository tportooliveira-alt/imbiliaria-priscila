"""Testes do dispatcher e clientes LLM (sem chamar rede)."""
from __future__ import annotations

import os

import pytest

from app import dispatcher
from app.clients import ClienteClaude, ClienteFallback, ClienteGemini
from app.dispatcher import analisar_pos_conversa, cliente_para, responder
from app.router import Rota


# ─────────────────────────────────────────────────────────────────────────────
# Disponibilidade — depende de env vars
# ─────────────────────────────────────────────────────────────────────────────
def test_fallback_sempre_disponivel() -> None:
    assert ClienteFallback().available() is True


def test_gemini_indisponivel_sem_chave(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert ClienteGemini().available() is False


def test_claude_indisponivel_sem_chave(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert ClienteClaude().available() is False


def test_gemini_disponivel_com_chave(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_API_KEY", "fake-key")
    assert ClienteGemini().available() is True


# ─────────────────────────────────────────────────────────────────────────────
# Fallback gera resposta amigável
# ─────────────────────────────────────────────────────────────────────────────
def test_fallback_gera_mensagem_offline() -> None:
    resp = ClienteFallback().gerar("system", "oi")
    assert resp.fallback is True
    assert "offline" in resp.texto.lower() or "modo" in resp.texto.lower()
    assert resp.modelo == "fallback"


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher escolhe cliente certo
# ─────────────────────────────────────────────────────────────────────────────
def test_cliente_para_sem_chaves_devolve_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    for rota in Rota:
        c = cliente_para(rota)
        assert isinstance(c, ClienteFallback), f"Rota {rota} deveria cair em fallback"


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline completo (com fallback ativo)
# ─────────────────────────────────────────────────────────────────────────────
def test_responder_pipeline_sem_chave(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    out = responder("oi, tudo bem?")
    assert set(out) == {
        "rota", "confianca", "motivo", "modelo", "fallback", "resposta",
        "lead_score", "lead_stage", "lead_next_question", "lead_fields",
    }
    assert out["rota"] == Rota.TRIAGEM.value
    assert out["fallback"] is True
    assert out["resposta"]
    assert isinstance(out["lead_score"], int)
    assert isinstance(out["lead_fields"], dict)


def test_responder_negociacao_seleciona_claude_quando_disponivel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Quando ANTHROPIC_API_KEY existe, negociação cai no Claude (mesmo que falhe na rede)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    cliente = cliente_para(Rota.NEGOCIACAO)
    assert isinstance(cliente, ClienteClaude)


def test_failover_para_secundario_quando_primario_falha(monkeypatch: pytest.MonkeyPatch) -> None:
    class PrimarioFalha:
        def available(self) -> bool:
            return True

        def gerar(self, system: str, mensagem: str, historico=None):
            from app.clients import RespostaLLM
            return RespostaLLM(texto="erro primario", modelo="primario", fallback=True)

    class SecundarioOk:
        def available(self) -> bool:
            return True

        def gerar(self, system: str, mensagem: str, historico=None):
            from app.clients import RespostaLLM
            return RespostaLLM(texto="resposta secundario", modelo="secundario", fallback=False)

    monkeypatch.setitem(dispatcher._FABRICAS, Rota.TRIAGEM, lambda: PrimarioFalha())
    monkeypatch.setitem(dispatcher._FABRICAS_FAILOVER, Rota.TRIAGEM, lambda: SecundarioOk())

    out = responder("oi")
    assert out["modelo"] == "secundario"
    assert out["fallback"] is False


def test_analisar_pos_conversa_sem_chave(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    out = analisar_pos_conversa([
        {"role": "user", "content": "quero comprar em Candeias"},
        {"role": "assistant", "content": "qual a faixa?"},
        {"role": "user", "content": "ate 700 mil"},
    ])
    assert set(out) == {
        "modelo", "fallback", "resumo", "lead_score", "lead_stage",
        "lead_next_question", "lead_fields",
    }
    assert out["lead_stage"] in {"frio", "morno", "quente", "pronto_visita", "pronto_proposta"}
