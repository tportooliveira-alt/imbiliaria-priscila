"""Testes do cliente WhatsApp + endpoints (W2.1)."""
from __future__ import annotations

import gc
import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv("DEV_OPEN_ADMIN", "0")
    monkeypatch.setenv(
        "JWT_SECRET",
        "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa",
    )

    from app import db as db_mod
    importlib.reload(db_mod)
    from app import auth as auth_mod
    importlib.reload(auth_mod)
    from app import imoveis as imoveis_mod
    importlib.reload(imoveis_mod)
    from app import leads as leads_mod
    importlib.reload(leads_mod)
    from app import whatsapp as wa_mod
    importlib.reload(wa_mod)
    from app import routes_admin as ra_mod
    importlib.reload(ra_mod)
    from app import routes_publicas as rp_mod
    importlib.reload(rp_mod)
    from app import routes_crm as rc_mod
    importlib.reload(rc_mod)

    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")

    import server as server_mod
    importlib.reload(server_mod)

    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def _login(cli: TestClient) -> dict:
    r = cli.post(
        "/api/auth/login",
        json={"email": "priscila@vdc.com", "senha": "senha-segura-123"},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


# ─── unit: cliente whatsapp ────────────────────────────────────────────────
def test_telefone_normalizacao_e_validacao(monkeypatch):
    from app import whatsapp
    assert whatsapp.telefone_valido("(77) 99999-0000") is True
    assert whatsapp.telefone_valido("5577999990000") is True
    assert whatsapp.telefone_valido("123") is False
    assert whatsapp._normalizar_telefone("(77) 99999-0000") == "5577999990000"


def test_envio_sem_config_devolve_fallback(monkeypatch):
    from app import whatsapp
    monkeypatch.delenv("EVOLUTION_API_URL", raising=False)
    monkeypatch.delenv("EVOLUTION_API_KEY", raising=False)
    r = whatsapp.enviar_mensagem("77999990000", "ola")
    assert r.fallback is True
    assert r.enviado is False


def test_envio_telefone_invalido(monkeypatch):
    from app import whatsapp
    monkeypatch.delenv("EVOLUTION_API_URL", raising=False)
    r = whatsapp.enviar_mensagem("123", "ola")
    assert r.enviado is False
    assert r.fallback is False
    assert "telefone" in (r.erro or "")


# ─── endpoints ─────────────────────────────────────────────────────────────
def test_enviar_whatsapp_lead_fallback_sem_config(cliente, monkeypatch):
    monkeypatch.delenv("EVOLUTION_API_URL", raising=False)
    h = _login(cliente)
    cliente.post(
        "/api/avaliar-imovel",
        json={"bairro": "Centro", "area_util": 80, "quartos": 2,
              "nome": "Ana", "contato": "77988880000"},
    )
    leads = cliente.get("/api/admin/leads", headers=h).json()["leads"]
    lead_id = leads[0]["id"]
    r = cliente.post(
        f"/api/admin/leads/{lead_id}/whatsapp",
        json={"texto": "Oi Ana, tudo bem?"},
        headers=h,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["fallback"] is True
    assert body["enviado"] is False


def test_enviar_whatsapp_lead_404(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/leads/99999/whatsapp",
        json={"texto": "oi"},
        headers=h,
    )
    assert r.status_code == 404


def test_enviar_whatsapp_lead_sem_telefone_400(cliente):
    h = _login(cliente)
    # cria lead so com email
    from app import leads as leads_repo
    lid = leads_repo.upsert_lead(nome="Sem tel", email="x@y.com", origem="manual")
    r = cliente.post(
        f"/api/admin/leads/{lid}/whatsapp",
        json={"texto": "oi"},
        headers=h,
    )
    assert r.status_code == 400


def test_webhook_evolution_cria_lead_e_interacao(cliente):
    payload = {
        "event": "messages.upsert",
        "instance": "priscila",
        "data": {
            "key": {"id": "ABC123", "remoteJid": "5577955551234@s.whatsapp.net", "fromMe": False},
            "pushName": "Joao Cliente",
            "message": {"conversation": "Oi, ainda tem aquela casa em Candeias?"},
        },
    }
    r = cliente.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is True
    lead_id = body["lead_id"]

    # confere que a interacao foi gravada
    h = _login(cliente)
    detalhe = cliente.get(f"/api/admin/leads/{lead_id}", headers=h).json()
    tipos = [i["tipo"] for i in detalhe.get("interacoes", [])]
    assert "whatsapp_recebido" in tipos


def test_webhook_ignora_from_me(cliente):
    payload = {
        "event": "messages.upsert",
        "data": {"key": {"fromMe": True, "remoteJid": "557799@s"}, "message": {"conversation": "x"}},
    }
    r = cliente.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200
    assert r.json().get("ignorado") is True


def test_webhook_ignora_evento_irrelevante(cliente):
    r = cliente.post("/api/whatsapp/webhook", json={"event": "presence.update", "data": {"x": 1}})
    assert r.status_code == 200
    assert r.json().get("ignorado") is True


# ─── W2.2: notificar alerta via WhatsApp ────────────────────────────────────
def test_notificar_alerta_whatsapp_fallback(cliente, monkeypatch):
    monkeypatch.delenv("EVOLUTION_API_URL", raising=False)
    h = _login(cliente)
    from app import leads as leads_repo
    from app import imoveis as imoveis_repo
    aid = leads_repo.criar_alerta(
        nome="Carla Lima", contato="77988887777",
        filtros={"bairro": "Candeias", "preco_max": 900000},
    )
    import time as _t
    _t.sleep(0.05)
    imoveis_repo.criar_imovel({
        "titulo": "Casa nova Candeias", "bairro": "Candeias",
        "tipo": "Casa", "quartos": 3, "preco": 700000, "ativo": True,
    })
    r = cliente.post(f"/api/admin/alertas/{aid}/notificar-whatsapp", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fallback"] is True
    assert "Candeias" in body["mensagem"]
    assert "Carla" in body["mensagem"]


def test_notificar_alerta_404(cliente):
    h = _login(cliente)
    r = cliente.post("/api/admin/alertas/99999/notificar-whatsapp", headers=h)
    assert r.status_code == 404


def test_notificar_alerta_sem_match_400(cliente):
    h = _login(cliente)
    from app import leads as leads_repo
    aid = leads_repo.criar_alerta(
        nome="Fulano", contato="77988880000",
        filtros={"bairro": "Inexistente XYZ"},
    )
    r = cliente.post(f"/api/admin/alertas/{aid}/notificar-whatsapp", headers=h)
    assert r.status_code == 400


# ─── W2.3: auto-resposta IA no webhook ──────────────────────────────────────
def test_webhook_sem_auto_reply_nao_responde(cliente, monkeypatch):
    monkeypatch.delenv("WHATSAPP_AUTO_REPLY", raising=False)
    payload = {
        "event": "messages.upsert",
        "data": {
            "key": {"id": "X1", "remoteJid": "5577955550001@s.whatsapp.net", "fromMe": False},
            "pushName": "Teste",
            "message": {"conversation": "tem casa em candeias?"},
        },
    }
    r = cliente.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body.get("auto_reply") is False


def test_webhook_auto_reply_sem_evolution_indisponivel(cliente, monkeypatch):
    monkeypatch.setenv("WHATSAPP_AUTO_REPLY", "1")
    monkeypatch.delenv("EVOLUTION_API_URL", raising=False)
    monkeypatch.delenv("EVOLUTION_API_KEY", raising=False)
    payload = {
        "event": "messages.upsert",
        "data": {
            "key": {"id": "X2", "remoteJid": "5577955550002@s.whatsapp.net", "fromMe": False},
            "pushName": "Teste2",
            "message": {"conversation": "oi"},
        },
    }
    r = cliente.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200
    assert r.json().get("auto_reply") is False


def test_webhook_auto_reply_chama_dispatcher(cliente, monkeypatch):
    """Quando Evolution disponivel + auto_reply=1, chama IA e envia."""
    monkeypatch.setenv("WHATSAPP_AUTO_REPLY", "1")
    monkeypatch.setenv("EVOLUTION_API_URL", "http://evo.local")
    monkeypatch.setenv("EVOLUTION_API_KEY", "key-fake")
    monkeypatch.setenv("EVOLUTION_INSTANCIA", "test")

    chamadas = {"dispatcher": 0, "envio": 0}

    def fake_responder(mensagem, **kwargs):  # **kwargs: robusto a novos params (ex.: nome_cliente)
        chamadas["dispatcher"] += 1
        return {"resposta": "Oi! Sim, tenho opcoes em Candeias.", "modelo": "fake", "rota": "atendimento"}

    def fake_enviar(telefone, texto, *, timeout=8.0):
        chamadas["envio"] += 1
        from app.whatsapp import RespostaEnvio
        return RespostaEnvio(enviado=True, mensagem_id="WAID123", fallback=False)

    from app import dispatcher as dispatcher_mod
    from app import whatsapp as wa_mod
    monkeypatch.setattr(dispatcher_mod, "responder", fake_responder)
    monkeypatch.setattr(wa_mod, "enviar_mensagem", fake_enviar)

    payload = {
        "event": "messages.upsert",
        "data": {
            "key": {"id": "X3", "remoteJid": "5577955550003@s.whatsapp.net", "fromMe": False},
            "pushName": "Teste3",
            "message": {"conversation": "tem casa em candeias?"},
        },
    }
    r = cliente.post("/api/whatsapp/webhook", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("auto_reply") is True
    assert chamadas["dispatcher"] == 1
    assert chamadas["envio"] == 1

    # registrou a interacao de saida
    h = _login(cliente)
    detalhe = cliente.get(f"/api/admin/leads/{body['lead_id']}", headers=h).json()
    tipos = [i["tipo"] for i in detalhe.get("interacoes", [])]
    assert "whatsapp_enviado" in tipos
    assert "whatsapp_recebido" in tipos


# ─── W2.2: notificar alerta via WhatsApp ────────────────────────────────────
