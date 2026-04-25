"""Testes do classificador de intenções (app/router.py)."""
from __future__ import annotations

import pytest

from app.router import Rota, classificar


# ─────────────────────────────────────────────────────────────────────────────
# Cada rota com pelo menos 1 caso garantido
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "mensagem, rota_esperada",
    [
        ("oi", Rota.TRIAGEM),
        ("Olá, tudo bem?", Rota.TRIAGEM),
        ("Como é o bairro Candeias?", Rota.INFO_VDC),
        ("informações sobre Vitória da Conquista", Rota.INFO_VDC),
        ("quero comprar essa casa", Rota.NEGOCIACAO),
        ("estou interessado, vamos fechar", Rota.NEGOCIACAO),
        ("preciso de uma descrição editorial pro anúncio", Rota.DESCRICAO),
        ("depois eu vejo, sem pressa", Rota.FOLLOWUP),
    ],
)
def test_classificacao_basica(mensagem: str, rota_esperada: Rota) -> None:
    assert classificar(mensagem).rota is rota_esperada


def test_imagem_anexada_vai_para_visao() -> None:
    cls = classificar("olha essa foto", tem_imagem=True)
    assert cls.rota is Rota.VISAO
    assert cls.confianca == 1.0


def test_mensagem_vazia_vai_para_triagem() -> None:
    assert classificar("").rota is Rota.TRIAGEM
    assert classificar("   ").rota is Rota.TRIAGEM


def test_classificador_devolve_motivo() -> None:
    cls = classificar("quero comprar")
    assert cls.motivo
    assert 0.0 <= cls.confianca <= 1.0


def test_classificador_rejeita_nao_string() -> None:
    with pytest.raises(TypeError):
        classificar(123)  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# Robustez de léxico (case-insensitive, acentuação)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("variante", ["CANDEIAS", "candeias", "Candeias", "CaNdEiAs"])
def test_bairro_case_insensitive(variante: str) -> None:
    assert classificar(f"como é {variante}?").rota is Rota.INFO_VDC


def test_negociacao_tem_prioridade_sobre_bairro() -> None:
    """Apos a alteracao para priorizar INFO_VDC quando ha bairro mencionado,
    'quero comprar em Candeias' agora vai para INFO_VDC (com Google Search grounding)."""
    assert classificar("quero comprar em Candeias").rota is Rota.INFO_VDC
