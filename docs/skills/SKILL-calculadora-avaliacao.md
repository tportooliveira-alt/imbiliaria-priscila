# 🧮 SKILL — Calculadora de Avaliação (AVM)

## O que faz
Estima o **valor de venda e o aluguel** de um imóvel em Vitória da Conquista, por bairro/m², tipo
(casa/apto/cobertura/terreno/comercial), padrão, estado, idade e extras. **Calibrada com 1.016
anúncios reais** (OLX, jun/2026) — bate ±0,1% com o mercado.

## Onde está o código
- `app/m2_vdc.py` — as TABELAS (o coração da calibração):
  - `M2_VDC` — R$/m² de apartamento por bairro (base).
  - `M2_CASA_MULT` — multiplicador casa/apto POR BAIRRO (ex.: Boa Vista 1.286, Recreio 0.632).
  - `M2_TERRENO_VDC` — R$/m² de terreno por bairro.
  - `FATOR_PADRAO/ESTADO/IDADE/TIPO/MOBILIA/LAZER/VISTA` + `fator_area()` (elasticidade por metragem).
- `app/avaliacao.py` — `avaliar(...)` aplica as tabelas e devolve faixa min/central/max + confiança.
- `app/routes_publicas.py` — endpoint `POST /api/avaliar-imovel` (monta a resposta + **yield de aluguel por bairro**),
  `GET /api/avaliacao/panorama` (gráfico), `GET /api/avaliacao/bairros`.

## Como testar
```bash
python3 /root/treino/teste_calculadora.py     # valida 24+ alvos reais; tem que dar "TODOS PASSARAM"
curl -s -X POST https://pvscelosimobiliaria.com/api/avaliar-imovel -H "Content-Type: application/json" \
  -d '{"bairro":"Candeias","area_util":100,"tipo":"apartamento","padrao":"medio","estado":"bom"}'
```

## Como recalibrar (quando chegarem dados novos)
1. Edite os números em `app/m2_vdc.py` (base, casa_mult, terreno) e os yields em `app/routes_publicas.py`.
2. `systemctl restart imobiliaria`
3. `python3 /root/treino/teste_calculadora.py` (ajuste os alvos do teste se mudou um bairro).

## Erros comuns
- **Valor muito alto/baixo num bairro** → conferir `M2_VDC[bairro]` e, p/ casa, `M2_CASA_MULT[bairro]`.
- **Casa grande superestimada** → é limite do MCDDM; `fator_area()` já dá deságio e a confiança vira "baixa".
- **Bairro não reconhecido** → cai em `"outro"` (fallback). Adicionar a chave em `M2_VDC` (snake_case, sem acento).
- **Aluguel errado** → yields em `routes_publicas.py` (`yield_bairro` p/ apto, `yield_tipo` p/ casa/comercial/terreno).
