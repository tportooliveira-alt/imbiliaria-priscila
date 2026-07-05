# Setup Meta Marketing API

## Credenciais (.env, fora do git)
- META_ACCESS_TOKEN
- META_AD_ACCOUNT_ID  (formato act_XXXXXXXX)
- META_PAGE_ID
- META_INSTAGRAM_ACTOR_ID
- META_PIXEL_ID

## Restrições HOUSING (OBRIGATÓRIO p/ imobiliária)
- special_ad_categories: ["HOUSING"] em TODA campanha.
- Idade travada 18-65+ · gênero travado "Todos".
- Sem segmentação por CEP · raio geográfico mínimo ~25km.
- Exclusões demográficas desabilitadas.
- Lookalike vira "Special Ad Audience".

## Campos obrigatórios por nível
- Campaign: name, objective, status, special_ad_categories
- Ad Set: name, campaign_id, targeting (mín. países), daily/lifetime_budget>0,
  billing_event, optimization_goal
- Ad: name, adset_id, creative {"creative_id":"<ID>"}, status

## optimization_goal (valores úteis)
- CONVERSATIONS      → ideal p/ WhatsApp/Ana
- LEAD_GENERATION    → formulário instantâneo
- OFFSITE_CONVERSIONS→ conversão no site
- LINK_CLICKS / REACH / THRUPLAY

## billing_event
- IMPRESSIONS · LINK_CLICKS · THRUPLAY

## Regras
- Orçamento em centavos (R$50 → 5000).
- Ad criado PAUSED.
- Versão da API: v24.0+.
