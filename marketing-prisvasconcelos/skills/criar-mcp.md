# Skill: Como criar tools MCP de alta qualidade

> O LLM depende 100% da clareza de schemas, nomes e descrições.

## 1. Nomes e escopo (responsabilidade única)
- Nome = ação exata: get_campaign_metrics, update_ad_budget.
- Evite "God Tools". Consultar banco E enviar email → 2 tools + orquestração.

## 2. Descrições (o "prompt" da tool)
- Seja exaustivo. Ruim: "Puxa dados". Bom: "Recupera métricas (cliques,
  impressões, ROAS) de uma campanha do Meta Ads nos últimos 30 dias".
- FastMCP lê o docstring automaticamente (Google/Sphinx/NumPy).

## 3. Input schema (tipagem estrita)
- Pydantic (Python) / Zod (TS). Field(description=...) em CADA parâmetro.
- Regras: max_length, pattern (regex), le/ge.

## 4. Erros e resiliência
- Erro descritivo que ensina a corrigir: "ID não encontrado. Use list_campaigns".
- mask_error_details=True (nunca devolver stack trace ao LLM).

## 5. Segurança
- Credenciais por injeção oculta (get_api_client interno). Token nunca no schema.
- Hints: @mcp.tool(readOnlyHint=False, destructiveHint=True).
