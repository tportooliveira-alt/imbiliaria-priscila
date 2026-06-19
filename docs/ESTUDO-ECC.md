# 📚 ESTUDO — ECC (Everything Claude Code) + Karpathy

Cérebro de estudo. **Cresce a cada rodada do `/loop estude mais`.** Objetivo: extrair o que adotar
no nosso projeto (Python/FastAPI + Claude Code + MCP), do jeito mais SIMPLES (Karpathy #2).
Repos clonados: `/root/everything-claude-code` (ECC) · `/root/andrej-karpathy-skills` (Karpathy).

## O que é o ECC
"Sistema operacional de agentes": 30 agentes especializados, 135 skills, 60 comandos, hooks
automáticos. Filosofia = **orquestração ESTRUTURADA com gates e escalation**, não "N agentes soltos".

## 🧐 CRÍTICA + DECISÃO (18/06) — ECC fica como REFERÊNCIA, NÃO instalado
- **Inchaço:** 3244 arquivos, regras de angular/cpp/dart/csharp... — ~90% irrelevante pro nosso Python.
  Irônico: viola a própria simplicidade que prega.
- **JS/TS-centric** (hooks rodam tsc/prettier/biome) — não encaixa no Python.
- **Cheiro de produto/hype** (211k estrelas, tier pago, npm, site, sponsors) → ceticismo saudável.
- **Frágil de instalar** (TROUBLESHOOTING, "não empilhe métodos", reset/uninstall).
- **A melhor coisa é o `CLAUDE.md` do Karpathy** (60 linhas, afiado), NÃO os 3244 arquivos do ECC.
- **DECISÃO DO DONO:** ECC **não é instalado**. Tentei instalar global e o dono corrigiu — **desinstalei**
  (505 arquivos removidos do `~/.claude/`). Fica como **pasta de referência** (`/root/everything-claude-code`),
  só puxar **quando o dono chamar**. Adotado de verdade (nosso, não ECC ativo): disciplina Karpathy no
  `CLAUDE.md` + `scripts/verificar.sh` (verification-loop, já provou valor).

## 5 princípios centrais (SOUL.md)
1. **Agent-First** — mandar a tarefa pro especialista certo o quanto antes.
2. **Test-Driven** — testar antes de confiar na implementação.
3. **Security-First** — validar input, proteger segredo, default seguro.
4. **Immutability** — transição de estado explícita, não mutação.
5. **Plan Before Execute** — quebrar mudança complexa em fases deliberadas.

## Fluxo multi-agente (o coração)
`PLAN → IMPLEMENT → REVIEW → VERIFY → loop até passar`
- **planner** → reafirma requisito, avalia risco, plano em passos (confirmar antes de tocar código).
- **tdd/implement** → testes primeiro, implementação mínima.
- **code-reviewer** → revisa logo após escrever (qualidade/segurança/manutenção; severidade CRITICAL→LOW).
- **agent-evaluator** → pontua o trabalho em 5 eixos (Accuracy, Completeness, Clarity, Actionability,
  Conciseness), 1-5, com evidência. Veredito: entrega / corrige N / refaz.
- **verify** → build, lint, test, type-check.
- Paralelo só pra tarefas independentes (ex.: architect + security-reviewer).

## loop-operator (rodar loop com FREIO)
- Começar de padrão explícito + modo + **condições de parada** claras.
- **Checkpoints** a cada iteração; detectar **travamento** (2 checkpoints sem progresso) e **retry storm**
  (mesma falha repetida) → PAUSAR, reduzir escopo, replay com critério explícito.
- Só retomar com: quality gate ativo, baseline de eval, caminho de rollback, isolamento (branch/worktree).
- **Escalar** pro humano: sem progresso em 2 checkpoints / falhas idênticas repetidas / custo fora do
  orçamento / conflito de merge travando.
- Anti-padrão: re-tentar 3× mudando só a frase. Bom: capturar → classificar → 1 check → mudar plano.

## Disciplina (Karpathy) — JÁ adotada no nosso CLAUDE.md
1. Pensar antes (não assumir, perguntar, verificar antes de afirmar).
2. Simplicidade (código mínimo, nada especulativo).
3. Mudança cirúrgica (mexer só no necessário, casar o estilo).
4. Meta + loop (critério verificável, plano `passo → verificar:`).

## O que JÁ adotamos
- Disciplina Karpathy no `CLAUDE.md`.
- `.claude/agents/`: planner, code-reviewer, agent-evaluator, loop-operator (4 de 67, mínimo).
- Detalhe técnico: cada agente do ECC tem um "Prompt Defense Baseline" no topo (anti prompt-injection) —
  bom pra Ana também (já temos "verdade com discrição"; isso reforça).

## ✅ Aplicado (log das rodadas do loop)
- **R2 (18/06):** ECC instalado GLOBAL (`~/.claude/`: 67 agentes, 92 comandos, 74 skills, sem hooks JS).
  Skill `verification-loop` → criado `scripts/verificar.sh` (py_compile + pytest + smoke site/Ana).
  Pegou 2× a remoção incompleta do Gemini (teste quebrado) e me barrou de dizer "pronto" sem verde.
- **Agentes/skills são SELETIVOS** (Agent-First): os 67/74 NÃO rodam juntos — cada um tem "quando usar";
  o sistema invoca o certo por tarefa. Instalar = disponibilizar; usar = filtrar por relevância.

## 🔜 Próximas rodadas de estudo (a fazer)
- [ ] Adaptar os 4 agentes pro nosso contexto Python/FastAPI (hoje vêm com sabor JS/npm).
- [ ] Estudar os HOOKS do ECC e qual quality-gate leve cabe (pytest/ruff em PostToolUse/Stop).
- [ ] Estudar skills úteis (agentic-engineering, continuous-learning) e o `agent-evaluator` a fundo.
- [ ] Definir 1 comando/fluxo que amarra `plan→review→loop` pro nosso uso.
- [ ] Model tiering pro nosso caso (Haiku exploração / Sonnet implementação / Opus arquitetura).
