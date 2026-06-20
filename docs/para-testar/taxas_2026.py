"""TABELA PARAMETRIZADA DE TAXAS 2026 — fonte única da verdade (PARA TESTE).

Objetivo: tirar as taxas chumbadas do JavaScript do simulador e centralizar TUDO aqui,
num lugar só, fácil de atualizar quando a pesquisa profunda (deep-research) retornar.

⚠️ Os valores abaixo são PLACEHOLDER (mistura do que já temos + o relatório de auditoria).
Marcados com:  # ⏳PESQUISA  = trocar pelo valor confirmado de 2026 quando o relatório chegar.
              # ✅CONFIRM  = já validado.

Plano: depois de preenchido e testado, isto vira `app/taxas_2026.py` e o
`app/financiamento.py` passa a importar daqui (uma fonte só). O simulador HTML chama
`/api/simular-financiamento`, que usa estes parâmetros — acabam os 12 bugs do JS.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# 1. MACRO
# ─────────────────────────────────────────────────────────────────────────────
SELIC_AA = 0.1425          # ⏳PESQUISA — Selic 2026 (relatório citou 14,25%)
DATA_REFERENCIA = "2026-06"  # carimbo da última atualização das taxas

# ─────────────────────────────────────────────────────────────────────────────
# 2. MINHA CASA MINHA VIDA (MCMV) — por FAIXA
#    renda_max: teto de renda mensal da faixa
#    taxa_aa / taxa_aa_cotista: taxa ao ano (sem / com 3+ anos de FGTS)
#    teto_imovel: valor MÁXIMO do imóvel pra se enquadrar na faixa
#    subsidio_max: subsídio máximo possível na faixa
# ─────────────────────────────────────────────────────────────────────────────
MCMV_FAIXAS = [
    # label,      renda_max, taxa_aa,  taxa_aa_cotista, teto_imovel, subsidio_max
    ("Faixa 1",     3200,    0.0400,   0.0400,          264000,      55000),   # ⏳PESQUISA (relatório: real 4,0-4,5%)
    ("Faixa 2",     5000,    0.0475,   0.0475,          264000,      35000),   # ⏳PESQUISA (real 4,75-5,5%)
    ("Faixa 3",     9600,    0.0766,   0.0766,          350000,      0),       # ⏳PESQUISA (real 7,66%)
    ("Faixa 4",    13000,    0.1000,   0.0900,          600000,      0),       # ⏳PESQUISA (teto F4 = 600k)
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. SBPE (mercado livre) — taxa a.a. por banco (financiamentos acima do teto MCMV)
# ─────────────────────────────────────────────────────────────────────────────
SBPE_BANCOS = {
    "Caixa":            0.1026,   # ⏳PESQUISA (relatório: 10,26% mín — ✅bate)
    "Banco do Brasil":  0.1160,   # ⏳PESQUISA (relatório: BUG, JS mostrava 9,89%; real ~11,60%)
    "Itau":             0.1160,   # ✅CONFIRM (relatório OK)
    "Bradesco":         0.1170,   # ✅CONFIRM
    "Santander":        0.1169,   # ⏳PESQUISA (relatório: real 11,69%, JS mostrava 11,79%)
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. PRO-COTISTA FGTS — taxa menor pra quem tem 3+ anos de FGTS (renda alta/SBPE)
#    (o simulador atual ESQUECE isso — BUG 12)
# ─────────────────────────────────────────────────────────────────────────────
PRO_COTISTA = {
    "exige_anos_fgts": 3,
    "teto_imovel": 1500000,        # ⏳PESQUISA (tinhamos 1,5 mi)
    "taxa_aa": {
        "Caixa":           0.0901,  # ⏳PESQUISA
        "Banco do Brasil": 0.0900,  # ⏳PESQUISA
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. LIMITES LEGAIS
# ─────────────────────────────────────────────────────────────────────────────
IDADE_MAX_FIM_CONTRATO = 80     # ✅CONFIRM (idade + prazo <= 80 anos e 6 meses)
LTV_MAX = 0.80                  # ⏳PESQUISA — % máx financiável (tínhamos 80%)

# ─────────────────────────────────────────────────────────────────────────────
# 6. CUSTOS DE AQUISIÇÃO — Vitória da Conquista/BA (pagos UMA vez)
# ─────────────────────────────────────────────────────────────────────────────
CUSTOS_VDC = {
    "itbi_pct": 0.03,            # ✅CONFIRM — ITBI 3% em VDC
    "cartorio_pct": 0.03,        # ⏳PESQUISA (1-2%? 3%? confirmar)
    "avaliacao_banco": 3500,     # ⏳PESQUISA (~R$ 3.500)
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. SEGUROS OBRIGATÓRIOS (já tratados no app/financiamento.py com tabela por idade)
# ─────────────────────────────────────────────────────────────────────────────
DFI_MENSAL = 0.000140           # ✅CONFIRM (0,014% a.m. sobre valor avaliação)
TARIFA_ADM_MENSAL = 25          # ⏳PESQUISA (R$ 25/mês)
# MIP: tabela por idade — já em app/financiamento.py::TABELA_MIP_MENSAL


def classificar_faixa(renda_mensal: float, valor_imovel: float, tem_fgts: bool):
    """Classifica a operação (corrige os BUGs 1-5 do simulador: fronteiras + teto MCMV).

    Retorna dict: {modalidade, faixa, taxa_aa, teto_ok}.
    Regra: se renda <= teto da faixa E imóvel <= teto_imovel da faixa -> MCMV.
           senão -> SBPE (com Pró-Cotista se tiver FGTS).
    """
    for label, renda_max, taxa, taxa_cot, teto_imovel, _sub in MCMV_FAIXAS:
        if renda_mensal <= renda_max:
            if valor_imovel <= teto_imovel:
                return {
                    "modalidade": "MCMV",
                    "faixa": label,
                    "taxa_aa": taxa_cot if tem_fgts else taxa,
                }
            break  # renda cabe na faixa mas imóvel acima do teto -> cai pra SBPE
    # SBPE — Pró-Cotista se tiver FGTS e imóvel dentro do teto
    if tem_fgts and valor_imovel <= PRO_COTISTA["teto_imovel"]:
        return {"modalidade": "Pró-Cotista FGTS", "faixa": "—",
                "taxa_aa": min(PRO_COTISTA["taxa_aa"].values())}
    return {"modalidade": "SBPE", "faixa": "Mercado Livre",
            "taxa_aa": min(SBPE_BANCOS.values())}
