# 📍 REFERÊNCIA — ECC (usar SÓ quando necessário)

**Decisão do dono (18/06):** o ECC **NÃO** fica instalado nem jogado no nosso repo. É **pasta de
referência**. No dia a dia vale o **Karpathy** (disciplina já no `CLAUDE.md`). O ECC só puxo
**quando for necessário E o dono pedir** — pego a skill/agente específico na hora, nunca tudo.

## ✅ ATIVO (nosso, sempre) — é isso que rege o trabalho
- **Disciplina Karpathy** → no `CLAUDE.md` (pensar antes / simplicidade / cirúrgico / meta+loop).
- **`scripts/verificar.sh`** → o verify antes de dizer "pronto" (py_compile + pytest + smoke). Já provou valor.
- Fonte do Karpathy: `/root/andrej-karpathy-skills/CLAUDE.md` (pequeno, afiado — o melhor de tudo).

## 📂 ECC = SÓ referência (puxar quando necessário)
- **Onde:** `/root/everything-claude-code` (clonado, **NÃO** instalado; o global foi desinstalado).
- **Regra:** não instalar global, não jogar no nosso repo. Quando uma tarefa REALMENTE precisar, copiar
  **só o arquivo útil** na hora — com o ok do dono. Cada agente/skill é usado **quando faz sentido**.
- **Os poucos que valem** (pra saber onde achar quando precisar):
  - Agentes: `agents/planner.md`, `agents/code-reviewer.md`, `agents/agent-evaluator.md`,
    `agents/loop-operator.md`, `agents/security-reviewer.md`, `agents/architect.md`.
  - Skills: `skills/verification-loop/`, `skills/production-audit/`, `skills/marketing-campaign/`,
    `skills/content-engine/`, `skills/continuous-learning-v2/`.
- **Como puxar (exemplo, só na hora de usar):**
  ```bash
  cp /root/everything-claude-code/agents/code-reviewer.md /var/www/imobiliaria/.claude/agents/
  ```

## Por quê assim (a crítica, resumida)
ECC é inchado (3244 arquivos, regras multi-linguagem JS) e meio produto/hype. ~90% não serve pro nosso
Python. O ouro é o **Karpathy**. Crítica completa em `docs/ESTUDO-ECC.md`.
