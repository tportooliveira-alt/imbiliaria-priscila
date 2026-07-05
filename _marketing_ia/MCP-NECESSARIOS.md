# MCPs necessarios para a sala de marketing

Objetivo: definir quais MCPs/conectores a sala de marketing da Priscila precisa para operar com dados reais, criar campanhas, medir resultado e automatizar atendimento sem perder controle humano.

## Regra principal

A sala de marketing pode ler dados e preparar acoes. Qualquer acao externa que publique, envie mensagem, altere campanha, gaste dinheiro ou mude producao exige confirmacao explicita de Thiago/Priscila.

## Prioridade 1 - base obrigatoria

| MCP/conector | Uso | Status desejado | Trava |
|---|---|---|---|
| Imobiliaria Priscila | Leads, imoveis, funil, agenda e financeiro | Obrigatorio | Sem PII em relatorio publico |
| Filesystem/Git local | Ler e salvar arquivos da sala em `_marketing_ia` | Obrigatorio | Nao mexer no site sem pedido explicito |
| GitHub | Pesquisar repos, versionar mudancas e revisar PRs | Obrigatorio | Nao commitar/pushar sem ordem |
| Browser/Chrome | Conferir site, landing, WhatsApp, pixel e experiencia | Obrigatorio | Usar para validacao, nao para clique sensivel sem confirmar |

## Prioridade 2 - marketing e vendas

| MCP/conector | Uso | Por que precisamos |
|---|---|---|
| Meta Ads MCP | Ler campanhas, anuncios, criativos, gasto, leads e CPL | Meta sera o primeiro canal pago forte |
| Google Ads MCP | Ler busca local, campanhas, termos, negativas e conversoes | Entrar depois, se houver volume de busca em VDC |
| Google Analytics/GA4 ou Google Tag | Medir eventos do site | Sem isso anuncio fica cego |
| Google Sheets | Criar mapas simples de pauta, leads agregados e relatorios | Bom para acompanhamento visual |
| Google Drive | Acessar fotos, contratos, assets, depoimentos aprovados | Fonte de arquivos da operacao |
| Gmail | Captar leads/e-mails, acompanhar respostas e oportunidades | So com cuidado para nao misturar PII em criativos |
| Google Calendar | Agendar visitas, reunioes e lembretes | Ja funciona no Cowork; manter como apoio comercial |

## Prioridade 3 - WhatsApp e automacao

| MCP/conector | Uso | Decisao |
|---|---|---|
| Evolution API via MCP proprio | Enviar/ler WhatsApp, carrossel de imoveis, handoff e status | Caminho ideal para a Priscila |
| Make MCP Server | Expor cenarios Make seguros como ferramentas para agentes externos | Comecar por `scenarioId`, nunca token em arquivo/chat |
| Make MCP Client | Permitir que cenarios Make chamem ferramentas de outros MCPs | Selecionar poucas ferramentas e evitar acao sensivel direta |
| Make AI Agent | Triagem, rascunho, validacao e relatorio dentro da Make | Agentes nao publicam, nao enviam WhatsApp e nao alteram Ads sem gate |
| n8n MCP/API | Orquestrar fluxos: lead ads -> CRM -> WhatsApp -> relatorio | Usar como automacao visual |
| Typebot | Qualificar leads com perguntas guiadas | Bom para funil antes do WhatsApp |
| Chatwoot | Atendimento humano quando Ana precisar passar o bastao | Opcional, bom se aumentar volume |

## Prioridade 4 - criativos e producao

| MCP/conector | Uso | Observacao |
|---|---|---|
| Canva | Criar e adaptar carrosseis, stories e pecas | Usar marca real, paleta e logo aprovados |
| Figma | Criar layouts/sistemas visuais se necessario | Opcional, mais para design refinado |
| Notion | Central externa de planejamento, se Thiago quiser | Opcional; `_marketing_ia` ja cumpre esse papel no repo |

