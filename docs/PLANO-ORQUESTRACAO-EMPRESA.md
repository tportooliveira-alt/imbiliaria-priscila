# PLANO DE ORQUESTRAÇÃO DA EMPRESA COM IA
## Priscila Vasconcelos Imobiliária — Vitória da Conquista/BA
### Cruzamento: deep-research (wjd5r4rqg) + estudos internos (15/06/2026)

---

## Resumo

A pesquisa confirma a tese central: **simplicidade primeiro, custo-gated, fundador vira orquestrador.** Para uma corretora solo com ticket de ~R$1 mi, a esmagadora maioria das tarefas deve rodar como **workflows baratos e previsíveis** (prompt chaining + routing), não como agentes autônomos caros. Multi-agente com orquestrador só se justifica quando o valor da tarefa é suficientemente alto para absorver o custo de ~15x tokens — o que cabe em pesquisa de mercado profunda e captação complexa, mas não em mensagens de WhatsApp rotineiras. O papel da Priscila (e do Thiago) já está se transformando: de executores de tarefa para **orquestradores de agentes** que delegam o repetitivo à IA e retêm julgamento, gosto, relação e responsabilidade legal.

---

## O que JA temos e esta certo

A pesquisa valida diretamente o que foi construído até aqui.

| Componente | Padrao Anthropic validado | Evidencia da pesquisa |
|---|---|---|
| **Ana** (routing + modelo por rota) | Routing — classifica a entrada e manda pro fluxo especializado | "Routing classifies an input and directs it to a specialized followup task... for distinct categories better handled separately" — Anthropic (alta confianca) |
| **Joao** (chaining: fala → JSON → valida → agenda) | Prompt Chaining — passos sequenciais com checagem entre eles | "Prompt chaining decomposes a task into a sequence of steps... to trade off latency for higher accuracy" — Anthropic (alta confianca) |
| **Servidor MCP** (ground truth do negocio: leads, agenda, financeiro) | Ferramenta consolidada de contexto | "Implement a get_customer_context tool which compiles all recent & relevant information at once" vs. endpoints atomicos — Anthropic Engineering (alta confianca) |
| **CRM com score/temperatura** | Contexto rico para o agente | Base para o orchestrator-workers quando escalarmos |
| **Calculadora de avaliacao + calculadora de ads** | Workflows fixos de alto valor | Decisao correta: workflows, nao agentes autonomos |
| **Filosofia "comece simples"** | Recomendacao primaria da Anthropic | "Find the simplest solution possible, and only increasing complexity when needed" — Anthropic (alta confianca) |

**O que o estudo 360 revelou que precisa correcao (nao e falha de arquitetura, e ajuste):**
- Webhook do WhatsApp sem autenticacao (seguranca critica — corrigir antes de tudo)
- Sem prompt caching na Ana — carteira+ficha reenviadas a cada turno (custo desnecessario)
- Guard-rail de alucinacao da Ana e so no prompt, nao no codigo (risco de inventar preco/imovel)
- Handoff nao notifica a Priscila quando lead esquenta (vazamento de funil alto impacto)

---

## Tarefas da corretora por ROI de automacao

> Confianca das estimativas de impacto: ALTA para as tarefas com dados de benchmark verificados (resposta <5min, qualificacao BANT, follow-up); MEDIA para conteudo e captacao (menos dados quantitativos disponiveis).

