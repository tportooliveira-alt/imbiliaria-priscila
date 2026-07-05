# Estudo avancado - Make, MCP e agentes para Priscila

Data: 04/07/2026  
Status: estudo operacional avancado  
Escopo: Make.com, Make MCP Server, Make MCP Client, Make AI Agent, Maia e aplicacao na sala de marketing da Priscila Vasconcelos Imoveis

## Veredito executivo

A Make pode virar a esteira visual da operacao: receber criativos do Codex, organizar fila de aprovacao, publicar somente o que estiver aprovado, captar leads de Meta/Instagram, registrar tudo no CRM/planilha e gerar relatorios.

O ponto mais forte para trabalharmos "com agentes" e este:

1. Make roda cenarios deterministicos, bons para rotina, fila, CRM, planilha, alerta e postagem aprovada.
2. Make MCP Server deixa agentes externos chamarem cenarios Make como ferramentas.
3. Make MCP Client deixa um cenario Make chamar ferramentas de outros servidores MCP.
4. Make AI Agent cria agentes dentro da propria Make, com ferramentas, conhecimento, memoria por conversa e saida estruturada.
5. Maia ajuda a montar, ajustar e explicar cenarios dentro do Scenario Builder.

Nada disso remove a regra principal da Priscila: publicar, enviar WhatsApp, ativar anuncio, mudar verba ou alterar producao exige aprovacao humana explicita.

## Fontes oficiais estudadas

| Fonte | Uso no estudo |
|---|---|
| https://developers.make.com/mcp-server | Make MCP Server, cenarios como ferramentas, ferramentas de gestao e escopos |
| https://developers.make.com/mcp-server/connect-using-mcp-token | Token MCP, escopo `mcp:use` e acesso por token |
| https://developers.make.com/mcp-server/connect-using-mcp-token/scenarios-as-tools-access-control | Restricao por `scenarioId`, `teamId` e `organizationId` |
| https://apps.make.com/mcp-client | Make MCP Client dentro de cenarios Make |
| https://developers.make.com/api-documentation/api-reference/scenarios | API de cenarios, zonas, tokens e execucao |
| https://help.make.com/webhooks | Webhooks, filas, resposta, limites e processamento |
| https://help.make.com/flow-control | Iterator, Array Aggregator, Repeater e controle de fluxo |
| https://help.make.com/how-features-use-credits | Operacoes/creditos por trigger, action, search, iterator e aggregator |
| https://help.make.com/introduction-to-make-ai-agent-new | Make AI Agent (New), conceitos, ferramentas e limites |
| https://help.make.com/create-your-first-ai-agent | Criacao de agente, instructions, inputs, files, conversation id e response format |
| https://help.make.com/introduction-to-maia-by-make | Maia by Make como assistente de criacao e manutencao de cenarios |

## Mapa mental da Make

### 1. Scenarios

Scenario e o fluxo visual. E onde ficam os modulos, as rotas, os filtros, o tratamento de erro e a agenda.

Para a Priscila, cada scenario deve ter uma responsabilidade clara:

- `fila_instagram_publicar_aprovados`
- `codex_receber_pacote_criativo`
- `meta_lead_ads_para_crm`
- `noticias_para_rascunho`
- `relatorio_funil_semanal`
- `calculadora_site_para_alerta`

Regra: scenario que publica ou envia mensagem nunca deve ser o mesmo que cria rascunho. Primeiro entra como `PENDENTE_REVISAO`; depois outro fluxo publica somente quando `status = APROVADO`.

### 2. Modules

Modulo e cada bloco do scenario. Existem gatilhos, buscas, acoes, transformacoes e ferramentas de IA.

Usos praticos:

| Tipo de modulo | Para que serve | Uso na Priscila |
|---|---|---|
| Trigger instantaneo | Comeca quando algo acontece | Webhook do Codex, lead novo, linha nova |
| Trigger agendado | Roda em horario definido | Relatorio, noticias, fila de posts |
| Search | Busca registros | Procurar linha aprovada, buscar lead, localizar post |
| Action | Faz algo | Criar post, atualizar planilha, criar CRM |
| HTTP | Chama API sem app pronto | Site, Postiz, endpoint proprio |
| JSON | Monta/parseia dados | Receber pacote do Codex |
| Data Store | Guarda estado | Evitar duplicidade de post/lead |
| AI/Agent | Raciocina sobre conteudo | Classificar lead, revisar noticia, gerar rascunho |

