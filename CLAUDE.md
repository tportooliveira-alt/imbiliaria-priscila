# CLAUDE.md — guia do projeto para o Claude Code

Guia para qualquer sessão de IA que for trabalhar neste repositório. Leia antes de editar.

## O que é
Plataforma da corretora **Priscila Vasconcelos** (Vitória da Conquista-BA): site + IA que
**capta e qualifica leads** e entrega "mastigado" para a Priscila fechar. A IA cliente-facing
se chama **Ana**. Dono/dev: **Thiago** (esposo/sócio); Priscila é a corretora de verdade.

## ▶️ COMECE POR AQUI (contexto automático — não pergunte, já carregue)
Ao abrir este projeto, JÁ tenha o contexto, sem o usuário pedir:
1. **Chame `panorama_geral`** no conector MCP → raio-x ao vivo (leads quentes, agenda de hoje,
   financeiro do mês, pendências). É a **fonte central** — comece sempre por ela.
2. **Leia o HANDOFF mais recente:** `docs/HANDOFF-<data>.md` (o de maior data) → o que está no ar,
   o que ficou parado, fatos do dia.
3. Pra achar o `.md` certo de cada tema, use a skill **`contexto-imobiliaria`** (mapa dos docs).
4. **PRODUÇÃO REAL:** tem cliente de verdade falando com a Ana. Mudança de comportamento da Ana /
   atendimento / dados → conservador, aditivo, **confirmar antes**. Todo restart vai pro ar.

## 🧰 Ferramentas e plugins disponíveis — USAR o que for preciso (não fazer na mão)
- **🔌 Conector MCP "Imobiliária Priscila"** (servidor MCP da VPS, `docs/MCP-SERVER.md`) — **30 ferramentas**, é a
  **fonte central de tudo**. USE SEMPRE, automaticamente, sem o usuário pedir e sem inventar:
  - **Visão geral:** `panorama_geral` (raio-x de tudo numa chamada — comece por ela).
  - **Ler:** `resumo_leads`, `listar_leads`, `detalhar_lead`, `listar_imoveis`, `buscar_imovel`, `imovel_fotos`,
    `agenda_listar`, `agenda_lembretes_pendentes`, `financeiro_resumo`, `listar_comissoes`, `listar_contas`,
    `listar_empreendimentos`, `listar_depoimentos`.
  - **Corrigir/criar** (escrita ligada): `corrigir_lead`, `lead_tag`, `criar_imovel`, `corrigir_imovel`,
    `desativar_imovel` (nunca apaga), `corrigir_foto`/`reordenar_fotos`/`remover_foto`, `criar/corrigir_comissao`,
    `criar_conta`/`marcar_conta_paga`, `criar/corrigir_depoimento`, `agenda_criar`, **`gerar_planilha_priscila`** (Excel).
  - Se a pergunta envolve lead/imóvel/foto/agenda/financeiro, consulte o conector PRIMEIRO. (Conecta com Basic Auth;
    no app do PC aparece como conector conectado.)
- **/deep-research** — workflow multi-agente (busca em paralelo + verifica + sintetiza). Para pesquisa
  profunda (mercado, ads, concorrentes). **Invocável** via `Workflow({name:"deep-research", args})`.
- **Plugin "Design" (Anthropic marketplace):** `/design-system`, `/design-critique`,
  `/accessibility-review`, `/design-handoff`, `/research-synthesis`, `/user-research`.
  ⚠️ Esses NÃO são invocáveis pelo modelo neste harness ("Unknown skill") — **aplicar o MÉTODO** deles
  manualmente ao ajustar design (auditar tokens, criticar hierarquia/usabilidade, a11y, handoff).
- **WebSearch / WebFetch** (pesquisa/leitura), **memória** (`/root/.claude/projects/-root/memory/`),
  **skills do site** (`docs/skills/*.md`), **plano-mestre** (`docs/PLANO-MESTRE.md`).
- Ao mexer em DESIGN, seguir a paleta: navy `#16284B` + dourado `#c9943a` + Playfair/Inter; imóvel-primeiro,
  marca da Priscila destacada, IA discreta. Deploy da home: editar `assets/preview.html` → regenerar `v3-editorial/index.html`.

## ⛔ Regras de ouro (NÃO violar)
1. **NUNCA inventar dado.** A Ana só pode oferecer/afirmar ter imóveis que existem no banco
   (tabela `imoveis`, `ativo=1`) ou números que estão em `data/dados_financeiros.md`. Faltou
   dado → "vou verificar com a Priscila". Inventar imóvel/preço é o pior erro.
2. **Afirmação casa com a pergunta.** Se perguntarem por um bairro/tipo que não temos, a 1ª frase
   nega aquilo ("no Brasil não tenho no momento") e só depois oferece alternativa real.
3. **Modelos válidos** (`claude_local` e API): Sonnet = `claude-sonnet-4-6`,
   Haiku = `claude-haiku-4-5-20251001`. ⚠️ `claude-haiku-4-6` **não existe** — quebra o agente.
4. **Custo importa.** Use o modelo mais barato que resolve (Haiku no volume). O dono é sensível a
   custo: não rode lotes grandes de testes/agentes; teste **≤3 cenários por vez** (degrau em degrau).
5. **Nunca hard-DELETE em `imoveis`.** Use `desativar_imovel` (`ativo=0`). A Priscila cadastra pelo
   admin; não recrie imóvel a partir de anúncio colado (gera duplicado).
