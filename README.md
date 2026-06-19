# Imobiliária Priscila Vasconcelos — Site + IA de captação de leads

Plataforma de captação e **qualificação automática de leads imobiliários** para a corretora
**Priscila Vasconcelos** (CRECI/BA 29.231), em Vitória da Conquista — BA.

O sistema atende o cliente no **site** e no **WhatsApp**, qualifica o interesse (perfil, orçamento,
prazo), guarda memória do lead, e entrega o lead **"mastigado"** para a Priscila fechar — como um
SDR (pré-vendas) que trabalha 24/7. A assistente de IA se chama **Ana**.

> **Domínio:** https://pvscelosimobiliaria.com · **Painel de gestão:** https://painel.pvscelosimobiliaria.com
> **Stack:** FastAPI + nginx + systemd + SQLite · **IA:** Claude (Sonnet + Haiku) — 100% Claude (Gemini removido em 18/06)

---

## Como funciona (visão geral)

```
Cliente (site / WhatsApp)
        │
        ▼
  Motor de IA do site (FastAPI)  ──►  classifica a intenção (6 rotas)
        │                              responde como "Ana", a assistente da Priscila
        │                              (lê a CARTEIRA real + a FICHA VIVA do lead + dados financeiros)
        ▼
  Qualificação do lead (score BANT)  ──►  grava perfil + temperatura no CRM (SQLite)
        │
        ▼
  Lead QUENTE  ──►  dossiê automático no PAPERCLIP + alerta à Priscila no WhatsApp  ──►  Priscila fecha
```

- **Ana** é a persona da IA: corretora-assistente, calorosa e honesta. Ela **só oferece imóveis reais
  do banco** (nunca inventa), qualifica com **BANT** em estágios, reconhece **captação** (quem oferece
  imóvel é ouro, não lead frio), reconhece **contato conhecido** (não trata como estranho) e faz o
  **handoff** para a Priscila no momento certo.

---

## Arquitetura

### 1. Motor de IA (`app/`) — o que conversa com o cliente
- **`app/router.py`** — classifica a mensagem em 6 rotas: `TRIAGEM`, `INFO_VDC`, `NEGOCIACAO`,
  `DESCRICAO`, `FOLLOWUP`, `VISAO`.
- **`app/dispatcher.py`** — orquestra a resposta: monta o contexto (carteira real + ficha viva do lead
  + dados financeiros), chama o LLM em **cascata com failover** (primário → failover Haiku → fallback
  estático) e devolve resposta + qualificação. **Tiering de modelo (custo):** Haiku no volume
  (`TRIAGEM`/`FOLLOWUP`/`VISAO`), **Sonnet** onde precisa de qualidade (`INFO_VDC`/`NEGOCIACAO`/`DESCRICAO`).
- **`app/clients.py`** — clientes LLM: `ClienteClaude` (Sonnet/Haiku) + `ClienteFallback` (resposta
  estática se tudo falhar). **Só Claude** — Gemini foi removido (decisão do dono).
- **`app/prompts.py`** — a **persona da Ana** (voz, anti-invenção, "verdade com discrição", BANT,
  captação, contato conhecido, não re-saudar, handoff) + prompts por rota.
- **`app/lead.py`** — **qualificação/score** (0–100): sinais de comprador (bairro/orçamento/prazo/
  telefone), vendedor, permuta, intenção, engajamento → estágio (frio/morno/quente/pronto_visita/
  pronto_proposta).
- **`app/memoria_lead.py`** — **ficha viva**: memória do lead que atravessa conversas (sem custo de IA;
  acumula o que já se sabe da pessoa). Regra: "verdade com discrição" — a Ana usa por dentro, não vaza.
- **`app/visao.py`** — **Ana enxerga imagem** (Claude Haiku vê a foto que o cliente manda e descreve no
  contexto, sem inventar). Depende do download da mídia via Evolution (`whatsapp.baixar_midia_base64`).
- **`data/dados_financeiros.md`** — ficha de **dados financeiros reais** (taxas 2026, ITBI, MCMV,
  Pró-Cotista, SFH) injetada no contexto — fonte de verdade dos números (atualizável). A FICHA vence.

### 2. Imóveis, fotos e CRM (`app/`)
- **`app/imoveis.py`** / **`app/imagens.py`** — CRUD de imóveis + imagens (otimização automática para
  **webp em 4 tamanhos**: 200/600/1200/2400, mantendo o `original.jpg`).
- **`app/empreendimentos.py`** — empreendimentos (lançamentos) e suas imagens.
- **`app/leads.py`** / **`app/routes_crm.py`** — leads, interações, funil, tags.
- **`app/avaliacao.py`** / **`app/m2_vdc.py`** / **`app/ruas.py`** — calculadora de avaliação (AVM) por
  bairro de Vitória da Conquista.
