# 🧠 HANDOFF / CÉREBRO ATIVO — 18/06/2026

> **Comece por aqui** ao retomar. Registro do que foi feito, as DECISÕES e o estado atual.
> Antecessor: `HANDOFF-17-06.md`. Estado vivo dos dados → chamar `panorama_geral` no MCP.

## ⚠️ Contexto que vale ouro
- **PRODUÇÃO REAL** (clientes de verdade com a Ana). Conservador, aditivo, **confirmar antes**, todo restart vai pro ar.
- **Regra de comportamento (lição de hoje):** VERIFICAR de verdade antes de reportar; CONFIRMAR antes
  de executar (infra/segurança/dado). Nada de "soar alarme" sem checar. (memória `verificar-antes-de-falar`)

## 🔧 ROBUSTEZ DA ANA — sessão 18/06 NOITE (o MAIS RECENTE, leia primeiro)

### Disciplina / organização (feito)
- **Karpathy agora é GLOBAL** → `~/.claude/CLAUDE.md` (vale pra TODO projeto, sempre ligado).
- **ECC desinstalado do global** → vira **referência** só (`/root/everything-claude-code`); como/quando
  puxar em `docs/REFERENCIA-ECC.md`. 4 agentes ECC soltos no projeto → removidos. (commit `8040707`)
- **Skill global nova:** `~/.claude/skills/disciplina-de-trabalho/SKILL.md` — o "como eu trabalho"
  (5 protocolos, cada um com o erro real que ensinou). Produzida com 2 agentes (1 estudou o projeto,
  1 revisou). É o **como**; a `contexto-imobiliaria` é o **onde** (não duplicam).

### Diagnóstico read-only das conversas reais (14 leads, 139 msgs)
- **R1 (resposta dobrada + re-saudação) JÁ ESTAVA FEITO** (commit `fec68e3`, no ar 17/06 17:55):
  idempotência + debounce no webhook + regra "não se reapresentar". As dobras na base são de ANTES disso.
- **🚨 CAPTAÇÃO tratada como lead frio (grave):** a 🍀 ("Priscila... amiga", "tenho casas prontas") foi
  tratada como compradora — Ana disse "acho que me confundiu" e saiu qualificando. Contato/parceiro que
  OFERECE imóvel é OURO, não lead frio.
- **🚨 VISÃO NUNCA FUNCIONOU:** 0 de 28 imagens descritas — todas ficaram em "[mídia recebida]". Causa:
  `whatsapp.baixar_midia_base64` volta vazio CALADO (download da Evolution falha; o `except` engolia o
  erro). **Não é o leitor (Claude vê bem) — é o download que não acontece.**
- **Suspeita @lid:** o webhook descarta remetente cujo número não tem 10-15 dígitos (linha 697) — contato
  via `@lid` do WhatsApp some calado. Pode ser por que mensagem do contato "some". (a confirmar pelo log)
- Observação: vários leads `temperatura=quente` mas `score=0` (desencontro a investigar).

### Subido HOJE (deploy — `verificar.sh` verde: 38 testes + site 200 + Ana não-fallback; restart OK)
1. **`app/prompts.py` — regra de CAPTAÇÃO:** acolhe, NÃO trata como lead frio, pede FOTOS + descrição
   curta de cada imóvel (bairro/quartos/metragem/valor), adianta pra Priscila e o cadastro.
   ✅ **Testada ao vivo** — Ana respondeu certinho ("a Priscila vai adorar... me manda as fotos...").
2. **`app/routes_publicas.py` — log `[DIAG-LID]` (TEMPORÁRIO):** grava jid cru + nome + texto de toda
   mensagem descartada por "não é telefone". Pra pegar contato via @lid.
3. **`app/whatsapp.py` — log `[DIAG-MIDIA]` (TEMPORÁRIO):** grava o erro real do download da Evolution.
   Pra descobrir por que a visão falha.

