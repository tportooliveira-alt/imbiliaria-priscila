# Alicerce MCP/VPS - Marketing e automacao da Priscila

Data: 05/07/2026  
Status: base para enviar a VPS e continuar a construcao das ferramentas  
Escopo: MCP da imobiliaria, Instagram/Meta, Make/MCP, ferramentas locais de marketing e seguranca operacional

## Objetivo

Construir o alicerce para a Priscila trabalhar com agentes e ferramentas de marketing sem depender de copiar/colar tudo na mao.

O alvo nao e publicar automaticamente agora. O alvo e deixar a VPS com:

1. MCP real da imobiliaria atualizado;
2. ferramentas de leitura seguras;
3. diagnostico de Instagram/Meta/WhatsApp/IAs;
4. ponte Instagram preparada, mas publicacao desligada por padrao;
5. suite local de marketing e blueprint MCP versionados;
6. documentacao clara para proximo passo.

## O que e MCP real

MCP real e codigo que um agente consegue chamar como ferramenta. No projeto, ele fica principalmente em:

- `app/mcp_server.py`
- `scripts/mcp_priscila_codex.py`
- `deploy/imobiliaria-mcp.service`
- `docs/MCP-SERVER.md`

Ferramentas principais:

| Grupo | Ferramentas | Status |
|---|---|---|
| Leads | `resumo_leads`, `listar_leads`, `detalhar_lead` | leitura |
| Imoveis | `listar_imoveis`, `buscar_imovel` | leitura |
| Agenda | `agenda_listar`, `agenda_lembretes_pendentes` | leitura |
| Financeiro | `financeiro_resumo` | leitura |
| Instagram/Meta | `ig_status`, `ig_perfil`, `ig_listar_midias`, `ig_insights` | leitura |
| Ecossistema | `status_ecossistema` | leitura segura |
| Instagram publicacao | `ig_publicar_foto`, `ig_publicar_carrossel`, `ig_publicar_reel` | so aparece se `MCP_IG_PUBLISH_ENABLED=1` |
| Agenda escrita | `agenda_criar` | so aparece se `MCP_WRITE_ENABLED=1` |
| WhatsApp envio | `enviar_whatsapp_lembrete` | so aparece se `MCP_WRITE_ENABLED=1` e `MCP_WHATSAPP_ENABLED=1` |

## O que e blueprint, nao MCP real ainda

A suite de marketing criada em `_marketing_ia/ferramentas/marketing-suite/` e uma bancada local/visual. Ela ajuda a gerar, validar e exportar material, mas ainda nao e servidor MCP.

O arquivo `mcp-blueprint.json` descreve as ferramentas que podem virar MCP depois:

- `gerar_copy_imovel_priscila`
- `validar_criativo_priscila`
- `gerar_briefing_campanha_priscila`
- `montar_payload_make_priscila`
- `relatorio_funil_agregado_priscila`
- `sugerir_prioridade_marketing_priscila`

## Principio de seguranca

Tudo que tem efeito externo fica bloqueado ate decisao humana:

- publicar Instagram;
- enviar WhatsApp;
- criar/alterar campanha;
- ativar anuncio;
- aumentar verba;
- apagar dado;
- mexer em infra/nginx/firewall.

O padrao para VPS e leitura e diagnostico. A escrita so entra com flags explicitas no `.env`.

## Pacote para jogar na VPS

### Codigo MCP e Instagram

- `app/mcp_server.py`
- `app/instagram.py`
- `scripts/mcp_priscila_codex.py`
- `scripts/verificar_instagram_meta.py`
- `scripts/publicar_instagram_lote.py`
- `.env.exemplo`

### Testes de seguranca

- `tests/test_instagram.py`
- `tests/test_instagram_preflight.py`
- `tests/test_mcp_instagram_safety.py`
- `tests/test_publicar_instagram_lote.py`

### Documentacao

- `docs/MCP-SERVER.md`
- `docs/ACESSO-INSTAGRAM-PASSO-A-PASSO.md`
- `_marketing_ia/pesquisas-avancadas/2026-07-04-estudo-avancado-make-agentes-mcp.md`
- `_marketing_ia/pesquisas-avancadas/2026-07-05-alicerce-mcp-vps-marketing.md`
- `_marketing_ia/MCP-NECESSARIOS.md`
- `_marketing_ia/SKILLS-AUTOMATICAS.md`
- `_marketing_ia/playbooks/2026-07-03-make-operacao-priscila.md`

### Ferramentas de marketing

- `_marketing_ia/ferramentas/marketing-suite/index.html`
- `_marketing_ia/ferramentas/marketing-suite/style.css`
- `_marketing_ia/ferramentas/marketing-suite/app.js`
- `_marketing_ia/ferramentas/marketing-suite/mcp-blueprint.json`

## O que nao deve ir neste primeiro pacote

- videos grandes;
- pacotes inteiros de imagens antigas sem necessidade;
- tokens;
- `.env` real;
- publicacao automatica habilitada;
- alteracao de nginx/firewall sem confirmacao separada.

## Ordem recomendada depois de chegar na VPS

1. `git pull` na VPS pelo `deploy.sh`.
2. Rodar testes pequenos de seguranca.
3. Reiniciar site.
4. Reiniciar/validar `imobiliaria-mcp` se o servico MCP estiver ativo.
5. Chamar `status_ecossistema`.
6. Configurar credenciais Meta/Instagram no `.env` real da VPS, sem salvar no git.
7. Rodar `ig_status`.
8. So depois pensar em `MCP_IG_PUBLISH_ENABLED=1`, e ainda assim com lote pequeno e confirmado.

## Decisao de hoje

Enviar para VPS a base de MCP/ferramentas, mantendo tudo sensivel travado.

Isso coloca a fundacao no servidor sem disparar posts, mensagens ou ads.
