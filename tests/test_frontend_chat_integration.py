"""Valida integração do widget de chat com o backend /api/chat.

Esses testes são estruturais (texto) porque o frontend roda em React no browser.
"""
from __future__ import annotations

from pathlib import Path


def _src(shared_dir: Path) -> str:
    return (shared_dir / "AIChat.jsx").read_text(encoding="utf-8")


def test_chat_usa_endpoint_api_chat(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert 'fetch("/api/chat"' in src


def test_chat_publico_nao_expoe_painel_interno(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert 'fetch("/api/funnel")' not in src
    assert 'fetch("/api/analisar-lead"' not in src
    assert "Painel da conversa" not in src
    assert "Rota / modelo" not in src
    assert "Grounding ativo" not in src


def test_chat_envia_post_json(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert 'method: "POST"' in src
    assert '"Content-Type": "application/json"' in src


def test_chat_envia_message_e_history(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert "message: userText" in src
    assert "history: historyPayload" in src


def test_chat_tem_fallback_local_em_erro(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert "catch (err)" in src
    assert "window.aiChatResponse(userText" in src


def test_chat_mostra_estado_de_erro(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert "setNetError(" in src
    assert "Conexao instavel" in src


def test_chat_renderiza_atendimento_publico(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert "Atendimento Priscila Vasconcelos" in src
    assert "Abrir chat com IA" in src
    assert "Digite sua mensagem" in src


def test_chat_para_typing_em_sucesso_e_erro(shared_dir: Path) -> None:
    src = _src(shared_dir)
    # Deve haver pelo menos 2 setTyping(false): sucesso e catch
    assert src.count("setTyping(false)") >= 2


def test_chat_escuta_evento_abrir_chat(shared_dir: Path) -> None:
    src = _src(shared_dir)
    assert 'addEventListener("abrir-chat"' in src
    assert 'setOpen(true)' in src
    assert 'setInput(texto)' in src
