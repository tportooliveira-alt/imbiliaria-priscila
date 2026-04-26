"""Calculadora de financiamento imobiliario — SAC e PRICE.

Inclui estimativa REAL dos seguros obrigatorios (MIP + DFI) e tarifa
de administracao mensal cobrados pelo banco. Sem isso a parcela
mostrada fica subestimada em 5-15% dependendo da idade do tomador.

Tudo em Python puro (sem numpy). Valores em reais (float).
Taxa anual em % (ex.: 11.5 para 11,5% a.a.).

Fontes (abril/2026):
- Tabela MIP: divulgacao publica Caixa Habitacional (faixas etarias)
- DFI: media mercado SBPE (~0,014% a.m. sobre valor avaliacao)
- Tarifa adm: R$ 25,00/mes (Caixa, BB, Itau, Bradesco, Santander)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Sistema = Literal["SAC", "PRICE"]


# ─────────────────────────────────────────────────────────────────────────────
# Seguros e tarifas reais (SBPE — referencia Caixa, abril/2026)
# ─────────────────────────────────────────────────────────────────────────────
# MIP (Morte e Invalidez Permanente) — taxa MENSAL sobre saldo devedor
# varia drasticamente com idade do tomador. Tabela aproximada Caixa SBPE.
TABELA_MIP_MENSAL = [
    (30,  0.000246),  # ate 30 anos
    (35,  0.000273),  # 31-35
    (40,  0.000335),  # 36-40
    (45,  0.000444),  # 41-45
    (50,  0.000590),  # 46-50
    (55,  0.000822),  # 51-55
    (60,  0.001156),  # 56-60
    (65,  0.001610),  # 61-65
    (70,  0.002233),  # 66-70
    (200, 0.003000),  # 71+
]

# DFI (Danos Fisicos ao Imovel) — taxa MENSAL sobre valor de avaliacao
DFI_MENSAL = 0.000140  # 0,014% a.m.

# Tarifa de administracao mensal (valor fixo)
TARIFA_ADM_MENSAL = 25.00

# Idade default quando nao informada (perfil mediano de 1a aquisicao)
IDADE_DEFAULT = 35

# Limite legal: idade + prazo nao pode passar de 80 anos e 6 meses (SFH)
IDADE_MAX_FIM_CONTRATO = 80


def _mip_mensal_para_idade(idade: int) -> float:
    """Retorna taxa MIP mensal sobre saldo devedor, conforme idade."""
    for limite, taxa in TABELA_MIP_MENSAL:
        if idade <= limite:
            return taxa
    return TABELA_MIP_MENSAL[-1][1]


def _seguros_mensais(saldo_devedor: float, valor_imovel: float, idade: int) -> tuple[float, float, float]:
    """(MIP, DFI, tarifa) cobrados em uma parcela.

    MIP incide sobre saldo devedor (cai junto com a divida).
    DFI incide sobre valor de avaliacao (constante).
    Tarifa e valor fixo.
    """
    mip = saldo_devedor * _mip_mensal_para_idade(idade)
    dfi = valor_imovel * DFI_MENSAL
    return mip, dfi, TARIFA_ADM_MENSAL


@dataclass(frozen=True)
class ResultadoSimulacao:
    sistema: Sistema
    valor_imovel: float
    entrada: float
    valor_financiado: float
    prazo_meses: int
    taxa_anual: float
    taxa_mensal: float
    # Parcela "tecnica" (so juros + amortizacao) — base para comparacao
    parcela_inicial: float
    parcela_final: float
    total_pago: float
    total_juros: float
    # Parcela REAL com seguros e tarifa estimados
    idade_tomador: int
    seguro_mip_inicial: float
    seguro_dfi_mensal: float
    tarifa_adm_mensal: float
    parcela_inicial_com_seguros: float
    parcela_final_com_seguros: float
    total_seguros_estimado: float
    total_pago_com_seguros: float
    renda_minima: float
    comprometimento_renda: float | None  # 0-1 (None se renda nao informada)
    primeiras_parcelas: list[dict]       # primeiras 12 parcelas (preview)
    custos_aquisicao: dict               # ITBI, registro, escritura


def _taxa_mensal(taxa_anual: float) -> float:
    """Converte taxa anual em mensal equivalente (juros compostos)."""
    return (1 + taxa_anual / 100) ** (1 / 12) - 1


def _validar(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float,
    idade_tomador: int | None = None,
) -> None:
    if valor_imovel <= 0:
        raise ValueError("valor_imovel deve ser positivo")
    if entrada < 0 or entrada >= valor_imovel:
        raise ValueError("entrada deve estar entre 0 e o valor do imovel")
    if prazo_meses < 12 or prazo_meses > 420:
        raise ValueError("prazo_meses deve estar entre 12 e 420")
    if taxa_anual < 0 or taxa_anual > 30:
        raise ValueError("taxa_anual fora do intervalo razoavel (0-30%)")
    if idade_tomador is not None:
        if idade_tomador < 18 or idade_tomador > 80:
            raise ValueError("idade_tomador deve estar entre 18 e 80")
        idade_fim = idade_tomador + prazo_meses / 12
        if idade_fim > IDADE_MAX_FIM_CONTRATO + 0.5:
            raise ValueError(
                f"idade ao fim do contrato ({idade_fim:.0f}) excede o limite SFH "
                f"({IDADE_MAX_FIM_CONTRATO} anos). Reduza o prazo."
            )


def _custos_aquisicao(valor_imovel: float) -> dict:
    """Custos pagos UMA VEZ ao comprar (sem entrar na parcela).

    Vitoria da Conquista/BA:
    - ITBI: 3% sobre valor de transmissao
    - Registro + escritura (Tabela CGJ/BA, faixa media): ~3% (degressivo)
    - Avaliacao do banco: ~R$ 3.500
    """
    itbi = valor_imovel * 0.03
    cartorio = valor_imovel * 0.03  # registro + escritura combinados
    avaliacao = 3500.0
    return {
        "itbi": round(itbi, 2),
        "cartorio": round(cartorio, 2),
        "avaliacao_banco": round(avaliacao, 2),
        "total": round(itbi + cartorio + avaliacao, 2),
    }


def calcular_sac(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float,
    renda_mensal: float | None = None,
    idade_tomador: int | None = None,
) -> ResultadoSimulacao:
    """Sistema de Amortizacao Constante: amortizacao fixa, parcela decrescente."""
    _validar(valor_imovel, entrada, prazo_meses, taxa_anual, idade_tomador)
    pv = valor_imovel - entrada
    i = _taxa_mensal(taxa_anual)
    amortizacao = pv / prazo_meses
    idade = idade_tomador if idade_tomador is not None else IDADE_DEFAULT

    parcelas: list[dict] = []
    saldo = pv
    total_pago = 0.0
    total_seguros = 0.0
    total_pago_com_seguros = 0.0
    parcela_inicial = parcela_final = 0.0
    parcela_inicial_cs = parcela_final_cs = 0.0
    mip_inicial = 0.0

    for n in range(1, prazo_meses + 1):
        juros = saldo * i
        parcela = amortizacao + juros
        mip, dfi, tarifa = _seguros_mensais(saldo, valor_imovel, idade)
        seguros = mip + dfi + tarifa
        parcela_cs = parcela + seguros
        saldo -= amortizacao
        total_pago += parcela
        total_seguros += seguros
        total_pago_com_seguros += parcela_cs
        if n == 1:
            parcela_inicial = parcela
            parcela_inicial_cs = parcela_cs
            mip_inicial = mip
        if n == prazo_meses:
            parcela_final = parcela
            parcela_final_cs = parcela_cs
        if n <= 12:
            parcelas.append({
                "n": n,
                "parcela": round(parcela, 2),
                "amortizacao": round(amortizacao, 2),
                "juros": round(juros, 2),
                "seguros": round(seguros, 2),
                "parcela_total": round(parcela_cs, 2),
                "saldo": round(max(saldo, 0), 2),
            })

    # Renda minima usa parcela COM seguros (e o que o banco analisa)
    renda_minima = parcela_inicial_cs / 0.30
    comprometimento = (parcela_inicial_cs / renda_mensal) if renda_mensal else None

    return ResultadoSimulacao(
        sistema="SAC",
        valor_imovel=valor_imovel,
        entrada=entrada,
        valor_financiado=pv,
        prazo_meses=prazo_meses,
        taxa_anual=taxa_anual,
        taxa_mensal=i * 100,
        parcela_inicial=round(parcela_inicial, 2),
        parcela_final=round(parcela_final, 2),
        total_pago=round(total_pago, 2),
        total_juros=round(total_pago - pv, 2),
        idade_tomador=idade,
        seguro_mip_inicial=round(mip_inicial, 2),
        seguro_dfi_mensal=round(valor_imovel * DFI_MENSAL, 2),
        tarifa_adm_mensal=round(TARIFA_ADM_MENSAL, 2),
        parcela_inicial_com_seguros=round(parcela_inicial_cs, 2),
        parcela_final_com_seguros=round(parcela_final_cs, 2),
        total_seguros_estimado=round(total_seguros, 2),
        total_pago_com_seguros=round(total_pago_com_seguros, 2),
        renda_minima=round(renda_minima, 2),
        comprometimento_renda=comprometimento,
        primeiras_parcelas=parcelas,
        custos_aquisicao=_custos_aquisicao(valor_imovel),
    )


def calcular_price(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float,
    renda_mensal: float | None = None,
    idade_tomador: int | None = None,
) -> ResultadoSimulacao:
    """Tabela Price: parcela fixa, juros decrescentes."""
    _validar(valor_imovel, entrada, prazo_meses, taxa_anual, idade_tomador)
    pv = valor_imovel - entrada
    i = _taxa_mensal(taxa_anual)
    n = prazo_meses
    idade = idade_tomador if idade_tomador is not None else IDADE_DEFAULT

    if i == 0:
        parcela = pv / n
    else:
        parcela = pv * (i * (1 + i) ** n) / ((1 + i) ** n - 1)

    parcelas: list[dict] = []
    saldo = pv
    total_pago = 0.0
    total_seguros = 0.0
    total_pago_com_seguros = 0.0
    parcela_inicial_cs = parcela_final_cs = 0.0
    mip_inicial = 0.0

    for k in range(1, n + 1):
        juros = saldo * i
        amort = parcela - juros
        mip, dfi, tarifa = _seguros_mensais(saldo, valor_imovel, idade)
        seguros = mip + dfi + tarifa
        parcela_cs = parcela + seguros
        saldo -= amort
        total_pago += parcela
        total_seguros += seguros
        total_pago_com_seguros += parcela_cs
        if k == 1:
            parcela_inicial_cs = parcela_cs
            mip_inicial = mip
        if k == n:
            parcela_final_cs = parcela_cs
        if k <= 12:
            parcelas.append({
                "n": k,
                "parcela": round(parcela, 2),
                "amortizacao": round(amort, 2),
                "juros": round(juros, 2),
                "seguros": round(seguros, 2),
                "parcela_total": round(parcela_cs, 2),
                "saldo": round(max(saldo, 0), 2),
            })

    renda_minima = parcela_inicial_cs / 0.30
    comprometimento = (parcela_inicial_cs / renda_mensal) if renda_mensal else None

    return ResultadoSimulacao(
        sistema="PRICE",
        valor_imovel=valor_imovel,
        entrada=entrada,
        valor_financiado=pv,
        prazo_meses=prazo_meses,
        taxa_anual=taxa_anual,
        taxa_mensal=i * 100,
        parcela_inicial=round(parcela, 2),
        parcela_final=round(parcela, 2),
        total_pago=round(total_pago, 2),
        total_juros=round(total_pago - pv, 2),
        idade_tomador=idade,
        seguro_mip_inicial=round(mip_inicial, 2),
        seguro_dfi_mensal=round(valor_imovel * DFI_MENSAL, 2),
        tarifa_adm_mensal=round(TARIFA_ADM_MENSAL, 2),
        parcela_inicial_com_seguros=round(parcela_inicial_cs, 2),
        parcela_final_com_seguros=round(parcela_final_cs, 2),
        total_seguros_estimado=round(total_seguros, 2),
        total_pago_com_seguros=round(total_pago_com_seguros, 2),
        renda_minima=round(renda_minima, 2),
        comprometimento_renda=comprometimento,
        primeiras_parcelas=parcelas,
        custos_aquisicao=_custos_aquisicao(valor_imovel),
    )


def simular(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float = 11.5,
    sistema: Sistema = "SAC",
    renda_mensal: float | None = None,
    idade_tomador: int | None = None,
) -> ResultadoSimulacao:
    """Atalho que escolhe SAC ou PRICE pela string."""
    if sistema == "SAC":
        return calcular_sac(valor_imovel, entrada, prazo_meses, taxa_anual, renda_mensal, idade_tomador)
    return calcular_price(valor_imovel, entrada, prazo_meses, taxa_anual, renda_mensal, idade_tomador)


# ─────────────────────────────────────────────────────────────────────────────
# Taxas referenciais por banco (atualizadas manualmente em 04/2026)
# ─────────────────────────────────────────────────────────────────────────────
TAXAS_BANCOS = {
    "caixa_sbpe": {"nome": "Caixa SBPE", "taxa_anual": 11.49, "lt_max": 0.80},
    "caixa_pro_cotista": {"nome": "Caixa Pro-Cotista (FGTS)", "taxa_anual": 9.49, "lt_max": 0.80},
    "bb_sbpe": {"nome": "Banco do Brasil", "taxa_anual": 11.79, "lt_max": 0.80},
    "itau": {"nome": "Itau", "taxa_anual": 11.99, "lt_max": 0.80},
    "bradesco": {"nome": "Bradesco", "taxa_anual": 12.20, "lt_max": 0.80},
    "santander": {"nome": "Santander", "taxa_anual": 11.89, "lt_max": 0.80},
}