| Tarefa | Padrao recomendado | Modelo | Esfoco | Impacto | Status |
|---|---|---|---|---|---|
| **Atendimento/triagem WhatsApp** | Routing (Ana ja faz) | Sonnet (rota simples) / Sonnet-full (negociacao) | Baixo — ja existe | CRITICO: <5 min = 21x mais qualificavel; corretor medio: 15h | JA NO AR ✓ |
| **Qualificacao de lead (BANT)** | Prompt Chaining dentro do atendimento | Sonnet | Baixo — ja existe | Alto: filtra morno/quente antes de gastar tempo humano | JA NO AR ✓ |
| **Notificacao de lead quente → Priscila** | Evento simples no CRM + Evolution API | Sonnet (1 chamada) | Baixo (horas) | CRITICO: lead quente esfria em minutos sem resposta humana | FALTANDO ← fazer ja |
| **Follow-up de lead morno** | Prompt Chaining (sequencia de 3 mensagens, cap diario) | Haiku (mensagens simples) | Baixo — infra pronta | Medio: reaquece pipeline sem esforco humano | Pronto mas timer nao instalado |
| **Agendamento de visita** | Prompt Chaining (Joao: fala → JSON → agenda) | Sonnet | Baixo — ja existe | Alto: agenda 24h sem intervencao humana | JA NO AR ✓ |
| **Conteudo de redes (carrosséis/noticias)** | Parallelization + Evaluator-Optimizer | Sonnet (gera) + Haiku (avalia formato) | Medio | Medio: topo de funil, alimenta indicacao | PENDENTE (carrosseis prontos, nada postado) |
| **Pesquisa de mercado (VDC/regiao)** | Orchestrator-Workers (Opus como orquestrador, Sonnet como workers) | Opus lider + Sonnet workers | Alto | Alto: 90,2% melhor que agente unico, justificado pelo ticket R$1mi | USAR COM PARCIMONIA (15x tokens) |
| **Captacao (abordagem de vendedor)** | Prompt Chaining (roteiro consultivo: referencia imovel → dor → proposta → CTA) | Sonnet | Medio | CRITICO: vendedor = pipeline proprio; comissao R$60k/venda | PENDENTE |
| **Financeiro (relatorio de comissoes, pipeline de receita)** | Workflow simples (consulta MCP → relatorio) | Haiku (relatorio padrao) | Baixo | Medio: libera tempo do Thiago, nao da Priscila diretamente | PENDENTE |

**Regra de ouro dos modelos (custo-gated):**
- Haiku: tarefas de classificacao, formatacao, mensagens simples, relatorios padrao
- Sonnet: atendimento, qualificacao, chaining complexo, conteudo
- Opus: SO para orchestrator-workers em tarefas de alto valor (pesquisa de mercado profunda, captacao estrategica complexa) — custa ~15x mais

---

## Quando NAO usar multi-agente

Esta secao e baseada em dados verificados com alta confianca (fontes primarias Anthropic + Gartner/Deloitte).

### O gate de custo (nao e opiniao, e dado verificado)

- Uma **chamada de chat** = 1x tokens (baseline)
- Um **agente com loop** = ~4x tokens do que um chat equivalente
- Um **sistema multi-agente** = ~15x tokens do que um chat equivalente

Fonte: Anthropic Engineering, "multi-agent systems use about ~15x more tokens than chats" — **confianca: alta** (3-0 na verificacao adversarial)

Para a nossa situacao:
- Mensagem de WhatsApp de qualificacao: workflow simples com Sonnet = correto. Multi-agente aqui = custo 15x sem ganho de qualidade.
- Pesquisa de mercado profunda (breadth-first, muitas fontes): orchestrator-workers com Opus = **justificado pelo valor** (ticket R$1mi absorve o custo).

### O dado Anthropic que parece tentador mas exige cautela

"Um sistema multi-agente (Opus como lider + Sonnet subagentes) superou um unico agente Opus em **90,2%**" — confianca: alta.

**Mas o contexto importa:** esse ganho foi medido no benchmark BrowseComp (pesquisa de informacao breadth-first em muitas fontes). **Nao e um numero universal**. Para atendimento de WhatsApp, follow-up, ou agenda, o ganho seria minimo e o custo 15x seria puro desperdicio.

Aplicar ao nosso sistema: orchestrator-workers **so** para pesquisa de mercado profunda e captacao multi-etapa. **Tudo o mais = workflow**.

### O alerta Gartner (confianca: media — voto 2-1 na verificacao)

"Mais de 40% dos projetos de IA agêntica serao cancelados ate o final de 2027, por custo escalante, valor de negocio nao claro, ou controles de risco inadequados."

Fonte: Gartner (via Deloitte TMT Predictions 2026) — https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/ai-agent-orchestration.html

**O que isso significa pra nos:** cada nova automacao precisa de ROI claro antes de construir. O nosso ticket alto (R$1mi, R$60k de comissao) nos da mais margem que a media das PMEs — mas o principio vale: **medir antes de escalar**.

### Os 3 sinais de que e cedo demais para multi-agente

1. Ainda ha leads quentes sem notificacao para a Priscila (vazamento de funil mais barato que qualquer agente novo)
2. Sem prompt caching ativo (custo desnecessario em todo atendimento)
3. Pixel/GA4 ainda sem dados proprios de VDC (sem dados nao ha como calibrar ROI de novos agentes)

---

## Roadmap priorizado (impacto x esforco)

Ordenado de: **mais barato + maior retorno imediato** → **mais avancado + curto prazo** → **escalamento futuro**.

