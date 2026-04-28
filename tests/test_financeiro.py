"""Testes W7: financeiro (comissoes, metas, contas)."""
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
    for mod in [
        "app.db", "app.auth", "app.imoveis", "app.leads",
        "app.financeiro",
        "app.routes_admin", "app.routes_publicas", "app.routes_crm",
    ]:
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
    r = c.post(
        "/api/auth/login",
        json={"email": "priscila@vdc.com", "senha": "senha-segura-123"},
    )
    return {"Authorization": f"Bearer {r.json()['token']}"}


# ─── repo ─────────────────────────────────────────────────────────────────────
def test_criar_comissao_calcula_valor(cliente):
    from app import financeiro
    c = financeiro.criar_comissao({
        "descricao": "Venda Apartamento Centro",
        "valor_venda": 500_000,
        "percentual": 5,
        "data_venda": "2025-01-15",
    })
    assert c["valor_comissao"] == 25_000
    assert c["status"] == "previsto"


def test_atualizar_status_comissao(cliente):
    from app import financeiro
    c = financeiro.criar_comissao({
        "descricao": "Casa Pituba",
        "valor_venda": 800_000,
        "percentual": 6,
        "data_venda": "2025-02-10",
    })
    upd = financeiro.atualizar_comissao(c["id"], {"status": "recebido"})
    assert upd["status"] == "recebido"


def test_excluir_comissao(cliente):
    from app import financeiro
    c = financeiro.criar_comissao({
        "descricao": "xx", "valor_venda": 100, "percentual": 1,
        "data_venda": "2025-01-01",
    })
    assert financeiro.excluir_comissao(c["id"])
    assert financeiro.buscar_comissao(c["id"]) is None


def test_upsert_meta(cliente):
    from app import financeiro
    m1 = financeiro.upsert_meta({"ano": 2025, "mes": 3, "meta_vendas": 1_000_000, "meta_comissao": 50_000})
    m2 = financeiro.upsert_meta({"ano": 2025, "mes": 3, "meta_vendas": 1_500_000, "meta_comissao": 75_000})
    assert m1["id"] == m2["id"]
    assert m2["meta_vendas"] == 1_500_000


def test_conta_pagar_marcar_paga(cliente):
    from app import financeiro
    c = financeiro.criar_conta({
        "tipo": "pagar", "descricao": "Aluguel sala", "valor": 2500,
        "vencimento": "2025-03-05",
    })
    assert c["pago"] is False
    paga = financeiro.marcar_conta_paga(c["id"], data_pagamento="2025-03-04")
    assert paga["pago"] is True
    assert paga["data_pagamento"] == "2025-03-04"


def test_dashboard_periodo(cliente):
    from app import financeiro
    financeiro.criar_comissao({
        "descricao": "venda 1", "valor_venda": 400_000, "percentual": 5,
        "data_venda": "2025-04-10", "status": "recebido",
    })
    financeiro.criar_comissao({
        "descricao": "venda 2", "valor_venda": 600_000, "percentual": 5,
        "data_venda": "2025-04-20",
    })
    financeiro.upsert_meta({"ano": 2025, "mes": 4, "meta_vendas": 800_000, "meta_comissao": 40_000})
    d = financeiro.dashboard(ano=2025, mes=4)
    assert d["comissoes"]["qtd"] == 2
    assert d["comissoes"]["valor_vendas"] == 1_000_000
    assert d["comissoes"]["valor_comissoes"] == 50_000
    assert d["comissoes"]["valor_recebido"] == 20_000
    assert d["metas"]["meta_vendas"] == 800_000
    assert d["metas"]["atingido_vendas_pct"] == 125.0


# ─── endpoints ────────────────────────────────────────────────────────────────
def test_endpoint_criar_listar_comissao(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/financeiro/comissoes",
        json={
            "descricao": "Apto Vitoria",
            "valor_venda": 1_200_000,
            "percentual": 5,
            "data_venda": "2025-05-12",
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    assert r.json()["valor_comissao"] == 60_000
    lista = cliente.get("/api/admin/financeiro/comissoes", headers=h).json()
    assert len(lista) == 1


def test_endpoint_filtrar_comissoes_por_status(cliente):
    h = _login(cliente)
    cliente.post("/api/admin/financeiro/comissoes", json={
        "descricao": "prev", "valor_venda": 100_000, "percentual": 5,
        "data_venda": "2025-01-01", "status": "previsto",
    }, headers=h)
    cliente.post("/api/admin/financeiro/comissoes", json={
        "descricao": "recebida", "valor_venda": 200_000, "percentual": 5,
        "data_venda": "2025-01-02", "status": "recebido",
    }, headers=h)
    r = cliente.get("/api/admin/financeiro/comissoes?status=recebido", headers=h)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["status"] == "recebido"


def test_endpoint_meta_upsert(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/financeiro/metas",
        json={"ano": 2025, "mes": 6, "meta_vendas": 2_000_000, "meta_comissao": 100_000},
        headers=h,
    )
    assert r.status_code == 200
    metas = cliente.get("/api/admin/financeiro/metas?ano=2025", headers=h).json()
    assert any(m["mes"] == 6 for m in metas)


def test_endpoint_conta_e_pagar(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/financeiro/contas",
        json={
            "tipo": "pagar", "descricao": "Internet escritorio",
            "valor": 250, "vencimento": "2025-07-10",
        },
        headers=h,
    )
    cid = r.json()["id"]
    r2 = cliente.post(f"/api/admin/financeiro/contas/{cid}/pagar", headers=h)
    assert r2.status_code == 200
    assert r2.json()["pago"] is True


def test_endpoint_dashboard(cliente):
    h = _login(cliente)
    cliente.post("/api/admin/financeiro/comissoes", json={
        "descricao": "venda agosto", "valor_venda": 300_000, "percentual": 4,
        "data_venda": "2025-08-15",
    }, headers=h)
    r = cliente.get("/api/admin/financeiro/dashboard?ano=2025&mes=8", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["comissoes"]["valor_vendas"] == 300_000
    assert body["comissoes"]["valor_comissoes"] == 12_000


def test_endpoint_proibe_sem_token(cliente):
    r = cliente.get("/api/admin/financeiro/dashboard")
    assert r.status_code in (401, 403)


def test_endpoint_excluir_comissao_404(cliente):
    h = _login(cliente)
    r = cliente.delete("/api/admin/financeiro/comissoes/9999", headers=h)
    assert r.status_code == 404