## MCP Meta Ads - escopo seguro

Fase 1, somente leitura:

- listar contas;
- listar campanhas;
- listar conjuntos;
- listar anuncios;
- ler criativos;
- ler paginas;
- puxar insights;
- gerar relatorio semanal.

Fase 2, rascunho pausado:

- criar campanha `PAUSED`;
- criar conjunto `PAUSED`;
- criar anuncio `PAUSED`;
- categoria especial sempre `HOUSING`;
- destino oficial testado;
- UTM aplicada.

Fase 3, operacao controlada:

- pausar criativo ruim;
- duplicar vencedor;
- ajustar verba dentro de limite aprovado;
- nunca ativar ou aumentar gasto sem confirmacao.

## MCP Evolution/WhatsApp - escopo seguro

Fase 1:

- ler status da instancia;
- receber eventos de mensagem;
- registrar origem no CRM;
- enviar respostas de teste para numero interno.

Fase 2:

- enviar carrossel/lista de imoveis com dados reais;
- acionar handoff humano;
- enviar lembrete de visita;
- responder leads vindos de campanha.

Fase 3:

- filas com n8n/RabbitMQ/SQS se o volume crescer;
- separar Baileys para teste/moderado e Cloud API oficial para escala;
- relatorio diario de atendimentos.

Nunca:

- disparo em massa sem opt-in;
- mensagem agressiva;
- prometer disponibilidade sem conferir;
- expor estrategia de bastidor pela Ana.

## Eventos que precisam ser medidos

| Evento | Onde |
|---|---|
| `clique_whatsapp` | Site, landing e paginas de imovel |
| `calculadora_concluida` | Avaliacao online |
| `lead_anunciar` | Captacao de proprietarios |
| `visualizar_imovel` | Pagina do imovel |
| `agendar_visita` | WhatsApp/site/admin |
| `lead_ads_meta` | Meta Lead Ads |
| `lead_google_ads` | Google Ads |

## Resultado de campanhas: tudo se encontrando

O painel ideal deve juntar:

- gasto e criativos do Meta/Facebook/Instagram Ads;
- gasto, termos e conversoes do Google Ads;
- origem e temperatura do lead no CRM;
- conversas e respostas do WhatsApp/Evolution;
- eventos do site: avaliacao, simulacao, agendamento e clique WhatsApp.

A primeira fase e somente leitura. O objetivo e responder:

1. Qual campanha trouxe lead?
2. Qual lead virou quente?
3. Qual canal gerou conversa no WhatsApp?
4. Quanto custou cada lead qualificado?
5. Qual campanha deve pausar, repetir ou virar criativo novo?

## Ordem recomendada de instalacao

1. Confirmar MCP Imobiliaria Priscila como fonte viva.
2. Instalar/validar pixel, GA4 e eventos.
3. Ligar Google Drive/Calendar/Gmail no app.
4. Preparar Meta Ads MCP somente leitura.
5. Preparar Make MCP com um scenario teste restrito por `scenarioId`.
6. Criar adaptador Evolution API como MCP proprio ou via n8n.
7. Criar fluxos Make/n8n de lead -> CRM -> WhatsApp -> relatorio.
8. Adicionar Google Ads MCP quando houver estrategia de busca.
9. Adicionar Canva/Figma para producao visual, se necessario.

## Segredos e acesso

- Tokens nunca entram em `.md`.
- Chaves ficam em `.env`/cofre/conector.
- Logs mascaram token, telefone e dados sensiveis.
- Qualquer MCP HTTP precisa autenticacao forte.
- MCP de Ads com escrita so depois de testes e checklist.

## Decisao atual

Comecar por uma sala de marketing conectada a dados reais e preparar os MCPs nesta ordem:

1. dados internos;
2. medicao;
3. Meta Ads leitura;
4. Evolution/WhatsApp;
5. Make MCP e agentes Make com acesso restrito;
6. n8n;
7. criativos;
8. Google Ads.
