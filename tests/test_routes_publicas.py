"""Testes end-to-end das rotas publicas (financiamento + avaliacao)."""
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
    from app import routes_admin as routes_mod
    importlib.reload(routes_mod)
    from app import routes_publicas as pub_mod
    importlib.reload(pub_mod)

    db_mod.init_db()

    import server as server_mod
    importlib.reload(server_mod)

    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def test_taxas_referenciais(cliente):
    r = cliente.get("/api/financiamento/taxas")
    assert r.status_code == 200
    body = r.json()
    assert "taxas" in body
    assert "caixa_sbpe" in body["taxas"]


def test_simular_financiamento_sac(cliente):
    r = cliente.post("/api/simular-financiamento", json={
        "valor_imovel": 500000, "entrada": 100000,
        "prazo_meses": 360, "taxa_anual": 11.5, "sistema": "SAC",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["sistema"] == "SAC"
    assert body["valor_financiado"] == 400000
    assert body["parcela_inicial"] > body["parcela_final"]
    assert len(body["primeiras_parcelas"]) == 12


def test_simular_financiamento_price_parcela_constante(cliente):
    r = cliente.post("/api/simular-financiamento", json={
        "valor_imovel": 500000, "entrada": 100000,
        "prazo_meses": 360, "taxa_anual": 11.5, "sistema": "PRICE",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["parcela_inicial"] == body["parcela_final"]


def test_simular_com_renda_devolve_comprometimento(cliente):
    r = cliente.post("/api/simular-financiamento", json={
        "valor_imovel": 500000, "entrada": 100000,
        "prazo_meses": 360, "taxa_anual": 11.5, "sistema": "SAC",
        "renda_mensal": 20000,
    })
    body = r.json()
    assert body["comprometimento_renda"] is not None
    assert body["comprometimento_ok"] is True


def test_simular_validacao_entrada_maior(cliente):
    r = cliente.post("/api/simular-financiamento", json={
        "valor_imovel": 300000, "entrada": 400000,
        "prazo_meses": 360, "taxa_anual": 11.5, "sistema": "SAC",
    })
    assert r.status_code == 400


def test_simular_persiste_no_db(cliente):
    cliente.post("/api/simular-financiamento", json={
        "valor_imovel": 600000, "entrada": 120000,
        "prazo_meses": 360, "taxa_anual": 10.5, "sistema": "SAC",
        "nome": "Joao", "contato": "joao@x.com",
    })
    from app.db import db_session
    with db_session() as conn:
        row = conn.execute("SELECT nome, contato, valor_imovel FROM simulacoes").fetchone()
    assert row is not None
    assert row["nome"] == "Joao"
    assert row["valor_imovel"] == 600000


def test_listar_bairros_avaliacao(cliente):
    r = cliente.get("/api/avaliacao/bairros")
    assert r.status_code == 200
    body = r.json()
    assert "bairros" in body
    assert "candeias" in body["bairros"]


def test_avaliar_imovel_basico(cliente):
    r = cliente.post("/api/avaliar-imovel", json={
        "bairro": "candeias", "area_util": 120, "quartos": 3,
        "suites": 1, "vagas": 2, "padrao": "alto",
        "estado": "reformado", "idade": "0_10", "tem_area_externa": True,
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["valor_minimo"] < body["valor_central"] < body["valor_maximo"]
    assert body["confianca"] == "alta"
    assert "texto" in body
    assert body["bairro_normalizado"] == "candeias"


def test_avaliar_imovel_validacao_area(cliente):
    r = cliente.post("/api/avaliar-imovel", json={
        "bairro": "candeias", "area_util": 0,
    })
    assert r.status_code == 422  # Pydantic gt=0


def test_avaliar_persiste_no_db(cliente):
    cliente.post("/api/avaliar-imovel", json={
        "bairro": "boa_vista", "area_util": 90, "quartos": 3,
        "nome": "Maria", "contato": "11999",
    })
    from app.db import db_session
    with db_session() as conn:
        row = conn.execute("SELECT nome, contato, bairro FROM avaliacoes").fetchone()
    assert row is not None
    assert row["nome"] == "Maria"
    assert row["bairro"] == "boa_vista"
