# 🧭 ROTA DE RETOMADA — quando formos "ligar pra valer" e medir retorno

Âncora pra próxima sessão. Onde paramos (14/06/2026) e a ordem do que fazer pra **gerar lead, vender e medir o retorno (ROI)**.

## ✅ Estado atual (pronto e no ar)
- **Site** moderno no ar (soft-launch, `noindex` global até a Priscila aprovar). Home leve, imóvel-primeiro, **CTAs de conversão em dourado** (marca), hero menor no mobile.
- **Calculadora de avaliação** calibrada (1.016 anúncios OLX) e **gateada por nome+WhatsApp** → vira lead no CRM.
- **/anunciar** (captação de vendedor), **/mercado** (panorama Chart.js), **simulador** com bancos, **360°** por imóvel.
- **Admin → Financeiro**: dashboard NOVO com gráficos (fluxo de caixa 12m, comissões por status, despesas por categoria) + **pipeline real da carteira** (VGV R$ 4.836.500 / comissão potencial R$ 290.190). Falta **lançar os dados reais** (despesas + vendas).
- **Pesquisa de leads/ads** concluída → `docs/PESQUISA-LEADS-2026.md`.

## 🎯 ORDEM quando retomarmos (alavancagem ↓)

### Degrau 1 — MEDIR (pré-requisito de tudo) 🔴
- **Instalar rastreamento/pixels**: Meta Pixel + Google Tag (GA4).
- Marcar **conversões nomeadas**: `calculadora_concluida`, `lead_anunciar`, `clique_whatsapp`, `agendar_visita`.
- _Sem isso, anúncio é cego — o algoritmo não otimiza e não dá pra medir retorno._

### Degrau 2 — QUALIFICAR o lead
- Adicionar **1 pergunta qualificadora** na calculadora gateada: "É pra morar ou investir?" / "Pretende vender em quanto tempo?".
- Ligar essa resposta ao **BANT da Ana** (já existe score de lead).

### Degrau 3 — FINANCEIRO vivo (medir retorno de verdade)
- Lançar **despesas reais** (VPS, domínio, anúncios, APIs de IA, CRECI, combustível) em Admin→Contas.
- Lançar **comissões** quando houver venda → o fluxo de caixa e o ROI dos ads aparecem no dashboard.
- (Opcional) cruzar gasto de ads (Contas) × leads gerados (CRM) = **CPL real local**.

### Degrau 4 — ATRAIR (tráfego)
- **1º teste Meta Ads**: criativo local + dor ("Quanto vale seu imóvel em VDC?"), geo 5-10 km p/ vendedor, orçamento pequeno.
- **Instagram orgânico**: posts salváveis (guia de bairros, "m² no seu bairro" — usar dados que já temos).
- **Google Ads** só depois, se houver volume de busca local (keywords transacionais).

### Degrau 5 — LANÇAR oficial
- Remover `noindex` do `server.py` quando a Priscila aprovar (sai no Google).
- Acumular **~150 clientes fechados** no CRM → lookalike value-based no Meta (o que mais converte).

## 📌 Pendências menores (quando der)
- 3ª da crítica de design: padronizar botões secundários (consistência total). *(o principal — CTA dourado — já foi.)*
- Calculadora DEGRAU 2: Método Evolutivo (CUB/BA + Ross-Heidecke) p/ casas de alto padrão.
- Pesquisa dedicada: impacto de **360°/vídeo/depoimentos** na conversão (ficou subcoberto).
- Resposta automática do WhatsApp (teste → produção) e Meta Lead Ads → funil.

## 🔑 Acessos / como retomar
- Admin: `pvscelosimobiliaria.com/admin/` · login `tportooliveira@gmail.com` / `233024` (senha temp.).
- Deploy home: editar `assets/preview.html` → regenerar `v3-editorial/index.html` (script no histórico).
- Git: branch `feat/calibracao-design-skills` (último commit da sessão: pesquisa + financeiro).
- Guia geral: `CLAUDE.md` (regras de ouro + ferramentas/plugins).
