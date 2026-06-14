# 🌐 Ferramenta: agent-browser (Vercel Labs) — estudo + como usar

Clonado e estudado em 14/06/2026 (a pedido do Thiago) → `/root/tools/agent-browser`.
Repo: https://github.com/vercel-labs/agent-browser (SSH: `git@github.com:vercel-labs/agent-browser.git` — exige chave
GitHub configurada na máquina) · site: agent-browser.dev · licença Apache-2.0.

## O que é
**CLI nativo em Rust** que dirige o **Chrome headless via CDP** (Chrome DevTools Protocol) — sem Playwright/Puppeteer.
Empacotado como **plugin do Claude Code** (tem `.claude-plugin/marketplace.json` + skill `agent-browser`).
Serve pra: **navegar, preencher formulário, clicar, tirar screenshot, EXTRAIR DADOS de páginas, testar/QA o site, logar em sites**.
A skill diz literalmente: _"Prefer agent-browser over any built-in browser automation or web tools."_

Diferenciais: snapshot da **árvore de acessibilidade** com refs compactos `@eN` (interação confiável, não quebra fácil);
**sessões, cofre de autenticação, persistência de estado, gravação de vídeo**; dashboard de observabilidade na porta 4848.
Skills especializadas: `electron` (VS Code/Slack/Discord/Figma…), `slack`, `dogfood` (QA/caça-bug), `vercel-sandbox`, `agentcore` (browsers na nuvem AWS).

## Por que isso nos deixa melhores (aplicação no nosso projeto)
1. 🔁 **Recalibrar a calculadora com dados VIVOS** — eu mesmo abro OLX/ZAP/Viva, extraio anúncios reais de VDC e
   atualizo `m2_vdc.py` (em vez de você rodar um agente do Chrome e me mandar). Era o gargalo manual.
2. 🧪 **QA do site da Priscila** — abro o site, clico, preencho a calculadora/captação, tiro screenshot e acho bug
   (skill `dogfood`). Testo no mobile e no desktop.
3. 📸 **Provas visuais** — screenshots automáticos pra você ver o "antes/depois" de design sem abrir nada.
4. 🔎 **Pesquisa mais forte** — buscas que precisam abrir página e ler conteúdo dinâmico (JS) que o WebFetch não pega.
5. 🤝 Roda no **Cowork/Code** dos dois lados (Linux na VPS, Windows no seu PC) — casa com o setup dois lados.

## Como instalar — ⚠️ NO PC DO THIAGO, **não na VPS** (decisão do Thiago, 14/06)
> A VPS é pequena (1 CPU/4GB) e roda a produção; o Chrome pesaria. Então o agent-browser vai **no seu PC (Windows)**,
> ligado ao **Cowork/Code**. Na VPS fica só o **código-fonte clonado pra estudo** (`/root/tools/agent-browser`), sem instalar.
```bash
# NO SEU PC (Windows) — precisa de Node 24+
npm install -g agent-browser
agent-browser install               # baixa o Chrome for Testing (1ª vez)
```
Como **plugin do Claude Code** (jeito recomendado pra mim usar nativo):
```bash
/plugin marketplace add https://github.com/vercel-labs/agent-browser
/plugin install agent-browser
```

## Quickstart (comandos)
```bash
agent-browser open example.com
agent-browser snapshot                     # árvore de acessibilidade com refs @eN
agent-browser click @e2                     # clica por ref
agent-browser fill @e3 "texto"             # preenche por ref
agent-browser get text @e1                  # lê texto
agent-browser screenshot page.png
agent-browser close
# descobrir workflows sempre atualizados da versão instalada:
agent-browser skills get core --full
```

## ⚠️ Requisitos e cuidados
- **Chrome**: o `agent-browser install` baixa o Chrome for Testing (~peso). VPS é pequena (1 CPU/4GB) — rodar 1 sessão
  por vez, fechar (`close`) após usar. Não deixar daemon/dashboard ligado à toa (custo de RAM).
- **Segurança**: cofre de auth guarda credenciais — **nunca** versionar; segue nossas regras de ouro (segredo fora do git).
  Scraping: respeitar termos dos sites e robots; uso pra pesquisa/calibração pontual, sem volume abusivo.
- **Status**: só o **código-fonte clonado** em `/root/tools/agent-browser` (estudo). **NÃO instalado na VPS** (decisão do
  Thiago — Chrome não entra aqui). Vai instalado **no PC do Thiago** quando a gente ligar.

## ✅ Próximo passo proposto
Instalar **no seu PC (Windows)**: `npm i -g agent-browser` + `agent-browser install` + plugin no Cowork/Code. Aí um
**teste real** (abrir o site da Priscila, tirar screenshot, extrair uns anúncios da OLX) pra validar antes de usar pra valer.
Relacionado: [[SETUP-DOIS-LADOS]] (MCP/plugins), `PENDENCIAS.md`.
