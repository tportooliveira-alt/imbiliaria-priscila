# Agent Skill: Detecção de Fadiga e Rotação de Criativos

## Objetivo
Detectar saturação e rotacionar criativos com confirmação da Priscila.

## Triggers
Diariamente OU quando o usuário disser "Verifique a fadiga de anúncios".

## Detecção (Insights API, level=ad, últimos 14 dias)
Sinalizar FADIGA quando SIMULTANEAMENTE:
- Frequency > 4
- CTR caiu > 20% week-over-week

## Rotação (ação)
1. Pausar anúncio antigo (status PAUSED).
2. Selecionar/gerar novo ativo.
3. upload_image → salvar image_hash.
4. POST /adcreatives (novo hash + copy atualizada).
5. Novo Ad com creative_id no adset_id original → criar PAUSED.
6. Ativar SÓ com confirmação da Priscila.
