# 🔬 MÉTODO DE ESTUDO — como a gente pesquisa (e por que confia no resultado)

Salvo a pedido do Thiago (14/06/2026). Este é o **método** que usamos pra estudar qualquer tema do negócio —
o mesmo que gerou os relatórios de leads/ads, Claude Code+MCP, 360°/vídeo e integrações. A ideia é **reaproveitar
esse método** e, depois, **construir algo em cima dele** (uma skill/rotina nossa de pesquisa).

---

## O que é (em 1 frase)
Em vez de "o Claude responde de cabeça", a gente **decompõe a pergunta, busca em várias fontes em paralelo,
verifica cada afirmação de forma adversarial (votação) e só então sintetiza** — com fontes e nível de confiança.
Resultado: **fato checado, não palpite**. (É o `/deep-research`.)

## O pipeline (5 fases)
1. **Escopo** — quebra a pergunta em ~5-6 ângulos (ex.: Meta Ads, Google Ads, lead magnet, sites, Instagram).
2. **Busca** — 1 agente por ângulo, buscas na web em paralelo (fan-out).
3. **Coleta** — junta as fontes, remove duplicadas, extrai **afirmações falsificáveis** (claims).
4. **Verificação adversarial** — cada afirmação importante é julgada por **3 votos** que tentam REFUTAR;
   só passa quem sobrevive (ex.: 2/3). **O que não se sustenta é DERRUBADO.**
5. **Síntese** — junta o que sobrou, ranqueia por confiança, **cita as fontes** e lista o que ficou em aberto.

## Por que funciona (a prova)
- Na pesquisa de **leads/ads**: 25 afirmações verificadas → **20 confirmadas, 5 DERRUBADAS** (mitos:
  "postar Reel no mesmo dia dá +50% alcance", "cidade pequena tem CPC menor"… caíram).
- Na de **Claude Code+MCP**: 25/25 confirmadas em docs oficiais (0 furada).
- Ou seja: o método **separa o que é real do que é hype** — é nisso que dá pra apostar dinheiro/tempo.

## Como a gente APLICA (o ciclo que deu certo nesta madrugada)
```
   Pergunta de negócio
        → /deep-research (método acima)
        → relatório .md em docs/ (com fontes + confiança)
        → VIRA feature/guia (ex.: "1 pergunta qualificadora" virou código; pesquisa MCP virou SETUP-DOIS-LADOS)
        → salvo no git + memória (não se perde)
```
Regra de ouro do método: **honestidade** — dizer o que é comprovado, o que é beta/incerto, e o que ficou em aberto.

## Estudos já feitos (biblioteca)
- `docs/PESQUISA-LEADS-2026.md` — Meta/Google Ads, lead magnet, Instagram (20 achados).
- `docs/SETUP-DOIS-LADOS.md` — veio da pesquisa Claude Code + MCP + automação (25/25).
- _(rodando)_ 360°/vídeo/depoimentos na conversão · "nobres integrações" (melhores conectores).

## 🚀 Depois: o que CRIAR com esse método (ideias)
- **Skill/rotina "pesquisa-priscila"**: um comando nosso que dispara o método já no formato do negócio (imobiliário,
  VDC, custo baixo) — é só dar o tema e sai o relatório + sugestão de ação.
- **Base de conhecimento viva**: cada pesquisa entra numa pasta `docs/estudos/`, indexada, pra consultar e atualizar.
- **Ciclo automático (Rotina no Cowork)**: ex. "todo mês, repesquisar CPL/tendências de ads e me avisar o que mudou".
- **Validação com dados reais**: cruzar o método (web) com o **agent-browser** (dados vivos OLX/ZAP) = pesquisa + campo.

> Quando o Thiago quiser, transformamos este método numa **ferramenta nossa** (skill + rotina) pra usar em qualquer
> decisão do negócio. Por ora, fica **salvo e documentado** — base pronta pra construir em cima.

_Relacionados: `PENDENCIAS.md`, `ROTA-PROXIMA.md`, `FERRAMENTA-AGENT-BROWSER.md`._
