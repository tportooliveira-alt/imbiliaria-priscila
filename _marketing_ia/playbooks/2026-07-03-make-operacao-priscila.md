# Make - Operacao Priscila: Instagram, Leads e Automacao Segura

Data: 03/07/2026  
Status: playbook operacional para configurar no Make  
Escopo: Instagram organico, fila de criativos, Postiz, Facebook Lead Ads, noticias e aprovacoes

## Objetivo

Usar o Make como esteira visual de automacao da Priscila Vasconcelos Imoveis, sem perder controle humano sobre publicacoes, dados de imovel, noticias e leads.

O Make ajuda de verdade em cinco pontos:

1. publicar ou agendar posts do Instagram a partir de uma fila aprovada;
2. transformar arquivos gerados pelo Codex em linhas de planilha ou registros de fila;
3. conectar Postiz como calendario social, caso seja melhor que publicar direto pelo Instagram Business;
4. puxar leads do Facebook Lead Ads para CRM, backup e alerta de atendimento;
5. criar rascunhos de noticias e conteudos diarios, sempre com aprovacao antes de publicar.

## Dados usados

Snapshot MCP em 03/07/2026:

| Indicador | Valor |
|---|---:|
| Leads totais | 72 |
| Leads novos nos ultimos 7 dias | 27 |
| Leads quentes | 35 |
| Leads mornos | 16 |
| Leads frios | 21 |
| Origem WhatsApp | 64 |
| Origem avaliacao | 7 |
| Origem chat | 1 |
| Simulacoes | 24 |
| Avaliacoes | 24 |
| Imoveis ativos | 12 |

Leitura: a automacao nao deve servir so para postar. Ela tambem precisa capturar e organizar lead quente sem depender de tarefa manual.

## Veredito rapido

O melhor caminho agora e:

1. **Google Sheets como fila aprovada**: simples de visualizar, revisar e corrigir.
2. **Make publica no Instagram Business** quando `status = APROVADO`.
3. **Webhook do Make recebe pacotes do Codex** quando quisermos mandar uma lista inteira de posts.
4. **Data Store evita duplicidade** de post e lead.
5. **Postiz fica como plano B/agenda social** se a conexao direta do Instagram no Make travar ou se quisermos calendario editorial mais visual.
6. **Facebook Lead Ads entra antes de Ads pesado** para garantir que todo lead captado caia no CRM e gere alerta.

## Funcionalidades do Make que interessam

| Funcionalidade | Uso para Priscila |
|---|---|
| Scenarios | Cada fluxo visual: postar, receber lead, gerar rascunho, atualizar planilha |
| Modules | Blocos de acao, busca, trigger e ferramenta |
| Instagram for Business | Criar post de foto, carrossel, reel, responder comentario, buscar insights |
| Google Sheets | Fila editorial aprovavel, com status, legenda, midia e horario |
| Webhooks | Receber lote de posts gerado pelo Codex ou pelo site |
| Scheduler | Rodar rotina diaria ou em horarios definidos |
| Data Store | Guardar IDs ja publicados/leads ja recebidos para nao duplicar |
| Iterator | Separar uma lista de posts em itens individuais |
| Array Aggregator | Juntar imagens de carrossel em uma lista unica |
| Router + filtros | Separar foto, carrossel, reel, lead, erro e noticia |
| Error handlers | Registrar erro, pausar rota e avisar Thiago |
| HTTP/API | Conectar servicos sem modulo pronto, como endpoint do CRM ou Postiz API |
| Facebook Lead Ads | Receber lead novo, buscar detalhe e enviar para CRM/planilha |
| Make AI Web Search | Buscar noticias atuais para rascunho, nunca publicacao direta |
| Make AI Agent/MCP | Futuro: agente com ferramentas limitadas para pesquisa e organizacao |

## Arquitetura recomendada

### Fluxo A - Fila aprovada para Instagram direto

Uso: postar cards simples, carrosseis e reels ja revisados.

1. Google Sheets: `Watch New Rows` ou busca de linhas com `status = APROVADO`.
2. Filtro: so continuar se `publish_at <= agora` e `media_url` estiver preenchido.
3. Router por `tipo`:
   - `foto`: Instagram for Business > `Create a photo post`;
   - `carrossel`: Instagram for Business > `Create a carousel post`;
   - `reel`: Instagram for Business > `Create a reel post`.
