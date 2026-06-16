---
name: design-priscila
description: >-
  Sistema/arquitetura de design do site da Priscila Vasconcelos — use SEMPRE que for criar ou editar
  QUALQUER tela, seção ou componente do site (HTML/CSS), revisar layout, ou quando algo estiver
  "desordenado"/bagunçado. Garante que tudo siga o MESMO sistema (tokens, escalas, 1 botão = 1 padrão,
  grid) em vez de ser desenhado "no olho". Base: design systems consagrados + UX imobiliário.
---

# Arquitetura de design — site Priscila Vasconcelos

Casa com [[priscila-contexto]] (persona + cores da marca). **A regra-mãe:** site fica "desordenado" quando cada seção
usa valores arbitrários (espaços no olho, 8 tamanhos de fonte, 5 botões diferentes). A cura **não é mais bom gosto — é um
SISTEMA FINITO de regras** (tokens) que TODAS as telas obedecem. Nada na UI usa valor "cru"; tudo aponta pra um token.
Tokens completos em `reference/tokens.css`. Checklist de revisão em `reference/checklist.md`.

## 1. Espaçamento — grid de 8pt (NUNCA "no olho")
Só use valores da escala: **4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 80** px (`--space-1..20`).
- **Regra de ouro do ritmo (interno ≤ externo):** o espaço AO REDOR de um elemento ≥ o espaço DENTRO dele.
  Ex.: padding do card 16-24px, mas gap ENTRE cards 32-40px. É isso que faz o olho agrupar certo e parecer "arrumado".
- Padding vertical de seção **fixo e igual** entre seções (ex.: 64-80px) → dá ritmo. Espaço irregular entre blocos = bagunça.

## 2. Tipografia — type scale (máx. ~6-7 tamanhos no total)
Papéis nomeados, não tamanhos avulsos: Display 56 · H1 40 · H2 32 · H3 24 (Playfair Display) · Body-lg 18 · Body 16 ·
Sm 14 · Xs 12 (Inter). **Playfair só em títulos, Inter no resto.** Line-height: títulos 1.1-1.25, texto 1.5-1.6.
Qualquer texto fora desses papéis = erro.

## 3. Cor — por PAPEL, com acento escasso (máx. ~4 por tela)
- **Navy `#16284B`** = primária estrutural (texto, header, botões escuros).
- **Dourado** = **acento ESCASSO** — 1 destaque forte por seção (selo, hairline, hover de CTA). **Nunca** como fundo grande.
- **Neutros** (ink/muted/line/bg) carregam ~80% da tela. **Semânticas** (success/warning/danger) só pra status.
- Dourado virando "cor de tudo" é o caminho mais rápido pro site parecer kitsch.

## 4. Componentes — Atomic Design + "1 padrão por componente"
Átomos (botão, input, tag, ícone) → moléculas (card de imóvel, campo de busca) → organismos (busca-portal, grid) → telas.
- **Botão = 3 variantes só:** `primary` (navy cheio) · `gold` (acento premium, raro) · `ghost` (outline/secundário).
  Mesmo padding, raio e altura nas 3. Botão "quase igual" diferente em cada tela = sintoma nº1 de site sem sistema.
- **Card de imóvel = UM componente** reutilizado em todo lugar: mesma proporção de imagem (escolha UMA, ex. 3:2),
  mesma ordem interna → **preço e localização dominam** → specs (quartos/área) em ícones/bullets → CTA.
- **Grid único:** um container (ex. max-width 1200px) + colunas/gap da escala; cards em `auto-fill minmax(300px,1fr)`.
- **Raio:** sm 6 / md 12 / lg 20 / pill 999. **Sombra:** 3 níveis (repouso → hover → flutuante). Nada além disso.
- Tudo via classe de componente — se precisou de um valor novo, ou ele entra na escala, ou não existe.

## 5. Hierarquia & layout (alta conversão)
- **Above-the-fold = 3 coisas só:** imagem/hero forte + a busca + **UMA** CTA primária. Sem propostas concorrentes.
- **1 CTA primária por seção** (resto = ghost). Páginas com CTA única convertem ~30% mais que com botões competindo.
- **Ordem das seções = funil:** Hero+busca → Imóveis em destaque → Empreendimentos → Simulador → Sobre/prova →
  Depoimentos → contato/rodapé.
- **White space generoso entre seções** = o "ar" editorial/elegante. Tela entupida custa conversão.
- **Mobile-first:** alvos de toque grandes, formulário enxuto, texto legível.

## 6. Os erros que deixam "desordenado" (e a cura)
Fontes demais → type scale. Espaço aleatório → escala 8pt + interno≤externo. Cores demais → ≤4 + dourado escasso.
Sem grid → um container/grid compartilhado. CTAs concorrentes → 1 primária. Seções sem ritmo → padding vertical fixo.
Cards inconsistentes → 1 componente, 1 proporção. Botões "quase iguais" → 3 variantes congeladas.

## Como trabalhar (processo anti-bagunça)
1. Antes de criar/editar tela: abrir `reference/tokens.css` e usar SÓ os tokens.
2. Reaproveitar componente existente (não inventar variação). Precisa de novo? Define como componente com tokens.
3. Ao terminar, passar a tela pelo **checklist** (`reference/checklist.md`) — é o gate. Se algo usa valor cru, corrige.
4. Mudança global (cor, raio) = trocar no `:root`, propaga pro site todo. É assim que o sistema se mantém sozinho.

_Fontes: Material 3, IBM Carbon, Atlassian, Shopify Polaris, Radix (organização de tokens) + UX imobiliário (conversão).
Duas deep-research em andamento vão enriquecer esta skill (arquitetura + skills de design no GitHub)._
