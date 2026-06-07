# Integração Meta Lead Ads — desenho (aprovado, a implementar)

Objetivo (org-chart do Thiago): **CMO monitora os formulários de leads do Meta → valida → abre ticket pra SDR (Ana) → Ana aborda no WhatsApp em ~2 min** com base no imóvel que o cliente clicou no anúncio.

## Como o Meta entrega o lead
Anúncio com **Formulário Instantâneo (Lead Ad)** no Facebook/Instagram. Quando alguém envia o form, o Meta dispara um **webhook `leadgen`** (não manda os dados no corpo — manda só `leadgen_id`). A gente busca os dados na **Graph API**.

Fluxo:
1. **Verificação (GET)** `/api/meta/webhook?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...` → responder o `hub.challenge` se o `verify_token` bater com `META_VERIFY_TOKEN`.
2. **Evento (POST)** `/api/meta/webhook` → corpo tem `entry[].changes[].value` com `leadgen_id`, `form_id`, `page_id`, `created_time`, `ad_id`.
3. Buscar o lead: `GET https://graph.facebook.com/v21.0/{leadgen_id}?access_token={PAGE_TOKEN}` → retorna `field_data` (nome, telefone, email + campos custom do form) + `ad_id`/`form_id`.
4. (Opcional, recomendado) Buscar contexto do anúncio: `GET /{ad_id}?fields=name,adcreatives{...}` pra saber **qual imóvel** o criativo anuncia → casar com `imoveis` do banco (por slug/tag no nome da campanha, ex.: `vdc-boavista-duplex`).
5. **Upsert do lead** (`leads_repo.upsert_lead`, `origem="meta_ads"`), registrar interação `meta_lead_recebido` com o `field_data` + imóvel de interesse.
6. **Qualificar** (`qualify_lead`) e gravar score/temperatura — igual ao webhook do WhatsApp.
7. **Rotear (a parte do org-chart):**
   - Criar **dossiê no Paperclip** atribuído ao **Gestor de Tráfego (CMO)** pra ele validar dados/origem da campanha (custo, criativo) — não à Ana direto. CMO valida → cria subtarefa pra **Ana (SDR)**.
   - OU, modo rápido (2 min): se `META_AUTO_OUTREACH=1` e o telefone vier no form, a Ana já dispara a 1ª mensagem no WhatsApp via Evolution referenciando o imóvel clicado, e o dossiê do CMO fica pra validação em paralelo.

## Espelha o webhook do WhatsApp
Reusar o padrão de `app/routes_publicas.py::whatsapp_webhook` (linhas ~544-670): upsert → interação → `qualify_lead` → `paperclip_bridge`. Criar `app/routes_meta.py` com:
- `GET /api/meta/webhook` (verify) e `POST /api/meta/webhook` (evento).
- `app/meta_ads.py`: `buscar_lead(leadgen_id)`, `buscar_imovel_do_anuncio(ad_id)`, `enviar_primeira_mensagem(lead)`.
- Estender `paperclip_bridge`: `escalar_meta_lead(lead_id)` → assignee = Gestor de Tráfego (`e61532da-b6ac-4ec1-acb8-a34a31f68fcd`), com subtarefa pra Ana (`a1ff2003-...`).

## Mapa de imóvel do anúncio → carteira
Convenção: nomear a campanha/criativo com o **slug do imóvel** (ex.: `MCMV-...`, `boavista-duplex`). O `buscar_imovel_do_anuncio` casa por slug/título com a tabela `imoveis`. Se não casar, lead entra como "interesse geral" e a Ana pergunta. **Nunca inventar** qual imóvel — se não souber, pergunta.

## O que o Thiago precisa providenciar (credenciais FB)
- **Meta App** (developers.facebook.com) com produto *Webhooks* + *Lead Ads*.
- **Página** do Facebook conectada ao Instagram da Priscila + permissão `leads_retrieval`, `pages_manage_ads`, `pages_read_engagement`.
- **Page Access Token** de longa duração (ou System User token) → env `META_PAGE_TOKEN`.
- **Verify Token** (string que a gente inventa) → env `META_VERIFY_TOKEN`.
- Assinar o campo `leadgen` da página no painel do App (callback = `https://pvscelosimobiliaria.com/api/meta/webhook`).
- IDs dos campos do formulário (pra mapear nome/telefone/email) — pegamos no `field_data`.

## Envs novas (.env do site)
```
META_VERIFY_TOKEN=<segredo nosso>
META_PAGE_TOKEN=<token da página>
META_GRAPH_VERSION=v21.0
META_AUTO_OUTREACH=0      # 1 = Ana manda 1ª msg em ~2min (depois de WHATSAPP_AUTO_REPLY firmar)
```

## Ordem de implementação (quando a Ana firmar nos cenários)
1. Rota de verify + POST stub que só loga (testar handshake do Meta).
2. `buscar_lead` na Graph API + upsert + qualificação.
3. Roteamento CMO→Ana no Paperclip.
4. (por último, com aprovação) `META_AUTO_OUTREACH=1` + `WHATSAPP_AUTO_REPLY=1` → abordagem automática em 2 min.

> Segurança: validar `X-Hub-Signature-256` (HMAC SHA256 com o App Secret) em todo POST do Meta. LGPD: registrar consentimento do form (o Lead Ad já tem opt-in), origem e finalidade.
