"""Testes da busca em linguagem natural — heuristica + endpoint."""
from __future__ import annotations

import gc
import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente_com_imoveis(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv("JWT_SECRET", "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa")
    # Sem GOOGLE_API_KEY -> testa caminho heuristico puro
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    from app import db as db_mod
    importlib.reload(db_mod)
    from app import imoveis as imoveis_mod
    importlib.reload(imoveis_mod)
    from app import busca_natural as bn_mod
    importlib.reload(bn_mod)
    from app import routes_publicas as pub_mod
    importlib.reload(pub_mod)

    db_mod.init_db()

    # Semeia 3 imoveis
    imoveis_mod.criar_imovel({
        "titulo": "Apartamento Candeias 3 quartos",
        "bairro": "Candeias", "tipo": "apartamento",
        "quartos": 3, "suites": 1, "vagas": 2,
        "area_util": 95, "preco": 480000,
        "descricao": "Lindo apto com varanda e piscina no condominio.",
        "caracteristicas": ["piscina", "varanda", "academia"],
        "destaque": True, "ativo": True,
    })
    imoveis_mod.criar_imovel({
        "titulo": "Casa Centro 2 quartos",
        "bairro": "Centro", "tipo": "casa",
        "quartos": 2, "suites": 0, "vagas": 1,
        "area_util": 110, "preco": 320000,
        "descricao": "Casa com quintal e churrasqueira.",
        "caracteristicas": ["quintal", "churrasqueira"],
        "destaque": False, "ativo": True,
    })
    imoveis_mod.criar_imovel({
        "titulo": "Cobertura Boa Vista 4 quartos",
        "bairro": "Boa Vista", "tipo": "cobertura",
        "quartos": 4, "suites": 2, "vagas": 3,
        "area_util": 200, "preco": 1_200_000,
        "descricao": "Cobertura duplex com vista panoramica.",
        "caracteristicas": ["vista", "varanda gourmet"],
        "destaque": True, "ativo": True,
    })

    import server as server_mod
    importlib.reload(server_mod)
    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def test_heuristica_extrai_bairro_e_quartos():
    from app import busca_natural as bn

    f = bn.extrair_filtros_heuristica("Quero apartamento em Candeias com 3 quartos")
    assert "candeias" in f["bairros"]
    assert f["tipo"] == "apartamento"
    assert f["quartos_min"] == 3


def test_heuristica_extrai_preco_ate_mil():
    from app import busca_natural as bn

    f = bn.extrair_filtros_heuristica("Casa ate R$ 400 mil no centro")
    assert f["preco_max"] == 400_000
    assert f["tipo"] == "casa"
    assert "centro" in f["bairros"]


def test_heuristica_extrai_tags():
    from app import busca_natural as bn

    f = bn.extrair_filtros_heuristica("Apto com piscina e churrasqueira")
    assert "piscina" in f["tags"]
    assert "churrasqueira" in f["tags"]


def test_endpoint_busca_natural_filtra(cliente_com_imoveis):
    r = cliente_com_imoveis.post(
        "/api/busca-natural",
        json={"texto": "apartamento em Candeias com piscina", "usar_ia": False},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1
    assert body["imoveis"][0]["bairro"] == "Candeias"
    assert "candeias" in body["filtros"]["bairros"]


def test_endpoint_busca_natural_preco_max(cliente_com_imoveis):
    r = cliente_com_imoveis.post(
        "/api/busca-natural",
        json={"texto": "qualquer imovel ate 500 mil", "usar_ia": False},
    )
    body = r.json()
    assert body["total"] == 2  # apto 480k + casa 320k
    for im in body["imoveis"]:
        assert im["preco"] <= 500_000


def test_endpoint_busca_natural_texto_vazio_400(cliente_com_imoveis):
    r = cliente_com_imoveis.post("/api/busca-natural", json={"texto": " "})
    assert r.status_code == 422  # Pydantic min_length