### 3. Bundles

Bundle e a unidade de dado que passa pelo fluxo. Se uma busca retorna 12 itens, a Make trata isso como pacotes/bundles que podem acionar modulos seguintes.

Isso afeta custo e seguranca:

- um post = um bundle;
- uma lista de fotos pode virar varios bundles com Iterator;
- cada bundle que passa por uma action pode consumir operacao;
- filtros cedo economizam credito e evitam acao errada.

### 4. Filtros e routers

Filtro decide se o fluxo continua. Router separa caminhos.

Padrao para a Priscila:

- filtro `status = APROVADO`;
- filtro `slug existe na carteira ativa`;
- filtro `media_url publica HTTPS`;
- filtro `noticia tem fonte_url e data_fonte`;
- router por `tipo`: foto, carrossel, reel, story, lead, noticia, erro.

### 5. Iterator e Array Aggregator

Iterator separa uma lista em itens individuais. Array Aggregator junta itens em uma lista de novo.

Uso para carrossel:

1. Codex envia `media_urls` com varias imagens.
2. Iterator valida uma por uma.
3. Array Aggregator remonta a lista final.
4. Modulo de Instagram/Postiz cria carrossel aprovado.

Regra de qualidade: foto de imovel precisa ser do mesmo `slug`. Se nao houver foto real do ambiente citado, usar grafico/infografico limpo em vez de inventar imagem.

### 6. Webhooks

Webhook e a porta de entrada. A Make pode receber JSON vindo do Codex, do site, de formulario, de Postiz, de CRM ou de outro sistema.

Uso ideal:

- Codex gera lote de posts;
- envia para webhook da Make;
- Make salva cada item como `PENDENTE_REVISAO`;
- Thiago/Priscila revisam;
- outro scenario publica os aprovados.

Observacoes importantes das fontes:

- webhooks instantaneos disparam o scenario quando recebem dado;
- webhooks agendados podem enfileirar dados;
- processamento sequencial deve ser usado quando ordem importa;
- resposta do webhook pode ser controlada por modulo de resposta;
- existe limite de volume e logs/filas precisam ser observados.

### 7. Data Stores

Data Store evita bagunca. Ele guarda chaves simples para o fluxo saber que algo ja foi feito.

Chaves recomendadas:

- `post_id_interno`
- `slug + tipo + data`
- `lead_id_meta`
- `telefone_hash + origem + data`
- `noticia_url`

Sem Data Store, um erro ou reprocessamento pode duplicar post ou lead.

### 8. Erros

Erro nao pode sumir. Todo scenario sensivel precisa de rota de erro:

1. marcar item como `ERRO`;
2. salvar mensagem resumida;
3. incrementar `tentativas`;
4. avisar humano;
5. parar depois de limite.

Nunca usar tentativa infinita em publicacao, WhatsApp, pagamento, Ads ou CRM.

### 9. Creditos e operacoes

Pelo modelo oficial, o custo depende de execucoes e bundles:

- trigger pode consumir credito por rodada;
- action consome por bundle de entrada;
- search costuma contar como uma operacao mesmo retornando varios bundles;
- iterator pode multiplicar o que vem depois;
- aggregator consome por agregacao;
- filtros/routers e alguns controles podem ser gratuitos ou de baixo impacto, mas nao devem virar desculpa para fluxo mal desenhado.

Regra pratica: filtrar cedo, deduplicar cedo e publicar tarde.

## Make MCP Server

Make MCP Server e quando a Make vira um servidor de ferramentas para agentes externos. Um agente pode chamar cenarios ativos e sob demanda como se fossem ferramentas.

Isso e poderoso para a Priscila porque eu poderia, depois de conectado corretamente, chamar ferramentas como:

- `registrar_pacote_criativo_pendente`
- `listar_status_fila_instagram`
- `gerar_relatorio_funil_agregado`
- `registrar_lead_teste`
- `consultar_erro_fila`

E devemos adiar ferramentas perigosas:

- `publicar_instagram_agora`
- `enviar_whatsapp`
- `ativar_campanha`
- `alterar_orcamento`
- `apagar_registro`

