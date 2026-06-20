#!/usr/bin/env python3
"""TESTE DE ESTRESSE da tabela parametrizada de taxas 2026 (taxas_2026.py).

Parte A: cenários nomeados (as fronteiras/bugs do relatório).
Parte B: VARREDURA em loop de 200+ combinações (renda x valor x FGTS), checando os
INVARIANTES que SEMPRE têm que valer. Acha qualquer buraco na lógica de faixa/teto/Pró-Cotista.

Uso:  venv/bin/python docs/para-testar/teste_taxas.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxas_2026 as T

OK = "✅"; FALHA = "❌"

# ── PARTE A: cenários nomeados ───────────────────────────────────────────────
CASOS = [
    ("Fronteira F1->F2 (renda 3.201)",       3201, 200000, False, "MCMV", "Faixa 2"),
    ("Fronteira F2->F3 (renda 5.001)",       5001, 300000, False, "MCMV", "Faixa 3"),
    ("Fronteira F3->F4 (renda 9.601)",       9601, 400000, False, "MCMV", "Faixa 4"),
    ("Fronteira F4->SBPE (renda 13.001)",   13001, 700000, False, "SBPE", "Mercado Livre"),
    ("Imovel 601k, renda 13k (>teto F4)",   13000, 601000, False, "SBPE", "Mercado Livre"),
    ("FGTS + imovel 450k (Pro-Cotista)",    13001, 450000, True,  "Pró-Cotista FGTS", "—"),
    ("FGTS + imovel 700k (>teto -> SBPE)",  13001, 700000, True,  "SBPE", "Mercado Livre"),
    ("MCMV F1 normal",                       2500, 180000, False, "MCMV", "Faixa 1"),
    ("MCMV F2 com FGTS",                     4500, 200000, True,  "MCMV", "Faixa 2"),
    ("Exato F1 (renda 3.200)",               3200, 200000, False, "MCMV", "Faixa 1"),
    ("Exato F2 (renda 5.000)",               5000, 250000, False, "MCMV", "Faixa 2"),
    ("Exato teto F4 (imovel 600k)",         13000, 600000, False, "MCMV", "Faixa 4"),
    ("Renda altissima 20k",                 20000, 800000, False, "SBPE", "Mercado Livre"),
    ("Renda baixa mas imovel caro 280k F1", 3000, 280000, False, "SBPE", "Mercado Livre"),
]

print(f"=== TESTE DE ESTRESSE — TAXAS 2026 (ref: {T.DATA_REFERENCIA}) ===\n")
print("PARTE A — cenarios nomeados:")
print(f"{'CENARIO':38} {'ESPERADO':22} {'OBTIDO':22} TAXA")
print("-" * 96)
passou_a = 0
for desc, renda, valor, fgts, mod_esp, faixa_esp in CASOS:
    r = T.classificar_faixa(renda, valor, fgts)
    obtido = f"{r['modalidade']}/{r['faixa']}"
    acerto = (r["modalidade"] == mod_esp and r["faixa"] == faixa_esp)
    passou_a += acerto
    print(f"{desc:38} {mod_esp+'/'+faixa_esp:22} {obtido:22} {r['taxa_aa']*100:5.2f}%  {OK if acerto else FALHA}")
print(f"\n>> Parte A: {passou_a}/{len(CASOS)} OK\n")

# ── PARTE B: varredura em loop + invariantes ─────────────────────────────────
TETO_MCMV_MAX = max(f[4] for f in T.MCMV_FAIXAS)      # 600k
RENDA_MCMV_MAX = max(f[1] for f in T.MCMV_FAIXAS)     # 13000
TETO_PRO = T.PRO_COTISTA["teto_imovel_novo"]          # 500k

def faixa_esperada(renda):
    for label, renda_max, *_ in T.MCMV_FAIXAS:
        if renda <= renda_max:
            return label
    return None

falhas = []
total = 0
for renda in range(1000, 16001, 250):          # 61 valores de renda
    for valor in range(100000, 800001, 50000):  # 15 valores de imovel
        for fgts in (False, True):               # 2
            total += 1
            r = T.classificar_faixa(renda, valor, fgts)
            mod, taxa = r["modalidade"], r["taxa_aa"]
            ctx = f"renda={renda} valor={valor} fgts={fgts} -> {mod}/{r['faixa']}"
            # INV1: sempre retorna taxa válida (0 < taxa < 0.20)
            if not (0 < taxa < 0.20):
                falhas.append(f"INV1 taxa fora de faixa: {ctx} taxa={taxa}")
            # INV2: MCMV só se renda<=13k E valor<=teto da faixa
            if mod == "MCMV":
                fx = faixa_esperada(renda)
                teto_fx = dict((f[0], f[4]) for f in T.MCMV_FAIXAS)[r["faixa"]]
                if renda > RENDA_MCMV_MAX or valor > teto_fx or r["faixa"] != fx:
                    falhas.append(f"INV2 MCMV indevido: {ctx} (faixa esp={fx}, teto={teto_fx})")
            # INV3: imovel > 600k NUNCA é MCMV
            if valor > TETO_MCMV_MAX and mod == "MCMV":
                falhas.append(f"INV3 imovel>600k virou MCMV: {ctx}")
            # INV4: renda > 13k NUNCA é MCMV
            if renda > RENDA_MCMV_MAX and mod == "MCMV":
                falhas.append(f"INV4 renda>13k virou MCMV: {ctx}")
            # INV5: Pró-Cotista só com FGTS e imovel<=500k
            if mod == "Pró-Cotista FGTS" and not (fgts and valor <= TETO_PRO):
                falhas.append(f"INV5 Pro-Cotista indevido: {ctx}")
            # INV6: imovel>500k com FGTS e fora de MCMV -> SBPE (nao Pro-Cotista)
            if fgts and valor > TETO_PRO and mod == "Pró-Cotista FGTS":
                falhas.append(f"INV6 Pro-Cotista acima do teto: {ctx}")

print(f"PARTE B — varredura: {total} combinacoes (renda x valor x FGTS)")
if not falhas:
    print(f">> {total}/{total} passaram TODOS os invariantes {OK}")
else:
    print(f">> {len(falhas)} FALHAS de invariante {FALHA}:")
    for f in falhas[:20]:
        print("   -", f)

print("\n" + "=" * 96)
print(f"RESULTADO FINAL: Parte A {passou_a}/{len(CASOS)} · Parte B {total-len(falhas)}/{total}")
print("✅ Taxas reais 2026 (verificadas no deep-research). MCMV/Selic/idade = alta confianca; SBPE por banco e ITBI = conferir oficial.")
