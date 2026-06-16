# 📐 Recalibração da calculadora de avaliação (AVM) — 16/06/2026

> Teste de calibração com **~65 anúncios REAIS** de Vitória da Conquista (rodadas 1-3, coletados por agentes
> em OLX + imobiliárias locais: Paullo Victor, MGF, Sales, Marcelo Santana, Arbo, DTomaz, + condomínios de
> construtora MRV/Souza Gomes/VOG). Preço = **PEDIDO** (ask). Método: degrau a degrau (3 bairros por rodada,
> conferir, corrigir). Dataset vive em `scripts/calibracao_eval.py`; CSV em `data/calibracao_olx.csv`.

## 🔴 O que o backtest revelou
A calculadora estava **supervalorizando** forte: **MAPE 50%**, viés mediano **+31%**, só **7/65** dentro da faixa.

**Causa raiz:** o R$/m² base de cada bairro foi calibrado em **medianas de anúncio premium**, mas o modelo
**ainda multiplicava** por padrão (alto/luxo) + extras (suítes/vagas). Ou seja, **contava a qualidade duas vezes** —
imóvel médio/popular estourava; casa grande de luxo explodia (deságio de área fraco demais).

## 🟢 Correções aplicadas (`app/m2_vdc.py`)
| O quê | Antes → Depois | Por quê |
|---|---|---|
| Padrão **alto** | 1,25 → **1,12** | prêmio de alto padrão por m² é menor em VDC |
| Padrão **luxo** | 1,55 → **1,30** | luxo grande NÃO comanda +55%/m² |
| Área **150-200m²** | 0,95 → **0,90** | casas médias-grandes sofrem mais deságio |
| Área **200-300m²** | 0,88 → **0,80** | R$/m² cai bem em casas grandes |
| Base **Recreio** | 6060 → **5000** | ancorada no topo (real apto ~4630) |
| Base **Ibirapuera** | 4300 → **2800** | real apto ~2870 / casa ~2530 |
| Base **Felícia** | 3700 → **3400** | real apto ~3535 / casa ~3175 |
| Base **Patagônia** | 1900 → **2600** | estava SUBvalorizado (real ~2969) |

## 📈 Resultado
| | MAPE | viés mediano | dentro da faixa |
|---|--:|--:|--:|
| Antes | 50,5% | +31% | 7/65 |
| Iteração-1 | 36,2% | +14% | 10/65 |
| **Iteração-2 (atual)** | **32,8%** | **+9%** | **14/65** |

5 dos 9 bairros já "ok". Teste de regressão: `tests/test_calibracao_real.py` (trava MAPE<40%, viés ±20%).

## ⚠️ Limites honestos / pendências
- **O modelo é só por BAIRRO** — não vê **rua** (tem rua cara/barata no mesmo bairro), **acabamento** ("no osso"
  vs pronto) nem **ponto comercial** (ruas comerciais valem mais). Por isso há dispersão; a saída é uma **FAIXA**,
  não número exato. Pra apertar, o agente/corretora precisa informar esses dados do anúncio.
- **Boa Vista** ainda +28% (cluster de casas de luxo novas — base já premium + luxo×novo empilhados).
- **Dados a recoletar** (suspeitos): apto "Felícia 161m²" (área mal-lida, ~61m²); condos "Vog Candeias"/"Prime
  Candeias" vieram rotulados como Patagônia mas são **Candeias**.
- **Bairros sem amostra fresca**: Brasil (n=1), Panorama, Urbis, Zabelê, Bateias, Vila Serrana, Guarani, Primavera.
- **Faltam rodadas**: 4 (terrenos), 5 (novo/luxo acabamento), 6 (mais condomínios de construtora), 7 (**ALUGUEL** —
  a calculadora NÃO faz aluguel hoje; precisa de modelo de yield à parte).

## ▶️ Como rodar
`PYTHONPATH=/var/www/imobiliaria venv/bin/python scripts/calibracao_eval.py` (imprime erro por anúncio + MAPE; salva CSV).
