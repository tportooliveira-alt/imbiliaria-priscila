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
7. **👁️ Ana ENXERGA imagem (visão multimodal)** — webhook baixa a mídia
   (`whatsapp.baixar_midia_base64`, Evolution getBase64) e `visao.analisar_para_atendimento`
   (Claude Haiku) descreve no contexto de lead (simulação Caixa, anúncio, foto, documento), sem
   inventar. Event-driven/barato, fallback total. **Resolveu a maior perda real** (Jorge/Ane
   esfriavam com "[mídia recebida]"). Testado em foto real. Doc: `DEGRAU-ANA-VISAO.md`.

## 🔒 Segurança endurecida (tarde 17/06)
Avaliação de risco completa + correções (tudo sem derrubar o site):
1. **MCP de escrita trancado** — Basic Auth no nginx (user `cowork` + senha). Antes era só a
   URL-segredo. `MCP_WRITE_ENABLED=1` agora exige login. Htpasswd em `/etc/nginx/.htpasswd-mcp`.
   → o cowork precisa da URL com credencial: `https://cowork:<senha>@.../mcp-bLFsLPlqXg...`
2. **Backup diário do banco** — `scripts/backup_db.py` (sqlite .backup + rotação 14 dias) via
   `/etc/cron.d/imobiliaria-backup` (03:30, roda como priscila). Pasta `backups/` (gitignored).
3. **SSH endurecido** — `PasswordAuthentication no` + `PermitRootLogin prohibit-password` no
   `/etc/ssh/sshd_config` (o `Include` da .d NÃO existe nesse host — editar o arquivo principal).
   Seguro: root+ubuntu têm chave SSH (conferido antes).
4. **Conta `priscila` fora do grupo `sudo`** (era inerte; defesa em profundidade).
- **NÃO feito de propósito:** rotacionar a chave do Google (Thiago vetou — Google não libera outra
  fácil, limite de projeto estourado). Ficamos com a chave atual. Ana autônoma (`WHATSAPP_AUTO_REPLY=1`)
  mantida — desligar pararia o produto; decisão de um "modo rascunho" fica pro futuro.

## ✅ QA do site (testado ao vivo, 17/06)
Tudo verde: 9 páginas (precisam de `.html` na URL: `/imovel.html?slug=`, `/agendar-visita.html`…) →
200; 5 APIs de leitura → 200; calculadora (`/api/avaliar-imovel`, campo **`area_util`**, resposta tem
`valor_minimo/valor_maximo`) → ok; **marcar horário ponta a ponta** (lead → agenda interna → Google
Agenda) → ok; Pixel Meta (`27844979038460971`) ligado no front via `assets/analytics.js` + `/api/config`.
Dados de teste sempre limpos depois (não sujar produção).

## 🩺 Raio-x das conversas reais (só observação)
- **Maior perda: Ana não enxerga imagem** (Jorge e Ane esfriaram por isso). → `DEGRAU-ANA-VISAO.md`.
- Ana demorou a entender intenção da Kenia (vender, não comprar).
- Possível resposta dobrada (Jorge recebeu 2 saudações no mesmo minuto) — investigar.
- **Protocolo combinado:** eu observo só leitura; se vir a Ana errar, reporto; o Thiago diz o que
  consertar; só então mexo.

## 🅿️ Parado de propósito (só com tempo + rodadas reais)
- ~~Visão multimodal da Ana~~ → **FEITO 17/06** (ver item 7 acima). Próximo: observar conversas
  reais com imagem e calibrar o prompt da visão se preciso.
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
