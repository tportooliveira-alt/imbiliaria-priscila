# Simulador de Financiamento 2026 — PARA TESTAR (não está no ar)

Arquivo: `simulador-financiamento-2026.html` (enviado pelo Thiago, 20/06).

## O que é
Página completa e bonita (cores da marca: navy #16284B / dourado #c9943a) com:
- Simulador paramétrico (renda, valor, entrada, SAC/Price, idade, FGTS) + gráfico de amortização (Chart.js)
- Comparativo de taxas dos bancos + bairros de VDC + custos ocultos (ITBI/cartório/seguros)
- Widget de chat IA (hoje aponta pro Gemini, chave vazia = modo demo)

## Plano (quando o Thiago liberar — NÃO agora)
- Implantar no site numa **aba à parte**, JUNTO com a calculadora de valor de imóvel (AVM) — pra ficar tudo organizado num "centro de ferramentas".
- Trocar a IA do Gemini pela NOSSA: chat → Ana (/api/chat); cálculo → /api/simular-financiamento (nosso backend, com aviso de estimativa).
- Manter o aviso "ESTIMATIVA — o banco confirma" bem claro (decisão do dono).

## Status: GUARDADO. Só testar depois.
