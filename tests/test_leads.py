"""Testes do repositorio de leads + classificacao automatica."""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest


@pytest.fixture
def leads_mod(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    from app import db as db_mod
    importlib.reload(db_mod)
    from app import leads as leads_module
    importlib.reload(leads_module)
    db_mod.init_db()
    yield leads_module
    import gc; gc.collect()


def test_upsert_cria_novo_lead(leads_mod):
    lid = leads_mod.upsert_lead(nome="Joao", telefone="(43) 99999-1111", origem="site")
    assert lid > 0
    lead = leads_mod.detalhar(lid)
    assert lead["nome"] == "Joao"
    assert lead["telefone"] == "43999991111"
    assert lead["estagio"] == "novo"
    assert lead["temperatura"] == "frio"
    assert lead["score"] == 0


def test_upsert_deduplica_por_telefone(leads_mod):
    a = leads_mod.upsert_lead(nome="Maria", telefone="43988887777", origem="simulador")
    b = leads_mod.upsert_lead(nome=None, telefone="43988887777", origem="avaliacao")
    assert a == b


def test_upsert_deduplica_por_email(leads_mod):
    a = leads_mod.upsert_lead(nome="Ana", email="ana@x.com", origem="site")
    b = leads_mod.upsert_lead(nome="Ana", email="ana@x.com", origem="chat")
    assert a == b


def test_simulacao_com_comprometimento_ok_torna_quente(leads_mod):
    lid = leads_mod.upsert_lead(nome="Carlos", telefone="43977776666", origem="simulador")
    leads_mod.registrar_interacao(
        lid, tipo="simulacao", descricao="simulou",
        metadata={"comprometimento_ok": True, "valor_imovel": 500000},
    )
    lead = leads_mod.detalhar(lid)
    assert lead["temperatura"] == "quente"
    assert lead["score"] >= 15


def test_estagio_visita_classifica_quente(leads_mod):
    lid = leads_mod.upsert_lead(nome="Pedro", telefone="43966665555")
    leads_mod.atualizar(lid, estagio="visita")
    lead = leads_mod.detalhar(lid)
    assert lead["temperatura"] == "quente"


def test_score_acumula_por_interacao(leads_mod):
    lid = leads_mod.upsert_lead(nome="Lucia", telefone="43955554444")
    leads_mod.registrar_interacao(lid, tipo="chat", descricao="oi")
    leads_mod.registrar_interacao(lid, tipo="avaliacao", descricao="avaliou imovel")
    lead = leads_mod.detalhar(lid)
    # chat=5 + avaliacao=15 = 20
    assert lead["score"] == 20
    assert lead["temperatura"] == "morno"


def test_avaliacao_classifica_morno(leads_mod):
    lid = leads_mod.upsert_lead(nome="Bia", telefone="43944443333", origem="avaliacao")
    leads_mod.registrar_interacao(lid, tipo="avaliacao", descricao="avaliou", metadata={})
    lead = leads_mod.detalhar(lid)
    assert lead["temperatura"] == "morno"


def test_atualizar_estagio_invalido_levanta(leads_mod):
    lid = leads_mod.upsert_lead(nome="x", telefone="43911112222")
    with pytest.raises(ValueError):
        leads_mod.atualizar(lid, estagio="banana")


def test_listar_filtra_por_temperatura(leads_mod):
    a = leads_mod.upsert_lead(nome="A", telefone="43900000001")
    b = leads_mod.upsert_lead(nome="B", telefone="43900000002")
    leads_mod.atualizar(b, estagio="visita")  # vira quente
    quentes = leads_mod.listar(temperatura="quente")
    ids = [l["id"] for l in quentes]
    assert b in ids
    assert a not in ids


def test_tags(leads_mod):
    lid = leads_mod.upsert_lead(nome="x", telefone="43900000003")
    leads_mod.adicionar_tag(lid, "vendedor")
    leads_mod.adicionar_tag(lid, "vendedor")  # idempotente
    leads_mod.adicionar_tag(lid, "vip")
    lead = leads_mod.detalhar(lid)
    assert sorted(lead["tags"]) == ["vendedor", "vip"]
    leads_mod.remover_tag(lid, "vendedor")
    lead = leads_mod.detalhar(lid)
    assert lead["tags"] == ["vip"]


def test_dashboard_agrega(leads_mod):
    leads_mod.upsert_lead(nome="A", telefone="43900000010", origem="site")
    leads_mod.upsert_lead(nome="B", telefone="43900000011", origem="simulador")
    d = leads_mod.dashboard()
    assert d["total_leads"] == 2
    assert d["por_origem"].get("site") == 1
    assert d["por_origem"].get("simulador") == 1
    assert d["novos_7d"] == 2
    assert "ultimos_leads" in d
