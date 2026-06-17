# HANDOFF — 17/06/2026 (sessão Thiago + Claude)

> **Comece por aqui** ao retomar. Resumo do que foi feito hoje, o que está NO AR, o que ficou
> parado de propósito, e onde estão os detalhes. Antecessor: `HANDOFF-16-06.md`.

## ⚠️ Contexto que muda tudo
**A imobiliária está EM PRODUÇÃO REAL** — leads de verdade conversando com a Ana (Ane, Kenia,
Karen, Jorge entraram hoje). Todo `systemctl restart` já vai pro ar. Postura: **conservadora,
aditiva, reversível, confirmar antes de mexer no comportamento da Ana**. (memória: `producao-real-postura`)

## ✅ O que foi feito HOJE (tudo no ar)
1. **Google Agenda LIGADO de verdade** — service account própria, `app/gcal.py` espelha cada
   compromisso no Google Calendar do Thiago (agenda "Imobiliária Priscila"). Chave em
   `secret/gcal-sa.json` (600, fora do git), IDs no `.env`. Testado ponta a ponta. Detalhe:
   `INTEGRACAO-GOOGLE-CALENDAR.md`.
2. **Agenda do site/interna conectada** — `/api/agendar-visita` agora cria o evento na agenda
   (antes só criava lead). **Bug de fuso corrigido**: horário sem timezone agora assume
   **Brasília −03:00** (antes virava UTC, 3h adiantado).
3. **MCP do cowork ampliado → 30 ferramentas** — fotos, correções (lead/imóvel/financeiro/
   depoimento), desativar imóvel (nunca apaga), gerar planilha Excel. Escrita atrás de
   `MCP_WRITE_ENABLED=1` (ligado). Detalhe: `MCP-SERVER.md` / memória `cowork-dashboard-multiapp`.
4. **Memória da Ana — Degrau 1 (ficha viva)** — `app/memoria_lead.py`: ela relê o que já sabe
   do cliente (situação, anotações, o que ele disse) quando ele volta. Sem custo de IA.
5. **Regra "VERDADE COM DISCRIÇÃO"** no prompt — nunca inventa/mente, mas não vaza ficha/rótulos/
   interno; desconversa com elegância e leva pra Priscila.
6. **Regra "contato já conhecido não é lead frio"** — pelo histórico OU pelo que a pessoa diz
   (ex.: "o contrato"), Ana retoma de onde parou e leva pra Priscila, sem rodar script de novato.
   (motivada pelo caso real da Karen.)

## 🩺 Raio-x das conversas reais (só observação)
- **Maior perda: Ana não enxerga imagem** (Jorge e Ane esfriaram por isso). → `DEGRAU-ANA-VISAO.md`.
- Ana demorou a entender intenção da Kenia (vender, não comprar).
- Possível resposta dobrada (Jorge recebeu 2 saudações no mesmo minuto) — investigar.
- **Protocolo combinado:** eu observo só leitura; se vir a Ana errar, reporto; o Thiago diz o que
  consertar; só então mexo.

## 🅿️ Parado de propósito (só com tempo + rodadas reais)
- **Visão multimodal da Ana** → `DEGRAU-ANA-VISAO.md` (usa a chave Claude que já está no `.env`).
- **Memória Degrau 2 (conhecer a fundo)** → `DEGRAU-ANA-MEMORIA-2.md` (destila retrato por IA,
  event-driven; custo recorrente → só depois de validar).
- **`panorama_geral` no MCP** (dashboard num retorno só) — próximo do cowork.

## 🔑 Fatos úteis
- Visita real da **Ane Caroline hoje 17/06 às 14h** (ligação WhatsApp, não presencial).
- App roda como usuário Linux **priscila** (uid 1001) — NÃO dar chown root nos segredos (derruba
  o site). Memória: `imobiliaria-permissoes-servico`.
- Branch: `feat/calibracao-design-skills`. Segredos nunca no git.

## 🧭 Como navegar os docs
Use a skill **`contexto-imobiliaria`** — ela mapeia qual `.md` ler pra cada assunto.
