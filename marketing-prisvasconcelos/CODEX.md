# CODEX.md — Operação Ads/MCP de Marketing

Esta pasta guarda a camada operacional de marketing: configurações, MCP, documentação de Meta/Google, campanhas pagas e integrações.

Para estratégia, pesquisa, criativos e relatórios de marketing, use a central:

`../_marketing_ia/CODEX.md`

## Papel desta pasta

- Documentar setup Meta/Google.
- Manter MCP e ferramentas de automação.
- Registrar regras de campanha paga.
- Apoiar medição de conversões e ROI.

## Regras obrigatórias

1. Todo Meta Ads imobiliário usa categoria especial `HOUSING`.
2. Todo anúncio nasce `PAUSED`.
3. Qualquer gasto, ativação, edição de campanha ou publicação externa exige confirmação explícita.
4. Não salvar tokens, chaves, cookies ou credenciais reais.
5. Não expor dados pessoais de leads em logs, exemplos ou relatórios públicos.
6. Usar dados reais do MCP/banco para imóveis, bairros, leads e funil.
7. Não inventar imóvel, preço, depoimento ou resultado de campanha.

## Relação com `_marketing_ia`

- Pesquisa avançada: `_marketing_ia/pesquisas-avancadas/`
- Sala de marketing: `_marketing_ia/SALA-DE-MARKETING.md`
- Quadro de comando: `_marketing_ia/QUADRO-DE-COMANDO.md`
- Briefings: `_marketing_ia/briefings/`
- Criativos: `_marketing_ia/criativos/`
- Campanhas e calendário: `_marketing_ia/campanhas/`
- Relatórios: `_marketing_ia/relatorios/`
- Operação técnica e MCP: `marketing-prisvasconcelos/`

## Referência Meta Ads MCP

Estudo interno:

`../_marketing_ia/pesquisas-avancadas/2026-06-28-raspagem-profunda-meta-ads-mcp-pipeboard.md`

Regra: o repo `pipeboard-co/meta-ads-mcp` é referência técnica, não base para cópia direta. A licença é BUSL 1.1. Para a Priscila, qualquer MCP/Ads deve começar somente leitura, depois criação pausada com `HOUSING` e confirmação humana antes de gasto.
