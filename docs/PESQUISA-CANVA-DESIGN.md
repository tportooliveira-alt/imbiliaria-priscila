# 🎨 Pesquisa — Claude operando o Canva (design automático p/ carrosséis)

> Deep-research (107 agentes, fontes oficiais canva.dev + Anthropic, jun/2026). Pergunta: como o Claude
> pode MEXER no Canva pra gerar carrosséis de Instagram da Priscila — e qual o melhor caminho pro nosso caso.

## ✅ Resposta curta
O Claude **já dirige o Canva hoje**, por dois canais oficiais — mas o recurso que a gente precisa (gerar
N carrosséis a partir de dados/tabela) é **pago (Canva Enterprise)**. Pro nosso caso, o caminho **mais barato e
100% sob controle** é continuar gerando os slides em **HTML/CSS → PNG** (Playwright/Puppeteer) na própria VPS,
usando a skill de carrossel que já temos. O Canva MCP fica como **acabamento manual ocasional** (grátis).

## 1) Canva MCP / "AI Connector" (no Claude Code)
- Servidor remoto oficial: `https://mcp.canva.com/mcp`. Liga no Claude Code com **1 comando**:
  `claude mcp add --transport http Canva https://mcp.canva.com/mcp` (+ login OAuth no navegador, uma vez).
- **Grátis em qualquer plano:** criar design a partir de texto, editar por linguagem natural, subir assets,
  **exportar PNG/JPG/PDF/PPTX/MP4**.
- **⚠️ Enterprise only:** *autofill* de templates + *brand templates/brand kit* — exatamente o que faria a
  geração em massa data-driven. Resize de design = Canva Pro+.
- É um fluxo de **PC/Claude Code com OAuth** (igual ao Figma) — não é automação headless de VPS por aqui.

## 2) Canva Connect API (REST, roda headless na VPS)
- Tem o fluxo completo: `POST /v1/autofills` (preenche um brand template com texto/imagem) → `GET /autofills/{id}`
  (poll) → `POST /v1/exports` (exporta). Auth OAuth 2.0 (auth-code + PKCE, Bearer, scopes `design:content:write/read`).
- **⚠️ O autofill + brand template exigem que a integração aja por um membro Canva ENTERPRISE.** Listar/ler brand
  template funciona em Pro/Teams; *autofill de verdade* = Enterprise. Só campos de **texto e imagem** são autofilláveis.

## 3) "Dev MCP" (`npx @canva/cli mcp`) — NÃO confundir
- Serve só pra **construir apps/integrações** Canva (scaffolding, Apps SDK, docs). **Não cria/edita/exporta design.**

## 4) Bônus: "Claude Design" (Anthropic Labs, abr/2026, Opus 4.7)
- Research preview que transforma texto em **visual Canva editável e on-brand** sem abrir o Canva. É recurso
  hospedado da Anthropic (Pro/Max/Team/Enterprise), **não** um caminho de API/VPS.

## 🎯 Recomendação pro caso da Priscila (FastAPI + skill de carrossel, sem Enterprise)
1. **Gerar os slides nós mesmos**: HTML/CSS (templates da marca #16284B/#5C7CB8) → **PNG via Playwright/Puppeteer**
   na VPS. Grátis, versionável, automatizável, sem depender de plano pago. Encaixa direto na skill `gerar-carrossel`.
2. **Canva MCP no Claude Code** só pro **polimento manual** pontual (criar/editar/exportar é grátis) quando a
   Priscila quiser mexer à mão.
3. **Só considerar Connect API/autofill** se um dia houver Canva Enterprise (caro; não compensa agora).

**Custo:** caminho 1 = R$0 de licença (só CPU da VPS). Canva Enterprise = caro e desnecessário pro volume atual.

_Arquivo de saída bruto da pesquisa: `/tmp/.../tasks/wvz177tdi.output`._
