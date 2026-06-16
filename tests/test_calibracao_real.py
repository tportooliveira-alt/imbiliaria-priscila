"""Backtest de calibracao da AVM contra ~65 anuncios REAIS de VDC (rodadas 1-3, OLX + imobiliarias).

Trava regressao: se a calculadora voltar a supervalorizar/subvalorizar feio, este teste quebra.
Limites FROUXOS de proposito — preco e PEDIDO (ask, ~5-15% acima do fechamento) e o modelo e so por
bairro (nao ve rua/acabamento), entao ha dispersao natural. O dataset vive em scripts/calibracao_eval.py.
"""
from __future__ import annotations

import importlib.util
import statistics
from pathlib import Path

import pytest

_EVAL = Path(__file__).resolve().parent.parent / "scripts" / "calibracao_eval.py"
_spec = importlib.util.spec_from_file_location("calibracao_eval", _EVAL)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

DATASET = _mod.RODADA_1 + _mod.RODADA_2 + _mod.RODADA_3


def _erros() -> list[float]:
    errs = []
    for it in DATASET:
        est, _vmin, _vmax, erro, _dentro = _mod.avalia_item(it)
        errs.append(erro)
    return errs


def test_dataset_tem_massa_critica():
    assert len(DATASET) >= 60, "dataset de calibracao encolheu — re-coletar anuncios reais"


def test_mape_global_aceitavel():
    """Erro medio absoluto vs pedido nao pode estourar (era ~50% antes da recalibracao de 16/06)."""
    errs = _erros()
    mape = statistics.mean(abs(e) for e in errs)
    assert mape < 40.0, f"MAPE {mape:.1f}% alto demais — calculadora descalibrou"


def test_vies_mediano_sem_delirio():
    """A mediana do erro deve ficar perto de zero (sem super/subvalorizar sistematicamente)."""
    med = statistics.median(_erros())
    assert -20.0 < med < 20.0, f"vies mediano {med:.1f}% — modelo enviesado"


def test_maioria_no_campo_certo():
    """Pelo menos ~70% dos imoveis devem cair dentro de +-60% do pedido (faixa larga, dado o ruido)."""
    errs = _erros()
    perto = sum(1 for e in errs if abs(e) <= 60)
    assert perto / len(errs) >= 0.70, f"so {perto}/{len(errs)} dentro de +-60% do pedido"
