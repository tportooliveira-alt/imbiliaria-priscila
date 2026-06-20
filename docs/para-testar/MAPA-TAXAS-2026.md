# 🏦 Mapa de Taxas 2026 — referência (do relatório de varredura completa, jun/2026)

Fonte: relatório do Sonnet/PC (MySide, BCB, Caixa). Já plugado em `taxas_2026.py`.

## MCMV (Minha Casa Minha Vida)
| Faixa | Renda até | c/ FGTS | s/ FGTS | Teto imóvel | Prazo |
|---|---|---|---|---|---|
| 1 | R$ 3.200 | 3,50–4,00% | 4,00–4,50% | R$ 275k | 420m |
| 2 | R$ 5.000 | 4,75% | 4,75–5,50% | R$ 275k | 420m |
| 3 | R$ 9.600 | 6,50% | 7,00–7,66% | R$ 400k | 420m |
| 4 | R$ 13.000 | 9,50% | 10,00% | R$ 600k | 420m |

## SBPE (mercado aberto, + TR, balcão jun/2026)
| Banco | Taxa mín | Pró-Cotista | Prazo | LTV |
|---|---|---|---|---|
| Caixa | 10,26% | 9,01% | 35a | 90% |
| Sicredi | ~10,33% | — | 30a | 80% |
| Sicoob | ~10,50% | — | 30a | 80% |
| Banco do Brasil | 11,60% | 9,00% | 30a | 80% |
| Itaú | 11,60% | — | 30a | 80% |
| Santander | 11,69% | — | 30a | 80% |
| Bradesco | 11,70% | — | 30a | 80% |
| Banco Inter | 13,76% (ou 9,5%+IPCA) | 9,00% | 30a | 75% |
| **Caixa Taxa Fixa** | **17,32% (SEM TR)** | — | 15a | 80% |

## Modalidades que o simulador NÃO tinha (agora mapeadas)
- **Pró-Cotista FGTS** no SBPE (renda alta + FGTS) → 9,00–9,01% (economia de R$ 24k–52k em 30a).
- **Home Equity** (garantia de imóvel quitado): 1,12–1,80%/mês, até 20a, LTV 60%.
- **Consórcio**: 0% juros + 1,5–2% adm/ano.
- **SFI** (imóvel > R$ 1,5M): 12–16%, sem FGTS.
- **IPCA + spread** (Inter): 9,5% + IPCA.
- **VCA Facilita** (LOCAL de Conquista): até 240x, sem IGPM/INCC, entrada em 36x — p/ autônomo/MEI.
- **Direto construtora** (Gráfico, AGRA, JC): parcelado, INCC durante a obra.

## Bugs do simulador JS que a lógica nova (taxas_2026.py) já resolve
Fronteiras de faixa · teto MCMV R$600k · Pró-Cotista no SBPE · taxa por banco (não 11% fixo) ·
bancos faltando (Inter/Sicoob/Sicredi). Validado em `teste_taxas.py` (8/8).

## Falta exibir (UX, quando implantar): 1ª parcela em texto · CET · comparativo por banco.

## ✅ Verificação adversarial (deep-research, fontes gov.br) — correções
- **ALTA confiança** (gov.br, 3 votos): MCMV 4 faixas + tetos (275k/275k/400k/600k, Portaria MCID 333,
  vigente 22/04/2026) · Selic 14,25% (corte 17/06/2026) · idade 75→**80 anos e 6 meses** · prazo 420m.
- 🔴 **CORREÇÃO — Pró-Cotista FGTS:** NÃO é até 1,5M. É pra imóveis **NOVOS até ~R$ 500 mil** (usados ~350k),
  taxa **~8,66%** (6,5%+2,16%) ou 9,00-9,01%+TR. (já corrigido em taxas_2026.py)
- 🟡 **SBPE por banco: NÃO confirmado** — fontes divergem (balcão vs média BCB abr/2026: Caixa 8,13%,
  Inter 9,12%, BB 9,89%...). No simulador: tratar como ESTIMATIVA e mandar conferir oficial.
- 🟡 **ITBI 3% VDC: NÃO confirmado** — conferir alíquota na Prefeitura de Vitória da Conquista.
- Teto SFH subiu pra R$ 2,25 milhões (Resolução CMN 5.255/25, 10/10/2025).

Relatório verificado completo: `pesquisa-taxas-verificada.txt`.