> ✅ **STATUS (15/06 noite — atualizado na revisao):** o **DEGRAU 1 INTEIRO** (webhook autenticado, notificacao de lead quente, promessa 24h corrigida, Postiz desligado) **e o item 7 (backup do site.db)** JA FORAM EXECUTADOS nesta sessao. **Comece pelo DEGRAU 2, itens 5 e 6** (prompt caching + 3 eventos de conversao). O resto do roadmap segue valido.

---

### DEGRAU 1 — Tapar vazamentos de seguranca e funil (dias, custo zero, retorno imediato) ✅ FEITO 15/06

**Por que primeiro:** um lead quente sem notificacao perde mais dinheiro do que qualquer novo agente ganha. Seguranca frouxa coloca toda a operacao em risco antes de escalar.

1. **Autenticar o webhook do WhatsApp** (`secret-no-path` em `/api/whatsapp/webhook/<TOKEN>`)
   - Fecha forjamento de mensagem, protege a Ana e o Joao, protege a conta da Priscila de ban
   - Esfoco: horas | Impacto: critico (seguranca)

2. **Notificar a Priscila quando lead esquenta**
   - Evento no CRM "temperatura = quente" → Evolution API → WhatsApp da Priscila
   - Esfoco: horas | Impacto: critico (funil — lead quente nao pode esfriar)

3. **Corrigir a promessa 24h do vendedor**
   - `routes_publicas.py:487` — mudar para Ana atender o vendedor na hora, igual ao comprador
   - Esfoco: horas | Impacto: alto (o lead mais valioso hoje nao recebe resposta instantanea)

4. **Desligar o Postiz (libera ~910 MB imediato)**
   - `docker stop` + `docker update --restart=no` nos 3 containers
   - Esfoco: minutos | Impacto: alto (estabilidade da VPS — ja houve OOM-kill em 02/jun)

---

### DEGRAU 2 — Ligar medicao e caching (dias, custo quase zero, base para tudo que vem)

**Por que segundo:** sem dados proprios de VDC nao da pra calibrar nada. Sem caching, pagamos mais por cada mensagem da Ana.

5. **Ligar prompt caching na Ana**
   - Cachear carteira de imoveis + ficha da Priscila no system prompt
   - Esfoco: horas | Impacto: medio (reducao de custo por token em todo atendimento)

6. **Ligar os 3 eventos de conversao que faltam**
   - `clique_whatsapp`, `calculadora_concluida`, `agendar_visita` (o `window.track` ja existe em `analytics.js`)
   - Esfoco: horas | Impacto: alto (sem isso o pixel e cego, nao da pra otimizar campanha)

7. **Backup automatico do `site.db`**
   - Timer diario com `sqlite3 .backup` + rotacao 7-14 dias
   - Esfoco: horas | Impacto: critico (PII de clientes, zero automacao hoje)

---

### DEGRAU 3 — Guard-rail da Ana + instalacao do follow-up (semana, baixo custo)

**Por que terceiro:** com o funil medido e o lead notificado, o risco de alucinacao e o morno sem follow-up sao os proximos gargalos.

8. **Guard-rail pos-resposta da Ana**
   - Extrair preco/nome de imovel citado na resposta → checar contra DB → bloquear se nao bater
   - Esfoco: 1-2 dias | Impacto: alto (evita a Ana inventar preco e perder credibilidade)
   - Confianca do padrao: alta (Evaluator-Optimizer recomendado pelo ESTUDO-ANTHROPIC-AGENTES)

9. **Instalar o followup.timer**
   - Arquivos de deploy ja existem em `deploy/`; so falta instalar no systemd
   - Esfoco: horas | Impacto: medio (reaquece pipeline sem esforco humano)

---

### DEGRAU 4 — Combustivel: depoimentos + 1ª campanha (semana, investimento monetario)

**Por que quarto:** o sistema esta pronto; falta combustivel. Sem trafego, os agentes ficam ociosos.

10. **Coletar 3-5 depoimentos reais de clientes**
    - Alavanca de 10-20x na conversao de indicacao vs lead pago frio
    - Nao e tecnico — e acao da Priscila | Impacto: critico (zero depoimentos hoje)

11. **1ª campanha Meta Ads (R$20-30/dia)**
    - Funil de comprador E funil de vendedor (captacao) — dois criativos separados
    - Esfoco: 1 dia de setup | Impacto: alto (sem trafego pago nao ha leads pra qualificar)
    - Remover `noindex` do site antes de ligar campanha

---

### DEGRAU 5 — Conteudo organico automatizado (semana-duas, medio esfoco)

**Por que quinto:** depois de ter depoimentos e campanha rodando, conteudo organico amplifica sem custo de midia.