### Regras MCP

1. Token nunca entra em chat, markdown ou print.
2. Comecar com `scenarioId`, nao organizacao inteira.
3. Scenario exposto precisa estar ativo e sob demanda.
4. Inputs e outputs precisam estar descritos dentro da Make.
5. Ferramenta precisa ter nome curto, claro e com verbo.
6. Acao sensivel so aceita item com `status = APROVADO`.
7. Testar primeiro com ferramenta sem efeito externo.

### Escopos

O escopo minimo citado nas fontes e `mcp:use`. Leitura/gestao de cenarios, conexoes, webhooks, data stores, times e organizacoes depende de escopos e plano.

Gestao de conta/cenario deve ficar fora do primeiro passo. Primeiro: chamar um scenario teste. Depois: chamar cenarios seguros. So entao pensar em gestao.

## Make MCP Client

Make MCP Client e o sentido inverso: um scenario Make chama ferramentas de um servidor MCP externo.

Aplicacao na Priscila:

- um scenario de noticia chama uma ferramenta de busca/apuracao;
- um scenario de relatorio chama uma ferramenta de dados agregados;
- um scenario de CRM chama uma ferramenta interna, sem expor PII em publico;
- um scenario de criativo chama uma ferramenta que valida slug, fotos e legenda.

Regra: selecionar poucas ferramentas. Quanto mais ferramentas habilitadas, maior o risco do agente escolher caminho errado.

## Make AI Agent (New)

Make AI Agent e o ambiente da Make para criar agentes com:

- modelo/provedor;
- instructions;
- knowledge;
- inputs;
- files;
- tools;
- conversation id;
- response format;
- historico e testes.

### Quando usar agente

Use agente quando houver julgamento:

- classificar lead como quente/morno/frio;
- resumir conversa;
- transformar noticia em rascunho;
- revisar se legenda esta coerente;
- sugerir pauta semanal;
- montar relatorio executivo.

Nao use agente quando o fluxo for deterministico:

- copiar linha da planilha;
- salvar registro no CRM;
- verificar `status = APROVADO`;
- publicar item aprovado;
- atualizar campo `post_id`.

### Agentes recomendados para a Priscila

| Agente | Funcao | Ferramentas | Saida |
|---|---|---|---|
| Validador de Criativo | Verifica se post tem slug, fonte, foto correta, marca e CTA | Carteira, planilha, regras da sala | `aprovavel`, `problemas`, `acao_sugerida` |
| Curador de Noticias | Busca/resume noticia atual e cria rascunho | Web search/HTTP, fila | `titulo`, `fonte_url`, `data_fonte`, `rascunho` |
| Triador de Leads | Classifica lead vindo de formulario/calculadora | CRM/site, planilha | `temperatura`, `motivo`, `proximo_passo` |
| Relator Semanal | Resume funil e conteudo sem PII | Dados agregados | `insights`, `riscos`, `acoes` |
| Operador de Fila | Organiza status e erros sem publicar | Planilha/Data Store | `itens_pendentes`, `itens_com_erro`, `prioridade` |

### Conversation id

Use `conversation_id` quando a memoria for util:

- por lead: acompanhar historico do mesmo interessado;
- por campanha: manter contexto de um lancamento;
- por pauta: acompanhar uma serie de posts.

Nao usar memoria para tarefa isolada de revisao simples.

## Maia by Make

Maia e uma assistente dentro da Make para criar, modificar, explicar e consertar cenarios no Scenario Builder.

Como usar bem:

- pedir objetivo claro;
- dizer quais apps entram;
- dizer quais campos precisa mapear;
- pedir filtros e rota de erro;
- revisar tudo antes de ativar;
- testar com `Run once`.

Prompt bom:

```text
Crie um scenario que leia a planilha Fila Instagram Priscila, pegue apenas linhas com status APROVADO e publish_at menor ou igual ao horario atual de Brasilia, separe por tipo foto/carrossel/reel, publique no Instagram Business, atualize a linha com PUBLICADO e post_id, e em caso de erro marque ERRO e grave a mensagem. Nao publique linhas PENDENTE_REVISAO.
```

## Arquitetura alvo da Priscila

### Fluxo 1 - Codex para fila aprovada

