"""AVM editorial — avalia imovel a partir de bairro + caracteristicas.

MVP heuristico (sem ML). Combina m²/bairro + fatores (padrao, estado, idade)
+ ajustes finos (vagas, suites, area_externa) e devolve faixa min-max.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.ruas import rua_eh_comercial, tier_da_rua
from app.m2_vdc import (
    FATOR_ESTADO,
    FATOR_IDADE,
    FATOR_LAZER,
    FATOR_MOBILIA,
    FATOR_PADRAO,
    FATOR_PONTO_COMERCIAL,
    FATOR_RUA,
    FATOR_TIPO,
    FATOR_VISTA,
    M2_CASA_MULT,
    EstadoConservacao,
    FaixaIdade,
    Lazer,
    Mobilia,
    PadraoConstrucao,
    TipoImovel,
    Vista,
    fator_area,
    m2_do_bairro,
    terreno_do_bairro,
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
    tipo: TipoImovel = "casa",
    mobilia: Mobilia = "vazio",
    lazer: Lazer = "sem",
    vista: Vista = "comum",
    andar_alto: bool = False,
    elevador: bool = False,
    banheiros: int = 0,
    area_terreno: float | None = None,
    rua: str | None = None,
    ponto_comercial: bool = False,
) -> ResultadoAvaliacao:
    """Calcula faixa de valor para um imovel em VDC (calculadora avancada)."""
    if area_util <= 0:
        raise ValueError("area_util deve ser positiva")

    chave, m2_base = m2_do_bairro(bairro)

    # Fator de RUA: rua nobre/condominio premium vale mais; popular menos; nao reconhecida = neutro.
    tier_rua = tier_da_rua(chave, rua)
    f_rua = FATOR_RUA.get(tier_rua, 1.0)
    # Ponto comercial (numa via comercial) ganha um premio adicional.
    eh_ponto_comercial = bool(ponto_comercial) and (rua_eh_comercial(chave, rua) or tipo == "comercial")
    f_comercial = FATOR_PONTO_COMERCIAL if eh_ponto_comercial else 1.0

    # Casa usa multiplicador POR BAIRRO (casa/apto varia 0,62 a 1,29); demais tipos, fator fixo.
    f_tipo = M2_CASA_MULT.get(chave, M2_CASA_MULT["_def"]) if tipo == "casa" else FATOR_TIPO[tipo]
    eh_terreno = tipo == "terreno"

    # Terreno e avaliado pelo m² de terra: fatores de construcao nao se aplicam.
    if eh_terreno:
        f_padrao = f_estado = f_idade = f_mobilia = f_lazer = 1.0
        f_vista = FATOR_VISTA[vista]
    else:
        f_padrao = FATOR_PADRAO[padrao]
        f_estado = FATOR_ESTADO[estado]
        f_idade = FATOR_IDADE[idade]
        f_mobilia = FATOR_MOBILIA[mobilia]
        f_lazer = FATOR_LAZER[lazer]
        f_vista = FATOR_VISTA[vista]

    # Ajustes secundarios (aditivos)
    f_extras = 1.0
    if not eh_terreno:
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
        if banheiros >= 3:
            f_extras += 0.02
        if andar_alto:
            f_extras += 0.02
        if elevador:
            f_extras += 0.02
        # Lote generoso (casa com terreno bem maior que a area construida)
        if area_terreno and area_terreno > area_util * 1.8:
            f_extras += 0.06
        elif area_terreno and area_terreno > area_util * 1.3:
            f_extras += 0.03

    f_extras = min(f_extras, 1.45)  # teto p/ nao estourar
    f_area = fator_area(area_util)  # elasticidade nao-linear pela metragem

    if eh_terreno:
        # Terreno: avaliado pelo m² de TERRA do bairro (dado de mercado), nao pelo construido.
        m2_terreno = terreno_do_bairro(chave, m2_base)
        area_base = area_terreno or area_util
        m2_ajustado = m2_terreno * f_vista * f_extras * f_rua * f_comercial
        valor_central = m2_ajustado * area_base
    else:
        m2_ajustado = (
            m2_base * f_tipo * f_padrao * f_estado * f_idade
            * f_mobilia * f_lazer * f_vista * f_area * f_extras * f_rua * f_comercial
        )
        area_base = area_util
        valor_central = m2_ajustado * area_base

    # Confianca primeiro (define a largura da faixa).
    confianca = "alta" if chave != "outro" and 30 <= area_util <= 300 else "media"
    # Tipos heterogeneos (terreno, comercial, casa grande) sao menos fiaveis no MCDDM
    # automatico -> a avaliacao precisa e pelo Metodo Evolutivo / vistoria. Nunca "alta".
    if eh_terreno or tipo == "comercial" or (tipo == "casa" and area_util > 250):
        confianca = "media" if confianca == "alta" else confianca
    if area_util > 800 or area_util < 20 or (tipo == "casa" and area_util > 350):
        confianca = "baixa"

    # Faixa: quanto MENOR a confianca, mais larga (menor precisao do automatico).
    margem = {"alta": 0.12, "media": 0.16, "baixa": 0.22}[confianca]
    valor_minimo = valor_central * (1 - margem)
    valor_maximo = valor_central * (1 + margem)

    return ResultadoAvaliacao(
        bairro_normalizado=chave,
        m2_base=round(m2_base, 2),
        m2_ajustado=round(m2_ajustado, 2),
        valor_central=round(valor_central, 2),
        valor_minimo=round(valor_minimo, 2),
        valor_maximo=round(valor_maximo, 2),
        fatores_aplicados={
            "tipo": f_tipo,
            "padrao": f_padrao,
            "estado": f_estado,
            "idade": f_idade,
            "mobilia": f_mobilia,
            "lazer": f_lazer,
            "vista": f_vista,
            "area": round(f_area, 3),
            "extras": round(f_extras, 3),
            "rua": f_rua,
            "comercial_ponto": f_comercial,
        },
        detalhes={
            "area_util": area_util,
            "area_terreno": area_terreno or 0,
            "quartos": quartos,
            "suites": suites,
            "vagas": vagas,
            "banheiros": banheiros,
            "padrao": padrao,
            "estado": estado,
            "idade": idade,
            "tipo": tipo,
            "mobilia": mobilia,
            "lazer": lazer,
            "vista": vista,
            "tem_area_externa": int(tem_area_externa),
            "andar_alto": int(andar_alto),
            "elevador": int(elevador),
        },
        confianca=confianca,
    )


def yield_aluguel_mensal(valor: float, tipo: str = "apartamento") -> float:
    """Yield mensal (aluguel/valor) — NAO e fixo: cai conforme o imovel encarece
    ('piso do aluguel'). Calibrado com 99 alugueis reais de VDC (17/06):
    barato ~0,70%/mes -> caro ~0,38%/mes. Comercial/terreno por tipo."""
    if tipo == "comercial":
        return 0.0070
    if tipo == "terreno":
        return 0.0015
    # Residencial (apto/casa/cobertura): curva por faixa de valor.
    if valor < 250_000:
        return 0.0065
    if valor < 400_000:
        return 0.0057
    if valor < 600_000:
        return 0.0050
    if valor < 1_000_000:
        return 0.0042
    return 0.0038


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
