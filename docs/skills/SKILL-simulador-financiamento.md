# 🏦 SKILL — Simulador de financiamento

## O que faz
Calcula a **parcela** (SAC ou Price, COM seguros MIP+DFI + tarifa) e **compara todos os bancos**
(do mais barato ao mais caro), além de checar a renda. Estilo portal (ZAP). É SIMULAÇÃO, não promessa.

## Onde está o código
- `app/financiamento.py` — motor:
  - `simular(valor, entrada, prazo, taxa, sistema, renda, idade)` → parcela inicial/final, total, renda mínima,
    custos de aquisição (ITBI/cartório), seguros reais (MIP por idade + DFI + tarifa).
  - `recomendar_financiamento(...)` — escolhe a modalidade mais barata por perfil (MCMV, Pró-Cotista, SBPE, SFI).
  - `TAXAS_BANCOS` / `data/taxas.json` — taxas por banco (fonte única editável; **gitignored** pois fica em data/).
- `app/routes_publicas.py`:
  - `POST /api/simular-financiamento` → simula + monta `comparativo_bancos` (todos os bancos, mesmo prazo) ordenado por parcela.
  - `GET /api/financiamento/taxas` — taxas de referência.
- Front: seção `#sim` na home (`assets/preview.html`) — form + `simular()` JS que chama o endpoint e
  monta o card do melhor banco + a tabela de comparação.

## Como testar
```bash
curl -s -X POST https://pvscelosimobiliaria.com/api/simular-financiamento -H "Content-Type: application/json" \
  -d '{"valor_imovel":500000,"entrada":100000,"prazo_meses":360,"taxa_anual":11.19,"sistema":"SAC","renda_mensal":12000}'
```

## Atualizar taxas
Editar `data/taxas.json` (no servidor) — é a fonte única. Sem restart (lido em runtime). Se faltar o arquivo,
usa o `_TAXAS_FALLBACK` em `financiamento.py`.

## Erros comuns
- **Comparação de bancos vazia** → `TAXAS_BANCOS`/`data/taxas.json` sem bancos válidos.
- **Parcela "estranha"** → conferir entrada (não pode ≥ valor), prazo (12–420 meses), idade+prazo ≤ 80,5 (SFH).
- **Taxa velha** → editar `data/taxas.json` (campo `atualizado_em` controla o aviso de "desatualizada").
