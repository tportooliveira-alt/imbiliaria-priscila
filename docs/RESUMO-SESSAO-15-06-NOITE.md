# 📋 RESUMO DA SESSÃO — 15/06/2026 (noite)

Tudo no ar e no git (branch `feat/calibracao-design-skills`). Resumo do que foi feito, com o que ainda depende de você/Priscila.

## ✅ FEITO (e verificado)

### 🔒 Segurança + alívio da VPS (urgentes do estudo)
- **Postiz desligado** — estava caído (precisa de Elasticsearch, não cabe na VPS) consumindo ~910 MB. Swap caiu de 1,7 Gi → ~0,9 Gi. VPS leve. Dados preservados (volumes).
- **Webhook do WhatsApp blindado** — estava SEM senha (qualquer um forjava mensagem/lead, disparava IA paga, podia mexer na agenda da Priscila). Agora usa **segredo no path** (`/api/whatsapp/webhook/<token>`); Evolution reapontado; testado (rota antiga rejeita, token errado 401, certo 200). Ana/João intactos.
- **Backup diário automático do CRM** — `site.db` tinha só 1 cópia manual. Agora timer systemd diário (06:30 BRT) com rotação 14 dias. Já rodou.
- **Hardening extra:** HSTS no nginx (ativo), `data/site.db` 640, `.env.BAK` 600, bypass `DEV_OPEN_ADMIN` só de localhost.
- **ChromaDB (8000) + motor_ia (8080)** que estavam abertos pra internet → fechados em 127.0.0.1.

### 🌐 Site — ajustes que a Priscila pediu (vídeo/Gemini)
- **Menu em CAIXA ALTA** + adicionada aba **EMPREENDIMENTOS** + **A ANA** (mantida).
- **"Como funciona"** reescrito sem o nome "Ana" no corpo: Descreva / **Filtra** / Você visita / **Fechamento** (textos exatos que ela ditou).
- **Mensagem do vendedor** trocada: tirei o "te chama em até 24h" (soava lento) por algo honesto e acolhedor.
- **Aviso no lead quente:** quando um lead esquenta, o sistema agora **avisa a Priscila no WhatsApp na hora** (alavanca nº1 — antes ela só via abrindo o painel).

### 🧠 Estudos + skill
- **Estudo 360° do projeto** (4 frentes: segurança, agentes IA, negócio/funil, infra) → `ESTUDO-PROJETO-360.md`.
- **Estudo do material da Anthropic** (looping/agent loop + 5 padrões aplicados ao nosso sistema) → `ESTUDO-ANTHROPIC-AGENTES.md`.
- **Deep-research "orquestrar a empresa com IA"** (108 agentes) → virou plano: `PLANO-ORQUESTRACAO-EMPRESA.md` (tarefas por ROI + roadmap + fontes).
- **Skill nova** `orquestrar-com-ia` — nosso playbook reutilizável (quando usar workflow vs agente, gate de custo, model tiering Sonnet/Opus, travas anti-alucinação). Versionada no git e ativa.
- **10 carrosséis prontos** pro Instagram → `CARROSSEIS-INSTAGRAM.md`.

## ⏳ DEPENDE DE VOCÊ / PRISCILA (não dá pra eu fazer sozinho)
1. 🖼️ **Logo nova** do site — me manda o arquivo que eu troco.
2. 🏢 **Página/seção "EMPREENDIMENTOS"** — a aba já está no menu, mas aponta provisoriamente pra lista de imóveis. Precisa de conteúdo (quais empreendimentos) pra virar uma página de verdade.
3. 🔎 **Busca como filtro direto** (ela pediu) — hoje a busca manda pra Ana (IA). Mudar pra filtro instantâneo é uma feature; me confirma se quer **trocar** ou **ter os dois** (IA + filtro).
4. 💰 **"Laudo/avaliação grátis"** — é decisão de negócio: a avaliação presencial da Priscila é grátis ou paga? Não mexi pra não errar. Me diz a política.
5. 📊 **GA4** (pixel do Google) — falta o ID. Meta Pixel já está ligado.
6. 🔐 **Trocar a senha do Facebook** (foi exposta numa conversa anterior).
7. 📣 **Subir a 1ª campanha Meta** (pronta em `CAMPANHA-META-1.md`) — precisa da conta de anúncios + orçamento.
8. 🗣️ **3-4 depoimentos reais** (textos prontos em `PEDIR-DEPOIMENTOS.md`) — a alavanca de 10-20×.
9. 🖼️ Os carrosséis com `[PREENCHER]` (Candeias, m² por bairro) esperam dado real de VDC.

## 🗺️ Próximo (quando você quiser)
Seguir o **roadmap** do `PLANO-ORQUESTRACAO-EMPRESA.md` — degrau a degrau, barato primeiro: medição + caching → guard-rail da Ana → combustível (campanha + depoimentos) → conteúdo automatizado → pesquisa de mercado com multi-agente.
