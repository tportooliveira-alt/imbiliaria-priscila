# Padrões de orquestração — referência

Os 5 padrões do "Building Effective AI Agents" (Anthropic), com sinais de QUANDO usar,
QUANDO NÃO usar, e exemplo prático de PME/imobiliária. Consulte ao escolher a arquitetura
de uma automação. Todos os números de custo vêm da eval interna da Anthropic (Multi-Agent
Research System).

## Índice
1. Prompt chaining
2. Routing
3. Parallelization
4. Orchestrator-workers
5. Evaluator-optimizer
6. Tabela de decisão rápida
7. Model tiering por padrão

---

## 1. Prompt chaining (corrente)
**O que é:** quebra a tarefa numa sequência de passos fixos; a saída de um passo é a
entrada do próximo, com gates (checagens programáticas) entre eles.

**Quando usar:** a tarefa se decompõe limpa e previsivelmente em subtarefas fixas;
você aceita trocar latência por mais precisão/confiabilidade.

**Quando NÃO:** os passos mudam caso a caso (aí é agente/orquestrador); ou é tão simples que 1 chamada resolve.

**Exemplo PME:** João (agenda): interpreta a fala → vira JSON → valida campos → cria o
evento. Conteúdo: rascunho → ajustar tom da marca → inserir CTA → revisar. Lead: capta dados → qualifica BANT.

**Tier:** geralmente Sonnet em todos os passos; suba a Opus só num passo que exija julgamento (ex.: a redação final).

---

## 2. Routing (roteamento)
**O que é:** classifica a entrada e a manda pro fluxo especializado certo. Separa preocupações.

**Quando usar:** há categorias distintas que se tratam melhor em separado E dá pra classificar com boa acurácia.

**Quando NÃO:** as categorias se confundem (classificação ruim envenena tudo); ou um fluxo único já dá conta.

**Exemplo PME:** triagem de WhatsApp — info-imóvel / negociação / agenda / marketing → cada
um pro fluxo certo (Ana x João). É o atendimento ao cliente clássico: tipo de pergunta → processo especializado.

**Tier:** o classificador costuma ser Sonnet (tarefa mecânica). O modelo do fluxo destino depende da dificuldade dele.

---

## 3. Parallelization (paralelização)
**O que é:** roda subtarefas independentes ao mesmo tempo. Duas formas:
- **Sectioning:** dividir em pedaços independentes e juntar.
- **Voting:** rodar a mesma coisa N vezes e votar/agregar (mais robustez/confiança).

**Quando usar:** as subtarefas não dependem umas das outras; ou você quer votação pra reduzir erro.

**Quando NÃO:** há dependência forte entre passos (use chaining); custo de N execuções não compensa.

**Exemplo PME:** gerar 10 carrosséis de uma vez (sectioning); verificação por votos
na deep-research; revisar um texto por 3 ângulos e consolidar.

**Tier:** Sonnet nos workers paralelos quando mecânico; Opus se cada peça exige criatividade.

---

## 4. Orchestrator-workers (orquestrador → trabalhadores)
**O que é:** um LLM central DINAMICAMENTE divide a tarefa, delega a worker-LLMs e
sintetiza os resultados. Diferente de routing: aqui as subtarefas não são fixas — o orquestrador decide na hora.

**Quando usar:** tarefa complexa, de ALTO VALOR, cujas subtarefas você não consegue
prever de antemão; e é decomponível/paralelizável (breadth-first).

**Quando NÃO:** as subtarefas são previsíveis (use workflow, é mais barato); há muita
dependência sequencial entre workers; ou o valor da tarefa não paga o custo.

**Custo / justificativa:** ~15x os tokens de um chat. Na eval da Anthropic, Opus-líder +
Sonnet-workers bateu Opus single em +90,2% em pesquisa larga — mas só por ser tarefa de
alto valor e paralelizável. **Não use pra mensagem de rotina.**

**Exemplo PME:** pesquisa de mercado profunda de Vitória da Conquista; captação que exige
investigar várias fontes; o modelo da "empresa orquestrada" (1 orquestrador coordena
workers de conteúdo, pesquisa, revisão).

**Tier:** Opus no orquestrador (julgamento/síntese) + Sonnet nos workers (execução barata).

---

## 5. Evaluator-optimizer (avaliador → otimizador)
**O que é:** um LLM gera, outro avalia contra critério e devolve feedback; repete até passar (loop com teto).

**Quando usar:** existe critério claro de qualidade E o refino iterativo melhora de verdade
o resultado; ou você precisa de uma trava de validação antes de algo sair.

**Quando NÃO:** não há critério objetivo (o loop fica subjetivo e caro); 1 passada já basta.

**Exemplo PME:** guard-rail anti-alucinação da Ana — gera a resposta → avaliador extrai
preços/nomes de imóvel e confere no DB → corrige antes de enviar. Marketing: revisar o post contra a marca antes de agendar.

**Tier:** o avaliador pode ser Sonnet com checagem programática (regra de código); use Opus
no avaliador só quando o julgamento for sutil.

---

## 6. Tabela de decisão rápida

| Pergunta | Se SIM → |
|---|---|
| Dá pra resolver com 1 chamada bem feita? | **1 chamada LLM** (não complique) |
| Os passos são fixos e sequenciais? | **Prompt chaining** |
| Há categorias distintas a separar e classificar? | **Routing** |
| Subtarefas independentes / quer votação? | **Parallelization** |
| Precisa gerar e validar/refinar com critério? | **Evaluator-optimizer** |
| Tarefa de alto valor, subtarefas imprevisíveis, decomponível? | **Orchestrator-workers** (passe o gate de custo) |

## 7. Model tiering por padrão (resumo)

| Padrão | Tier típico |
|---|---|
| Prompt chaining | Sonnet (Opus só no passo de julgamento) |
| Routing | Sonnet no classificador |
| Parallelization | Sonnet nos workers (Opus se criativo) |
| Orchestrator-workers | **Opus** orquestrador + **Sonnet** workers |
| Evaluator-optimizer | Sonnet + checagem de código (Opus se julgamento sutil) |

Regra de ouro: Sonnet pro mecânico, Opus pro difícil. Comece embaixo, suba só se a qualidade exigir.
