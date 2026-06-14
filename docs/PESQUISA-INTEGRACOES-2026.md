# 🔌 Pesquisa — Melhores integrações/MCP pro Claude (Cowork+Code) 2026

Síntese do /deep-research (104 agentes, 22 fontes, **24/25 confirmadas, 1 derrubada**). Foco: dev/corretor solo.

## ✅ Confirmado (alta confiança, fontes oficiais Anthropic)
1. **Conectores customizados via remote MCP** existem em **todos os planos** (BETA; Free=1, pagos=vários), com OAuth 2.0.
   Pro/Max: **Customize → Connectors → + → Add custom connector** (URL do servidor + OAuth opcional).
2. **Gmail / Google Calendar / Microsoft 365 NÃO autenticam pelo Claude Code** — só conectando em **claude.ai →
   Settings → Connectors**; aí aparecem automaticamente no Claude Code (v2.1.162+). _← é por isso que o Calendar
   funciona no seu Cowork mas NÃO aparece na sessão da VPS. Tudo certo._
3. **Claude Code MCP**: transportes `stdio` / `HTTP` (recomendado) / `SSE` (deprecado), via `claude mcp add`. Comandos
   prontos: **GitHub** (PAT em Bearer → api.githubcopilot.com/mcp/), **Postgres read-only** (`@bytebase/dbhub`), Sentry.
4. **Zapier = a PONTE** pra ~9.000 apps sem conector nativo (CRM, e-mail mkt) — caminho realista pro solo. Tem custo de task.
5. **Você pode expor o NOSSO stack (FastAPI/CRM/SQLite) como custom remote MCP server** → é o **plano F** (Cowork age no
   sistema). Design oficial do MCP. ✅ caminho validado.
6. **Cowork Rotinas** (Scheduled Tasks): planos pagos no **Desktop**; hourly/daily/weekly/weekdays/manual; herdam
   conectores+skills+plugins. ⚠️ **só rodam com o PC ligado e o app aberto** → pra automação crítica, melhor **cron/agente na VPS**.

## ⚠️ Negócio imobiliário (honestidade)
- **WhatsApp via MCP: NÃO tem conector oficial.** Só projetos open-source imaturos (`evoapi-mcp` usa a **Evolution API**
  — a mesma que JÁ usamos; e `whatsapp-mcp` via conta pessoal/QR). Risco de segurança e ban. **→ Não usar na conta de
  produção da Priscila.** Melhor: **manter nossa integração Evolution direta (já funciona) e expô-la pelo NOSSO MCP server.**
- **Portais ZAP/VivaReal (Grupo OLX): NÃO é MCP** — é **feed XML VRSync** (único formato vivo desde out/2024). Pra publicar
  anúncio nos portais, o caminho é gerar/validar o XML VRSync e um job publica.
- **Repo `modelcontextprotocol/servers`**: só 7 servidores de referência ativos; GitHub/Drive/Postgres/SQLite/Slack foram
  **arquivados** (não são "produção"). Os conectores oficiais existem em outros repos.

## ❌ Derrubado
- "Conectores pré-prontos disponíveis em TODOS os usuários (web/Cowork/Desktop/Mobile)" — falso (0-3).

## 🎯 Aplicação no nosso caso
- 📅 **Google Calendar/Gmail/Drive**: conectar em **claude.ai → Settings → Connectors** (no Cowork já fez o Calendar ✅).
- 🔧 **Plano F confirmado**: expor a VPS como **custom remote MCP server** (OAuth, HTTP) → o Cowork manda WhatsApp/marca
  agenda/deploy. Segurança: só ações seguras, escopos limitados, atenção a prompt injection, sem ações de escrita perigosas.
- 💬 **WhatsApp**: seguir com **nossa Evolution direta** (não o evoapi-mcp imaturo); expor pelo nosso MCP.
- 🔗 **Zapier** como ponte rápida se precisar ligar algo sem conector (ex.: e-mail mkt).
- 🏠 **Portais**: se for anunciar no ZAP/Viva, gerar **VRSync XML** (não MCP).

_Fontes: support/docs oficiais Anthropic (connectors, claude-code/mcp, integrations, desktop-extensions),
modelcontextprotocol, grupozap developers, Zapier. Ressalva: muitos recursos em BETA/preview — reconferir._