- **`app/financiamento.py`** / **`app/financeiro.py`** — simulação de financiamento (SBPE, Pró-Cotista
  FGTS, MCMV) — sempre SIMULAÇÃO, nunca promessa de aprovação.
- Banco: **SQLite** em `data/site.db` (NÃO versionado).

### 3. Fotos + marca d'água
- As fotos ficam em `assets/imoveis/<slug>/<hash>/` e `assets/empreendimentos/...`, cada uma com os
  webp (200/600/1200/2400) + `original.jpg` (master limpo).
- **Marca d'água** (19/06): o selo redondo da marca (`assets/logo-selo.jpeg`, fundo removido) é
  carimbado **centralizado e transparente** em todos os webp (o `original.jpg` fica intacto = backup).

### 4. WhatsApp (Evolution API)
- **Evolution API** (Docker, `EVOLUTION_API_URL`) é o gateway do WhatsApp da Priscila.
- `app/whatsapp.py` envia (texto/áudio) e baixa mídia; o webhook em `app/routes_publicas.py`
  (`/api/whatsapp/webhook/<segredo>`) recebe → cria/qualifica o lead → (se `WHATSAPP_AUTO_REPLY=1`) a
  Ana responde.
- **Freios de segurança (Evolution não-oficial, evita ban):** só responde a quem escreve primeiro,
  ignora grupos/broadcast, respeita **opt-out** ("pare"), **teto diário** (`WHATSAPP_DAILY_CAP`),
  **atraso humano** antes de enviar, **idempotência** (não re-responde o mesmo evento) e **debounce**
  (rajada de mensagens → uma resposta só, sem re-saudação).

### 5. Agenda / Secretária / Voz
- **`app/gcal.py` + `app/agenda.py`** — Google Calendar: agendamento de visitas (aparece no painel).
- **`app/secretaria.py`** — **Sofia**: SÓ o número da Priscila (com a palavra "Sofia") agenda pelo
  WhatsApp; responde por texto + **áudio** (voz "João" via ElevenLabs). Cliente nunca cai aqui.
- `scripts/` — agentes de **lembrete** de visita e **follow-up** (systemd).

### 6. MCP (cowork / claude.ai)
- **`app/mcp_server.py`** — servidor **MCP** (FastMCP) com **17 ferramentas de leitura** (panorama
  geral, leads, conversas da Ana, métricas, imóveis, fotos...). Usado pelo Claude do PC ("cowork") como
  cérebro central. **Read-only + sem senha** (compatível com o conector do claude.ai). Escrita liga sob
  demanda (`MCP_WRITE_ENABLED=1`). Roda em `127.0.0.1:8765` (systemd `imobiliaria-mcp`), exposto pelo
  nginx num caminho secreto.

### 7. Paperclip (painel de gestão de leads quentes)
- **`app/paperclip_bridge.py`** — quando um lead vira **QUENTE**, monta um **dossiê** (com simulação
  financeira + análise BANT + próximo passo) e cria um **card/issue no Paperclip** via API local
  (`127.0.0.1:3100`), atribuído à "Ana". Também alerta a Priscila no WhatsApp.
- O Paperclip é um sistema separado na VPS (pm2 `paperclip` + postgres em Docker). Painel externo:
  **https://painel.pvscelosimobiliaria.com** (basic-auth). Detalhes no doc de setup.

### 8. Admin (`admin/`)
- Painel da corretora: login, cadastro de imóveis, upload de fotos, geração de descrição por IA,
  dashboard. **Biometria (passkey/WebAuthn)** + **2FA por e-mail** (`app/passkey.py`,
  `app/email_util.py`, `app/routes_admin.py`). Front em React via Babel-standalone (pinado em
  `@babel/standalone@7.24.7` — CDN sempre com versão fixa).

### 9. Front-end (`v3-editorial/`, `shared/`, `admin/`)
- Site editorial em **React via Babel-standalone (sem build)**. O catálogo é lido **do banco** em tempo
  real (`/api/imoveis`) — todo imóvel cadastrado no admin aparece no site automaticamente.

---

## Estrutura de pastas

```
imobiliaria/
├── server.py              # app FastAPI (monta rotas, /api/chat, bootstrap)
├── app/                   # motor de IA, CRM, rotas, qualificação, MCP, pontes (38 módulos)
│   ├── router.py  dispatcher.py  prompts.py  clients.py  lead.py  memoria_lead.py  visao.py
│   ├── imoveis.py  imagens.py  empreendimentos.py  leads.py  avaliacao.py  m2_vdc.py
│   ├── routes_publicas.py  routes_admin.py  routes_crm.py  whatsapp.py  gcal.py  agenda.py
│   ├── secretaria.py  passkey.py  email_util.py  financiamento.py
│   ├── mcp_server.py            # servidor MCP (cowork)
│   └── paperclip_bridge.py      # ponte lead-quente → Paperclip
├── data/                  # SQLite (site.db) + dados_financeiros.md + backups  (NÃO versionado)
├── assets/                # fotos dos imóveis/empreendimentos (webp + original.jpg) + logos
├── admin/                 # painel (admin.jsx, admin.css)
├── v3-editorial/          # site público (index.html, app.jsx)
├── shared/                # componentes JSX compartilhados + data.jsx
├── scripts/               # automações (lembretes, follow-up, verificar.sh)
├── docs/                  # documentação operacional + HANDOFFs (cérebro do projeto)
├── secret/                # segredos (NÃO versionado)
├── tests/                 # pytest (dispatcher, leads, avaliação, webhook...)
├── requirements.txt  .env  .gitignore  CLAUDE.md  AGENTS.md
```

