# ⚔️ PLANO DE ATAQUE — o que as pesquisas mandam fazer (consolidado)

Síntese das 4 pesquisas verificadas (leads/ads · integrações/MCP · 360/vídeo/depoimentos · Instagram/Meta Ads) +
o que já fizemos. **Objetivo: gerar lead e venda, barato.** Ordem por alavancagem. ✅=feito 🔴=alta 🟡=média 🟢=depois.

---

## 🥇 OS 3 QUE DESTRAVAM TUDO (atacar primeiro)
1. **🔴 Pixels / rastreamento** (Meta Pixel + Google Tag/GA4) com conversões nomeadas (calculadora, lead, WhatsApp, visita).
   _Sem isso, anúncio é cego — o algoritmo não otimiza e não dá pra medir retorno._ Precisa: seus IDs.
2. **🔴 Seção de DEPOIMENTOS reais** no site (texto + estrelas). _Pesquisa 360/vídeo: prova social é a alavanca de
   conversão MAIS comprovada (≥20 reviews, média 4,5+). 360/vídeo são "bom ter", não convertem sozinhos._
3. **🔴 Corrigir a oferta** (avaliação grátis ≠ laudo pago) no site e na Ana. _Honestidade = confiança = converte._

## 🌐 MELHORIAS NO SITE (o que a pesquisa pede)
- ✅ **Calculadora gateada por nome+WhatsApp** (ímã de lead) — já no ar.
- ✅ **Pergunta qualificadora** ("prazo de venda" → urgência/score) — já no ar.
- 🔴 **Depoimentos/prova social** (acima) — maior alavancagem comprovada.
- 🟡 **Fotos + descrições fortes** dos imóveis primeiro (mais impacto que tour 360). 360 fica como opção barata.
- 🟡 **Lead magnet "quanto vale meu imóvel" em destaque** (capta VENDEDOR → cresce a carteira). É o motor do volante.
- 🟢 Padronizar botões secundários; aplicar microcopy de confiança (CRECI, "sem compromisso").

## 🔌 MCP / AUTOMAÇÃO (pesquisa de integrações — como o Claude age sozinho)
- 🟡 **Expor a VPS como custom remote MCP server** → o Cowork **age no sistema** (mandar WhatsApp, marcar agenda, deploy),
  conversando comigo. É o caminho oficial e seguro (OAuth, escopos limitados, deny rules). _Plano F._
- 🟡 **Conectar no claude.ai → Settings → Connectors**: Google **Drive** (contratos/fotos), **Gmail** (e-mails de lead),
  **Calendar** (✅ já no Cowork). _Eles NÃO autenticam pela VPS — só pelo claude.ai; depois aparecem no Code._
- 🟡 **WhatsApp: seguir com nossa Evolution direta** (já funciona) exposta pelo nosso MCP. _Os MCP de WhatsApp de
  terceiros são imaturos/arriscados — NÃO usar na conta da Priscila._
- 🟢 **Zapier** como ponte pra apps sem conector nativo (e-mail mkt, CRMs externos) — quando precisar.
- 🟢 **Cowork Rotinas** (resumo de leads de manhã, notícias diárias) — ⚠️ só roda com o PC ligado/app aberto; pra
  automação crítica 24/7, usar **cron/agente na VPS**.

## 📣 CAMPANHA DE ADS (pesquisa de leads)
- ✅ **Calculadora de investimento** (`/ads`) + **keywords marca/site** — já feito.
- 🔴 **Campanha PRINCIPAL = marca/site** (comprar/vender em VDC + avaliação grátis), por-imóvel é complemento.
- 🟡 **Começar pelo Meta** (lead mais barato; o **criativo local é a segmentação** em 2026; geo 5-10 km p/ captar vendedor).
- 🟡 **Meta Ads via Graph API na VPS** (Método 2) — começar SÓ leitura (analisar), depois gerir. Precisa: app Meta + token.
- 🟢 **Google Ads** só se houver volume de busca local; keywords transacionais.
- 🟢 **Dado próprio do CRM** (quem fechou) → lookalike no Meta (a partir de ~150 contatos). É o que mais converte.

## 📸 INSTAGRAM / CONTEÚDO (pesquisa de leads + campanha)
- ✅ **Campanha montada** (`CAMPANHA-INSTAGRAM-PRISCILA.md`): 5 pilares, calendário, 10 carrosséis, plano de crescimento.
- 🟡 **Gerar os 10 carrosséis** (texto+estrutura) e publicar (manual ou **Upload-Post** quando ligar).
- 🟡 **Rotina de notícias diárias** do mercado/VDC (stories).
- 🟢 Otimizar tudo pra **salvar/compartilhar** (sinal nº1 de 2026) e puxar pra calculadora (vira lead).

## ❌ NÃO desperdiçar (mitos derrubados na verificação)
- ❌ Investir pesado em **360/vídeo** esperando conversão — efeito ~1%, "de novidade a norma". Mantém barato.
- ❌ Acreditar em "**X% mais leads** com tour/vídeo" — marketing de fornecedor, sem método.
- ❌ **MCP de WhatsApp de terceiros** na conta de produção — imaturo, risco de ban.
- ❌ Contar com "**cidade pequena tem CPC menor**" — mito, sem evidência.
- ❌ Postar Reel no mesmo dia por "+50% alcance" — falso.

---

## 🎯 ORDEM DE ATAQUE (degrau a degrau, custo baixo)
1. **Pixels** (destrava ads + medição) → precisa seus IDs.
2. **Depoimentos** no site (prova social = maior alavancagem) + **corrigir oferta do laudo**.
3. **Meta Ads** (campanha marca/site, criativo local) — começa pequeno, mede pelo pixel.
4. **Instagram**: gerar carrosséis + rotina de notícias.
5. **MCP**: expor VPS + conectar Drive/Gmail → Claude age sozinho nos 2 lados.
6. **Google Ads / lookalike** conforme volume e CRM crescem.

_Fontes: docs/PESQUISA-LEADS-2026.md, PESQUISA-INTEGRACOES-2026.md, PESQUISA-360-VIDEO-DEPOIMENTOS.md,
INTEGRACOES-INSTAGRAM-METAADS.md. Detalhe operacional: PLANO-AMANHA-15-06.md + PENDENCIAS.md._
