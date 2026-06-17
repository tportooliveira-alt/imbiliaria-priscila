# Degrau 2 da memória da Ana — "CONHECER a pessoa" (planejado, NÃO fazer ainda)

**Status:** planejado. Fazer **com tempo, devagar, depois de MAIS RODADAS REAIS.** Aberto 17/06/2026.
**Decisão do Thiago:** segurar a Ana — ela não pode muita coisa de uma vez. Acumular conversas
de verdade primeiro, observar, e só então ligar este degrau. Não tem pressa.

## A ideia (a analogia do Thiago)
Hoje (Degrau 1) a Ana **consulta a ficha** do cliente — camada de FATOS (o que ele disse,
temperatura, anotações). É como "abrir o arquivo".

O Degrau 2 é fazer a Ana **CONHECER** o cliente "do jeito que o Claude conhece o Thiago":
um **retrato que ACUMULA e cresce**, com o *porquê* e o *como agir* — não "ele falou X", mas
*"a Ane é cautelosa, sonha com a casa própria, tem medo de não conseguir financiar, responde
melhor quando a tranquilizam"*. Igual às memórias do Claude têm "Por quê" e "Como aplicar".

## Como seria (quando chegar a hora)
- Campo permanente por lead (ex.: `leads.dossie` / reutilizar `observacoes` estruturado).
- Destilação por IA (a chave **potente do Claude** que já está no `.env`), **event-driven**:
  roda **1 vez quando a conversa ESFRIA** (não a cada mensagem) e atualiza o retrato.
- A Ana relê esse retrato no início (já existe o gancho `responder(memoria_lead=...)`).
- Mantém a regra **VERDADE COM DISCRIÇÃO** (já no prompt): conhecer por dentro, nunca expor
  a ficha/rótulos/juízos ao cliente.

## Custo (o motivo de segurar)
Adiciona **1 chamada de IA por conversa** (no esfriamento). Hoje isso não existe. É barato pelo
gatilho, mas é recorrente — por isso só ligar depois de validar com rodadas reais que vale.

## Pré-requisitos antes de ligar (o "com tempo")
1. Acumular **N conversas reais** com a memória de fatos (Degrau 1) rodando.
2. Ver na prática o que falta — onde a Ana "esquece" algo que importaria.
3. Medir custo/uso real do atendimento antes de somar a destilação.
4. Só então construir, **um degrau só**, e observar.

## Princípio geral (vale pra Ana toda)
Segurar capacidades. Não dar muito poder de uma vez. Event-driven, ≤3 por vez, barato.
Verdade sempre, nunca inventar, discreta. Relacionado: `DEGRAU-ANA-VISAO.md` (visão multimodal,
também segurando até ter base).
