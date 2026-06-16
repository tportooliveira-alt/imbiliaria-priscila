"""Testes da API FastAPI (server.py) com TestClient — sem rede."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client(monkeypatch_session) -> TestClient:
    # Garante modo offline para todos os testes
    monkeypatch_session.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch_session.delenv("ANTHROPIC_API_KEY", raising=False)
    from server import app
    return TestClient(app)


@pytest.fixture(scope="module")
def monkeypatch_session():
    """monkeypatch com escopo de módulo (built-in só dá function)."""
    from _pytest.monkeypatch import MonkeyPatch
    mp = MonkeyPatch()
    yield mp
    mp.undo()


# ─────────────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────────────
def test_health_responde_200(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "google_api_key" in body
    assert "anthropic_api_key" in body


# ─────────────────────────────────────────────────────────────────────────────
# /api/chat
# ─────────────────────────────────────────────────────────────────────────────
def test_chat_aceita_mensagem_simples(client: TestClient) -> None:
    r = client.post("/api/chat", json={"message": "oi"})
    assert r.status_code == 200
    body = r.json()
    assert body["rota"] == "triagem"
    assert body["resposta"]
    assert body["session_id"]
    assert body["conversation_id"]
    assert "lead_score" in body
    assert "lead_stage" in body
    assert "provider_metadata" in body


def test_chat_classifica_negociacao(client: TestClient) -> None:
    r = client.post("/api/chat", json={"message": "quero comprar essa casa"})
    assert r.status_code == 200
    assert r.json()["rota"] == "negociacao"


def test_chat_classifica_visao_com_imagem(client: TestClient) -> None:
    r = client.post("/api/chat", json={"message": "olha", "has_image": True})
    assert r.status_code == 200
    assert r.json()["rota"] == "visao"


def test_chat_rejeita_mensagem_vazia(client: TestClient) -> None:
    r = client.post("/api/chat", json={"message": ""})
    assert r.status_code == 422  # pydantic validation


def test_chat_rejeita_mensagem_gigante(client: TestClient) -> None:
    r = client.post("/api/chat", json={"message": "x" * 3000})
    assert r.status_code == 422


def test_chat_aceita_historico(client: TestClient) -> None:
    r = client.post("/api/chat", json={
        "message": "e ai?",
        "history": [
            {"role": "user", "content": "oi"},
            {"role": "assistant", "content": "olá"},
        ],
    })
    assert r.status_code == 200


def test_analisar_lead_responde_200(client: TestClient) -> None:
    r = client.post("/api/analisar-lead", json={
        "history": [
            {"role": "user", "content": "quero comprar em Candeias"},
            {"role": "assistant", "content": "qual faixa de investimento?"},
            {"role": "user", "content": "ate 700 mil"},
        ],
    })
    assert r.status_code == 200
    body = r.json()
    assert "resumo" in body
    assert "lead_stage" in body


def test_funnel_responde_200(client: TestClient) -> None:
    r = client.get("/api/funnel")
    assert r.status_code == 200
    body = r.json()
    assert "total" in body
    assert "stages" in body


# ─────────────────────────────────────────────────────────────────────────────
# Estáticos
# ─────────────────────────────────────────────────────────────────────────────
def test_root_serve_home(client: TestClient) -> None:
    # URL limpa: / serve a home direto (sem redirect p/ /v3-editorial/)
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200
    assert "text/html" in r.headers.get("content-type", "")


def test_v3_index_serve_html(client: TestClient) -> None:
    r = client.get("/v3-editorial/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


def test_assets_servem_video(client: TestClient) -> None:
    r = client.head("/assets/ia-falando.mp4")
    assert r.status_code == 200


def test_shared_servem_jsx(client: TestClient) -> None:
    r = client.get("/shared/OpeningVideo.jsx")
    assert r.status_code == 200
    assert "OpeningVideo" in r.text
