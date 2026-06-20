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

## ⚠️ As DUAS IAs do simulador (Thiago apontou)
O HTML tem 2 pontos de IA, hoje ambos ligados na Ana (mesma função `fetchGeminiResponse`):
1. **Chat consultor** (`sendChatMessage`) → Ana conversa/qualifica. OK do jeito que está.
2. **Relatório IA** (`generateAIReport`) → analisa a simulação. PROBLEMA: a Ana tem trava de
   não cravar número, então ela desvia em vez de comentar a conta.

**Como resolver ao implantar:** no relatório, NÃO pedir pra Ana calcular. Passar pra ela os
números que a CALCULADORA já computou (parcela, taxa, faixa) e pedir só a leitura qualitativa
("esse perfil está confortável? ponto de atenção?"), sempre marcando "estimativa". A ferramenta
calcula (com disclaimer), a Ana só interpreta — assim ela não infringe a trava.