12. **Workflow de geracao de carrosseis (Parallelization)**
    - Orchestrador simples dispara N workers (Sonnet) para gerar carrosseis de imoveis/mercado em paralelo
    - Evaluator revisa formato e linguagem antes de agendar publicacao
    - Padrao: Parallelization + Evaluator-Optimizer (ver ESTUDO-ANTHROPIC-AGENTES, secao 3)
    - Esfoco: 2-3 dias | Impacto: medio (topo de funil, alimenta indicacao organicamente)

---

### DEGRAU 6 — Pesquisa de mercado com Orchestrator-Workers (futuro, quando houver dados)

**Por que por ultimo:** e o padrao mais caro (Opus + multiplos Sonnet = ~15x tokens). So justifica quando:
- Ha leads reais para suportar a decisao com dados de mercado
- O CPL proprio de VDC esta calibrado (60-90 dias de campanha)
- Uma pesquisa de captacao ou de posicionamento tem impacto direto numa negociacao de R$1mi+

13. **Pesquisa de mercado profunda (Orchestrator-Workers)**
    - Opus como orquestrador → delega para workers Sonnet (busca de imoveis, analise de preco, tendencias VDC)
    - Resultado: dosie de mercado para embasar captacao e negociacao
    - Padrao: Orchestrator-Workers (confianca: alta — exatamente o que a deep-research usou)
    - Esfoco: 1 semana de implementacao | Impacto: alto (porem condicional a volume de negociacao)

---

## Honestidade e confiancas

| Afirmacao | Confianca | Nota |
|---|---|---|
| Routing + Prompt Chaining para workflows de PME | ALTA | Fontes primarias Anthropic, voto 3-0 |
| 15x tokens para multi-agente vs chat | ALTA | Anthropic Engineering, voto 3-0 |
| 90,2% de ganho do orchestrator-workers | ALTA (com ressalva) | Medido em BrowseComp (pesquisa breadth-first); nao universal |
| <5min de resposta = 21x mais qualificavel | ALTA | Multiplos estudos independentes (InsideSales/MIT) |
| Indicacao converte 10-20x mais que lead pago | ALTA | Multiplas fontes, verificadas no PLANO-MARKETING-CALIBRADO |
| >40% dos projetos agênticos cancelados ate 2027 (Gartner) | MEDIA | Voto 2-1; a atribuicao de causa ("custo + valor nao claro") esta certa, "complexidade" e leve exagero |
| CPL real em VDC/BA | BAIXA | Nenhum dado proprio ainda; benchmarks dos EUA nao transferem |
| ROI especifico de cada tarefa automatizada | MEDIA | Baseado em blogs e benchmarks de mercado, nao em experimento proprio |

---

## Referencias (fontes primarias da pesquisa)

- Anthropic — "Building Effective AI Agents": https://www.anthropic.com/engineering/building-effective-agents  _(URL verificada nesta sessao)_
- Anthropic Engineering — "Building effective agents" (PDF): https://resources.anthropic.com/hubfs/Building%20Effective%20AI%20Agents-%20Architecture%20Patterns%20and%20Implementation%20Frameworks.pdf
- Anthropic Engineering — "How we built our multi-agent research system": https://www.anthropic.com/engineering/multi-agent-research-system
- Anthropic Engineering — "How to build effective tools for agents": https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic — "The Founder's Playbook: Building an AI-Native Startup" (maio 2026): _URL exata a confirmar — o PDF oficial estava num link website-files.com (ver imagem que o Thiago enviou); citado de fonte secundaria, nao verificado diretamente._
- Gartner/Deloitte TMT Predictions 2026 (alerta de cancelamento de projetos): https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2026/ai-agent-orchestration.html
- whatsapp-mcp (integracao WhatsApp pessoal via MCP): https://github.com/lharries/whatsapp-mcp

**Fontes internas cruzadas neste plano:**
- `/var/www/imobiliaria/docs/ESTUDO-ANTHROPIC-AGENTES.md` — estudo dos padroes aplicado ao nosso sistema
- `/var/www/imobiliaria/docs/ESTUDO-PROJETO-360.md` — auditoria 360 (seguranca, agentes, funil, infra)
- `/var/www/imobiliaria/docs/PLANO-MARKETING-CALIBRADO.md` — funil calibrado e taxas verificadas

---

_Gerado em 15/06/2026. Proximo: Degrau 1 (autenticar webhook + notificar Priscila no lead quente). Ver ROTA-PROXIMA.md para sequencia de execucao._
