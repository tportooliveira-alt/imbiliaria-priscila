# 📂 Pesquisa de imóveis — Vitória da Conquista (para a Priscila)

Pasta com toda a pesquisa de mercado de VDC (jun/2026): **~890 imóveis à venda + 99 aluguéis** reais,
coletados dos 25 bairros (OLX, ZAP, VivaReal, ImovelWeb + imobiliárias locais).

## 📊 `IMOVEIS-VDC.xlsx` — a planilha (abra no Excel/Google Sheets)
| Aba | O que tem |
|---|---|
| **Imóveis à venda** | Cada casa/apto: bairro, rua, área, quartos, **preço anunciado**, **R$/m²**, e o **valor que nossa calculadora estima** (com faixa mín/máx) + diferença % + aluguel estimado |
| **Aluguéis** | 99 aluguéis reais com R$/m² de locação |
| **Resumo por bairro** | R$/m² mediano, preço mín/máx e nº de imóveis por bairro |
| **Ruas por bairro** | Ruas premium (caras), populares (baratas) e corredores comerciais |

**Como a Priscila usa:**
- Comparar o **preço anunciado** vs o **valor estimado** → identificar imóvel **caro** (acima da faixa) ou **barato/oportunidade** (abaixo).
- Ver o **R$/m² do bairro** na hora de avaliar/precificar.
- Saber as **ruas mais valorizadas** de cada bairro.

## 📄 Estudos (contexto)
- `PESQUISA-PRECOS-VDC.md` — R$/m² por bairro + ruas top.
- `ESTUDO-ALUGUEL-VALOR.md` — como aluguel se relaciona com o valor (yield, piso, mobiliado).
- `CALIBRACAO-AVM-16-06.md` — como a calculadora foi calibrada.

> ⚠️ Preços são de **anúncio (pedido)** — o fechamento real é menor (~5-15%). A avaliação final é sempre da Priscila.
> Atualizar: rodar `venv/bin/python scripts/gerar_planilha_priscila.py` quando coletar mais dados.
