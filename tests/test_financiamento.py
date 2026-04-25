"""Testes do calculador SAC + PRICE."""
from __future__ import annotations

import pytest

from app.financiamento import (
    calcular_sac,
    calcular_price,
    simular,
    TAXAS_BANCOS,
)


def test_sac_parcela_inicial_maior_que_final():
    r = calcular_sac(500_000, 100_000, 360, 11.5, None)
    assert r.parcela_inicial > r.parcela_final
    assert r.sistema == "SAC"
    assert r.valor_financiado == 400_000


def test_price_parcela_constante():
    r = calcular_price(500_000, 100_000, 360, 11.5, None)
    assert r.parcela_inicial == r.parcela_final
    assert r.sistema == "PRICE"


def test_sac_total_pago_menor_que_price():
    sac = calcular_sac(500_000, 100_000, 360, 11.5, None)
    pri = calcular_price(500_000, 100_000, 360, 11.5, None)
    # SAC sempre tem total de juros menor
    assert sac.total_juros < pri.total_juros


def test_taxa_zero_total_juros_zero():
    r = calcular_sac(300_000, 60_000, 120, 0.0, None)
    assert r.total_juros == pytest.approx(0, abs=1)
    assert r.parcela_inicial == pytest.approx(r.parcela_final, abs=1)


def test_renda_minima_e_comprometimento():
    r = simular(500_000, 100_000, 360, 11.5, "SAC", renda_mensal=20_000)
    assert r.renda_minima > 0
    assert r.comprometimento_renda is not None
    assert 0 < r.comprometimento_renda < 1
    # parcela ~4-5mil em renda 20mil = ~25% comprometimento
    assert r.comprometimento_renda <= 0.30


def test_comprometimento_alta_quando_renda_baixa():
    r = simular(500_000, 100_000, 360, 11.5, "SAC", renda_mensal=3_000)
    assert r.comprometimento_renda > 0.30


def test_validacao_entrada_maior_que_valor():
    with pytest.raises(ValueError):
        simular(300_000, 400_000, 360, 11.5, "SAC")


def test_validacao_prazo_invalido():
    with pytest.raises(ValueError):
        simular(300_000, 60_000, 5, 11.5, "SAC")
    with pytest.raises(ValueError):
        simular(300_000, 60_000, 600, 11.5, "SAC")


def test_validacao_taxa_negativa():
    with pytest.raises(ValueError):
        simular(300_000, 60_000, 360, -1.0, "SAC")


def test_primeiras_parcelas_tem_12():
    r = simular(500_000, 100_000, 360, 11.5, "SAC")
    assert len(r.primeiras_parcelas) == 12
    p1 = r.primeiras_parcelas[0]
    assert "n" in p1 and "parcela" in p1 and "juros" in p1 and "amortizacao" in p1


def test_taxas_bancos_estrutura():
    assert "caixa_sbpe" in TAXAS_BANCOS
    for k, v in TAXAS_BANCOS.items():
        assert "nome" in v and "taxa_anual" in v
        assert 0 < v["taxa_anual"] < 30

