# 🔬 ESTUDO 360° DO PROJETO — revisão aprofundada (15/06/2026)

Revisão multi-especialista (4 frentes: Segurança · Agentes de IA · Negócio/Funil · Infra/Custo). A 5ª frente
(Arquitetura/código) ficou pendente (interrompida) → **TODO amanhã**. Tudo read-only; nada foi alterado por este estudo.

> **Veredito honesto:** a engenharia está ACIMA DA MÉDIA pra uma corretora solo (Ana, calculadora calibrada, CRM,
> pixel, MCP). O que falta **não é mais sistema** — é (a) tapar poucos vazamentos baratos, (b) ligar medição que já está
> 80% pronta, (c) pôr combustível (campanha + depoimentos), e (d) **aliviar a VPS** (que já sofreu 1 OOM este mês).

---

## 🔴 OS 2 ITENS URGENTES (fazer primeiro)

### 1. Webhook do WhatsApp SEM autenticação (segurança)
`app/routes_publicas.py:628` — o `POST /api/whatsapp/webhook` está exposto na internet e **não valida** o
`EVOLUTION_WEBHOOK_TOKEN` (apesar do docstring dizer que valida). Consequências:
- Qualquer um que saiba a URL pode **forjar mensagens** → criar leads falsos, e com `WHATSAPP_AUTO_REPLY=1` **dispara a IA
  paga** (custo + risco de ban da conta da Priscila).
- **Escalada:** o "João" identifica a Priscila **só pelo número do remetente** (que vem no payload, forjável) → um atacante
  pode **escrever/alterar a agenda real dela**.
- **Correção:** validar segredo no início do handler — de preferência **secret-no-path** (`/api/whatsapp/webhook/<TOKEN>`,
  igual ao MCP) já que o header do Evolution é instável. Fecha o risco do webhook E do João de uma vez.

### 2. Postiz CAÍDO consumindo ~910 MB numa VPS que já deu OOM (recurso)
- A VPS tem 3,8 Gi RAM, **só ~1 Gi livre, swap 43% cheio**, e **já houve OOM-kill em 02/jun** (kernel matou processo de 2,6 GB).
- O **Postiz não funciona** (backend caído por falta de Temporal/Elasticsearch) e mesmo assim ocupa **~910 MB (¼ da máquina)**.
- **Correção (alinhada ao "trabalhar mais leve"):** `docker stop` + `docker update --restart=no` nos 3 containers do Postiz →
  **libera ~910 MB na hora**, sai do regime de swap. Decidir depois: versão leve do Postiz **ou** Metricool (nuvem, zero VPS).

---

## 🔐 SEGURANÇA — resumo
**Base boa:** bcrypt+JWT (TTL 8h), rate-limit no login, ~50 rotas admin/CRM com `Depends(requer_admin)`, **SQL 100%
parametrizado**, Pydantic forte, CSP completa, serviços internos presos em 127.0.0.1, nenhum segredo hardcoded ou servido. ✅

**Achados (além do webhook 🔴):**
- 🟠 `DEV_OPEN_ADMIN` (`routes_admin.py:96`) — flag que faz login aceitar qualquer senha. Hoje OFF, mas é porta-dos-fundos a
  um `export` de distância → **remover do código** (ou travar a 127.0.0.1).
- 🟠 nginx **sem HSTS** → adicionar `Strict-Transport-Security` no bloco 443.
- 🟡 `.env.BAK-20260601` está **644 (world-readable)** com segredos antigos → `chmod 600` ou apagar (+rotacionar se as chaves ainda valem).
- 🟡 **Sem rate-limit** nos endpoints públicos de escrita e no `/api/chat` (IA paga) → limitar por IP (reusar `login_attempts` ou nginx `limit_req`).
- 🟡 `data/site.db` está **644** (PII de clientes/LGPD) → `chmod 640` + `data/` `750`.
- 🟡 Postiz cadastro aberto (`DISABLE_REGISTRATION=false`) — some se desligarmos o Postiz.

## 🤖 AGENTES DE IA — resumo
- **Ana** (cliente): prompt excelente (anti-invenção forte, BANT, 3ª pessoa, opt-out, teto diário). **Risco nº1: a trava
  anti-alucinação é SÓ no prompt**, não há validação de código que confira imóvel/preço citado contra o DB (agravado na
  rota INFO_VDC que usa Google Search). → **guard-rail pós-resposta** (extrair preços/nomes e checar no DB antes de enviar).
- **João** (agenda da Priscila): trava dupla (número + "joão") sólida — cliente **não aciona por engano**. Fragilidades:
  match por "últimos 8 dígitos" tem colisão teórica; e o spoofing via webhook aberto (ver 🔴). Ele **não** se passa pela Priscila. ✅
