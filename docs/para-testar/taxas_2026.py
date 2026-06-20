"""TABELA PARAMETRIZADA DE TAXAS 2026 — fonte única da verdade (PARA TESTE).

Valores REAIS de 2026 (jun/2026), do relatório de varredura completa (Sonnet/PC + MySide/BCB/Caixa).
Centraliza TUDO aqui pra tirar as taxas chumbadas do JavaScript do simulador.

Plano: depois de testado, vira `app/taxas_2026.py` e o `app/financiamento.py` importa daqui.
O simulador HTML chama `/api/simular-financiamento`, que usa estes parâmetros — acabam os bugs.
"""
from __future__ import annotations

SELIC_AA = 0.1425            # Selic 2026
DATA_REFERENCIA = "2026-06"  # jun/2026

# ─────────────────────────────────────────────────────────────────────────────
# 1. MCMV — Minha Casa Minha Vida (por FAIXA)
#    (label, renda_max, taxa_sem_fgts, taxa_com_fgts, teto_imovel, prazo_meses, subsidio_max)
# ─────────────────────────────────────────────────────────────────────────────
MCMV_FAIXAS = [
    ("Faixa 1",  3200, 0.0450, 0.0400, 275000, 420, 55000),
    ("Faixa 2",  5000, 0.0550, 0.0475, 275000, 420, 35000),
    ("Faixa 3",  9600, 0.0766, 0.0650, 400000, 420, 0),
    ("Faixa 4", 13000, 0.1000, 0.0950, 600000, 420, 0),
]

# ─────────────────────────────────────────────────────────────────────────────
# 2. SBPE — mercado aberto (taxa a.a. + TR) por banco
#    ⚠️ CONFIANÇA BAIXA (deep-research refutou): fontes DIVERGEM muito — estas sao taxas
#    de "balcao"/anunciadas; as MEDIAS do BCB (abr/2026) sao outras (Caixa 8,13%, Inter 9,12%,
#    BB 9,89%, Sicoob 11,69%, Sicredi 11,72%, Bradesco 11,76%, Santander 11,85%, Itau 11,86%).
#    → no simulador, SEMPRE rotular como ESTIMATIVA e mandar conferir na simulacao oficial do banco.
#    inclui prazo_max (anos) e LTV máx financiável.
# ─────────────────────────────────────────────────────────────────────────────
SBPE_BANCOS = {
    #  banco              taxa_aa  prazo_anos  ltv
    "Caixa":            (0.1026,  35, 0.90),
    "Sicredi":          (0.1033,  30, 0.80),
    "Sicoob":           (0.1050,  30, 0.80),
    "Banco do Brasil":  (0.1160,  30, 0.80),
    "Itau":             (0.1160,  30, 0.80),
    "Santander":        (0.1169,  30, 0.80),
    "Bradesco":         (0.1170,  30, 0.80),
    "Banco Inter":      (0.1376,  30, 0.75),
}
# Caixa Taxa Fixa (SEM TR, previsibilidade total): 17,32% a.a., prazo 15 anos.
CAIXA_TAXA_FIXA = (0.1732, 15, 0.80)

# ─────────────────────────────────────────────────────────────────────────────
# 3. PRÓ-COTISTA FGTS — ✅VERIFICADO (deep-research, fontes gov): voltou em 2026 pra imoveis
#    NOVOS ate ~R$ 500 mil (usados ~R$ 350 mil) — NAO ate 1,5M (isso era erro).
#    Taxa-base 6,5% + 2,16% (remuneracao do agente) = ~8,66% a.a. ao consumidor, OU 9,00-9,01%+TR
#    conforme o banco. Exige 3+ anos de FGTS (ou saldo >= 10% da avaliacao).
# ─────────────────────────────────────────────────────────────────────────────
PRO_COTISTA = {
    "exige_anos_fgts": 3,
    "teto_imovel_novo": 500000,
    "teto_imovel_usado": 350000,
    "taxa_aa_base": 0.0866,  # 6,5% + 2,16%
    "taxa_aa": {"Banco do Brasil": 0.0900, "Banco Inter": 0.0900, "Caixa": 0.0901},
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. MODALIDADES ALTERNATIVAS (faltavam no simulador) — referência
# ─────────────────────────────────────────────────────────────────────────────
OUTRAS_MODALIDADES = {
    "SFI (imovel > 1,5M)":      {"taxa_aa": (0.12, 0.16), "fgts": False, "obs": "alto padrão, negociável"},
    "IPCA + spread (Inter)":    {"taxa": "9,5% a.a. + IPCA", "obs": "classe média digital"},
    "Home Equity":              {"taxa_am": (0.0112, 0.0180), "prazo_anos": 20, "ltv": 0.60,
                                 "obs": "garantia de imóvel quitado (Santander/Inter/Itaú/Creditas)"},
    "Consorcio":                {"juros": 0.0, "taxa_adm_aa": (0.015, 0.020),
                                 "obs": "sem juros, sem pressa, disciplinado"},
    "VCA Facilita (LOCAL VDC)": {"taxa": "sem IGPM/INCC", "parcelas": 240, "entrada_parcelada": 36,
                                 "obs": "programa local p/ autônomo/MEI/sem renda formal"},
    "Direto construtora (VDC)": {"obs": "Gráfico, AGRA, JC Imóveis — parcelado, INCC durante a obra"},
    "INCC (imóvel na planta)":  {"taxa_aa": 0.065, "obs": "índice da construção durante a obra"},
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. LIMITES + CUSTOS + SEGUROS
# ─────────────────────────────────────────────────────────────────────────────
IDADE_MAX_FIM_CONTRATO = 80     # ✅VERIFICADO — idade + prazo <= 80 anos e 6 meses (subiu de 75)
# ⚠️ ITBI 3% NAO confirmado (deep-research refutou) — e tributo municipal do comprador, mas a
#    aliquota exata precisa ser conferida na Prefeitura de Vitoria da Conquista. cartorio/avaliacao idem.
CUSTOS_VDC = {"itbi_pct": 0.03, "cartorio_pct": 0.03, "avaliacao_banco": 3500}  # ⏳conferir oficial
DFI_MENSAL = 0.000140
TARIFA_ADM_MENSAL = 25
# MIP: tabela por idade — já em app/financiamento.py::TABELA_MIP_MENSAL


def classificar_faixa(renda_mensal: float, valor_imovel: float, tem_fgts: bool) -> dict:
    """Classifica a operação — corrige os bugs: fronteiras de faixa + teto MCMV + Pró-Cotista."""
    for label, renda_max, taxa_sem, taxa_com, teto_imovel, _prazo, _sub in MCMV_FAIXAS:
        if renda_mensal <= renda_max:
            if valor_imovel <= teto_imovel:
                return {"modalidade": "MCMV", "faixa": label,
                        "taxa_aa": taxa_com if tem_fgts else taxa_sem}
            break  # renda cabe mas imóvel acima do teto da faixa -> SBPE
    if tem_fgts and valor_imovel <= PRO_COTISTA["teto_imovel_novo"]:
        return {"modalidade": "Pró-Cotista FGTS", "faixa": "—",
                "taxa_aa": PRO_COTISTA["taxa_aa_base"]}  # ~8,66% (6,5%+2,16%)
    melhor = min(SBPE_BANCOS.items(), key=lambda kv: kv[1][0])  # banco mais barato
    return {"modalidade": "SBPE", "faixa": "Mercado Livre",
            "taxa_aa": melhor[1][0], "melhor_banco": melhor[0]}
