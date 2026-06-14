# 🔗 SETUP DOIS LADOS — PC (Cowork/Code) ↔ VPS, com acesso direto via MCP

Guia prático pro Thiago. **Objetivo:** o Claude lê/age direto nos seus arquivos dos dois lados (PC + VPS + Drive),
sem você alimentar nada na mão. Base: pesquisa /deep-research (25/25 afirmações confirmadas em docs oficiais
da Anthropic — `code.claude.com/docs`, `claude.com/blog`, `modelcontextprotocol/servers`). _Rascunho pra a gente
executar junto — alguns recursos estão em beta (anotado)._

---

## 🧩 Como as peças se encaixam (o conceito)
- **Git é a ponte** PC↔VPS: edita de um lado → `push` → o outro `pull`. Histórico, seguro, sem mexer em rede.
- **MCP** (Model Context Protocol) = como o Claude **enxerga e usa** ferramentas externas (arquivos, banco,
  GitHub, Drive). É isso que te dá o "acesso direto".
- **Plugins** = pacotes que juntam skills + agentes + hooks + **MCP servers** + comandos, instalados via `/plugin`.
- **Cowork (Ctrl+2)** = modo agente p/ tarefas + **Rotinas** (automação). **Code** = mexer no projeto.

---

## ① PASSO 1 — Salvar o projeto no seu PC (Windows)
1. Instale o **Git para Windows** (git-scm.com) se ainda não tem.
2. Abra o terminal (ou o painel do app) e clone:
   ```bash
   git clone https://github.com/tportooliveira-alt/imbiliaria-priscila.git
   cd imbiliaria-priscila
   git checkout feat/calibracao-design-skills
   ```
   → Agora a **pasta inteira do projeto está no seu PC**.
3. ⚠️ **Segredos NÃO vêm no clone** (`.env`, `data/`, fotos — estão no `.gitignore`, de propósito). O app real
   roda na VPS com esses segredos. No PC você **edita código**; a VPS executa. Isso é o certo e o seguro.

## ② PASSO 2 — Fluxo do dia a dia (como você vai usar)
```
   No PC (Cowork/Code):  você pede → Claude edita → você revisa
   → git add -A && git commit -m "o que mudou" && git push
   Na VPS:               ./deploy.sh   (puxa + reconstrói a home + reinicia)
```
- **Regra de ouro:** antes de editar no PC, faça `git pull` (pega o que a VPS/eu mudamos). **Não edite os dois
  lados ao mesmo tempo** — evita conflito. O `deploy.sh` usa `pull --ff-only` (recusa em vez de bagunçar).

## ③ PASSO 3 — Dar ACESSO DIRETO ao Claude (MCP + conectores)
MCP tem **3 escopos**: `local` (só você, este projeto) · `project` (vai no `.mcp.json`, compartilhado no git) ·
`user` (todos os seus projetos). Comando base: `claude mcp add <nome> -- <comando>` (ou `claude mcp add-json`).

**Servidores que valem pra você (dev solo):**
| Quero que o Claude… | MCP server | Como ligar (exemplo) |
|---|---|---|
| Ler/editar **arquivos** de uma pasta | filesystem (oficial) | `claude mcp add fs -- npx -y @modelcontextprotocol/server-filesystem "C:/.../imbiliaria-priscila"` |
| Mexer no **GitHub** (issues, PRs) | GitHub MCP (oficial/remoto) | conector GitHub no app, ou `claude mcp add --transport http github https://...` |
| Consultar o **banco** (só leitura) | postgresql-mcp (`sgaunet`, read-only) ou sqlite | `claude mcp add db -- <bin> ...` |
| Acessar seu **Google Drive** | **conector do app do Claude** | app → Conectores → Google Drive → autorizar |
| Navegar/abrir sites | browser/Playwright MCP | `claude mcp add ...` |

- **Google Drive** (você pediu): é um **conector do app** (Cowork/claude.ai), não um server de terminal — liga em
  **Configurações → Conectores → Google Drive** e autoriza com sua conta.
- Os conectores que já aparecem nesta sessão: **Box, Microsoft 365, Slack, monday, Gamma, Metaview** (precisam de login).
- Pra **compartilhar** uma config de MCP entre PC e VPS, use escopo `project` → grava em `.mcp.json` no repo
  (⚠️ **sem segredos dentro** — use variáveis de ambiente).

## ④ PASSO 4 — Plugins (turbinar o Claude)
- `/plugin` gerencia tudo. **Marketplace** = repositório git com um catálogo; adiciona com
  `/plugin marketplace add <git-url>` e instala os que quiser.
- Você já usa o marketplace **"Design"** (design-system, design-critique…). Dá pra adicionar outros.
- _Beta:_ o sistema de `/plugin` ainda está em evolução — vale conferir a versão.

## ⑤ PASSO 5 — Automação (Cowork Rotinas + agentes) com SEGURANÇA e baixo custo
- **Rotinas (no Cowork):** tarefas que repetem (ex.: "todo dia, resuma os leads novos do CRM"). Liga na aba Rotinas.
- **Headless/cron (na VPS):** dá pra rodar o Claude sem tela pra tarefas agendadas (Agent SDK). Use **Haiku** no
  volume (barato), Sonnet/Opus só quando precisa de cabeça.
- 🔒 **Segurança (regras confirmadas na pesquisa):**
  - **Nunca** colocar segredo em arquivo versionado; usar **proxy de credencial** / variáveis de ambiente.
  - **Deny rules** bloqueiam ferramentas **mesmo em modo "aceitar tudo"** — configure o que o agente NÃO pode tocar.
  - Rodar comandos em **sandbox** quando possível (preview).
  - ⚠️ Banco "somente leitura" **ainda permite SELECT** — ou seja, pode LER dados sensíveis; cuidado com o que expõe.
  - Casa com as nossas regras de ouro do `CLAUDE.md` (infra exige sua autorização; nada de segredo no git).

---

## ✅ Ordem sugerida pra ligar (quando você quiser, juntos)
1. Clonar a pasta no PC (Passo 1) — **fundação**.
2. Testar o fluxo `push` → `deploy.sh` de ponta a ponta (Passo 2).
3. Ligar **filesystem MCP** na pasta do projeto + **Google Drive** (Passo 3) — é o "acesso direto" que você quer.
4. Depois: GitHub MCP, banco read-only, plugins e Rotinas conforme a necessidade.

_Fontes: docs oficiais Anthropic (Claude Code, Agent SDK, MCP), `modelcontextprotocol/servers`, blog de plugins.
Verificação adversarial: 25/25 confirmadas. Nomes de pacotes/comandos podem mudar — confirmamos na hora de ligar._
