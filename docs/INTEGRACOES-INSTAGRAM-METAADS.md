# 📲 Integração Claude Code ↔ Instagram + Meta Ads (pesquisa do Thiago, 14/06)

Material que o Thiago trouxe sobre como ligar o Claude no Instagram e no Meta Ads. Salvo pra executar no
**PLANO-AMANHA-15-06**. ⚠️ Tratar como **input a verificar** (nomes de skills/comandos/ferramentas mudam) — a
pesquisa "nobres integrações" (rodando) cruza isso. Casa com nossa arquitetura: **VPS + Claude Code + Python +
CLAUDE.md + segredos fora do git**.

---

## 📸 Instagram — postar automático (carrossel, foto, vídeo)
**Pré-requisitos:** conta IG **Profissional/Business ou Criador** + vinculada a uma **Página do Facebook**.
**Caminho (skill Upload-Post):**
1. Instalar a skill (ex.: `npx skills add Upload-Post/upload-post-skill`) — ou subir manual na interface.
2. Criar app em `developers.facebook.com` → caso de uso **"gerenciamento de conteúdo"** (publicar posts/stories, responder DM).
3. Gerar **token de acesso** (adicionar-se como testador do Instagram → aceitar convite → copiar token).
4. No Claude Code: pasta de credenciais + `/setup Instagram` → fornecer o token → validar → pedir em linguagem natural
   ("lê esse artigo, cria o carrossel e posta").
> **Upload-Post** publica também em TikTok, YouTube, LinkedIn, Threads, X, Pinterest, Páginas do Facebook (texto/foto/MP4).

## 📣 Meta Ads — gerir/analisar anúncios
### Método 1 — Conector MCP (rápido, Claude Desktop/Cowork)
- Requer **Claude Desktop + Claude Pro** (MCP nessa modalidade). Usar **Ryze AI**: cria conta → conecta Facebook
  Business via **OAuth** (sem senha) → Ryze dá **API key + account ID** → Config. → Servidores MCP (JSON) no Desktop.
- Daí: auditoria de campanha, fadiga de criativo, cruzamento de públicos, ROAS em tempo real, mexer em orçamento.

### Método 2 — Graph API direta na VPS (controle total) ✅ **É O NOSSO CASO**
- Temos VPS + Claude Code + Python. App em `developers.facebook.com` (uso **Negócios/Business**) ligado ao Gerenciador.
- No **Graph API Explorer**, gerar token com `ads_read` + `business_management`; **estender** (token longo) ou usar
  **usuário de sistema** (token permanente). Anotar **Ad Account ID**.
- Segurança: exportar como **variáveis de ambiente** (`META_ACCESS_TOKEN`, `META_AD_ACCOUNT`) — **nunca no git**.
- `.claudeignore` no projeto pra o Claude **ignorar** as chaves; `CLAUDE.md` diz que as chaves estão no ambiente.
- Aí o Claude gera scripts Python que leem a Graph API: subir campanha, criar públicos, analisar ROAS, mudar orçamento.

## 🧰 Ferramentas 2026 (do material)
- **High Story + Claude MCP** — automação end-to-end (cria campanha, gera imagem, agenda/publica LinkedIn/X/IG).
- **Claude Code** — agentes autônomos (ler artigo → carrossel → publicar; gestor de tráfego via API).
- **Ryze AI** — gestão autônoma de tráfego (Google+Meta), otimiza lance/orçamento 24/7 + conector MCP.
- **Upload-Post** — habilidade multi-rede (publica/agenda/rastreia engajamento).
- **Buffer AI / Jasper** — agendamento / copywriting (mais supervisão).
- **n8n / Make** — orquestrar workflows complexos junto com os agentes.

## 🎯 Como aplicamos no negócio da Priscila (amanhã)
1. **Meta Ads = Método 2 (Graph API na VPS)** — encaixa no que já temos; começa lendo/analisando (ads_read) antes de
   gastar. Casa com a **calculadora de ads** do plano. Segurança via env + `.claudeignore` (já fazemos isso).
2. **Instagram = Upload-Post** (ou similar) pra postar **carrosséis** + a **rotina de notícias diárias** — do Cowork.
3. **Pré-requisito do Thiago:** IG Business da Priscila vinculado à Página do FB + criar o app na Meta (tokens).
> Antes de ligar pra valer: **validar** nomes/comandos e custos (Claude Pro? Ryze pago?) com a pesquisa de integrações.

_Relacionados: `PLANO-AMANHA-15-06.md`, `PESQUISA-LEADS-2026.md`, `SETUP-DOIS-LADOS.md`, `PENDENCIAS.md`._

---

## 🧰 Ferramentas-ponte (input do Thiago — aula 14/06) — A VERIFICAR na pesquisa
Princípio da aula: **não se "instala plugin nativo" — usa-se CONECTORES (APIs/MCP) que fazem a ponte** entre o Claude e a rede social. A ferramenta precisa ter **API aberta ou servidor MCP**. Configura em **Claude → Conectores/Personalizar**, fornecendo as credenciais da conta (leitura/escrita).

| Ferramenta | Pra que serve (segundo a aula) |
|---|---|
| **Composio** (composio.dev) | Plataforma centralizadora p/ criar conectores customizados — o chat **lê e CRIA dados** em plataformas externas. Tem MCP + muitos apps. _Forte candidata._ |
| **Windsor AI** (windsor.ai) | Consolida dados de várias fontes — conecta Claude ao **Instagram/YouTube** p/ **métricas e relatórios** de desempenho. _(analytics/relatório, não necessariamente publicar)_ |
| **Unipile** (unipile.com) | Interações com **mensagens/DMs** (LinkedIn e redes similares) — automação de leitura/envio/resposta. _(mensageria)_ |

> 💡 **Dica-chave da aula (vale ouro):** o gargalo NÃO é a ferramenta de conexão — é **detalhar o PROCESSO (o passo a passo do workflow)**. Primeiro estruturar **o que a IA deve fazer** (ex.: ao receber um comentário/lead), DEPOIS montar a automação técnica.

**Como aplicar:** a pesquisa "postar Instagram/FB" (rodando) vai **verificar maturidade, custo e segurança** dessas 3 (Composio, Windsor, Unipile) + comparar com Upload-Post/Ayrshare/Graph API. Decidimos a melhor combinação com os dados na mão.
