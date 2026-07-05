# 🔱 Inventário da Marca — Priscila Vasconcelos

**Regra:** todo criativo usa a **logomarca REAL** desta pasta. **Nunca inventar** monograma/logo (erro grave).

Guia completo de uso: `assets/marketing/GUIA-MARCA-PRISCILA.md`.

## Logomarca (a marca PV = telhado/losango + nome)
| Arquivo | O que é | Usar quando |
|---|---|---|
| `assets/logo-branco.jpeg` | Lockup completo (ícone + "PRISCILA VASCONCELOS · CORRETORA DE IMÓVEIS · CRECI/BA 29.231") sobre **fundo branco** | Fundo claro/off-white |
| `assets/logo-icone-branco.jpeg` | Só o ícone PV, fundo branco | Selo pequeno, avatar, fundo claro |
| `assets/logo-icone.jpeg` | Ícone PV | Variante |
| `assets/logo-preto.jpeg` | Versão escura | Fundo claro de alto contraste |
| `assets/logo-selo.jpeg` | Selo | Carimbo/marca d'água |
| `assets/logo-branco-creci.jpeg` | Lockup com CRECI | Quando precisar destacar o CRECI |
| `assets/logo.svg` | ⚠️ versão **provisória** simplificada (azul claro) — não usar em criativo final | — |

## Versões tratadas para FUNDO ESCURO (navy) — geradas a partir da logo real
| Arquivo | O que é |
|---|---|
| `assets/marketing/logo-mono-offwhite.png` | Logo completa em **off-white knockout**, fundo transparente — padrão p/ fundo navy |
| `assets/marketing/logo-mono-gold.png` | Mesma logo em **dourado**, fundo transparente — uso pontual |

## Regra de marca d'água nas fotos
- Toda foto usada em post, carrossel, story, anúncio, capa ou peça pública deve sair com **marca d'água/logomarca real da Priscila**.
- Usar preferencialmente `assets/marketing/logo-mono-offwhite.png` sobre faixa navy, ou `assets/logo-selo.jpeg` quando a peça pedir carimbo discreto.
- A marca deve ficar discreta, com respiro, de preferência no canto inferior. Nunca cobrir rosto, imóvel, preço, metragem, planta, legenda ou detalhe comercial importante.
- As fotos originais podem permanecer sem marca como arquivo-mestre; a versão final de publicação precisa estar marcada.
- Nunca inventar selo, monograma ou logo alternativa.

## Cores da marca
- Navy `#16284B` · Dourado `#c9943a` · Off-white `#F5F1E9`.
- A **logo em si** é azul (navy + azul-aço); o **dourado** é a cor de acento do sistema (CTAs, fios, selos).

## Tipografia dos criativos
- Títulos: serifa elegante de alto contraste (no infográfico: **Italiana** / números **Gloock**); no site: **Playfair Display**.
- Texto/labels: sans limpa (**Inter** / **Instrument Sans**).

## Como reaplicar a logo num design (script de referência)
`assets/marketing/infografico.py` mostra o tratamento: carregar a logo real, gerar knockout off-white
(luminância → alpha) e posicionar com margem. Reusar essa função em qualquer peça nova de fundo escuro.