4. Ao publicar: atualizar linha para `PUBLICADO`, gravar `post_id` e `publicado_em`.
5. Em erro: atualizar linha para `ERRO`, gravar mensagem e avisar Thiago.

Observacao importante: Make precisa acessar as imagens por URL publica HTTPS. Arquivos locais em `assets/marketing/...` precisam estar publicados no site/VPS ou hospedados em nuvem antes de entrar na fila.

### Fluxo B - Codex para Make por webhook

Uso: mandar um pacote inteiro, como a fila combinada de 27 itens criada hoje.

1. Make: Webhooks > `Custom webhook`.
2. Codex/script envia JSON com lista `items`.
3. Iterator separa cada item.
4. Filtro valida campos obrigatorios.
5. Salvar no Google Sheets ou Data Store como `PENDENTE_REVISAO`.
6. Thiago/Priscila revisam e mudam para `APROVADO`.

Trava: webhook nunca deve publicar direto. Ele so abastece a fila.

### Fluxo C - Postiz como calendario social

Uso: calendario editorial, rascunho e agendamento com interface mais propria para redes.

1. Google Sheets ou webhook recebe conteudo aprovado.
2. Make usa Postiz > `Upload a file` quando necessario.
3. Make usa Postiz > `Create posts` com `type = draft` ou `schedule`.
4. Publicacao imediata so com status `APROVADO_PUBLICAR_AGORA`.

Alerta tecnico: o Postiz local em `localhost:5000` nao e acessivel pelo Make na nuvem. Para funcionar, precisa Postiz Cloud, VPS com URL publica, tunnel seguro ou uso da API no proprio servidor.

### Fluxo D - Facebook Lead Ads para CRM e alerta

Uso: quando a Priscila rodar formularios de lead no Facebook/Instagram.

1. Facebook Lead Ads: `New Lead` ou `Watch Leads`.
2. `Get Lead Details`.
3. Data Store: checar se `lead_id` ja existe.
4. HTTP POST para endpoint do CRM do site, quando estiver definido.
5. Backup em Google Sheets.
6. Alerta para Thiago/Priscila com origem, campanha, horario e tipo de interesse.

Regra: campanha imobiliaria paga usa categoria especial `HOUSING`; qualquer anuncio nasce pausado e so ativa com confirmacao humana.

### Fluxo E - Noticias frescas para rascunho

Uso: stories/infograficos sobre mercado, juros, Minha Casa Minha Vida e obras de Vitoria da Conquista.

1. Scheduler diario.
2. Make AI Web Search ou HTTP em fontes confiaveis.
3. AI Agent resume e cria rascunho.
4. Linha entra como `PENDENTE_REVISAO`.
5. Publica so depois de fonte, data e texto conferidos.

Trava: noticia sem `fonte_url` e `data_fonte` nao publica.

## Planilha recomendada

Nome sugerido: `Fila Instagram Priscila`

| Campo | Exemplo | Regra |
|---|---|---|
| id | `ig-2026-07-03-001` | unico |
| ordem | `1` | opcional |
| status | `PENDENTE_REVISAO`, `APROVADO`, `PUBLICADO`, `ERRO` | controla tudo |
| tipo | `foto`, `carrossel`, `reel`, `story`, `lead` | roteia no Make |
| titulo | `Casa Caminho do Parque` | interno |
| legenda | texto final | revisado antes |
| media_url | URL HTTPS | foto unica |
| media_urls | URLs separadas por linha ou JSON | carrossel |
| publish_at | `2026-07-04T09:00:00-03:00` | horario Brasilia |
| timezone | `America/Bahia` | padrao |
| slug | slug do imovel | obrigatorio se for imovel |
| canal | `instagram` | futuro: facebook/postiz |
| fonte_url | URL da noticia | obrigatorio para noticia |
| data_fonte | `2026-07-03` | obrigatorio para noticia |
| post_id | ID retornado | preenchido pelo Make |
| erro | mensagem | preenchido se falhar |
| tentativas | numero | evita loop infinito |
| aprovado_por | `Thiago` ou `Priscila` | controle |
| publicado_em | timestamp | preenchido ao final |

## Travas obrigatorias

