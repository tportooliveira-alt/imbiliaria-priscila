"""Base de m² medio por bairro de Vitoria da Conquista (BA).

Valores indicativos coletados de portais imobiliarios + experiencia local
da Priscila (atualizado 04/2026). Devem ser revisados trimestralmente.

Unidade: R$/m² medio para imoveis de padrao medio prontos para morar.
"""
from __future__ import annotations

from typing import Literal

PadraoConstrucao = Literal["simples", "medio", "alto", "luxo"]
EstadoConservacao = Literal["reformado", "bom", "regular", "precisa_reforma"]
FaixaIdade = Literal["novo", "0_10", "10_20", "20_mais"]


# R$/m² medio por bairro (padrao medio, conservacao bom)
M2_VDC: dict[str, float] = {
    "candeias": 5800,
    "boa_vista": 5600,
    "recreio": 4900,
    "patagonia": 4700,
    "centro": 4400,
    "ibirapuera": 4300,
    "alto_maron": 3900,
    "guarani": 3700,
    "primavera": 3500,
    "felicia": 3300,
    "urbis": 3000,
    "brasil": 3200,
    "panorama": 3400,
    "bateias": 2800,
    "outro": 3500,  # fallback
}

# Multiplicadores aplicados sobre o m² do bairro
FATOR_PADRAO: dict[PadraoConstrucao, float] = {
    "simples": 0.78,
    "medio": 1.00,
    "alto": 1.25,
    "luxo": 1.55,
}

FATOR_ESTADO: dict[EstadoConservacao, float] = {
    "reformado": 1.10,
    "bom": 1.00,
    "regular": 0.90,
    "precisa_reforma": 0.75,
}

FATOR_IDADE: dict[FaixaIdade, float] = {
    "novo": 1.08,
    "0_10": 1.00,
    "10_20": 0.93,
    "20_mais": 0.85,
}


def normalizar_bairro(bairro: str) -> str:
    """Normaliza nome do bairro para chave da base."""
    import unicodedata

    s = unicodedata.normalize("NFKD", bairro).encode("ascii", "ignore").decode()
    s = s.lower().strip().replace(" ", "_").replace("-", "_")
    return s if s in M2_VDC else "outro"


def m2_do_bairro(bairro: str) -> tuple[str, float]:
    """Retorna (chave_normalizada, valor_m2)."""
    chave = normalizar_bairro(bairro)
    return chave, M2_VDC[chave]


BAIRROS_DISPONIVEIS = sorted(k for k in M2_VDC if k != "outro")
