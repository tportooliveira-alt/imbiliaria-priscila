# 🔜 O QUE FALTA FAZER (prioridade) — 15/06/2026

Detalhe completo em `PENDENCIAS.md`. Aqui o essencial, em ordem de impacto.
**Frase-chave:** o MOTOR está pronto (Ana, João, calculadora, MCP). Falta o **COMBUSTÍVEL: leads reais** → vêm dos ads.

## 🔴 AGORA (encher o funil) — precisa do Thiago
1. **Ligar os PIXELS** — pegar os 2 IDs:
   - **Meta Pixel ID** (business.facebook.com → Gerenciador de Eventos → criar conjunto "Site Priscila" → copiar o ID)
   - **GA4 ID** (analytics.google.com → Admin → Fluxos de dados → `G-XXXXX`) — opcional, pode depois
   - → manda os números pro Claude colocar no `.env` (a infra já está pronta).
2. **1ª campanha de ads** (Meta + Google) — precisa da conta de anúncios + orçamento. Usar a calculadora `/ads` pra decidir o valor.
3. **Coletar depoimentos reais** (a Priscila pede aos clientes; textos prontos em `PEDIR-DEPOIMENTOS.md`). Indicação converte 10-20× mais.

## 🟡 EM SEGUIDA (eu faço, alguns precisam do Thiago)
4. **Postiz na VPS** (postar Instagram/Facebook) — eu instalo (Docker); o Thiago conecta as contas (IG Business + Página FB).
5. **Gerar os 10 carrosséis** do Instagram (eu faço o conteúdo).
6. **Lembrete automático de visita** (24h/2h antes) — eu monto.
7. **Ligar o follow-up de lead morno** (`FOLLOWUP_ENABLED=1`) quando houver leads REAIS.
8. **Meta Ads via Graph API** (analisar campanhas na VPS) — precisa do token Meta.

## 🟢 DEPOIS (com dados / aprovação)
9. **Painel de funil** no admin (leads por etapa, gargalo) — depois do pixel coletar.
10. **Recalibrar a calculadora** com nossos números reais (a cada venda + pixel, 60-90 dias).
11. **Remover `noindex`** (lançar oficial no Google) quando a Priscila aprovar.
12. **Trocar a senha temporária** do admin · **Calculadora degrau 2** (alto padrão) · blog/SEO.

## ⚠️ Segurança / housekeeping
- Trocar a **senha do Facebook** (foi exposta no chat).
- Tokens/segredos sempre no `.env` (fora do git).
- Leads inválidos (ID de grupo) — o webhook novo já filtra; CRM foi limpo.