### DECISÃO de design (dono concordou — "você está certo")
**O gargalo da visão é o DOWNLOAD, não o leitor.** NÃO adicionar serviço/agente externo de imagem agora.
Degraus: (1) próximo upload cai no `[DIAG-MIDIA]` → conserto o download (Ana passa a enxergar);
(2) captação usa visão **Sonnet** (descrição mais rica, troca de 1 linha); (3) só depois, um agente
"montador de cadastro" (fotos+descrição → ficha pronta pra Priscila).

### 🔜 Próximo (a fazer)
- [ ] Esperar a próxima imagem/contato cair nos logs `[DIAG-MIDIA]`/`[DIAG-LID]` → consertar o download
  da Evolution e o caso @lid.
- [ ] **REMOVER os 2 logs temporários** depois de diagnosticar (não deixar no ar pra sempre).
- [ ] Captação: subir visão Haiku→Sonnet.
- [ ] "Colocar na MCP" (pedido do dono, pendente) — definir o quê: tag `contato_priscila`? captação no panorama?
- [ ] Investigar `score=0` vs `temperatura=quente`.

## ✅ O que foi feito nesta sessão (17→18/06)
1. **👁️ Ana enxerga imagem** (visão multimodal, Claude Haiku) — baixa a mídia + descreve no contexto de
   lead, sem inventar. `app/visao.py` + `whatsapp.baixar_midia_base64` + webhook.
2. **🧠 Memória + persona da Ana:** ficha viva (`app/memoria_lead.py`), regra "verdade com discrição",
   regra "contato conhecido não é lead frio", "não se reapresentar a cada mensagem". Correção da
   **resposta dobrada** (debounce + idempotência no webhook).
3. **🩹 Admin TELA BRANCA — consertado.** Causa: o **Babel 8** (CDN "latest") parou de transformar JSX.
   Fix: `admin/index.html` pinado em `@babel/standalone@7.24.7` + `data-presets="react"`. Também pinei
   **chart.js@4.4.1** (mercado + calculadora-ads). **CDN SEMPRE com @versão.**
4. **🔐 Biometria (passkey/WebAuthn) + 2FA por e-mail no admin** — `app/passkey.py`, `app/email_util.py`,
   endpoints em `routes_admin.py`, UI em `admin.jsx` ("Entrar com digital/rosto" + "Ativar biometria").
   Gated/aditivo (login por senha intacto). Testado **fim-a-fim com autenticador virtual** (cadastro+login OK).
   Bugs corrigidos: `user["id"]`→`user["sub"]`; origin aceita **www e sem-www**.
   ⏳ Falta: a Priscila **cadastrar a biometria 1x** (clicar "Ativar biometria"); 2FA e-mail só liga com
   `ADMIN_2FA_ENABLED=1` + senha de app do Gmail.
5. **🔌 MCP ampliado e blindado:** + `panorama_geral` (raio-x central) + conversas da Ana
   (`listar_conversas_ia`, `detalhar_conversa_ia`, `metricas_ia`) → **17 ferramentas de leitura**.
   Resiliência: `Restart=always` + auto-recupera (testado matando o processo, voltou em ~3s).
6. **🛡️ Segurança:** SSH endurecido (senha off, root só por chave), backup diário do banco (cron),
   conta `priscila` fora do sudo. (detalhes em `HANDOFF-17-06.md`)
7. **🧭 Contexto pro cowork:** `CLAUDE.md` atualizado (comece por panorama+handoff+skill, 30 ferramentas,
   produção real, pin do babel) · `CENTRO-MARCA-MARKETING.md` (marca/persona/Instagram/marketing) ·
   `GOOGLE-ADS-SETUP.md` (setup + as confirmações). Skill `contexto-imobiliaria` mapeia os docs.
8. **💾 Backup:** banco enviado pro PC do Thiago; tudo no GitHub (sem segredo).

