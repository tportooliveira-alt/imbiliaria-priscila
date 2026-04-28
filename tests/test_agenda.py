"""Testes da Agenda (W4)."""
from __future__ import annotations

import gc
import importlib
from datetime import datetime, timedelta, timezone
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

    for mod in ["app.db", "app.auth", "app.imoveis", "app.leads",
                "app.whatsapp", "app.agenda", "app.routes_admin",
                "app.routes_publicas", "app.routes_crm"]:
        if mod in importlib.sys.modules:
            importlib.reload(importlib.sys.modules[mod])
        else:
            importlib.import_module(mod)

    from app import db as db_mod, auth as auth_mod
    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")

    import server as server_mod
    importlib.reload(server_mod)
    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def _login(c: TestClient) -> dict:
    r = c.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "senha-segura-123"})
    return {"Authorization": f"Bearer {r.json()['token']}"}


def _futuro(horas: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=horas)).isoformat()


# ─── unit: repo ─────────────────────────────────────────────────────────────
def test_criar_e_listar(cliente):
    from app import agenda
    aid = agenda.criar(
        titulo="Visita casa Centro",
        inicio=_futuro(5), fim=_futuro(6), tipo="visita",
    )
    assert aid > 0
    items = agenda.listar()
    assert len(items) == 1
    assert items[0]["titulo"] == "Visita casa Centro"
    assert items[0]["status"] == "agendado"
    assert items[0]["lembrete_enviado"] == 0


def test_criar_tipo_invalido(cliente):
    from app import agenda
    with pytest.raises(ValueError):
        agenda.criar(titulo="X", inicio=_futuro(1), fim=_futuro(2), tipo="cafe")


def test_criar_fim_antes_de_inicio(cliente):
    from app import agenda
    with pytest.raises(ValueError):
        agenda.criar(titulo="X", inicio=_futuro(5), fim=_futuro(3))


def test_atualizar_status(cliente):
    from app import agenda
    aid = agenda.criar(titulo="Reuniao", inicio=_futuro(2), fim=_futuro(3), tipo="reuniao")
    item = agenda.atualizar(aid, status="confirmado")
    assert item["status"] == "confirmado"


def test_atualizar_status_invalido(cliente):
    from app import agenda
    aid = agenda.criar(titulo="X", inicio=_futuro(2), fim=_futuro(3))
    with pytest.raises(ValueError):
        agenda.atualizar(aid, status="esquecido")


def test_remover(cliente):
    from app import agenda
    aid = agenda.criar(titulo="X", inicio=_futuro(2), fim=_futuro(3))
    assert agenda.remover(aid) is True
    assert agenda.detalhar(aid) is None


def test_lembretes_a_enviar_filtra_janela(cliente):
    from app import agenda
    a1 = agenda.criar(titulo="Amanha", inicio=_futuro(5), fim=_futuro(6))
    a2 = agenda.criar(titulo="Semana que vem", inicio=_futuro(200), fim=_futuro(201))
    pendentes = agenda.lembretes_a_enviar(janela_horas=24)
    ids = [p["id"] for p in pendentes]
    assert a1 in ids
    assert a2 not in ids


def test_marcar_lembrete_enviado_remove_da_lista(cliente):
    from app import agenda
    aid = agenda.criar(titulo="X", inicio=_futuro(5), fim=_futuro(6))
    agenda.marcar_lembrete_enviado(aid)
    pendentes = agenda.lembretes_a_enviar()
    assert aid not in [p["id"] for p in pendentes]


# ─── endpoints ──────────────────────────────────────────────────────────────
def test_endpoint_criar_e_listar(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/agenda",
        json={"titulo": "Visita Candeias", "inicio": _futuro(10),
              "fim": _futuro(11), "tipo": "visita"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    item = r.json()["item"]
    assert item["titulo"] == "Visita Candeias"

    r = cliente.get("/api/admin/agenda", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1


def test_endpoint_exige_admin(cliente):
    r = cliente.post("/api/admin/agenda", json={"titulo": "X", "inicio": _futuro(1), "fim": _futuro(2)})
    assert r.status_code == 401


def test_endpoint_validacao_422(cliente):
    h = _login(cliente)
    # fim antes do inicio
    r = cliente.post(
        "/api/admin/agenda",
        json={"titulo": "X", "inicio": _futuro(5), "fim": _futuro(3), "tipo": "visita"},
        headers=h,
    )
    assert r.status_code == 422


def test_endpoint_patch_status(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/agenda",
        json={"titulo": "Reuniao", "inicio": _futuro(2), "fim": _futuro(3)},
        headers=h,
    )
    assert r.status_code == 201, r.text
    aid = r.json()["item"]["id"]
    r = cliente.patch(f"/api/admin/agenda/{aid}", json={"status": "realizado"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "realizado"


def test_endpoint_delete_404(cliente):
    h = _login(cliente)
    r = cliente.delete("/api/admin/agenda/9999", headers=h)
    assert r.status_code == 404


def test_lembretes_endpoint_fallback_sem_evolution(cliente, monkeypatch):
    monkeypatch.delenv("EVOLUTION_API_URL", raising=False)
    h = _login(cliente)
    cliente.post(
        "/api/admin/agenda",
        json={"titulo": "Visita", "inicio": _futuro(5), "fim": _futuro(6)},
        headers=h,
    )
    r = cliente.post("/api/admin/agenda/lembretes/enviar", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1
    assert body["fallback"] is True


def test_lembretes_endpoint_dispara_whatsapp(cliente, monkeypatch):
    monkeypatch.setenv("EVOLUTION_API_URL", "http://evo")
    monkeypatch.setenv("EVOLUTION_API_KEY", "k")
    monkeypatch.setenv("EVOLUTION_INSTANCIA", "test")
    h = _login(cliente)

    # cria lead com telefone
    from app import leads as leads_repo
    lid = leads_repo.upsert_lead(nome="Carla", telefone="77999991111", origem="manual")
    cliente.post(
        "/api/admin/agenda",
        json={"titulo": "Visita Candeias", "inicio": _futuro(5), "fim": _futuro(6),
              "lead_id": lid},
        headers=h,
    )

    enviados = {"n": 0}
    def fake_enviar(tel, txt, *, timeout=8.0):
        enviados["n"] += 1
        from app.whatsapp import RespostaEnvio
        return RespostaEnvio(enviado=True, mensagem_id="WA1", fallback=False)

    from app import whatsapp as wa_mod
    monkeypatch.setattr(wa_mod, "enviar_mensagem", fake_enviar)

    r = cliente.post("/api/admin/agenda/lembretes/enviar", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["enviados"] == 1
    assert enviados["n"] == 1

    # segunda chamada nao deve reenviar
    r2 = cliente.post("/api/admin/agenda/lembretes/enviar", headers=h)
    assert r2.json()["total"] == 0
