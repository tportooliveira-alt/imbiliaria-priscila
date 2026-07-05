# Setup Google Ads — Data Manager API

## ⚠️ Mudança crítica
UploadClickConversions legado está sendo descontinuado para contas novas.
A partir de 01/abr/2026, Customer Match via OfflineUserDataJobService falha
para contas novas. Em 02/fev/2026 o Google parou de aceitar raw IP.
→ Usar Data Manager API. Versão alvo: Google Ads API v24.2.

## Credenciais (.env)
- GOOGLE_ADS_DEVELOPER_TOKEN
- GOOGLE_ADS_CLIENT_ID / CLIENT_SECRET
- GOOGLE_ADS_REFRESH_TOKEN
- GOOGLE_ADS_LOGIN_CUSTOMER_ID  (MCC, sem hífens)
- GOOGLE_ADS_CUSTOMER_ID        (conta da Priscila, sem hífens)

## 1. Conversão por GCLID
Captura: site recebe ?gclid=... → salvar em cookie 1ª parte (90 dias) + no lead.
ClickConversion:
| Campo | Obrig. | Formato |
|---|---|---|
| gclid | sim | string |
| conversion_action | sim | resource name, type UPLOAD_CLICKS |
| conversion_date_time | sim | yyyy-mm-dd HH:mm:ss-03:00 |
| conversion_value | recom. | número (ex: 21000 = comissão) |
| currency_code | recom. | "BRL" (ISO 4217) |
| order_id | recom. | id único do lead (dedup) |

## 2. Enhanced Conversions for Leads (sem gclid)
user_identifiers (até 5): email, phone, first/last name, address.
Hash SHA-256 LOCAL antes de enviar.
Normalização:
- Email: minúsculas, sem espaço. Gmail: remover pontos antes do @ e +tag.
- Telefone: E.164 (+5577999999999).

## 3. Relatórios (GAQL)
- cost_micros ÷ 1.000.000 = Reais (50000000 = R$50,00 | 1550000 = R$1,55).
- segments.date no SELECT agrupa por dia.

## 4. Recommendations (aplicar só com confirmação da Priscila)
CAMPAIGN_BUDGET · MOVE_UNUSED_BUDGET · MARGINAL_ROI_CAMPAIGN_BUDGET ·
FORECASTING_CAMPAIGN_BUDGET.

## Regras
- order_id sempre (dedup + ajuste futuro de valor).
- Valor da conversão = comissão, não preço do imóvel.
- Hash sempre local.
