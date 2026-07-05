# CLAUDE.md — Marketing Priscila Vasconcelos Imobiliária

## Contexto do negócio
Imobiliária em Vitória da Conquista (BA). Atende TODOS os segmentos:
popular, médio e alto padrão. Ticket médio de venda R$350.000,
comissão 6% → ~R$21.000 por venda. A IA (Ana) atende leads via WhatsApp.

> Leia também: llms.txt (mapa) e os arquivos em docs/, campanhas/, criativos/,
> calculadora/, skills/ e mcp/.

## Regras INVARIÁVEIS (valem para todo código gerado)
1. `special_ad_categories: ["HOUSING"]` é OBRIGATÓRIO em toda campanha Meta.
   Omitir = falha no payload + risco de suspensão da conta.
2. Orçamento Meta SEMPRE em centavos (R$50/dia → daily_budget: 5000).
3. Custos Google vêm em micros: cost_micros ÷ 1.000.000 = Reais.
4. Todo Ad é criado com status "PAUSED". Só ativa com confirmação da Priscila.
5. Sempre 2-3 criativos ativos por Ad Set. Nunca pausar o último sem substituto.
6. NUNCA inventar dado de imóvel. NUNCA hard-delete (usar ativo=0).
7. PII sempre com hash SHA-256 LOCAL, nunca em texto puro.
8. Secrets fora do git. App roda como usuário 'priscila'. Fuso UTC-3.
9. Confirmar SEMPRE antes de qualquer mutação em produção (gasto/criação/edição).
10. API Orgânica (Instagram Graph) ≠ API Paga (Marketing API). Não confundir.

## Restrições HOUSING (segmentação)
- Idade TRAVADA 18-65+ · Gênero TRAVADO "Todos".
- Segmentação por CEP PROIBIDA · raio geográfico mínimo ~25km.
- Exclusões demográficas DESABILITADAS.
- Lookalike vira "Special Ad Audience" automaticamente.

## Versões alvo
- Meta Marketing API: v24.0+ (exemplos em v25.0).
- Google Ads API: v24.2.

## Comportamento esperado do agente
- Antes de gastar/criar/editar em produção → mostrar o plano e PEDIR confirmação.
- Ler dados reais do CRM; nunca simular imóvel inexistente.
- Em erro de API: ler a mensagem, corrigir e, se necessário, perguntar.
