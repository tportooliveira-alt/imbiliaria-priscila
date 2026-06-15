---
name: orquestrar-com-ia
description: >-
  Playbook para projetar e orquestrar tarefas/automações com IA (Claude) numa
  PME — começando simples, escolhendo o padrão certo (chaining/routing/parallel/
  orchestrator-workers/evaluator-optimizer), fazendo model tiering (Sonnet x Opus)
  e pondo travas anti-custo e anti-alucinação. Use SEMPRE que for desenhar um
  agente, workflow ou automação de IA, decidir entre solução simples vs multi-agente,
  estimar custo de tokens, escolher modelo por tarefa, ou orquestrar uma tarefa
  grande (pesquisa, geração de conteúdo em lote, qualificação de leads, follow-up).
  Vale para a imobiliária da Priscila e qualquer projeto futuro de orquestração com IA.
---

# Orquestrar com IA — playbook de PME

Este é o nosso método para construir automações com Claude sem queimar dinheiro
nem inventar dado. A regra que vale mais que todas as outras: **comece simples**.
A maioria das tarefas de uma PME é workflow barato e previsível — não agente solto.

Base: "Building Effective AI Agents", "Multi-Agent Research System" e o "Founder's
Playbook" da Anthropic, destilados na nossa deep-research de orquestração.

---

## 1. A regra-mãe: suba a escada de complexidade um degrau por vez

Sempre tente o degrau MAIS BAIXO que resolve. Só sobe quando o de baixo comprovadamente não dá conta.

1. **1 chamada LLM** (prompt bem feito, talvez com 1 ferramenta) — resolve a maioria.
2. **Workflow fixo** (caminho decidido por nós no código: chaining, routing, parallelization, evaluator-optimizer) — previsível, testável, barato.
3. **Agente autônomo** (a IA decide os próprios passos em loop) — só para tarefas abertas onde não dá pra prever os passos.
4. **Multi-agente / orchestrator-workers** (um cérebro divide e delega a vários workers) — só no topo, e só passando o gate de custo abaixo.

> **Workflow vs Agente:** workflow = caminho fixo que NÓS definimos no código (previsível, barato).
> Agente = a IA escolhe os passos e ferramentas sozinha (flexível, mas mais caro e com erro que se acumula).
> Frameworks pesados de agente escondem os prompts/respostas e empurram complexidade cedo demais — prefira chamadas diretas à API.

## 2. O GATE DE CUSTO (leia antes de fazer multi-agente)

Números da própria Anthropic (eval interna de pesquisa):

- Agente típico usa **~4x** os tokens de um chat.
- Sistema **multi-agente usa ~15x** os tokens de um chat.
- Multi-agente (Opus líder + Sonnet workers) bateu Opus single-agent em **+90,2%** — mas só em tarefa de pesquisa larga (breadth-first), paralelizável e de alto valor.
- ~80% da variação de desempenho foi explicada só pelo volume de tokens.

**Regra:** multi-agente só se paga quando o valor da tarefa é alto o bastante para
cobrir o custo. Um ticket de ~R$1mi (avaliação, captação, pesquisa de mercado profunda)
justifica. Responder WhatsApp de rotina **não** justifica — isso é routing/chaining barato.

> Sinal contrário (Gartner via Deloitte): >40% dos projetos agênticos podem ser cancelados
> até 2027 por custo, valor pouco claro e controle de risco fraco. Reforça: simplicidade primeiro, valor antes de complexidade.

## 3. QUAL padrão usar (resumo; tabela completa em `reference/padroes.md`)

| Padrão | Quando usar | Exemplo na imobiliária/PME |
|---|---|---|
| **Prompt chaining** | tarefa que se quebra em passos fixos, com checagem entre eles | João: fala → JSON → valida → cria na agenda. Gerar 1 post: rascunho → revisar tom → CTA. |
| **Routing** | há categorias distintas, melhor tratadas separado, e dá pra classificar bem | Triagem de WhatsApp: info-imóvel / negociação / agenda → fluxo certo (Ana x João). |
| **Parallelization** | subtarefas independentes ao mesmo tempo, ou votação | Gerar 10 carrosséis de uma vez; verificação por votos da deep-research. |
| **Orchestrator-workers** | tarefa complexa de alto valor cujos subtarefas NÃO dá pra prever | Pesquisa de mercado VDC; captação; um orquestrador dispara workers e sintetiza. |
| **Evaluator-optimizer** | gerar → avaliar com critério → refinar em loop | Guard-rail da Ana: gera resposta → confere preço/imóvel no DB → corrige antes de enviar. |

