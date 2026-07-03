# Log 2026-07-01 — Ana muda o dia todo: teto diário + reforço DeepSeek

## Sintoma
Ana (WhatsApp) parou de responder; clientes ficaram no vácuo, Priscila respondeu na mão.

## Diagnóstico (com prova)
- Serviços (imobiliaria/agente/mcp) e site **sempre no ar**; **sem crash**.
- DeepSeek **no ar e com saldo** (US$ 4,96); fallback DeepSeek→Claude já existia.
- **Causa raiz: teto diário `WHATSAPP_DAILY_CAP=20`.** A Ana bateu 20/20 às **02:38** (madrugada
  movimentada) e ficou **muda o dia inteiro** (volta só à meia-noite). Vários clientes 12h–17h sem resposta.
- Anthropic **estava no ar** hoje (31 chamadas, todas 200) — não foi queda de provedor.
- Gap real identificado: rotas triagem/handoff/followup/visão usam Claude como primário **E** reserva
  (Claude→Claude) — desprotegidas se a Anthropic cair. (pendente — Lote 2)

## Mudanças aplicadas (LOTE 1 + multi-chave)
1. `.env`: `WHATSAPP_DAILY_CAP` **20 → 50**.
2. `app/clients.py`: `ClienteDeepSeek.MODELO` **deepseek-chat → deepseek-v4-pro** (modelo forte;
   conta oferece v4-flash e v4-pro). Custa mais que o flash — vigiar saldo.
3. `app/clients.py`: `ClienteDeepSeek` agora é **multi-chave** — lê `DEEPSEEK_API_KEY`,
   `DEEPSEEK_API_KEY_2`, `DEEPSEEK_API_KEY_3` em ordem; se uma falhar (sem saldo/bloqueio/429),
   entra a próxima sozinha. `metadata.chave` diz qual respondeu.
4. `.env`: `DEEPSEEK_API_KEY` = chave nova ($24,96, principal) ; `DEEPSEEK_API_KEY_2` = antiga ($4,96, reserva).

## Verificação
- Restart limpo (`Application startup complete`), serviço `active`.
- Teste do app: `n_chaves=2`, resposta via `chave 1` (nova), v4-pro, texto natural.
- `.env` permanece `priscila:priscila 600` (segredo intacto).
- Backups: `.env.bak.*` e `app/clients.py.bak.*` (mesmo diretório).

## ⚠️ Segurança
A chave nova (`sk-c300…e3d6`) foi **colada no chat** → considerar **exposta**. **Gerar nova no painel
DeepSeek e trocar** (direto no `.env`, sem colar em chat).

## Rede de segurança (FEITO 01/07 — "cliente nunca sem resposta")
- Função `_rede_seguranca()` em `app/routes_publicas.py`; acionada em 3 gates do webhook:
  **teto batido**, **IA erro** (except), **IA vazia**.
- Efeito: manda 1 bilhete ao cliente ("já já te respondo, a Priscila foi avisada") + avisa a Priscila
  (`PRISCILA_WHATSAPP`) pra assumir. **1x por lead por dia** (dedup por `metadata.motivo='rede_seguranca'`),
  anti-spam/ban. Nunca propaga erro. Verificado: sintaxe OK, restart limpo, app/site 200.
- Também ajustado: ícone do Instagram antes do @ no rodapé do site React
  (`design-recebido/pvscelos-imobiliaria/src/Home.jsx`, rebuild vite → dist).

## BUG DA VISÃO — Ana não reconhecia imagens (FEITO 02/07)
- Sintoma: desde ~25/06, TODA imagem/mídia virava `[midia recebida]` (0 análises OK numa semana).
- Causa raiz: o método `classificar_imagem` estava na classe ERRADA — dentro de `ClienteDeepSeek`,
  mas o corpo usa a API Anthropic (`messages.create` + `self.modelo`). `ClienteClaude` (quem a visão
  chama, via `app/visao.py`) NÃO tinha o método → `AttributeError` engolido pelo try/except → placeholder.
- Fix: movido `classificar_imagem` de `ClienteDeepSeek` → `ClienteClaude` em `app/clients.py`
  (único caller é `ClienteClaude(...).classificar_imagem` em visao.py:95,121 — o do DeepSeek era código morto).
- Verificado: teste real `visao.analisar_para_atendimento()` descreveu a imagem; restart limpo, app/site 200.
- Backup: `app/clients.py.bak.20260702-223508`.

## CANAL DEV — Ana manda fotos p/ carrossel (FEITO 03/07)
- Objetivo: Thiago pede fotos de imóvel pelo WhatsApp p/ montar propaganda/carrossel.
- Comando: **`fotos <bairro/nome>`** → Ana devolve até 10 fotos do imóvel (com legenda).
- Peças: `whatsapp.enviar_imagem()` (Evolution `sendMedia`, por URL pública `…/assets/{arquivo}/original.jpg`);
  `_dev_fotos()` + `_dev_fotos_worker()` (thread, não trava webhook) em `routes_publicas.py`; intercepta ANTES
  do fluxo de lead, só p/ o número `DEV_WHATSAPP` (compara últimos 8 dígitos). DEV também DEScontado do teto/lead.
- **LIGAR:** setar `DEV_WHATSAPP=55DDDNUMERO` no `.env` + restart. Vazio = canal desligado.
- Verificado (seco): "Candeias" → imóvel 3, 10 fotos, URLs 200; sintaxe OK, restart limpo, app/site 200.
- Backups: `app/whatsapp.py.bak.20260703-081143`, `app/routes_publicas.py.bak.20260703-081143`.

## Pendências (LOTE 2 — o que ainda falta)
- **LIGAR o canal DEV**: falta o número do Thiago em `DEV_WHATSAPP` (+ restart) e testar "fotos Candeias" ao vivo.
- **Status do dia pelo WhatsApp** (mesmo canal DEV): `/status` → resumo do dia (leads, conversas, teto, erros).
  Reusar `metricas_ia`/`panorama_geral`.
- Cross-provider em TODAS as rotas (DeepSeek como reserva também em triagem/handoff/followup/visão).
- Watchdog no agente 24/7: alertar se a Ana ficar muda com cliente esperando.
- Top-up no DeepSeek (v4-pro consome mais) + rotacionar a chave exposta no chat.
