"""Testes do dispatcher e clientes LLM (sem chamar rede)."""
from __future__ import annotations

import os

import pytest

from app import dispatcher
from app.clients import ClienteClaude, ClienteFallback, ClienteGemini
from app.dispatcher import cliente_para, responder
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
    assert set(out) == {"rota", "confianca", "motivo", "modelo", "fallback", "resposta"}
    assert out["rota"] == Rota.TRIAGEM.value
    assert out["fallback"] is True
    assert out["resposta"]


def test_responder_negociacao_seleciona_claude_quando_disponivel(monkeypatch: pytest.MonkeyPatch) -> None:
    """Quando ANTHROPIC_API_KEY existe, negociação cai no Claude (mesmo que falhe na rede)."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    cliente = cliente_para(Rota.NEGOCIACAO)
    assert isinstance(cliente, ClienteClaude)
