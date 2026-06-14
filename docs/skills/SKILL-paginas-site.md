# 🖥️ SKILL — Páginas do site (front)

## O que faz
O site público (home, página de imóvel, captação, panorama de mercado) — navy + dourado + Playfair,
imóvel-primeiro, IA discreta.

## Arquivos (servidos por nginx/StaticFiles)
- **Home:** `v3-editorial/index.html` — **GERADA** a partir de `assets/preview.html` (a fonte de dev).
- **Imóvel:** `v3-editorial/imovel.html` (= `assets/imovel.html`) — galeria, mapa, agendar visita.
- **Captação/Avaliação:** `v3-editorial/anunciar.html` (= `assets/anunciar.html`) — calculadora venda+aluguel + lead vendedor.
- **Mercado:** `v3-editorial/mercado.html` (= `assets/mercado.html`) — gráfico Chart.js de R$/m² por bairro.
- PWA: `v3-editorial/manifest.webmanifest` + `sw.js` (cache; bumpar a versão `pv-shell-vNN` ao publicar).
- Logos/fotos: `assets/logo-*.jpeg`, `assets/priscila-*.jpg`.

## Rotas (server.py)
`/` → `/v3-editorial/` · `/anunciar` e `/avaliar` → anunciar.html · `/mercado` e `/panorama` → mercado.html.
**noindex global** no middleware (soft-launch) — remover pra lançar no Google.

## ⚠️ Como publicar uma mudança na HOME (importante)
A home no ar é `v3-editorial/index.html`, mas ela é **gerada** de `assets/preview.html`. Fluxo:
1. Edite **`assets/preview.html`**.
2. Rode o transform (tira a barra de PREVIEW + noindex, ajusta links `/assets/imovel.html`→`imovel.html`,
   injeta SEO/manifest/SW) que **regenera** `v3-editorial/index.html`. (Ver o bloco python usado nas publicações.)
3. Bumpe a versão do SW: `sed -i 's/pv-shell-vNN/pv-shell-vNN+1/' v3-editorial/sw.js`.
4. Não precisa restart (são estáticos). No celular, force refresh (cache do SW).

As páginas imovel/anunciar/mercado são editadas direto e copiadas pra `assets/` e `v3-editorial/`.

## Erros comuns
- **Editei a home e não mudou** → você editou `assets/preview.html` mas não regenerou `v3-editorial/index.html`.
- **Gráfico do /mercado não aparece** → CSP precisa de `https://cdn.jsdelivr.net` no `script-src` (server.py) — já liberado.
- **Fonte feia (sem Playfair)** → CSP `style-src`/`font-src` precisa de fonts.googleapis/gstatic (já liberado).
- **Mostra versão antiga no celular** → cache do service worker; bumpar `pv-shell-vNN` e refresh forte.
- **Logo com fundo branco/preto errado** → usar a versão certa (logo-branco no claro, logo-preto no escuro) + `mix-blend-mode`.
