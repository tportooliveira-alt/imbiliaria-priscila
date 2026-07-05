# Fluxo de Conversões Offline — Loop Completo

## Loop
CLIQUE → VISITA (captura IDs) → LEAD (WhatsApp/form) → VENDA → ENVIO → ALGORITMO.

## Identificador único = chave da deduplicação
O id único do lead vira:
- event_id  → na Meta CAPI
- order_id  → no Google Ads

## 1. Captura no clique/visita
| Plataforma | Capturar | Origem |
|---|---|---|
| Meta | _fbc (do fbclid na URL) e _fbp | cookies 1ª parte |
| Google | gclid | cookie 90 dias |
Salvar AMBOS no lead do CRM no início do contato.

## 2. Meta CAPI (POST graph.facebook.com/vXX.0/{pixel_id}/events)
Campos mínimos:
- event_name: "Lead" (contato) ou "Purchase" (venda)
- event_time: timestamp UNIX
- event_id: id único do lead (DEDUP)
- action_source: "chat" (WhatsApp) ou "website"
- user_data: { ph, em, fn, ln, _fbc, _fbp }  → PII em SHA-256 local; tel E.164

## 3. Deduplicação Meta (Pixel + CAPI)
Pixel e CAPI enviam o MESMO event_name + MESMO event_id.
A Meta cruza, RETÉM o evento do Pixel e DESCARTA o do servidor → 1 conversão.

## 4. Google (Data Manager API)
ClickConversion: gclid, conversion_action (UPLOAD_CLICKS),
conversion_date_time (yyyy-mm-dd HH:mm:ss-03:00), conversion_value,
currency_code "BRL", order_id (= id do lead).

## 5. Valor
- Lead/contato: 0 ou simbólico.
- Venda: comissão (~R$21.000), nunca o preço do imóvel.

## Regras
- Hash sempre local.
- Reenviar _fbc/_fbp guardados (prova de qual anúncio gerou a venda).
- order_id obrigatório se for ajustar o valor da venda depois.
