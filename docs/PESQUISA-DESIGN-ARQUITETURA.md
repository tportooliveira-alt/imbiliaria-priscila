# 🔬 PESQUISA — Arquitetura de design para site imobiliário (deep-research, 16/06)

Deep-research verificada (107 agentes, votação adversarial). Base da skill `design-priscila`. Confirma os princípios
e traz dados de conversão + referência open-source aplicável a HTML/CSS.

## Síntese
Um site imobiliário organizado e de alta conversão se constrói sobre um **SISTEMA DE TOKENS**: base de espaçamento
**8pt** (8/16/24/32/40/48/56...) com **meio-passo de 4pt** (ícones, texto pequeno, line-heights) — convenção unânime
Carbon/Atlassian/Material. A organização vem de **tokens nomeados** (substituem hex/px hard-coded por papéis), aplicados
via **Atomic Design**. A hierarquia usa **whitespace/proximidade (Gestalt)** como mecanismo primário. O hero deve ter
**UMA ação primária** — simplificá-lo **elevou conversão ~46%** em teste A/B.

## Achados (confiança)
1. **Espaçamento 8pt + meio-passo 4pt** [ALTA, 3-0] — escala 8/16/24/32/40/48/56; margens/padding sempre múltiplos fixos.
   _Mito refutado (0-3): "8pt porque telas são divisíveis por 8" — use 8pt pelo equilíbrio variáveis×distinção, não pelo mito._
2. **Baseline 4pt p/ tipografia** [ALTA] — line-heights escalam de 4 em 4 (passos de 8 ficam distantes demais). Alinhar
   espaçamento 8pt + baseline 4pt habilita ritmo vertical (na web exige espaçamento deliberado, não é automático).
3. **Tokens = base da organização** [ALTA, 3-0] — substituir valores crus por tokens (cor/tipografia/espaçamento no mínimo).
   Modelo Atlassian: sufixo = % da base 8px (space.100=8, space.200=16, space.300=24, space.400=32, space.600=48, space.800=64, space.1000=80).
   _Refutado: não citar nomes semânticos de cor do Polaris como fato._
4. **Atomic Design (HTML/CSS)** [ALTA] — átomos (botão/input) → moléculas (busca = label+input+botão) → organismos (header, card) → templates → páginas.
5. **Whitespace = agrupamento primário (Gestalt)** [ALTA] — elementos próximos = relacionados; variar o espaço ao redor agrupa/separa e cria hierarquia.
6. **Hero de alta conversão** [ALTA] — UMA ação primária (busca OU contato) visível sem rolar; no mobile a busca na faixa inferior (alcance do polegar).
7. **Dado de conversão** [MÉDIA] — simplificar o hero/above-the-fold **+46% (259→398)** no mesmo tráfego (A/B Carrot); versão simplificada venceu em 3 sites (+22%, +47%).
8. **Erro nº1 de "desordenado"** [BAIXA] — excesso de ícones nas características do imóvel sobrecarrega. Cura: poucos ícones, foco no que importa.
9. **Referência GitHub** [ALTA] — **`codewithsadee/homeverse`**: imobiliário, responsivo, **100% HTML/CSS/JS** (sem framework/build), type scale de 7 passos em CSS variables. Modelo direto pra site codado à mão.

## Fontes principais
Carbon (IBM) 2x-grid · Atlassian spacing · Material/freeCodeCamp 8pt+4pt · designsystems.com · Shopify Polaris tokens ·
GC Design System tokens · Brad Frost Atomic Design · Carrot (dado de conversão A/B) · github.com/codewithsadee/homeverse.

_Aplicação: já destilado em `cowork-plugin/.../skills/design-priscila/` (SKILL.md + reference/tokens.css + checklist.md)._
