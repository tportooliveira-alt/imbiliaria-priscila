#!/usr/bin/env python3
"""TESTE da tabela parametrizada de taxas 2026 (docs/para-testar/taxas_2026.py).

Roda os cenários EXATOS que o relatório de auditoria marcou como BUG no simulador JS
e confere se a lógica nova (classificar_faixa) acerta. Quando a pesquisa profunda
atualizar os números em taxas_2026.py, é só rodar isto de novo.

Uso:  venv/bin/python docs/para-testar/teste_taxas.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taxas_2026 as T

OK = "✅"; FALHA = "❌"

# (descricao, renda, valor_imovel, tem_fgts, modalidade_esperada, faixa_esperada)
CASOS = [
    # Fronteiras de faixa (BUGs 1-3,5) — o JS errava todos
    ("Fronteira F1→F2 (renda 3.201)",        3201, 200000, False, "MCMV", "Faixa 2"),
    ("Fronteira F2→F3 (renda 5.001)",        5001, 300000, False, "MCMV", "Faixa 3"),
    ("Fronteira F3→F4 (renda 9.601)",        9601, 400000, False, "MCMV", "Faixa 4"),
    ("Fronteira F4→SBPE (renda 13.001)",    13001, 700000, False, "SBPE", "Mercado Livre"),
    # Teto MCMV (BUG 4) — imóvel acima de 600k não pode ser MCMV
    ("Imóvel 601k, renda 13.000 (>teto F4)",13000, 601000, False, "SBPE", "Mercado Livre"),
    # Pró-Cotista (BUG 12) — renda alta + FGTS deve pegar Pró-Cotista, não SBPE cheio
    ("Renda alta + FGTS (Pró-Cotista)",     13001, 700000, True,  "Pró-Cotista FGTS", "—"),
    # Casos normais (devem continuar certos)
    ("MCMV F1 normal",                       2500, 180000, False, "MCMV", "Faixa 1"),
    ("MCMV F2 com FGTS",                     4500, 200000, True,  "MCMV", "Faixa 2"),
]

print(f"=== TESTE TAXAS 2026 (ref: {T.DATA_REFERENCIA}) ===\n")
print(f"{'CENÁRIO':40} {'ESPERADO':22} {'OBTIDO':22} TAXA")
print("-" * 100)
passou = 0
for desc, renda, valor, fgts, mod_esp, faixa_esp in CASOS:
    r = T.classificar_faixa(renda, valor, fgts)
    obtido = f"{r['modalidade']}/{r['faixa']}"
    esperado = f"{mod_esp}/{faixa_esp}"
    acerto = (r["modalidade"] == mod_esp and r["faixa"] == faixa_esp)
    passou += acerto
    print(f"{desc:40} {esperado:22} {obtido:22} {r['taxa_aa']*100:.2f}%  {OK if acerto else FALHA}")

print("-" * 100)
print(f"\nRESULTADO: {passou}/{len(CASOS)} cenários corretos.")
print("⏳ Os valores de TAXA ainda são placeholder — trocar em taxas_2026.py quando a pesquisa cair.")