Entrada: pacote criado em `_marketing_ia`.  
Make: webhook -> validar campos -> iterator -> Google Sheets/Data Store.  
Saida: itens `PENDENTE_REVISAO`.

Esse fluxo pode ser exposto via MCP como `registrar_pacote_criativo_pendente`.

### Fluxo 2 - Publicacao Instagram aprovada

Entrada: planilha/fila com `status = APROVADO`.  
Make: buscar linhas -> filtros -> router -> Instagram/Postiz -> atualizar status.  
Saida: `PUBLICADO` ou `ERRO`.

Esse fluxo nao deve ser exposto livremente para agente. Se for exposto, precisa checar aprovacao dentro do scenario.

### Fluxo 3 - Facebook Lead Ads para CRM

Entrada: lead novo.  
Make: Lead Ads -> detalhes -> deduplicar -> CRM/site -> backup -> alerta.  
Saida: lead registrado e alerta interno.

Regra: campanha imobiliaria paga usa categoria especial `HOUSING` e nasce pausada.

### Fluxo 4 - Noticias frescas

Entrada: agenda diaria.  
Make: buscar fonte -> agente resume -> fila de rascunho.  
Saida: `PENDENTE_REVISAO` com fonte e data.

Nunca publicar noticia sem fonte e data.

### Fluxo 5 - Calculadoras do site

Entrada: simulacao de financiamento ou avaliacao online.  
Make: receber evento -> classificar interesse -> CRM -> alerta -> relatorio.  
Saida: lead priorizado.

Gancho de marketing:

- simulacao de financiamento mostra possibilidade de compra;
- avaliacao online capta proprietario vendedor;
- laudo formal continua sendo servico pago da Priscila.

### Fluxo 6 - Relatorio semanal

Entrada: dados agregados de leads, posts, fontes e calculadoras.  
Make: buscar dados -> agente relator -> salvar relatorio.  
Saida: resumo sem PII com proximas acoes.

## Checklist para conectar Make MCP com seguranca

1. Criar um scenario teste sem acao externa.
2. Marcar como ativo e sob demanda.
3. Definir inputs e outputs no scenario.
4. Criar token MCP na Make com escopo minimo.
5. Nunca colar token em chat ou arquivo.
6. Configurar endpoint MCP com restricao por `scenarioId`.
7. Testar chamada simples.
8. Registrar no playbook o nome da ferramenta.
9. So depois criar cenarios reais.
10. Manter publicacao/WhatsApp/Ads sempre com gate humano.

## Habilidades Codex criadas

Foram criadas quatro skills permanentes:

| Skill | Quando usar |
|---|---|
| `$make-scenario-architect` | Desenhar/revisar cenarios Make, modulos, filtros, webhooks, erros e credito |
| `$make-mcp-operator` | Conectar Make MCP Server/Client, cenarios como ferramentas, escopos e restricoes |
| `$make-ai-agent-builder` | Criar agentes Make com tools, knowledge, conversation id e saida estruturada |
| `$priscila-make-ops` | Aplicar Make na operacao da Priscila: Instagram, leads, noticias, CRM e fila aprovada |

## Estado atual nesta maquina

Nesta sessao, o Codex ainda nao tem uma ferramenta nativa do Make carregada. Ou seja: eu consigo estudar, planejar, criar arquivos, preparar fila e orientar a configuracao, mas ainda nao consigo operar a Make diretamente por MCP sem a conexao ser adicionada.

Estado conhecido:

- Make abriu no navegador anteriormente.
- A conexao com Google Sheets pediu autorizacao.
- Nenhum scenario foi ativado por mim.
- Nenhum post foi publicado por mim.
- Nenhum token Make/MCP foi salvo em arquivo.

## Proximo passo recomendado

Criar um scenario teste chamado:

`registrar_pacote_criativo_pendente`

Ele deve receber JSON por webhook/MCP, validar campos e gravar tudo como `PENDENTE_REVISAO`. Esse e o primeiro scenario seguro para virar ferramenta de agente.

Depois dele, criar:

1. `listar_status_fila_instagram`
2. `registrar_lead_teste`
3. `gerar_relatorio_funil_agregado`
4. `publicar_instagram_aprovados` com trava interna de status

Esse caminho deixa a Make trabalhar forte, mas sem soltar postagem, mensagem ou dinheiro antes da aprovacao.
