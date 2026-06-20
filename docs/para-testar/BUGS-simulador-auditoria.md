# 🐞 Auditoria do Simulador 2026 — 12 bugs (rodada pelo Thiago/Gemini)

## Resumo: o que está OK
- Motor SAC e PRICE (taxa efetiva composta) — correto.
- Faixa 4 e SBPE — OK. Comparativo Caixa/Itaú/Bradesco — OK.

## Bugs achados
- 🔴 BUG 1/2/3/5: fronteiras de faixa quebradas (R$3.201 ainda Faixa 1, R$5.001 Faixa 2, R$9.601 Faixa 3, R$13.001 ainda Faixa 4).
- 🔴 BUG 4: não valida teto MCMV (imóvel >R$600k com renda baixa continua MCMV em vez de SBPE).
- 🔴 BUG 7: taxa BB no gráfico 9,89% (real ~11,60% — misturou Pró-Cotista com SBPE).
- 🟡 BUG 6: Santander 11,79% vs real 11,69%.
- 🟡 BUG 9: taxas MCMV F1-F3 subestimadas ~0,5pp (otimista demais).
- 🟡 BUG 8/11: não mostra a 1ª parcela em texto (só no gráfico).
- 🟡 BUG 10: não valida idade+prazo > 80 anos.
- 🔴 BUG 12: não oferece Pró-Cotista (FGTS) pra renda alta (SBPE/F4) — cliente perde 1-2pp.

## RECOMENDAÇÃO (sênior): NÃO corrigir o JS frágil bug-a-bug
A calculadora do HTML tem taxas CHUMBADAS no JavaScript — vão desatualizar sempre e taxa de banco
errada é enganoso/risco. Quando implantar, o certo é:
1. **Usar o NOSSO motor** `/api/simular-financiamento` (`app/financiamento.py`) pra a parcela — ele já
   tem MIP real por idade, DFI, tarifa, LIMITE DE IDADE (80 anos), comparativo de bancos. Resolve
   BUG 8/10/11 + parcela com seguros de uma vez.
2. **Faixa MCMV + teto + Pró-Cotista**: hoje só o cliente-JS classifica faixa (com os bugs). O backend
   recebe a taxa pronta. → Mover a classificação de faixa/teto/subsídio/Pró-Cotista pro BACKEND (uma
   fonte só), corrigindo BUG 1-5, 7, 9, 12 num lugar robusto e testável.
3. Front só desenha (sliders + gráfico Chart.js) e chama o backend. Sempre com o aviso "ESTIMATIVA".

Assim a gente conserta TUDO em um lugar (backend, com teste) em vez de remendar JS que vai quebrar de novo.

## Status: REGISTRADO. Decidir quando implantar (com o Thiago).