- **Follow-up:** filtros muito bons (empresa, telefone real, opt-out, máx 3, cap diário, gate `FOLLOWUP_ENABLED`). Spam improvável.
  ⚠️ O **timer nem está instalado** neste host → roda só pelo painel.
- **MCP:** escrita só existe com `MCP_WRITE_ENABLED=1` (off por padrão) — as tools nem são registradas. Seguro. ✅
- **Custo:** sem **prompt caching** — carteira+ficha inteira reenviada a cada turno (Sonnet na negociação). → ligar cache da Anthropic.

## 📈 NEGÓCIO / FUNIL — resumo
**Já gera valor:** Ana instantânea (alavanca nº1, no ar), calculadora de avaliação (ímã de vendedor), CRM com
score/temperatura + `eventos_funil`, **pixel Meta JÁ ligado** (vários docs estão desatualizados dizendo que falta), calculadora `/ads` honesta.

**3 vazamentos BARATOS de tapar (alto retorno):**
1. **Promessa contradiz a tese:** o lead de vendedor (o mais valioso, ~R$60k) recebe *"a Priscila te chama em 24h"*
   (`routes_publicas.py:487`) — justo ele não pega a resposta instantânea. → Ana atende o vendedor na hora também.
2. **Bug de honestidade ainda no ar:** `anunciar.html:154/159` promete *"avaliação final gratuita feita pela Priscila"* →
   a online é grátis (ímã), o **laudo CRECI é pago**. (decisão já documentada, **não aplicada**).
3. **Handoff não notifica a Priscila:** quando o lead esquenta/pede humano, **nenhum código pinga o WhatsApp dela** — o lead
   quente pode esfriar na fila do admin. → notificar a Priscila no evento "quente" (infra Evolution já existe). **Altíssimo impacto.**

**Medição 80% pronta:** só `lead_anunciar` dispara; faltam `clique_whatsapp`, `calculadora_concluida`, `agendar_visita`
(o `window.track` já existe em `analytics.js`, falta só chamar nos CTAs). **GA4 vazio.**

**Faltam pra entrar lead real:** campanha rodando (combustível), 3-5 depoimentos reais (alavanca 10-20×, zero hoje),
conteúdo orgânico (carrosséis desenhados, nenhum postado). Site ainda em `noindex` (soft-launch).

**Risco de negócio nº1 = EXPECTATIVA:** ticket R$1mi tem ciclo longo; com R$20-30/dia é normal passar **semanas com 0 venda
e CPL "caro"** antes da 1ª conversão. Disciplina de medir CPL **sem desligar cedo demais** vale mais que otimização de código.

## 🖥️ INFRA / CUSTO — resumo
**Pressão real:** 2,8 Gi/3,8 Gi usados, ~137 Mi livres, **swap 1,3 Gi**, disco 70%. **OOM já ocorreu em 02/jun.**
- **Postiz** = maior peso inútil hoje (~910 MB, caído) → **desligar** (item urgente nº2).
- **Backup do CRM = o ponto mais frágil:** `site.db` tem **só 1 cópia manual** de hoje, **zero automação**. (O Paperclip, em
  contraste, tem backup automático a cada 3h.) → **criar timer diário** `sqlite3 .backup` com rotação 7-14d, idealmente off-site.
- **Disco:** `docker builder prune` recupera ~2,9 GB; backups do Paperclip (2 GB) sem rotação.
- **Containers sem limite de RAM** (evolution, paperclip_postgres, motor_ia, chroma) → o OOM-killer escolhe vítima
  imprevisível. Pôr `mem_limit` e proteger o `imobiliaria` (`oom_score_adj`).
- **followup.timer não instalado** (`deploy/` tem os arquivos prontos) → instalar quando houver leads reais.

---

## ✅ PLANO DE AÇÃO PRIORIZADO (derivado do estudo)
**🔴 Agora (segurança + alívio):** 1) autenticar o webhook (secret-no-path) · 2) desligar o Postiz (libera 910 MB) ·
3) backup automático do `site.db`.
**🟠 Barato e alto retorno:** 4) tapar os 3 vazamentos do funil (promessa 24h, laudo grátis, notificar Priscila no lead quente) ·
5) wirar os 3 eventos de conversão que faltam · 6) `chmod` nos arquivos sensíveis + remover `DEV_OPEN_ADMIN` + HSTS.
**🟡 Combustível:** 7) 3-5 depoimentos reais · 8) 1ª campanha Meta · 9) ligar GA4 · 10) carrosséis.
**🟢 Com dados:** 11) painel de funil (dado interno já existe) · 12) recalibrar CPL com números próprios (60-90d).

_Frente pendente: **revisão de arquitetura/código** (a 5ª, interrompida) — rodar amanhã._
