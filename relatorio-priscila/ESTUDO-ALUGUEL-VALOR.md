# 📚 Estudo a fundo — Aluguel × Valor do imóvel (VDC + Brasil)

> Pesquisa web (jun/2026) + 99 aluguéis reais de Vitória da Conquista. Embasa a calculadora de aluguel
> (`app/avaliacao.yield_aluguel_mensal` + `routes_publicas` piso) e a de venda. Fontes no fim.

## 1. A regra base (e ela bate com VDC)
- **Yield bruto** = aluguel anual ÷ valor do imóvel. No Brasil ≈ **5,8-6%/ano** (FipeZAP jan/2026) = ~0,5%/mês.
- **VDC (nossos 99 dados):** mediana **0,55%/mês (6,6%/ano)** — levemente acima do nacional (cidade média + muito imóvel popular).

## 2. ⭐ A descoberta-chave: yield é INVERSO ao valor (piso do aluguel)
Confirmado na web E nos dados:
> *"a metragem menor reduz o preço de compra, enquanto o valor do aluguel **não cai na mesma proporção** — sustenta rentabilidade maior."* (QuintoAndar)

| Faixa de valor | Yield (VDC, real) | Equivalente nacional |
|---|--:|---|
| Barato / compacto (≤250k) | **0,65-0,70%/mês** | studios/1dorm ~6,7-8%/ano |
| Médio (250-600k) | 0,50-0,58%/mês | ~6%/ano |
| Caro / luxo (>1M) | **0,38%/mês** | alto padrão **3,83%/ano** (não cobre nem a inflação!) |

**Por quê:** o aluguel tem um **PISO de mercado** — ninguém aluga abaixo de ~R$1.000/mês em VDC, por mais barato que seja o imóvel. E o de luxo não aluga proporcional ao preço (público pequeno, contratos longos).

## 3. 🧱 O piso do aluguel em VDC
- **Mínimo real: R$900** · **cluster do piso: R$1.000-1.200** (apês 50-60m², 2q). Só 1/99 abaixo de R$1.000.
- O modelo linear achou o piso estatístico em **R$1.007** (`aluguel ≈ R$1.007 + 0,30%×valor`).
- **Aplicado:** a calculadora trava **piso de R$950/mês** (imóvel barato não cai abaixo disso).

## 4. Bruto vs LÍQUIDO (o que sobra de verdade)
- **Líquido = bruto − custos.** No Brasil cai pra **3,5-4,5%/ano**.
- Custos que comem o yield: **vacância** 25-30 dias/ano (~7%), **IPTU** 0,5-1%/ano do valor, **condomínio** R$0,50-1,50/m², **IR** 7,5-27,5% sobre o aluguel.
- _Cap rate = NOI ÷ valor_ (yield líquido operacional).
- **Implicação:** o que a calculadora mostra é **BRUTO**. Mostrar também o líquido (~−25%) é honesto e vira argumento.

## 5. Mobiliado = +15-30%
- Imóvel **mobiliado aluga 15-30% mais caro** que vazio (completo até +20-30%). Vários aluguéis nossos eram mobiliados → inflam o yield.
- **Implicação:** detectar "mobiliado" e ajustar tira o maior ruído que sobrou.

## 6. Como isso já está / falta na calculadora
| Item | Status |
|---|---|
| Yield por faixa de valor (piso/inverso) | ✅ `yield_aluguel_mensal` |
| Piso R$950/mês | ✅ travado |
| Validação com regra de mercado | ✅ bate (0,5-0,55%/mês) |
| **Fator mobiliado (+20%)** | 🔜 maior ganho pendente |
| **Mostrar yield líquido (~−25%)** | 🔜 honestidade + venda |
| Mais dados de luxo (>600k, n baixo) | 🔜 firmar ponta da curva |

## Fontes
- [Exame — Como calcular o rendimento de um imóvel](https://exame.com/mercado-imobiliario/como-calcular-o-rendimento-de-um-imovel-para-aluguel/)
- [QuintoAndar — Imóveis que geram mais renda](https://www.quintoandar.com.br/guias/investimento/imoveis-que-geram-renda/)
- [Exame — Aluguel de luxo perde para o CDI](https://exame.com/mercado-imobiliario/renda-com-aluguel-de-imovel-de-luxo-perde-para-o-cdi-e-ate-a-inflacao/)
- [Jetimob — Cap rate](https://www.jetimob.com/blog/cap-rate/)
- [Tarjab — Apartamento vazio ou mobiliado](https://www.tarjab.com.br/blog/investir-em-imoveis/apartamento-vazio-ou-mobiliado/)
- [FipeZAP — Locação Residencial](https://www.datazap.com.br/wp-content/uploads/2025/08/fipezap-202507-residencial-locacao.pdf)
