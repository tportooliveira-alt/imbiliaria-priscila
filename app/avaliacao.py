"""AVM editorial — avalia imovel a partir de bairro + caracteristicas.

MVP heuristico (sem ML). Combina m²/bairro + fatores (padrao, estado, idade)
+ ajustes finos (vagas, suites, area_externa) e devolve faixa min-max.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.m2_vdc import (
    FATOR_ESTADO,
    FATOR_IDADE,
    FATOR_PADRAO,
    EstadoConservacao,
    FaixaIdade,
    PadraoConstrucao,
    m2_do_bairro,
)


@dataclass(frozen=True)
class ResultadoAvaliacao:
    bairro_normalizado: str
    m2_base: float
    m2_ajustado: float
    valor_central: float
    valor_minimo: float
    valor_maximo: float
    fatores_aplicados: dict[str, float]
    detalhes: dict[str, float | str | int]
    confianca: str  # "alta" | "media" | "baixa"


def avaliar(
    *,
    bairro: str,
    area_util: float,
    quartos: int = 2,
    suites: int = 0,
    vagas: int = 0,
    padrao: PadraoConstrucao = "medio",
    estado: EstadoConservacao = "bom",
    idade: FaixaIdade = "0_10",
    tem_area_externa: bool = False,
) -> ResultadoAvaliacao:
    """Calcula faixa de valor para um imovel em VDC."""
    if area_util <= 0:
        raise ValueError("area_util deve ser positiva")

    chave, m2_base = m2_do_bairro(bairro)

    f_padrao = FATOR_PADRAO[padrao]
    f_estado = FATOR_ESTADO[estado]
    f_idade = FATOR_IDADE[idade]

    # Ajustes secundarios
    f_extras = 1.0
    if suites > 0:
        f_extras += 0.03 * suites
    if vagas >= 2:
        f_extras += 0.04
    elif vagas == 1:
        f_extras += 0.02
    if tem_area_externa:
        f_extras += 0.05
    if quartos >= 4:
        f_extras += 0.04

    m2_ajustado = m2_base * f_padrao * f_estado * f_idade * f_extras
    valor_central = m2_ajustado * area_util

    # Faixa: ±12% (heuristica conservadora)
    valor_minimo = valor_central * 0.88
    valor_maximo = valor_central * 1.12

    # Confianca: alta se bairro mapeado e dados completos
    confianca = "alta" if chave != "outro" and area_util >= 30 else "media"
    if area_util > 600 or area_util < 30:
        confianca = "baixa"

    return ResultadoAvaliacao(
        bairro_normalizado=chave,
        m2_base=round(m2_base, 2),
        m2_ajustado=round(m2_ajustado, 2),
        valor_central=round(valor_central, 2),
        valor_minimo=round(valor_minimo, 2),
        valor_maximo=round(valor_maximo, 2),
        fatores_aplicados={
            "padrao": f_padrao,
            "estado": f_estado,
            "idade": f_idade,
            "extras": round(f_extras, 3),
        },
        detalhes={
            "area_util": area_util,
            "quartos": quartos,
            "suites": suites,
            "vagas": vagas,
            "padrao": padrao,
            "estado": estado,
            "idade": idade,
            "tem_area_externa": int(tem_area_externa),
        },
        confianca=confianca,
    )


def texto_editorial(r: ResultadoAvaliacao, bairro_original: str) -> str:
    """Gera texto curto de fallback (caso Claude nao esteja disponivel)."""
    faixa = f"R$ {r.valor_minimo:,.0f} a R$ {r.valor_maximo:,.0f}".replace(",", ".")
    central = f"R$ {r.valor_central:,.0f}".replace(",", ".")
    return (
        f"Pela metragem de {r.detalhes['area_util']}m² em {bairro_original}, "
        f"a faixa estimada e de {faixa}, com valor central proximo de {central}. "
        f"Confianca da estimativa: {r.confianca}. "
        "Esta e uma analise rapida online — para um valor preciso, agende uma "
        "visita com a Priscila Vasconcelos para avaliacao presencial."
    )