Routing e orchestrator-workers se parecem mas NÃO são a mesma coisa: routing é estático
(classifica e manda pro fluxo certo); orchestrator-workers é dinâmico (o cérebro central
**decide na hora** como dividir e junta os resultados).

## 4. MODEL TIERING — Sonnet x Opus por dificuldade

Escolha o modelo por tarefa, não um só pra tudo. Mais barato embaixo, mais caro só onde precisa.

- **Sonnet** → tarefas simples/mecânicas/estruturadas: classificar, extrair, formatar,
  rascunho de mensagem padrão, validar JSON, roteamento, follow-up. É o cavalo de batalha.
- **Opus** → tarefas difíceis/criativas/de julgamento: pesquisa profunda, síntese,
  estratégia, código não-trivial, redação que precisa de gosto, o **orquestrador** de um multi-agente.
- **Padrão multi-agente:** Opus como líder/orquestrador + Sonnet nos workers. Líder pensa, workers executam barato.

Pergunta de decisão: *"essa subtarefa exige julgamento/criatividade ou é mecânica?"*
Mecânica → Sonnet. Julgamento → Opus. Na dúvida em tarefa de baixo valor, comece no Sonnet e suba só se a qualidade não bastar.

## 5. Checklist de TRAVAS (não pule)

Antes de declarar uma automação pronta, confira:

- [ ] **Checkpoints** — pontos de parada/revisão humana antes de ações irreversíveis (escrever na agenda, mandar mensagem pro cliente, gastar dinheiro).
- [ ] **Limite de iteração** — todo loop de agente tem teto de passos/custo. Nunca rode infinito.
- [ ] **Guard-rail de validação (anti-alucinação)** — números/nomes que a IA cita (preço, imóvel, data) são conferidos **no código contra a fonte real (DB)** antes de sair. Prompt sozinho NÃO é trava.
- [ ] **Nunca inventar dado** — se não está na fonte, a IA diz que não sabe / encaminha. Não preenche lacuna com chute.
- [ ] **Ground truth real** — o agente decide olhando o resultado de verdade de cada ferramenta (MCP/DB), não uma suposição.
- [ ] **Segredo fora do git** — chaves/tokens em `.env`/secret-manager, com permissão restrita (ex.: `chmod 600`), nunca commitados nem servidos.
- [ ] **Poucas ferramentas, fortes** — prefira 1 `get_customer_context` que junta o que importa a 10 chamadas granulares. Mais ferramentas ≠ melhor; o agente tem contexto limitado.
- [ ] **Custo controlado** — prompt caching no que se repete (carteira/ficha no system); tier por dificuldade; multi-agente só passando o gate.

## 6. FLUXO: como orquestrar uma tarefa grande

Quando cair uma tarefa grande (ex.: "pesquisa o mercado de VDC", "gera o conteúdo do mês", "qualifica essa leva de leads"):

1. **Decompor** — quebre em subtarefas. São previsíveis e fixas? Então é workflow (vá pra chaining/routing), não agente. Imprevisíveis e exploratórias? Aí justifica orquestrador.
2. **Tier por dificuldade** — marque cada subtarefa: mecânica (Sonnet) ou julgamento (Opus). O orquestrador, se houver, é Opus.
3. **Checar o gate de custo** — vai mesmo precisar de fan-out multi-agente (~15x tokens)? O valor da tarefa paga? Se não, faça em série/workflow barato.
4. **Fan-out** — dispare os workers independentes em paralelo (parallelization), cada um com escopo claro e ferramentas mínimas.
5. **Avaliar** — passe os resultados por um avaliador (evaluator-optimizer): confere contra a fonte real, corta alucinação, pede refino do que ficou fraco.
6. **Sintetizar** — o orquestrador junta tudo numa entrega coerente. Humano dá o checkpoint final e decide.

## 7. O papel humano (Founder's Playbook)

Numa operação AI-native, o fundador/corretora deixa de ser executor e vira **orquestrador de agentes**:
entrega à IA o repetitivo (pesquisa, rascunhos, ads, operação) e guarda pra si **julgamento, gosto,
trade-offs, confiança, validação com cliente real e responsabilidade por qualidade/legal/segurança**.
A IA propõe; o humano decide e assina embaixo.

---

**Resumo de bolso:** comece simples → suba degrau a degrau → passe o gate de custo antes de multi-agente
→ Sonnet pro mecânico, Opus pro difícil → trave com checkpoint + limite + validação no código → nunca invente dado.

Detalhe dos padrões com sinais de "quando usar / quando NÃO usar": veja `reference/padroes.md`.
