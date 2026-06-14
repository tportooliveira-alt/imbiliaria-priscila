# 🧩 Servidor MCP da imobiliária — o Cowork agindo no nosso sistema

Construído 15/06 (plano F do quebra-cabeça). Expõe o sistema como **ferramentas** pro Claude (Cowork/Code):
o agente conversa e **age** — consulta leads, vê agenda, marca compromisso, resumo financeiro, manda WhatsApp.

## Estado — ✅ NO AR (15/06)
- **Exposto** em `https://pvscelosimobiliaria.com/mcp-<TOKEN>/` (token secreto no `.env`, modo SÓ LEITURA, validado: conecta + lista 8 ferramentas + lê dados reais). systemd `imobiliaria-mcp` ativo. nginx OK, site intacto.
- ✅ `app/mcp_server.py` (FastMCP 3.4.2) — **construído e testado local** (127.0.0.1:8765, endpoint `/mcp`).
- ✅ **8 ferramentas**, modo **SÓ LEITURA por padrão** (seguro): `resumo_leads`, `listar_leads`, `detalhar_lead`,
  `listar_imoveis`, `buscar_imovel`, `agenda_listar`, `agenda_lembretes_pendentes`, `financeiro_resumo`.
- 🔒 Ações de **escrita** (`agenda_criar`, `enviar_whatsapp_lembrete`) só ligam com flags no `.env`:
  `MCP_WRITE_ENABLED=1` e `MCP_WHATSAPP_ENABLED=1` (padrão **off**) — proteção contra abuso/prompt-injection.
- ⏳ `deploy/imobiliaria-mcp.service` — template systemd (NÃO instalado).

## ⚠️ Falta pra o Cowork conectar (precisa de DECISÃO do Thiago — é infra/segurança)
1. **Rodar como serviço** (systemd) — `cp deploy/imobiliaria-mcp.service /etc/systemd/system/ && systemctl enable --now imobiliaria-mcp`.
2. **Expor publicamente com HTTPS + AUTH** via nginx (ex.: `https://pvscelosimobiliaria.com/mcp`). ⚠️ **Mudança de
   rede/infra → exige sua autorização** (regra de ouro). E precisa de **autenticação** (senão qualquer um acessa o sistema):
   - Opção A: **token Bearer** (mais simples) — header secreto; ou
   - Opção B: **OAuth 2.0** (padrão do conector customizado do claude.ai; mais trabalho).
   _A pesquisa de integrações deixou isso como questão aberta — vamos resolver junto._
3. **Conectar no Cowork**: claude.ai → **Customize → Connectors → + → Add custom connector** → URL do servidor.
4. **Testar** do seu Cowork ("resuma os leads quentes", "marca visita amanhã 14h").

## Segurança (da pesquisa)
- Só servidores confiáveis; revisar escopos; cuidado com prompt injection; **desabilitar ações de escrita** quando não precisar.
- Por isso o padrão é **só leitura**; escrita/WhatsApp só com flag explícita; e nunca expor sem auth.

## Decisão pendente
**Expor agora (com token) ou segurar?** Eu recomendo: ligar primeiro **só leitura** com **token Bearer** (rápido e seguro)
pra você testar no Cowork; e só depois habilitar escrita/WhatsApp com cuidado. Aguardando seu OK pra mexer no nginx.

_Relacionado: `PESQUISA-INTEGRACOES-2026.md`, `SETUP-DOIS-LADOS.md`, `PLANO-DE-ATAQUE.md`._
