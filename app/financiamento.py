"""Calculadora de financiamento imobiliario — SAC e PRICE.

Tudo em Python puro (sem numpy). Valores em reais (float).
Taxa anual em % (ex.: 11.5 para 11,5% a.a.).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Sistema = Literal["SAC", "PRICE"]


@dataclass(frozen=True)
class ResultadoSimulacao:
    sistema: Sistema
    valor_imovel: float
    entrada: float
    valor_financiado: float
    prazo_meses: int
    taxa_anual: float
    taxa_mensal: float
    parcela_inicial: float
    parcela_final: float
    total_pago: float
    total_juros: float
    renda_minima: float
    comprometimento_renda: float | None  # 0-1 (None se renda nao informada)
    primeiras_parcelas: list[dict]       # primeiras 12 parcelas (preview)


def _taxa_mensal(taxa_anual: float) -> float:
    """Converte taxa anual em mensal equivalente (juros compostos)."""
    return (1 + taxa_anual / 100) ** (1 / 12) - 1


def _validar(valor_imovel: float, entrada: float, prazo_meses: int, taxa_anual: float) -> None:
    if valor_imovel <= 0:
        raise ValueError("valor_imovel deve ser positivo")
    if entrada < 0 or entrada >= valor_imovel:
        raise ValueError("entrada deve estar entre 0 e o valor do imovel")
    if prazo_meses < 12 or prazo_meses > 420:
        raise ValueError("prazo_meses deve estar entre 12 e 420")
    if taxa_anual < 0 or taxa_anual > 30:
        raise ValueError("taxa_anual fora do intervalo razoavel (0-30%)")


def calcular_sac(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float,
    renda_mensal: float | None = None,
) -> ResultadoSimulacao:
    """Sistema de Amortizacao Constante: amortizacao fixa, parcela decrescente."""
    _validar(valor_imovel, entrada, prazo_meses, taxa_anual)
    pv = valor_imovel - entrada
    i = _taxa_mensal(taxa_anual)
    amortizacao = pv / prazo_meses

    parcelas: list[dict] = []
    saldo = pv
    total_pago = 0.0
    parcela_inicial = parcela_final = 0.0

    for n in range(1, prazo_meses + 1):
        juros = saldo * i
        parcela = amortizacao + juros
        saldo -= amortizacao
        total_pago += parcela
        if n == 1:
            parcela_inicial = parcela
        if n == prazo_meses:
            parcela_final = parcela
        if n <= 12:
            parcelas.append({
                "n": n,
                "parcela": round(parcela, 2),
                "amortizacao": round(amortizacao, 2),
                "juros": round(juros, 2),
                "saldo": round(max(saldo, 0), 2),
            })

    renda_minima = parcela_inicial / 0.30  # 30% comprometimento
    comprometimento = (parcela_inicial / renda_mensal) if renda_mensal else None

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
        renda_minima=round(renda_minima, 2),
        comprometimento_renda=comprometimento,
        primeiras_parcelas=parcelas,
    )


def calcular_price(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float,
    renda_mensal: float | None = None,
) -> ResultadoSimulacao:
    """Tabela Price: parcela fixa, juros decrescentes."""
    _validar(valor_imovel, entrada, prazo_meses, taxa_anual)
    pv = valor_imovel - entrada
    i = _taxa_mensal(taxa_anual)
    n = prazo_meses

    if i == 0:
        parcela = pv / n
    else:
        parcela = pv * (i * (1 + i) ** n) / ((1 + i) ** n - 1)

    parcelas: list[dict] = []
    saldo = pv
    total_pago = 0.0

    for k in range(1, n + 1):
        juros = saldo * i
        amort = parcela - juros
        saldo -= amort
        total_pago += parcela
        if k <= 12:
            parcelas.append({
                "n": k,
                "parcela": round(parcela, 2),
                "amortizacao": round(amort, 2),
                "juros": round(juros, 2),
                "saldo": round(max(saldo, 0), 2),
            })

    renda_minima = parcela / 0.30
    comprometimento = (parcela / renda_mensal) if renda_mensal else None

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
        renda_minima=round(renda_minima, 2),
        comprometimento_renda=comprometimento,
        primeiras_parcelas=parcelas,
    )


def simular(
    valor_imovel: float,
    entrada: float,
    prazo_meses: int,
    taxa_anual: float = 11.5,
    sistema: Sistema = "SAC",
    renda_mensal: float | None = None,
) -> ResultadoSimulacao:
    """Atalho que escolhe SAC ou PRICE pela string."""
    if sistema == "SAC":
        return calcular_sac(valor_imovel, entrada, prazo_meses, taxa_anual, renda_mensal)
    return calcular_price(valor_imovel, entrada, prazo_meses, taxa_anual, renda_mensal)


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