6. **Mudanças de rede/infra** (iptables, MTU, firewall) exigem **autorização direta do dono**.
7. **Segredos nunca no git** (`.env`, chaves, `data/`, fotos) — já no `.gitignore`. Não comite.
8. **⏰ FUSO HORÁRIO = Brasília (BRT, UTC-3). CRÍTICO p/ reuniões/agenda.** Os timestamps das mensagens chegam em
   **UTC**; a hora do Thiago é **UTC − 3h** (ex.: 05:58 UTC = **02:58 em Brasília**). SEMPRE converter antes de
   falar/agendar horário. Ao criar lembrete/cron e o runtime estiver em UTC, somar 3h ao horário-Brasília desejado
   (ex.: reunião 9h Brasília = **12:00 UTC**). Nunca marcar reunião no relógio errado.

## Arquitetura (mapa rápido)
- **Conversa com cliente** = motor do site (rápido, barato). Fluxo:
  `router.py` (classifica em 6 rotas) → `dispatcher.py` (monta contexto = carteira real +
  ficha financeira; cascata Gemini→Claude→fallback) → resposta + `lead.py` (score).
- **Persona da Ana:** `app/prompts.py` (`PRISCILA_PERSONA`) — voz, anti-invenção, **BANT**
  (Necessidade/Orçamento/Prazo/Decisão), **estágios** (entender→mostrar imóvel→qualificar→handoff).
- **Score do lead:** `app/lead.py::qualify_lead` — comprador (bairro/orçamento/prazo/telefone) +
  vendedor + permuta + intenção + engajamento → estágio. Lead quente dispara o dossiê.
- **Ponte p/ painel de gestão:** `app/paperclip_bridge.py::escalar_se_quente`.
- **WhatsApp:** `app/routes_publicas.py` webhook (`/api/whatsapp/webhook`) →
  qualifica → auto-resposta se `WHATSAPP_AUTO_REPLY=1` (gate de teste: `WHATSAPP_TEST_NUMBER`).
- **Admin/CRUD imóveis:** `app/routes_admin.py` + `app/imoveis.py`.
- **Front lê o banco:** `shared/data.jsx` faz `fetch('/api/imoveis')` e popula o site.

## Como rodar e testar
- Reiniciar o site: `systemctl restart imobiliaria.service` (uvicorn em `127.0.0.1:8001`).
- Testar a Ana (rápido e barato — é o jeito certo de validar conversa):
  ```bash
  curl -s -X POST https://pvscelosimobiliaria.com/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"quero casa no boa vista, tenho 1.5 milhao","history":[]}'
  ```
  `history` = lista de `{"role":"user"|"assistant","content":"..."}`. Resposta traz
  `resposta`, `rota`, `lead_score`, `lead_stage`, `lead_fields`, `modelo`.
- Validar mudança de persona/score: rode **≤3 cenários** via `/api/chat`, observe, ajuste o prompt,
  re-teste. Nunca jogue centenas de uma vez.

## Armadilhas conhecidas (gotchas)
- **Bug de boot inofensivo:** a cada restart, 1 worker pode morrer com
  `UNIQUE constraint failed: usuarios.email` (o bootstrap tenta recriar o admin existente). Outro
  worker sobe e atende — não é fatal, mas vale corrigir com `if not exists`.
- **`PRAGMA foreign_keys` OFF:** cascade não dispara — por isso nunca hard-DELETE imóvel.
- **`data/` e fotos** não estão no git: ao clonar, o banco começa vazio (bootstrap cria schema).
- **VPS pequena (1 CPU / 4 GB):** não rode muitos processos pesados em paralelo.

## Convenções de código
- Python 3 + FastAPI + Pydantic. SQLite via `app/db.py` (`db_session`).
- Texto/persona em PT-BR. Mantenha o estilo dos arquivos vizinhos.
- Front é React via Babel-standalone (sem build) — scripts `text/babel`. ⚠️ **CDN SEMPRE com versão fixa:**
  o Babel "latest" virou v8 e quebrou o admin (tela branca) — `admin/index.html` usa `@babel/standalone@7.24.7`
  + `data-presets="react"`; `chart.js@4.4.1`. Nunca volte pra CDN sem `@versão`.

## Documentos internos (FORA do repo, contêm credenciais — não versionar)
- `/root/CONTEXTO-SISTEMA.md` — estado mestre detalhado do sistema.
- `/root/ESTADO-ATUAL.md` — âncora curta de retomada (estado + próximo passo).
- `/root/.claude/projects/-root/memory/` — memória persistente do Claude.
- `docs/META-LEAD-ADS.md` — desenho da integração Meta Lead Ads (próximo marco).

## Próximos passos
Estado e roadmap REAIS estão em **`docs/HANDOFF-17-06.md`** (leia ele) — resumo:
- **No ar:** Ana (com memória + discrição + visão de imagem), Google Agenda sincronizado, MCP de 30
  ferramentas, biometria/2FA no admin, segurança endurecida + backup diário.
- **Sprint atual = ROBUSTEZ:** corrigir vacilos do atendimento (resposta dobrada já feita), reconhecer
  contatos da Priscila, observar a Ana em conversas reais. Detalhe no plano do handoff.
- **Backlog:** marketing (noindex/GA4/carrosséis/campanha), memória degrau 2 da Ana, dados reais no
  financeiro. Sempre **enxuto e barato**, **≤3 por vez**, **confirmar antes** de mudar a Ana.
