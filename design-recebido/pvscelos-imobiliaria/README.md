# PVSCELOS Imobiliária — Capa nova (front) + handoff pro Claude da VPS

Redesign visual do site da **Priscila Vasconcelos Imobiliária** (Vitória da Conquista/BA).
Isto é **só a CAPA** (Vite + React 19 + Tailwind 4, com o design da marca). O **motor** — dados, IA "Ana", avaliação, simulador, captação → Paperclip — já existe no backend de produção e deve ser **plugado por você (Claude da VPS)**, que tem toda a lógica calibrada.

> **Pega esta capa e coloca o motor dentro.** As telas e o visual já estão prontos; troca o que precisar pra ligar ao backend.

## Rodar
```bash
npm install
npm run dev      # http://localhost:5173
```
O proxy do Vite (`vite.config.js`) encaminha `/api` e `/assets` pra produção (`pvscelosimobiliaria.com`). Em produção é o mesmo domínio (same-origin), então os caminhos relativos continuam valendo.

## Stack & design
React 19 · Vite · Tailwind 4 · lucide-react.
Paleta: navy `#16284B`/`#0f1c38` · periwinkle `#5C7CB8`/`#7b95c8` · dourado `#c9943a`/`#e8b55a` · areia `#f5f0e8` · bg `#FBFCFE`. Fontes: **Playfair Display** (títulos) + **Inter** (corpo).

## Telas (`src/`)
`App.jsx` (navegação por useState, sem router) · `Home.jsx` (hero, "A Arte do Morar Bem", carrossel, seção IA, footer) · `BuscaMapa.jsx` (**Catálogo** — grade compacta + filtros) · `DetalhesImovel.jsx` · `Lancamentos.jsx` · `Captacao.jsx` · `Login.jsx` · `Sobre.jsx` · `api.js` (camada de leitura).

## O que JÁ liguei (reusar ou trocar à vontade)
- **Home (carrossel)** e **Catálogo (BuscaMapa)** → `GET /api/imoveis`; fotos `/assets/<arquivo>/600.webp`.
- Catálogo: cards **compactos** (ver vários de uma vez) + filtros **client-side** (bairro/tipo/faixa/busca). **Fotos grandes ficam só nos Empreendimentos.**

## CONTRATOS DE API que mapeei/testei (pra você plugar o resto)
**Leitura:**
- `GET /api/imoveis` → `{total, items[]}` — item: `titulo, bairro, tipo, quartos, suites, vagas, area_util, preco, descricao, caracteristicas[], destaque, slug, tour_360_url, imagens[]{arquivo, ordem, tipo}`
- `GET /api/empreendimentos` · `GET /api/depoimentos`
- `GET /api/avaliacao/bairros` → `{bairros[]}` (24 bairros)
- Fotos: `/assets/<arquivo>/<200|600|1200|2400>.webp` ou `/original.jpg`

**Calculadoras (testei — retornam certo):**
- `POST /api/avaliar-imovel` — body `{bairro, area_util, quartos, suites, vagas, padrao(simples|medio|alto|luxo), estado(reformado|bom|regular|precisa_reforma), idade(novo|0_10|10_20|20_mais), tem_area_externa}` → `{valor_minimo, valor_central, valor_maximo, aluguel_estimado, aluguel_yield_anual_pct, fatores{}, confianca, texto}`.
  ⚠️ A versão de produção (`anunciar.html`) tem **campos extras** (rua, mobília, lazer, vista) + **GATE DE LEAD** (nome, contato/WhatsApp, valor pretendido, prazo). **NÃO montei a avaliação — é a sua, dos 2000 testes. Você coloca a sua.**
- `POST /api/simular-financiamento` — body `{valor_imovel, entrada, prazo_meses, taxa_anual, sistema(SAC|PRICE), renda_mensal?, idade_tomador?, nome?, contato?, bairro?, tipo_imovel?}` → `{parcela_inicial(_com_seguros), comparativo_bancos[], custos_aquisicao{itbi,cartorio,...}, primeiras_parcelas[], renda_minima, comprometimento_renda, ...}`
- `POST /api/busca-natural` · `POST /api/lead-vendedor` (captação) · `POST /api/agendar-visita` · `POST /api/chat` `{message, history[{role,content}], session_id}` → `{resposta, session_id}` · `POST /api/consentimento` · `POST /api/alerta-busca` `{nome, contato, filtros}`

## O que falta — VOCÊ pluga o motor:
- **Avaliação** (a sua, com gate de lead) · **Simulador** · **Chat "Ana"** · **Captação** → `/api/lead-vendedor` → Paperclip · **Login OTP** real · **Agendar visita** · **Depoimentos**.
- **Detalhe** e **Lançamentos** ainda com dados de exemplo — ligar a `/api/imoveis` (por slug) e `/api/empreendimentos`.

## ⚠️ Cuidado
Captação e avaliação **geram lead → ponte Paperclip (viva)**. Usa flag/modo de teste pra não sujar o painel real da Priscila.

---
*Capa desenhada com o Thiago (Claude no PC). Pronta pra receber o motor.*
