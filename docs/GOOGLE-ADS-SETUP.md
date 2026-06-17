# 🟢 Google Ads — análise detalhada e passo a passo (setup + confirmações)

Análise do que falta pra rodar Google Ads MEDINDO de verdade (não às cegas). O site **já está
preparado** — só faltam IDs e configurações no lado do Google. Pixel da Meta já mede; aqui é o
equivalente do Google.

## 📍 Onde estamos (o site já tem)
- `assets/analytics.js` liga o **Google Tag (GA4)** SOZINHO quando `GA4_ID` existir no `.env`
  (igual o Pixel). Hoje `GA4_ID` está **vazio**.
- Eventos de conversão já disparam: **`agendar_visita`**, **`lead_anunciar`**, **`calculadora_concluida`**,
  **`clique_whatsapp`**. Falta só esses eventos virarem "conversão" no Google.

## 🪜 Passo a passo (ordem certa)

### 1. GA4 (a base de tudo) — **Thiago providencia o ID**
- analytics.google.com → criar propriedade GA4 da Priscila → pegar o **Measurement ID** (`G-XXXXXXX`).
- Me manda o `G-...` → eu ponho no `.env` (`GA4_ID=`) e reinicio. O site passa a medir tudo (já testei o encanamento).

### 2. Marcar os eventos como "Key events" (conversões) no GA4
- GA4 → Administrar → Eventos → marcar como **evento-chave**: `agendar_visita`, `lead_anunciar`,
  `calculadora_concluida`, `clique_whatsapp`. (São os que o site já envia.)

### 3. Conta Google Ads + cobrança
- ads.google.com → criar conta (ou usar existente) da Priscila → **adicionar forma de pagamento**
  (cartão). Fuso/moeda: Brasil / BRL.

### 4. ⚠️ As "CONFIRMAÇÕES" que o Google exige (o que o Thiago perguntou)
- **Verificação de identidade do anunciante** (obrigatória pra veicular): o Google pede documento +
  às vezes dados da empresa. Fica em **Ads → Faturamento/Configurações → Verificação do anunciante**.
  Pode levar alguns dias — **começar cedo**.
- **Verificar o domínio** `pvscelosimobiliaria.com` (e-mail ou DNS) pra usar como destino.
- Aceitar políticas (imobiliário não é categoria restrita no BR, mas seguir as regras de anúncio).

### 5. Ligar GA4 ↔ Google Ads e importar as conversões
- GA4 → Administrar → **Vínculos com o Google Ads** → vincular a conta de Ads.
- Google Ads → Objetivos → Conversões → **Importar** os eventos-chave do GA4 (agendar_visita, lead, etc.).
- (Alternativa mais precisa: tag de conversão `AW-` direto — mas o caminho GA4→import é mais simples e suficiente.)

### 6. Campanha + palavras-chave (já temos material)
- Keywords por imóvel/bairro: `docs/ADS-KEYWORDS-POR-IMOVEL.md`.
- Calculadora de investimento (quanto investir / CPL estimado): página **`/ads`** do site.
- Começar com **orçamento pequeno**, geo-segmentado em Vitória da Conquista + raio, e medir CPL real.

## ✅ O que EU faço (quando chegar o GA4 ID)
- Ligo o `GA4_ID` no `.env` (1 linha) → o site mede automático.
- Confirmo no headless que o gtag dispara os eventos.
- Ajusto nomes/parametros de evento se o Google pedir algo específico.

## 🔲 O que DEPENDE do Thiago/Priscila (lado Google, eu não acesso)
- Criar GA4 e mandar o `G-...`.
- Criar conta Google Ads + cartão.
- **Verificação do anunciante** (documento) — começar logo.
- Vincular GA4↔Ads e importar conversões.

> Resumo: o site está pronto. O gargalo é **as confirmações/verificação no Google** (passos 3-5),
> que só o dono faz. Começar pela **verificação do anunciante** (demora) e pelo **GA4 ID** (me manda).
