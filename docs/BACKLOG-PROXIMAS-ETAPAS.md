# 📌 Backlog — Próximas etapas (registro pra frente)

## 🏢 Reajuste do simulador de ALUGUEL (por finalidade/uso)
**Registrado em:** 01/07/2026 · **Pedido do Thiago.**

**Situação hoje:** o simulador de aluguel sai **dentro da avaliação da casa** ("Avalie sua casa" →
bloco "Potencial de aluguel"). Ele usa um yield/faixa **genérico por valor do imóvel**, sem separar
por tipo de uso.

**O que precisa ajustar (próxima etapa):**
- O **aluguel comercial** (centro comercial, ponto comercial, sala/loja) é **mais caro** que o
  residencial — o cálculo atual não diferencia isso.
- Considerar **tipo de imóvel** (comercial × residencial) e o **ponto/localização** (ex.: centro
  comercial, avenida movimentada) no valor do aluguel estimado.
- Casa com [[avm-granularidade-rua]]: preço varia por rua/ponto dentro do mesmo bairro — o aluguel
  também.

**Por que ficou pra depois:** exige calibrar fatores de aluguel por uso/ponto (dado + ajuste no
`app/avaliacao.py` / `yield_aluguel_mensal`). Não é urgente; o texto atual já é honesto (aluguel
sai na avaliação).

**Onde mexer quando for fazer:** `app/avaliacao.py` (função de yield/aluguel), possível novo fator
`uso` (comercial/residencial) e `ponto` no `app/routes_publicas.py` (endpoint de avaliação).

---
*(Adicionar aqui outras ideias de próximas etapas conforme forem surgindo.)*
