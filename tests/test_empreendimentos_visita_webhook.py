"""Testes E2E das features novas (16/06): empreendimentos, agendar-visita, webhook auth (segredo no path)."""
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
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa")

    for nome in ("db", "auth", "imoveis", "empreendimentos", "leads", "routes_admin", "routes_publicas"):
        mod = importlib.import_module(f"app.{nome}")
        importlib.reload(mod)

    from app import db as db_mod, auth as auth_mod
    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")

    import server as server_mod
    importlib.reload(server_mod)
    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def _token(cli: TestClient) -> dict:
    r = cli.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "senha-segura-123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


_EMP = {
    "nome": "Residencial Teste Aurora", "construtora": "Construtora X", "bairro": "Candeias",
    "descricao": "Lançamento de teste", "status_obra": "em_obras", "entrega_prevista": "Dez/2027",
    "num_torres": 3, "num_unidades": 120, "num_andares": 18, "vagas_info": "2 por unidade",
    "area_total": "8.000 m²", "lazer": ["Piscina", "Academia"], "diferenciais": ["Portaria 24h"],
    "proximidades": "Shopping a 500m", "condicoes_pagamento": "Entrada + financiamento",
    "tipologias": [
        {"nome": "Apartamento Tipo 1", "area_util": 75, "quartos": 2, "suites": 1, "vagas": 1, "preco_a_partir": 450000},
        {"nome": "Cobertura", "area_util": 140, "quartos": 3, "suites": 2, "vagas": 2, "preco_a_partir": 890000},
    ],
}


# ───────────── Empreendimentos ─────────────
def test_empreendimento_exige_token(cliente):
    r = cliente.post("/api/admin/empreendimentos", json=_EMP)
    assert r.status_code == 401


def test_empreendimento_crud_completo(cliente):
    h = _token(cliente)
    # criar
    r = cliente.post("/api/admin/empreendimentos", json=_EMP, headers=h)
    assert r.status_code == 201, r.text
    emp = r.json()
    assert emp["nome"] == _EMP["nome"]
    assert emp["num_torres"] == 3 and emp["num_unidades"] == 120
    assert emp["lazer"] == ["Piscina", "Academia"]          # JSON array parseado em lista
    assert emp["diferenciais"] == ["Portaria 24h"]
    assert len(emp["tipologias"]) == 2
    slug = emp["slug"]

    # listagem pública + detalhe
    pub = cliente.get("/api/empreendimentos").json()
    assert pub["total"] == 1
    det = cliente.get(f"/api/empreendimentos/{slug}").json()
    assert det["construtora"] == "Construtora X"
    assert det["tipologias"][0]["preco_a_partir"] == 450000

    # atualizar (status -> pronto, substitui tipologias)
    up = cliente.put(f"/api/admin/empreendimentos/{emp['id']}",
                     json={"status_obra": "pronto", "tipologias": [{"nome": "Studio", "area_util": 40, "preco_a_partir": 300000}]},
                     headers=h)
    assert up.status_code == 200
    det2 = cliente.get(f"/api/empreendimentos/{slug}").json()
    assert det2["status_obra"] == "pronto"
    assert [t["nome"] for t in det2["tipologias"]] == ["Studio"]

    # soft-delete -> some da listagem ativa
    d = cliente.delete(f"/api/admin/empreendimentos/{emp['id']}", headers=h)
    assert d.status_code == 204
    assert cliente.get("/api/empreendimentos").json()["total"] == 0


# ───────────── Agendar visita ─────────────
def test_agendar_visita_documenta_lead(cliente):
    body = {"nome": "Cliente Teste", "telefone": "5577955551234", "data_preferida": "2026-06-25",
            "turno": "tarde", "codigo_imovel": "7", "titulo_imovel": "Casa X", "bairro": "Candeias"}
    r = cliente.post("/api/agendar-visita", json=body)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["ok"] is True
    lead_id = j["lead_id"]
    # documentado: lead tem interação tipo "visita"
    h = _token(cliente)
    det = cliente.get(f"/api/admin/leads/{lead_id}", headers=h).json()
    tipos = [i["tipo"] for i in det.get("interacoes", [])]
    assert "visita" in tipos


# ───────────── Webhook auth (segredo no path) ─────────────
def _payload(jid="5577955559999"):
    return {"event": "messages.upsert",
            "data": {"key": {"id": "W1", "remoteJid": f"{jid}@s.whatsapp.net", "fromMe": False},
                     "pushName": "Teste", "message": {"conversation": "oi, tem casa em candeias?"}}}


def test_webhook_rota_antiga_rejeita_com_token_configurado(cliente, monkeypatch):
    monkeypatch.setenv("EVOLUTION_WEBHOOK_TOKEN", "tok-secreto-abc")
    r = cliente.post("/api/whatsapp/webhook", json=_payload())
    assert r.status_code == 200
    assert r.json().get("ignorado") is True   # rota sem token desativada


def test_webhook_secret_path_token_certo_processa(cliente, monkeypatch):
    monkeypatch.setenv("EVOLUTION_WEBHOOK_TOKEN", "tok-secreto-abc")
    r = cliente.post("/api/whatsapp/webhook/tok-secreto-abc", json=_payload())
    assert r.status_code == 200
    assert r.json().get("ok") is True          # processou (criou lead)


def test_webhook_secret_path_token_errado_401(cliente, monkeypatch):
    monkeypatch.setenv("EVOLUTION_WEBHOOK_TOKEN", "tok-secreto-abc")
    r = cliente.post("/api/whatsapp/webhook/tok-errado", json=_payload())
    assert r.status_code == 401
