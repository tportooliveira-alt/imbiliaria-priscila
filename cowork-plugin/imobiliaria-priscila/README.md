# 🔌 Plugin Cowork/Claude Code — Imobiliária Priscila

Empacota o que a gente construiu pra reusar no **Cowork** (app do Claude) ou no **Claude Code** do PC:

- **Skill `orquestrar-com-ia`** — playbook de como construir automação com IA sem queimar dinheiro
  (workflow vs agente, gate de custo, 5 padrões, model tiering Sonnet/Opus, travas anti-alucinação).
- **Skill `priscila-contexto`** — carrega o contexto do negócio + a arquitetura do sistema + as **regras de ouro**
  (nunca inventar dado, fuso Brasília, branch certa, etc.) — pra qualquer sessão já começar orientada.

> O plugin **não contém segredo nenhum** (pode versionar no git tranquilo). O conector MCP é opcional e fica fora do arquivo.

## 📥 Como instalar no teu PC

O plugin já vem junto no repositório (`cowork-plugin/imobiliaria-priscila`). No PC, depois de um `git pull`:

**Opção A — carregar só nesta sessão (teste):**
```bash
claude --plugin-dir "CAMINHO\ATE\imbiliaria-priscila\cowork-plugin\imobiliaria-priscila"
```

**Opção B — instalar de vez (marketplace local):**
```bash
claude plugin marketplace add "CAMINHO\ATE\imbiliaria-priscila\cowork-plugin"
claude plugin install imobiliaria-priscila@imobiliaria-priscila
```
(Use o caminho real onde clonaste o repo, ex.: `C:\Users\Thiago Porto\imbiliaria-priscila\...`)

**Validar / recarregar:**
```bash
claude plugin validate "...\cowork-plugin\imobiliaria-priscila"
# dentro de uma sessão, após editar: /reload-plugins
```

Depois de instalado, as skills aparecem como **`/imobiliaria-priscila:orquestrar-com-ia`** e
**`/imobiliaria-priscila:priscila-contexto`** (e o Claude também pode acioná-las sozinho quando fizer sentido).

## 🔗 (Opcional) Conector MCP da VPS — ler o sistema ao vivo
O teu Cowork **já está conectado** ao MCP da VPS (lê leads, agenda, imóveis, financeiro). Se precisar reconectar:
- É um MCP **HTTP remoto** com **segredo no path** (a URL inteira é o segredo) → **NÃO colocar no git.**
- Pega a URL secreta no teu lado (`/mcp-…` do nginx da VPS) e adiciona como conector no app do Claude
  (Configurações → Conectores → MCP), OU num `.mcp.json` LOCAL (fora do repo).
- As ferramentas são **somente leitura** (escrita desligada por padrão).

## 🧩 Estrutura
```
imobiliaria-priscila/
├── .claude-plugin/plugin.json
├── skills/
│   ├── orquestrar-com-ia/   (SKILL.md + reference/padroes.md)
│   └── priscila-contexto/   (SKILL.md)
└── README.md
```