## 🧭 DECISÕES tomadas (registradas)
- **MCP = só-leitura + SEM senha.** Motivo: o conector do app claude.ai só faz OAuth ou sem-auth — Basic
  Auth quebrava. Read-only protege (vazou o link = só lê). **Escrita liga sob demanda** quando precisar corrigir.
- **Postiz roda no PC, não na VPS** (pesa ~1.3 GB; VPS tem ~1.7 GB livre, esmaga o site). Prompt: `PROMPT-COWORK-POSTIZ.md`.
- **Instagram = @priscilavasconcelosvca** (precisa ser Business + Página do Facebook pra publicar via Postiz).
- **Google Ads:** site pronto (GA4 liga sozinho); falta GA4 ID + **verificação do anunciante** (dono faz, demora dias).
- **Link "Painel da corretora" fica na home** (Priscila quer). Não é furo — admin tem login.
- **Não rotacionar a chave do Google** (Thiago vetou — limite de projeto estourado).
- **Fotos foram pro git** (via git add -A) — não é segredo (públicas no site); Thiago já tem cópia local.

## 📊 Estado atual (18/06 ~01h)
- Serviços `imobiliaria` (always) + `imobiliaria-mcp` (always, auto-recupera) → **active**. Site **200**.
- Dados: **13 leads · 6 imóveis · 5 empreendimentos · 7 conversas**.
- MCP: 17 ferramentas leitura, sem senha, read-only, dados frescos. URL:
  `https://pvscelosimobiliaria.com/mcp-bLFsLPlqXgJt1itB2vr3tpIseITl8F8Q`

## 🛠️ Feito autônomo (18/06 madrugada, sem o dono)
- **Checagem dos 5 empreendimentos:** todos têm foto + descrição + bairro, mas **NENHUM tem
  tipologia/preço** cadastrado → no site aparecem sem valores. (ação do dono abaixo)
- **Carrossel 1 pronto:** `docs/CARROSSEL-1-MAISON-BORDEAUX.md` — pacote completo (8 slides + legenda,
  dado real, identidade da marca) pro cowork gerar no PC. Sem preço (não cadastrado).

## 🔲 Pendente / ação do dono
- **Cadastrar tipologias/preços** dos 5 empreendimentos no admin (hoje aparecem sem valor no site).
- **Reconectar o cowork** no claude.ai (remover → adicionar com a URL limpa acima). 1x.
- **`git pull`** no PC (pega CLAUDE.md/contexto novo).
- **Cadastrar a biometria** no admin (Priscila, 1 clique).
- **GA4 ID** (manda → eu ligo) + **verificação do anunciante** no Google Ads.
- **Postiz no PC** + conectar Instagram/Facebook.
- (opcional) trocar a senha admin `233024` — ou usar a biometria.

## 🅿️ Parado de propósito (só com tempo + rodadas reais)
- Memória Degrau 2 da Ana (retrato que acumula) → `DEGRAU-ANA-MEMORIA-2.md`.
- Escrita do MCP (liga sob demanda).
- Carrosséis: o cowork gera no PC com `CENTRO-MARCA-MARKETING.md` + dados do MCP.

## 🗑️ Limpeza de docs (18/06) — APAGUEI estes (superados; git guarda o histórico)
Pra não atrapalhar (só ficou o que tem qualidade/é atual). Apaguei porque viraram os handoffs/CLAUDE.md:
`PLANO-AMANHA-15-06.md`, `PLANO-AMANHA-16-06.md` (planos de dias passados) · `RESUMO-SESSAO-15-06-NOITE.md`
(resumo antigo) · `FEITO.md`, `FALTA.md`, `PENDENCIAS.md`, `ROTA-PROXIMA.md`, `QUEBRA-CABECA.md`
(snapshots de status → substituídos por este handoff) · `GANHOS-DOS-ESTUDOS.md` (balanço antigo) ·
`HANDOFF-16-06.md` (substituído por 17 e 18). De 56 docs → **46**.
