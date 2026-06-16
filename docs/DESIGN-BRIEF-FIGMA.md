# 🎨 BRIEF DE DESIGN — site Priscila Vasconcelos (pra recriar no Figma)

Fonte da verdade: o código real em `assets/preview.html` (home) e `v3-editorial/` (páginas). Este brief resume os
**tokens, componentes e telas** pro PC-Claude montar o design system no Figma com fidelidade.

## 🎨 Tokens da marca (cores — exatas do `:root`)
| Token | Hex | Uso |
|---|---|---|
| navy | **#16284B** | cor principal (texto, header, botões escuros) |
| navy-2 | #0f1c38 | navy escuro |
| peri | **#5C7CB8** | azul claro de apoio |
| peri-2 | #7b95c8 | peri claro |
| gold | **#c9943a** | dourado (CTAs, destaques) |
| gold2 | #e8b55a | dourado claro |
| areia | #f5f0e8 | bege/areia (fundos quentes) |
| bg | #FBFCFE | fundo geral |
| surface | #EEF2F8 | superfícies/cards suaves |
| line | #dde5f0 | bordas |
| ink | #16284B | tinta/texto |
| muted | #5d6b86 | texto secundário |
- **Gradiente marca:** `linear-gradient(120deg,#16284B 0%,#2c4a82 55%,#5C7CB8 100%)`
- **Gradiente dourado:** `linear-gradient(120deg,#c9943a,#e8b55a)`
- **Sombra:** `0 18px 50px -20px rgba(22,40,75,.35)` · **Raio:** 20px (cards), 999px (pills/botões)

## ✍️ Tipografia
- **Títulos:** **Playfair Display** (serif), 600/700, itálico nos destaques (ex.: "Vitória da Conquista" em itálico dourado).
- **Texto/UI:** **Inter**, 400/500/600/700.

## 🧩 Componentes (recriar como components no Figma)
- **Botões:** `primary` (gradiente navy, branco), `gold` (gradiente dourado, branco — CTAs), `ghost` (branco, borda), `wa` (verde #25D366 WhatsApp). Pill (raio 999px).
- **Header:** logo à esquerda + nav institucional (Como funciona · Financiamento · Mercado · Conquista · Sobre) + botão WhatsApp. Sticky, blur.
- **Barra de setores** (sticky): Avaliar meu imóvel · Empreendimentos · A Ana.
- **Busca-portal** (a estrela): caixa branca arredondada com **abas** (Comprar / Alugar), campo **Tipo** (dropdown), campo **texto** (bairro/característica), botão **Buscar** (dourado). + painel **Filtros avançados** (quartos, vagas, faixa de preço, área) + **Ordenar por**.
- **Card de imóvel:** foto (capa), badge, título, bairro, m²/quartos/vagas, preço, botão.
- **Card de empreendimento:** foto, **badge de status** (Na planta / Em obras / Pronto — cores distintas), construtora, nome, bairro, "A partir de R$".
- **Pill/eyebrow:** dourada (ex.: "✦ Imóveis de alto padrão · CRECI/BA 29.231").
- **Steps "Como funciona":** 4 cards numerados (Descreva · Filtra · Você visita · Fechamento).
- **Simulador de financiamento:** form + card de resultado (gradiente dourado) + tabela de bancos.
- **Depoimentos:** card com estrelas + texto + nome.
- **Footer:** navy, links + contato.

## 📱 Telas (frames a desenhar — desktop + mobile)
1. **Home** — hero (logo, headline "Seu próximo imóvel em *Vitória da Conquista*", busca-portal) → setores → grid de imóveis (com filtros/ordenação) → Como funciona → Financiamento (simulador) → Conquista (bairros) → Sobre a Priscila → Depoimentos → footer.
2. **Detalhe do imóvel** — galeria + lightbox, dados, descrição, CTA WhatsApp/visita.
3. **Empreendimentos (listagem)** — chips de status (Todos/Na planta/Em andamento/Prontos) + grid de cards.
4. **Detalhe do empreendimento** — galeria, vídeo (embed), descrição, **tabela de tipologias** ("A partir de R$"), CTAs.
5. **Anunciar/Avaliar** — calculadora de avaliação (capta vendedor) + form nome/WhatsApp.

## 🗣️ Tom / marca pessoal
Próxima, didática, honesta, "clareza antes de decidir". Marca pessoal (rosto/voz da Priscila). CRECI/BA 29.231.
Local (VDC, bairros: Candeias, Recreio, Boa Vista). Elegante, clean, editorial.

## 🔗 Onde o PC-Claude pega o design real
O repositório está clonado no PC (`imbiliaria-priscila`). Os arquivos-fonte do visual:
- `assets/preview.html` — home completa (CSS no `:root`, todos os componentes).
- `v3-editorial/imovel.html`, `empreendimentos.html`, `empreendimento.html`, `anunciar.html`, `mercado.html`.
Ler esses arquivos dá **as medidas, cores e estrutura exatas** pra reproduzir no Figma.