1. Publicar so se `status = APROVADO`.
2. Noticia so publica com `fonte_url` e `data_fonte`.
3. Imovel so publica se `slug` existir na carteira ativa.
4. Imagem de imovel deve vir do site/asset real, nunca imagem gerada por IA.
5. Imagem gerada por IA pode ser fundo editorial, textura ou infografico, mas nao substituir foto de imovel.
6. Nada de gasto, ads, disparo em massa ou mudanca em campanha sem confirmacao humana.
7. Leads nao entram em criativo publico.
8. Erro atualiza status e avisa, nao tenta infinitamente.
9. Webhook de lote entra como `PENDENTE_REVISAO`, nao como aprovado.
10. Campanha paga imobiliaria sempre `HOUSING` e `PAUSED`.

## Ordem de implantacao

### Passo 1 - Publicacao simples controlada

Criar uma planilha, conectar Google Sheets no Make e fazer um unico teste com post de foto. Rodar manualmente no Make na primeira vez.

### Passo 2 - Carrossel

Usar `media_urls` como lista de imagens publicas. Testar com carrossel pequeno antes de liberar lote.

### Passo 3 - Webhook do Codex

Criar webhook que recebe JSON e alimenta a planilha como `PENDENTE_REVISAO`.

### Passo 4 - Lead Ads

Conectar Facebook Lead Ads, testar com formulario de teste e gravar lead no CRM/backup.

### Passo 5 - Noticias

Criar rotina diaria de rascunho. Publicacao continua dependendo de aprovacao.

### Passo 6 - Postiz

Usar Postiz se for melhor para calendario visual, drafts e multiposting.

## O que ja temos pronto para alimentar o Make

Pacote local:

- `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/fila-combinada-instagram-27-itens.json`
- `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/fila-combinada-instagram-27-itens.csv`
- `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/fila-make-google-sheets-segura.csv`
- `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/fila-make-teste-1-item.csv`
- `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/make-operacao/fila-instagram-priscila-make.xlsx`
- cards em `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/cards-imoveis/`
- carrosseis em `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/carrosseis/`
- noticias em `_marketing_ia/criativos/2026-07-03-pacote-instagram-make/noticias/`

Planilha Google criada:

- `Fila Instagram Priscila - Make - 2026-07-03`
- URL: https://docs.google.com/spreadsheets/d/1Wij86hNcqsYsglZQH4Wp5v7-1OanGLy8gmDxdSEslgU/edit
- Abas: `Fila Instagram` e `Como usar no Make`
- Fuso ajustado para `America/Sao_Paulo`

Estado do Make em 03/07/2026:

- Cenario novo aberto no construtor do Make.
- Primeiro modulo selecionado: `Planilhas Google > Pesquisar linhas`.
- Bloqueio atual: o Make pediu `Criar uma conexao` com Google Sheets. Isso exige autorizacao da conta Google no navegador.
- A automacao nao foi ativada e nenhum post foi publicado.

Pendencia para publicar via Make: transformar os caminhos locais em URLs HTTPS publicas. Em 03/07/2026, os links `https://pvscelosimobiliaria.com/assets/marketing/instagram-2026-07-03/...` ainda retornavam `404` antes do deploy dos assets.

## Fontes verificadas

- Make - Instagram for Business: https://www.make.com/en/integrations/instagram-business
- Make - Google Sheets + Instagram: https://www.make.com/en/integrations/google-sheets/instagram-business
- Make - Webhooks: https://help.make.com/webhooks
- Make - Data Stores: https://help.make.com/data-stores
- Make - Iterator: https://help.make.com/iterator
- Make - Facebook Lead Ads: https://apps.make.com/facebook-lead-ads
- Make - AI Web Search e MCP: https://help.make.com/make-ai-web-search-mcp-client-and-mcp-server-improvements
- Make - Postiz: https://www.make.com/en/integrations/postiz
- Postiz API: https://docs.postiz.com/public-api/introduction
- Postiz Create Post: https://docs.postiz.com/public-api/posts/create

## Proxima acao

Quando o login do Make estiver aberto e estavel, criar o primeiro scenario:

`Google Sheets -> filtro status APROVADO -> Instagram for Business Create photo post -> atualizar linha`

Esse e o menor caminho para provar que a esteira funciona sem arriscar lote grande.