---

## Rodando localmente

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.exemplo .env          # edite as chaves (veja abaixo)
uvicorn server:app --reload --port 8001
# checagem antes de dizer "pronto":
bash scripts/verificar.sh     # py_compile + pytest + smoke (site + Ana viva)
```

### Variáveis de ambiente (`.env`)
| Variável | Para quê |
|---|---|
| `ANTHROPIC_API_KEY` | IA (Claude Sonnet + Haiku) — **obrigatória** |
| `EVOLUTION_API_URL` / `EVOLUTION_API_KEY` / `EVOLUTION_INSTANCIA` | gateway WhatsApp |
| `WHATSAPP_AUTO_REPLY` | `1` liga a resposta automática |
| `WHATSAPP_TEST_NUMBER` | se setado, só responde a esse número (modo teste seguro) |
| `WHATSAPP_DAILY_CAP` | máximo de auto-respostas por dia (warm-up) |
| `WHATSAPP_DELAY_MIN` / `WHATSAPP_DELAY_MAX` | atraso (s) antes de enviar — simula digitação |
| `GROQ_API_KEY` | transcrição de áudio do WhatsApp (Whisper) — opcional |
| `ELEVENLABS_VOICE_ID_JOAO` | voz da secretária Sofia (áudio) — opcional |
| `PAPERCLIP_API` / `PAPERCLIP_CID` / `PAPERCLIP_ASSIGNEE` / `PAPERCLIP_GOAL` | ponte do painel (têm default) |
| `MCP_WRITE_ENABLED` | `1` libera as ferramentas de ESCRITA do MCP (padrão: só leitura) |

> **Nunca** comite o `.env` — o `.gitignore` já protege `.env`, `secret/`, banco (`data/`) e segredos.

---

## Produção (VPS)

- **systemd:** `imobiliaria.service` (uvicorn `127.0.0.1:8001`, Restart=always, User=priscila) +
  `imobiliaria-mcp.service` (MCP) + `imobiliaria-agente.service` (lembretes) + `imobiliaria-backup.timer`
  (backup diário do banco).
- **nginx** reverse proxy + SSL (Let's Encrypt): `/` → site; `/api/*` → backend; `/admin/` → painel;
  caminho secreto → MCP.
- **App roda como usuário `priscila`** — NUNCA dar `chown root` nos segredos (derruba o site).
- Reiniciar: `systemctl restart imobiliaria.service`. Deploy: `bash deploy.sh` (roda py_compile antes).

---

## Segurança & LGPD

- Segredos (`.env`, `secret/`, chaves) e dados pessoais (`data/` = banco com conversas reais de cliente,
  fotos) **não são versionados**.
- A IA **nunca inventa** imóvel, preço ou dado — só usa o que existe no banco/fichas; financiamento é
  sempre **simulação**, nunca promessa.
- Consentimento LGPD no contato; a Ana se identifica como assistente da Priscila ("verdade com discrição").

---

## Status (jun/2026)

- [x] Site editorial no ar, lendo imóveis do banco · IA (Ana) 100% Claude, anti-invenção, BANT, estágios
- [x] Memória do lead (ficha viva) · Visão (Ana lê imagem) · Captação reconhecida · contato conhecido
- [x] WhatsApp (Evolution) + auto-resposta com freios (opt-out, teto, debounce, anti-re-saudação)
- [x] Google Calendar (visitas) · Secretária Sofia (voz) · Admin com biometria/2FA
- [x] MCP (17 ferramentas) pro cowork · Paperclip recebendo dossiê de lead quente
- [x] Marca d'água nas fotos (selo da marca, transparente)
- [ ] Ana ENVIAR foto/link do imóvel sob pedido (com a regra de não importunar) — *degrau seguinte*
- [ ] Escalonar Haiku→Sonnet por complexidade/tamanho da conversa — *planejado*
- [ ] Consertar o download da mídia (a visão hoje falha no download da Evolution — em diagnóstico)

> Documentação operacional e decisões do dia-a-dia: `docs/HANDOFF-<data>.md` (o cérebro ativo do projeto).
