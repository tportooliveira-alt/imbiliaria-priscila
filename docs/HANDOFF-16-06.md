# 🤝 HANDOFF — estado do projeto (16/06/2026, madrugada)

Documento de **contexto compactado** pro próximo agente. Leia ISTO primeiro (resume a sessão 15-16/06).
Branch: `feat/calibracao-design-skills` (nunca push na `main`). Tudo commitado e no GitHub.

## 🟢 Estado atual (no ar)
- **Site** `pvscelosimobiliaria.com` (soft-launch, `noindex`): home com **busca-portal** (abas Comprar/Alugar + tipo +
  texto + Buscar), **filtros avançados** (quartos/vagas/preço/área) + **ordenação**, grid de imóveis, **menu sem duplicação**.
- **Empreendimentos**: módulo COMPLETO — admin (ficha técnica rica: 12 campos + lazer/diferenciais checklist + tipologias
  + galeria) e páginas públicas (listagem com filtro de status, detalhe com ficha/chips/vídeo/tipologias).
- **Ana** (atendimento WhatsApp) + **João** (agenda) no ar. **Webhook autenticado** (segredo no path).
- **Voz da Priscila** clonada no ElevenLabs (`ELEVENLABS_VOICE_ID_PRISCILA=m2YLX47J2Ij6MwTI4xwc`) — instantânea,
  **precisa de gravação mais longa** pra ficar fiel (roteiro em `docs/ROTEIRO-VOZ-PRISCILA-LONGO.md`).
- **SQLite em WAL** + busy_timeout (anti-lock). **Backup diário** do CRM ativo. **Postiz desligado** (liberou RAM).
- **MCP da VPS** no ar (PC lê o sistema). **Ponte SSH** PC↔VPS ativa.

## ✅ Feito nesta sessão (commits principais)
- Segurança: webhook auth, ChromaDB/motor_ia fechados, HSTS, `DEV_OPEN_ADMIN` só localhost, chmods.
- Infra: Postiz off, backup CRM, **WAL+busy_timeout**, rota duplicada removida.
- Funil: aviso de lead quente no WhatsApp da Priscila, mensagem do vendedor.
- Site: busca-portal + filtros + ordenação + dedup de menu + empreendimentos rico.
- **Plugin Cowork** `imobiliaria-priscila` (6 skills): orquestrar-com-ia, priscila-contexto, gerar-carrossel,
  carrossel-noticias, rotina-conteudo-diario, **design-priscila** (sistema de design: tokens 8pt, type scale, checklist).
- Docs: ESTUDO-PROJETO-360, ESTUDO-ARQUITETURA, ESTUDO-ANTHROPIC-AGENTES, PLANO-ORQUESTRACAO-EMPRESA,
  GANHOS-DOS-ESTUDOS, DESIGN-BRIEF-FIGMA, CARROSSEIS-INSTAGRAM, VOZ-PRISCILA-ELEVENLABS, ROTEIRO-VOZ-PRISCILA-LONGO.

## 🔬 Pesquisas em background (16/06 ~04:30)
- `w90xuv68s` — deep-research **arquitetura de design** (sites imobiliários, design systems).
- `wg9yzg74o` — deep-research **skills de design no GitHub**.
- _STATUS: rodando quando este doc foi escrito. Resultados (ou falha) serão anexados abaixo ao terminarem._
  ⚠️ A deep-research de notícias FALHOU antes (erro `StructuredOutput` na síntese) — risco de estas falharem igual.

<!-- RESULTADO-PESQUISAS: preencher ao terminar -->

## 🔜 PENDENTE (pro próximo agente / Thiago)
**Quick wins de arquitetura (do `ESTUDO-ARQUITETURA.md`) — faltam 3:**
- #3 **Consertar 9 testes falhando** (isolar env no `tests/conftest.py` — limpar chaves). ⚠️ a suíte completa é LENTA
  headless (timeout); rodar por arquivo. Falham por *env leakage* (`.env` real carregado), não por bug de lógica.
- #4 Rodar `pytest`/`py_compile` no `deploy.sh` antes do restart.
- #5 Limpar código morto: `FUNIL_COUNTER`/`funnel_summary` (`lead.py`), `detalhe_por_id` hasattr (`routes_admin.py`),
  `CORS_ORIGINS` não-lido, `.bak` no diretório. + `datetime.utcnow()`→`timezone.utc` (279 warnings).
**Design (Thiago adiou pra "amanhã"):**
- Aplicar a skill `design-priscila` no `preview.html` (padronizar espaços/type scale) — PRECISA de print do que está
  "desordenado" (não mexer às cegas). Fundação (tokens no `:root`) já aplicada.
- Figma: via PC-Claude (brief em `DESIGN-BRIEF-FIGMA.md`).
**Voz:** Priscila grava o roteiro LONGO → refazer clone (fica fiel).
**Mapa (Google Maps):** precisa da chave do Google Maps + decidir pin exato vs por bairro.
**Marketing:** 1ª campanha Meta (`CAMPANHA-META-1.md`), GA4 ID, depoimentos reais, gerar carrosséis, trocar senha do Facebook.

## 🔑 Fatos que o próximo agente precisa saber
- Webhook WhatsApp = `/api/whatsapp/webhook/<EVOLUTION_WEBHOOK_TOKEN>` (a rota sem token REJEITA). Token no `.env`.
- Empreendimento: `status_obra` ∈ {na_planta, em_obras, pronto}; `lazer`/`diferenciais` são JSON arrays.
- Front da home é GERADO: editar `assets/preview.html` → rodar `scripts/build_home.py` → vira `v3-editorial/index.html`.
- Admin é React/Babel no navegador (validar com `npx esbuild admin/admin.jsx`); bumpar `?v=` em `admin/index.html`.
- Páginas em `v3-editorial/` são servidas direto (sem build).
