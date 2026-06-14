# 🗺️ PLANO-MESTRE — Site Priscila Vasconcelos
> Auditoria do site + plano de leads/ads + 360° + **compactação do contexto** (passo a passo).
> Data: 14/06/2026. Use junto com `docs/skills/` (1 skill por área).

═══════════════════════════════════════════════════════════════════════
## PARTE 1 — ESTADO ATUAL (o que está NO AR)
═══════════════════════════════════════════════════════════════════════
Site em **soft-launch**: pvscelosimobiliaria.com → `/v3-editorial/` (noindex global no `server.py` até
a Priscila aprovar). Admin: `/admin/` (login tportooliveira@gmail.com / 233024). Git: branch
`feat/calibracao-design-skills`.

**✅ Pronto e funcionando:**
- Home imóvel-primeiro (navy+dourado+Playfair, logo destacada, abas por setor, IA discreta).
- Página de imóvel (galeria + lightbox, mapa, agendar visita, "perguntar pra Ana").
- Captação `/anunciar` + Mercado `/mercado` (gráfico) — **calculadoras gateadas (viram lead)**.
- Calculadora de avaliação **calibrada com 1.016 anúncios OLX** (±0,1%) — venda + aluguel.
- Simulador de financiamento com **comparação de bancos**.
- Ana (IA) com dados EXATOS da carteira, áudio (Groq) + voz (ElevenLabs).
- Admin: cadastro com foto + IA descreve + sugere preço + auto-organiza foto (Claude vision).
- CRM/captação: lead vendedor, agenda, financeiro, dossiê quente.

═══════════════════════════════════════════════════════════════════════
## PARTE 2 — AUDITORIA: o que FALTA (priorizado)
═══════════════════════════════════════════════════════════════════════
| # | Item | Status | Prioridade |
|---|---|---|---|
| 1 | **Nova seção "Anúncios/Leads" (Meta/Google/Insta)** — landings + pixels | ❌ falta | 🔴 alta (Parte 3) |
| 2 | **Tour 360° embutido** por imóvel (passeio) | ⚠️ parcial (campo existe; falta embed bonito) | 🔴 alta (Parte 4) |
| 3 | **Depoimentos reais** de clientes | ❌ falta (precisa material) | 🟡 média |
| 4 | **Vídeo curto da Priscila** (humaniza) | ❌ falta | 🟡 média |
| 5 | **Filtros de busca** (bairro/tipo/preço) | ⚠️ só busca por IA | 🟢 baixa (3-4 imóveis) |
| 6 | **Mais imóveis** na carteira (Priscila cadastra) | em andamento | 🔴 alta (conteúdo) |
| 7 | **Pixels/tags** (Meta Pixel + Google Tag + conversões) | ❌ falta | 🔴 alta (p/ ads) |
| 8 | **Lançar no Google** (tirar noindex) | aguardando aprovação | quando aprovar |

═══════════════════════════════════════════════════════════════════════
## PARTE 3 — PLANO DE LEADS + ADS (Meta · Google · Instagram)
═══════════════════════════════════════════════════════════════════════
**Estratégia (full-funnel, padrão 2026):**
- **Google Ads = intenção** (quem já procura): palavras "apartamento à venda Vitória da Conquista",
  "casa Candeias", "avaliar meu imóvel VDC". Manda pra landing certa (imóvel ou /anunciar).
- **Meta Ads (Facebook+Instagram) = desejo/alcance**: segmenta por idade/renda/interesse/local (VDC e região),
  usa **Advantage+** (IA acha o público). Criativo: foto do imóvel + "quanto vale o seu?" → /anunciar.
- **Instagram da Priscila** (orgânico): reels dos imóveis, "quanto vale seu imóvel?", bastidores, depoimentos.

**Nova seção do site a construir — "landings de campanha" + rastreamento:**
1. **Pixels/tags:** instalar **Meta Pixel** + **Google Tag (gtag)** no site, e disparar **evento de conversão**
   quando alguém deixa nome+WhatsApp (avaliação/simulador/captação) — pra medir custo por lead.
2. **Landings dedicadas por campanha** (URLs limpas que já temos: `/anunciar`, `/mercado`, página de imóvel):
   reaproveitar o "portão de lead" que já existe (preencheu dados → vira lead).
3. **Formulário-nativo (Lead Form)** do Meta/Insta: opção de captar sem sair do app (sincroniza com o CRM depois).
4. **Lead magnet:** "Descubra quanto vale seu imóvel" (avaliação grátis) — o ímã de lead nº 1 em 2026.

