# Pesquisa — Como a Ana deve CAPTURAR contato (deep-research, 22/06)

Fonte: deep-research (19 fontes, 91 alegações, 15 confirmadas / 10 refutadas na checagem adversarial).
Objetivo: aumentar a taxa de captura de contato no chat (estava ~0%) sem perder o tom caloroso.

## Achados de ALTA confiança (consenso 3-0)
1. **NÃO pedir contato cedo / na 1ª mensagem.** Abrir com 1 pergunta leve ("comprar, vender ou só
   olhando?") → entregar valor real (responder sobre imóvel/bairro) → pedir o contato **quando o lead já
   esquentou**. Aí o pedido soa natural, não forçado.
2. **Máximo 3-5 perguntas de qualificação, UMA por vez** (progressive profiling). Nunca formulário
   multi-campo de uma vez — espanta (abandono).
3. **Pedir contato como TROCA DE VALOR**, não cobrança: oferecer a simulação / avaliação / lista de
   imóveis em troca. Script de referência: *"posso te mandar os detalhes/a simulação por aqui? me passa
   seu WhatsApp"*. A simulação/lista é a "moeda".
4. **Assertiva ≠ agressiva.** Fazer o pedido com CONFIANÇA e justificativa de benefício, UMA vez. Se a
   pessoa recuar/ficar quieta → cutucar de leve UMA vez e PARAR (badgerar derruba a conversão).
5. **Erros que zeram a conversão:** pedir cedo demais, muitos dados de uma vez, tom robótico, interromper
   na hora da decisão. (provável causa do ~0% em bots mal calibrados)

## ⚠️ Refutado (NÃO usar como meta)
Números bombásticos (+300%, 10-25%, 0,6%→3-5x, 80% open rate, 68% abandono) foram REFUTADOS na
verificação (vote 0-3) — quase tudo é blog de fornecedor. Usar os PADRÕES qualitativos, não os números.

## Aplicado na Ana (app/prompts.py, rota NEGOCIACAO) — 22/06
- Quando esquenta: 1 pedido de contato como troca de valor ("posso já te mandar a simulação e os imóveis
  que batem no seu zap?"), com confiança, UMA vez. Se recuar: 1 cutucada leve e para. Nunca vários dados
  de uma vez. Sempre ESTIMATIVA no financiamento.
- Casa com o gate das calculadoras (avaliação/financiamento exigem contato → garantem o lead).

## LGPD / WhatsApp Brasil (a fazer)
- Opt-in/consentimento ao pedir contato (a confirmação no zap que o Thiago pediu serve a isso).
