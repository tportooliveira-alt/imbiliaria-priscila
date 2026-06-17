# 🏘️ Pesquisa de preços — Vitória da Conquista/BA (jun/2026)

> **792 anúncios reais** à venda (último 1 ano), coletados dos **25 bairros** da cidade via OLX/ZAP/VivaReal/
> ImovelWeb + imobiliárias locais (Paullo Victor, MGF, Marcelo Santana, Sales, DTomaz). Coleta feita pelo
> Thiago (Claude no Chrome) + agentes. Preço = **PEDIDO** (ask, ~5-15% acima do fechamento).
> Dataset: `calibracao/*.psv` e `*.json`. Backtest: `scripts/calibracao_eval.py`. Mapa de ruas: `calibracao/ruas_vdc.json`.

## 📊 Resultado da calibração
| | Antes | **Agora (792 reais)** |
|---|--:|--:|
| Viés mediano | +31% (supervalorizava) | **−0,1%** (sem viés) |
| MAPE (erro médio) | 50% | **28%** |
| Dentro da faixa | 14% | 30% |

O **viés foi a zero** — a calculadora não super/subvaloriza mais. O **MAPE ~28% é o teto do modelo por-bairro**:
a dispersão restante vem de **rua, acabamento e ponto comercial** (que o modelo ainda não lê). Próximo degrau = **fator de rua**.

## 💰 R$/m² REAL por bairro (mediana do pedido ÷ área)
| Bairro | n | Apto R$/m² | Casa R$/m² | Perfil |
|---|--:|--:|--:|---|
| **Recreio** | 56 | 6.047 | 3.500 | nobre (verticalizado) |
| **Candeias** | 213 | 4.934 | 4.491 | nobre Zona Leste |
| **Boa Vista** | 97 | 4.947 | 5.445 | nobre |
| **Universidade/Alphaville** | 46 | — | 5.876 | **luxo (topo)** |
| **Espírito Santo** | 24 | 3.529 | 5.219 | médio-alto (Verana) |
| **Primavera** | 44 | 4.431 | 4.527 | médio-alto (Horto Premier) |
| **Alto Maron** | 34 | 4.479 | 3.278 | médio |
| **Felícia** | 54 | 3.647 | 3.889 | médio |
| **Ibirapuera** | 29 | 5.946 | 2.993 | médio |
| **Jatobá** | 20 | — | 3.607 | popular-médio |
| **Bateías** | 16 | 4.114 | 3.189 | popular (crescimento) |
| **Centro** | 25 | 3.669 | 2.756 | misto (residencial barato + comércio caro) |
| **Brasil** | 10 | 3.010 | 3.016 | popular zona sul |
| **Zabelê** | 26 | 3.704 | 2.852 | popular bimodal |
| **São Pedro** | 18 | — | ~3.600 | popular |
| **Patagônia** | 18 | 2.486 | 2.415 | popular |
| **Ayrton Senna** | 10 | 3.714 | 3.879 | popular |
| **Jurema** | 10 | 4.998 | — | popular-médio |
| **Lagoa das Flores** | 3 | — | 1.600 | rural barato |

## 🛣️ Ruas TOP da cidade (do `ruas_vdc.json`)
- **Mais caras (premium):** Portal das Árvores (Recreio, **R$9.354/m²** — topo), Maison Bordeaux (Recreio, ~R$11k/m²),
  Av. Gilenilda Alves/Bosque dos Pinheiros (Boa Vista, R$8.400-9.800/m²), Alphaville 1 e 2 (Universidade, R$6.462-11.047/m²),
  Av. Olívia Flores (Candeias), Av. Jonas Hortélio (Recreio), Horto Premier (Primavera).
- **Corredores comerciais:** Av. Olívia Flores, Av. Gilenilda Alves, Centro (geral), Av. Ilhéus (Brasil), Av. Juracy Magalhães (Jurema).
- **Bairros bimodais** (rua cara × rua popular no mesmo bairro): Zabelê, Centro — ver [[avm-granularidade-rua]].

## ⚠️ Limites honestos
- Modelo é **por bairro** — não lê rua/acabamento/comercial (por isso MAPE ~28%; a saída é uma **FAIXA**).
- Preço = **pedido**; o fechamento real é da Priscila.
- Poucos bairros com n baixo (Guarani, Cruzeiro, Campinhos, periferia) — base ainda grosseira lá.

## ▶️ Próximo degrau
Ligar o **fator de rua** (premium/popular/comercial → multiplicador) + acabamento (`no_osso` → desconto), usando o
`ruas_vdc.json` já montado. É o que corta a dispersão abaixo de 28%.