**Funil:** Anúncio → landing (/anunciar ou imóvel) → portão (nome+WhatsApp) → **lead no CRM** → Ana qualifica → Priscila fecha.

**Orçamento sugerido (começar pequeno):** R$ 15–30/dia por campanha, medir **custo por lead** semanal, escalar o que converte.
Começar com 2 campanhas: (a) Google "avaliar/comprar em VDC", (b) Meta "quanto vale seu imóvel".

*Fontes: Luxury Presence, KBK, Stape, Cyberlink (lead gen imobiliário 2026).*

═══════════════════════════════════════════════════════════════════════
## PARTE 4 — PLANO 360° (passeio pelo imóvel, opção por imóvel)
═══════════════════════════════════════════════════════════════════════
**O que já existe:** campo `tour_360_url` no imóvel (admin: "Tour 360° — URL Matterport/iframe/YouTube 360")
+ botão na página do imóvel quando preenchido + **Pannellum já liberado na CSP** (`connect-src`).

**Como funciona (opção por imóvel — nem todos precisam):**
- Priscila grava o 360 (celular com app 360, ou contrata) e gera o link/embed (Matterport, CloudPano, Kuula, ou
  **Pannellum grátis** pra fotos 360 próprias). Cola a URL no cadastro do imóvel. Só os imóveis com URL mostram o tour.

**A fazer (melhoria):** trocar o "botão que abre em nova aba" por um **player 360 embutido na página**
(iframe Matterport, ou `pannellum` p/ foto 360 própria) — "passeio" dentro do próprio site (mais tempo na página + SEO).
Para fotos 360 hospedadas por nós: usar Pannellum (1 arquivo, grátis) lendo a imagem de `/assets/...`.

═══════════════════════════════════════════════════════════════════════
## PARTE 5 — ROADMAP (degrau a degrau, do mais alto retorno)
═══════════════════════════════════════════════════════════════════════
- **A)** Pixels + conversões (Meta Pixel + Google gtag + evento no "deixou contato"). → liga os ads ao site.
- **B)** Tour 360° embutido (Pannellum/iframe) na página do imóvel. → "passeio" por imóvel.
- **C)** Priscila cadastra mais imóveis (conteúdo) + começa o Instagram orgânico.
- **D)** Subir 2 campanhas (Google intenção + Meta "quanto vale"), medir custo/lead, escalar.
- **E)** Depoimentos reais + vídeo da Priscila.
- **F)** Lançar oficial (remover noindex do server.py) quando ela aprovar.

═══════════════════════════════════════════════════════════════════════
## PARTE 6 — COMPACTAÇÃO DO CONTEXTO (passo a passo técnico)
═══════════════════════════════════════════════════════════════════════
**Onde está cada coisa** (detalhe em `docs/skills/*.md`):
- Backend: `/var/www/imobiliaria/` · serviço `systemctl restart imobiliaria` · entrada `server.py` (uvicorn).
- Calculadora: `app/m2_vdc.py` + `app/avaliacao.py` (+ yields em `routes_publicas.py`); teste `python3 /root/treino/teste_calculadora.py`.
- Ana: `app/dispatcher.py` (`_montar_contexto_carteira`, `_sem_markdown`), `app/prompts.py`, `app/clients.py`.
- Admin: `admin/admin.jsx` + `app/routes_admin.py` + `app/visao.py` (foto) + `app/auth.py` (login bcrypt).
- Front: **home** = `v3-editorial/index.html` GERADA de `assets/preview.html`; imóvel/anunciar/mercado direto.
- Simulador: `app/financiamento.py` + `/api/simular-financiamento` + `data/taxas.json`.

**Como publicar mudança na HOME:** editar `assets/preview.html` → rodar o transform python que regenera
`v3-editorial/index.html` (tira barra PREVIEW/noindex, ajusta links, injeta SEO/manifest/SW) → bumpar `pv-shell-vNN` no `sw.js`.

**Lançar no Google:** remover a linha `X-Robots-Tag noindex` global no middleware do `server.py` + restart.

**Regras:** nunca commitar segredo (.env/.db gitignored); nunca push na main (usar branch); valores da Ana
sempre EXATOS; financiamento é SIMULAÇÃO; calculadora calibrada (rodar o teste após mexer).

**Memória persistente:** `/root/.claude/projects/-root/memory/` (site-novo-publicado, admin-priscila-plano, etc.).
