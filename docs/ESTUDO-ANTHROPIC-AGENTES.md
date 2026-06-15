# 🧠 ESTUDO — "Building Effective AI Agents" (Anthropic) aplicado ao nosso sistema

Análise do material da Anthropic que o Thiago mandou (15/06): o anúncio **"The Founder's Playbook: Building an
AI-Native Startup"** (Anthropic, maio/2026) + o guia técnico **"Building Effective AI Agents"** — incluindo a
**"parte do looping"** (o ciclo do agente). Aqui o resumo + **como cada conceito se aplica ao sistema da Priscila**.

> Fonte técnica: anthropic.com/engineering/building-effective-agents. O "Founder's Playbook" (PDF oficial) trata da
> **transição do papel do fundador numa empresa AI-native** — como dividir o trabalho entre humano e IA. Não consegui
> baixar o PDF aqui (link truncado na imagem); a deep-research em andamento cobre esse ângulo com fontes.

## 1) A distinção que muda tudo: WORKFLOW vs AGENTE
- **Workflow** = a IA segue um **caminho fixo, decidido por nós no código** (previsível, barato, testável).
- **Agente** = a IA **decide sozinha** os passos e quais ferramentas usar (flexível, mas mais caro e com erro acumulável).
- **Conselho nº1 da Anthropic:** *comece simples.* Só vire "agente autônomo" quando o workflow fixo **não** dá conta.
  A maioria dos casos de PME = **workflow**, não agente solto.

## 2) O "LOOPING" (o ciclo do agente) — o que é
Um agente roda **em loop**: recebe a tarefa → **planeja** → **age** (usa ferramenta) → **observa o resultado real do
ambiente** → avalia se avançou → **repete** até terminar. Duas travas obrigatórias: **checkpoints** (pontos de
parada/revisão humana) e **limite de iterações** (pra não rodar infinito/queimar custo). O segredo é o "ground truth":
o agente só sabe se está indo bem porque **vê o resultado de verdade** de cada ferramenta (não chuta).

➡️ **No nosso caso:** o **Claude Code (eu) na VPS + o do teu PC** já operam nesse loop (ler arquivo → editar → testar →
ver resultado → repetir). O **MCP** é o que dá o "ground truth" do negócio (leads/agenda/financeiro reais) pro agente
do teu PC. Já estamos usando o padrão certo.

## 3) Os 5 PADRÕES da Anthropic — e onde cada um encaixa no nosso sistema
| Padrão | O que é | Onde JÁ usamos / ONDE USAR |
|---|---|---|
| **Prompt Chaining** (corrente) | quebrar em passos sequenciais com checagem entre eles | **João**: interpreta fala → vira JSON → valida → cria na agenda. **Calculadora→Ana**: capta → qualifica. |
| **Routing** (roteamento) | classificar a entrada e mandar pro tratamento certo | **Ana já faz isso** (`router.py`/`dispatcher.py`): decide a rota (info imóvel / negociação / mercado VDC) e o modelo por rota. ✅ |
| **Parallelization** (paralelo) | rodar subtarefas independentes ao mesmo tempo / votar | O **estudo 360** de hoje (5 especialistas em paralelo) e a **deep-research** (busca + verificação por votação). Usar pra **gerar 10 carrosséis** de uma vez. |
| **Orchestrator-Workers** (orquestrador→trabalhadores) | um cérebro central divide a tarefa e junta os resultados | O **modelo da "empresa orquestrada"** que tu quer: 1 orquestrador (eu) coordenando trabalhadores (gerar conteúdo, pesquisar, revisar). É o coração do "Founder's Playbook". |
| **Evaluator-Optimizer** (avaliador→otimizador) | gera → avalia com critério → refina em loop | **Guard-rail anti-alucinação da Ana** (recomendado no estudo): gera resposta → confere preço/imóvel no DB → corrige. E revisar conteúdo de marketing antes de postar. |

## 4) Quando usar AGENTE solto vs WORKFLOW (regra prática pra nós)
- **Workflow (padrão):** captação de lead, qualificação, follow-up, agendamento, postar conteúdo agendado → **caminho
  fixo, barato, previsível.** É 90% do nosso sistema e está certo assim.
- **Agente autônomo:** só pra **tarefas abertas** onde não dá pra prever os passos — ex.: "pesquisa de mercado profunda",
  "revisar o projeto inteiro", "montar um plano". É o que a deep-research e o estudo 360 fazem. Custo maior, com travas.

## 5) O que isso valida e o que sugere mudar no nosso projeto
**Valida (estamos no caminho certo):**
- Ana com **routing + modelo por rota** = exatamente o padrão recomendado. ✅
- João com **prompt chaining + travas** (número+keyword, JSON validado) = correto. ✅
- **MCP** dando ground truth real pro agente = a base de um sistema agêntico saudável. ✅
- **"Comece simples":** quase tudo nosso é workflow barato, não agente caro. ✅

**Sugere adicionar (alinhado ao estudo 360):**
1. **Evaluator-optimizer na Ana** — validar preço/imóvel citado contra o DB **antes de enviar** (trava de código, não só prompt).
2. **Orchestrator-workers pro marketing** — um orquestrador que dispara N "trabalhadores" pra gerar carrosséis/notícias
   em paralelo (parallelization), depois um avaliador revisa antes de agendar.
3. **Sempre com checkpoint + limite de iteração** nos agentes (já fazemos; manter como regra).
4. **Prompt caching** (custo) — o material reforça eficiência; cachear a carteira+ficha no system da Ana.

## 6) Ligação com "orquestrar a empresa toda" (o que o Thiago pediu)
O "Founder's Playbook" da Anthropic é exatamente sobre isso: o fundador deixa de fazer tarefa e passa a **orquestrar
agentes**. Pro nosso caso: a Priscila (e o Thiago) viram **orquestradores** — a IA faz atendimento (Ana), agenda (João),
conteúdo (workers de marketing), pesquisa (deep-research), e o humano decide e fecha. **A deep-research em andamento vai
detalhar quais tarefas priorizar.** Este doc é a base conceitual; o plano prático sai do cruzamento com ela.

_Próximo: quando a deep-research terminar, cruzar com este doc → `PLANO-ORQUESTRACAO-EMPRESA.md` priorizado._
