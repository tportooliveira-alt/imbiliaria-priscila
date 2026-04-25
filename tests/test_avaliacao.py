"""Testes do AVM heuristico."""
from __future__ import annotations

import pytest

from app.avaliacao import avaliar, texto_editorial
from app.m2_vdc import BAIRROS_DISPONIVEIS, m2_do_bairro, normalizar_bairro


def test_normalizar_bairro_acentos_e_caso():
    assert normalizar_bairro("Candeias") == "candeias"
    assert normalizar_bairro("BOA VISTA") == "boa_vista"
    assert normalizar_bairro("Felícia") == "felicia"
    assert normalizar_bairro("alto-maron") == "alto_maron"


def test_m2_do_bairro_mapeado():
    chave, valor = m2_do_bairro("Candeias")
    assert chave == "candeias"
    assert valor > 0


def test_m2_do_bairro_desconhecido_usa_fallback():
    chave, valor = m2_do_bairro("Bairro Inexistente XYZ")
    assert chave == "outro"
    assert valor > 0


def test_avaliar_padrao_alto_maior_que_simples():
    base = dict(bairro="candeias", area_util=100, quartos=3, suites=1, vagas=1)
    r_simples = avaliar(**base, padrao="simples")
    r_alto = avaliar(**base, padrao="alto")
    assert r_alto.valor_central > r_simples.valor_central


def test_avaliar_estado_reformado_maior_que_precisa_reforma():
    base = dict(bairro="candeias", area_util=100)
    r_ref = avaliar(**base, estado="reformado")
    r_pre = avaliar(**base, estado="precisa_reforma")
    assert r_ref.valor_central > r_pre.valor_central


def test_avaliar_idade_novo_maior_que_20mais():
    base = dict(bairro="candeias", area_util=100)
    r_novo = avaliar(**base, idade="novo")
    r_velho = avaliar(**base, idade="20_mais")
    assert r_novo.valor_central > r_velho.valor_central


def test_avaliar_extras_aumentam_valor():
    base = dict(bairro="candeias", area_util=100, quartos=2)
    r0 = avaliar(**base, suites=0, vagas=0, tem_area_externa=False)
    r1 = avaliar(**base, suites=2, vagas=2, tem_area_externa=True)
    assert r1.valor_central > r0.valor_central


def test_faixa_min_central_max_consistente():
    r = avaliar(bairro="candeias", area_util=100)
    assert r.valor_minimo < r.valor_central < r.valor_maximo


def test_confianca_alta_quando_bairro_mapeado():
    r = avaliar(bairro="candeias", area_util=90)
    assert r.confianca == "alta"


def test_confianca_baixa_area_extrema():
    r = avaliar(bairro="candeias", area_util=10)
    assert r.confianca == "baixa"
    r2 = avaliar(bairro="candeias", area_util=900)
    assert r2.confianca == "baixa"


def test_confianca_media_bairro_desconhecido():
    r = avaliar(bairro="bairro inexistente", area_util=80)
    assert r.confianca == "media"


def test_avaliar_area_invalida():
    with pytest.raises(ValueError):
        avaliar(bairro="candeias", area_util=0)


def test_texto_editorial_contem_dados():
    r = avaliar(bairro="candeias", area_util=120)
    txt = texto_editorial(r, "Candeias")
    assert "Candeias" in txt
    assert "120" in txt


def test_bairros_disponiveis_lista():
    assert isinstance(BAIRROS_DISPONIVEIS, list)
    assert len(BAIRROS_DISPONIVEIS) > 5
    assert "candeias" in BAIRROS_DISPONIVEIS
