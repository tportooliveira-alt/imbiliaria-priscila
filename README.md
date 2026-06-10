# Imobiliária Priscila Vasconcelos — Site + IA de captação de leads

Plataforma de captação e **qualificação automática de leads imobiliários** para a corretora
**Priscila Vasconcelos** (CRECI/BA 29.231), em Vitória da Conquista — BA.

O sistema atende o cliente no **site** e no **WhatsApp**, qualifica o interesse (perfil, orçamento,
prazo) e entrega o lead **"mastigado"** para a Priscila fechar — funcionando como um SDR
(pré-vendas) que trabalha 24/7.

> **Domínio:** https://pvscelosimobiliaria.com · **Stack:** FastAPI + nginx + SQLite · **IA:** Claude (+ Gemini opcional)

---

## Como funciona (visão geral)

```
Cliente (site / WhatsApp)
        │
        ▼
  Motor de IA do site (FastAPI)  ──►  classifica a intenção (6 rotas)
        │                              responde como "Ana", a assistente da Priscila
        ▼
  Qualificação do lead (score BANT)  ──►  grava perfil + temperatura no CRM
        │
        ▼
  Lead QUENTE  ──►  dossiê automático no painel + alerta  ──►  Priscila fecha
```

- **Ana** é a persona da IA: corretora-assistente, calorosa e honesta. Ela **só oferece imóveis
  reais do banco** (nunca inventa), qualifica com a metodologia **BANT** (Necessidade, Orçamento,
  Prazo, Decisão) em **estágios** (entender → mostrar imóvel → qualificar → próximo passo) e faz o
  **handoff** para a Priscila no momento certo.

---

## Arquitetura

### 1. Motor de IA do site (`app/`) — o que conversa com o cliente
- **`app/router.py`** — classifica a mensagem em 6 rotas: `TRIAGEM`, `INFO_VDC`, `NEGOCIACAO`,
  `DESCRICAO`, `FOLLOWUP`, `VISAO`.
- **`app/dispatcher.py`** — orquestra a resposta: monta o contexto (carteira real de imóveis +
  ficha financeira), chama o LLM em **cascata com failover** (Gemini → Claude → fallback estático)
  e devolve resposta + qualificação.
- **`app/prompts.py`** — a **persona da Ana** (voz, postura, regra anti-invenção, BANT, estágios,
  handoff) e os prompts por rota.
- **`app/lead.py`** — **qualificação/score do lead** (0–100): sinais de comprador
  (bairro, orçamento, prazo, telefone), **vendedor**, permuta, intenção e engajamento → estágio
  (frio/morno/quente/pronto_visita/pronto_proposta).
- **`app/clients.py`** — clientes LLM (Claude, Gemini) com fallback gracioso.
- **`data/dados_financeiros.md`** — ficha de **dados financeiros reais** (taxas 2026, ITBI, MCMV,
  Pró-Cotista, SFH) injetada no contexto — é a fonte de verdade dos números (atualizável).

### 2. Imóveis e CRM (`app/`)
- **`app/imoveis.py`** — CRUD de imóveis + imagens (otimização automática para webp em 3 tamanhos).
- **`app/leads.py`** / **`app/routes_crm.py`** — leads, interações, funil.
- **`app/routes_admin.py`** — painel administrativo (login, cadastro de imóveis, upload de fotos,
  geração de descrição por IA, ordenação de imagens).
- **`app/routes_publicas.py`** — endpoints públicos: `/api/chat`, simuladores, avaliação,
  **webhook do WhatsApp** (`/api/whatsapp/webhook`), consentimento LGPD.
- Banco: **SQLite** em `data/site.db` (NÃO versionado).

### 3. Integração WhatsApp
- **Evolution API** (Docker) como gateway do WhatsApp da Priscila.
- O webhook recebe a mensagem → cria/qualifica o lead → (se `WHATSAPP_AUTO_REPLY=1`) a Ana
  responde automaticamente. Suporta **modo teste** (`WHATSAPP_TEST_NUMBER`) que só responde a um
  número específico, para validar ao vivo sem atingir clientes reais.
- **Modo seguro (Evolution não-oficial)** — para não arriscar banimento do número: só responde a
  quem escreve primeiro (nunca cold), **ignora grupos/listas**, respeita **opt-out** ("pare"), tem
  **teto diário** de envios (warm-up) e **atraso humano** antes de enviar (simula digitação).
- Lead quente → **ponte** (`app/paperclip_bridge.py`) cria um dossiê no painel de gestão.

### 4. Front-end (`v3-editorial/`, `shared/`)
- Site editorial em React via Babel-standalone (sem build).
- O catálogo é lido **do banco** em tempo real (`/api/imoveis`) — todo imóvel cadastrado no admin
  aparece no site automaticamente.

---

## Estrutura de pastas

```
imobiliaria/
├── server.py              # app FastAPI (monta rotas, /api/chat, bootstrap)
├── app/                   # motor de IA, CRM, rotas, qualificação
│   ├── router.py  dispatcher.py  prompts.py  lead.py  clients.py
│   ├── imoveis.py  leads.py  auth.py  db.py
│   ├── routes_publicas.py  routes_admin.py  routes_crm.py
│   └── paperclip_bridge.py
├── data/                  # SQLite + dados_financeiros.md   (NÃO versionado)
├── admin/                 # painel (admin.jsx, admin.css, calculadora-ads.html)
├── v3-editorial/          # site público (index.html, app.jsx)
├── shared/                # componentes JSX compartilhados + data.jsx
├── assets/                # mídia e fotos de imóveis (fotos NÃO versionadas)
├── scripts/               # automações (ex.: agente de lembretes)
├── docs/                  # documentação operacional
├── deploy/                # unit systemd
├── requirements.txt  .env.exemplo  .gitignore
```

---

## Rodando localmente

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.exemplo .env          # edite as chaves (veja abaixo)
uvicorn server:app --reload --port 8001
```

### Variáveis de ambiente (`.env`) — veja `.env.exemplo`
| Variável | Para quê |
|---|---|
| `ANTHROPIC_API_KEY` | IA (Claude) — obrigatória |
| `GOOGLE_API_KEY` | Gemini (opcional; sem ela, cai no Claude por failover) |
| `EVOLUTION_API_URL` / `EVOLUTION_API_KEY` / `EVOLUTION_INSTANCIA` | gateway WhatsApp |
| `WHATSAPP_AUTO_REPLY` | `1` liga a resposta automática (padrão: desligado) |
| `WHATSAPP_TEST_NUMBER` | se setado, só responde a esse número (modo teste seguro) |
| `WHATSAPP_DAILY_CAP` | máximo de auto-respostas por dia (warm-up; padrão 30) |
| `WHATSAPP_DELAY_MIN` / `WHATSAPP_DELAY_MAX` | atraso (s) antes de enviar — simula digitação |

> **Nunca** comite o `.env` — o `.gitignore` já protege `.env`, chaves, banco e fotos.

---

## Produção (VPS)

- **systemd:** `imobiliaria.service` (uvicorn em `127.0.0.1:8001`) + `imobiliaria-agente.service`
  (lembretes/automações). Unit em `deploy/`.
- **nginx** como reverse proxy + SSL (Let's Encrypt). `/` → site; `/api/*` → backend;
  `/admin/` → painel.
- Reiniciar: `systemctl restart imobiliaria.service`.

---

## Cadastro de imóveis (admin)

1. Acesse `/admin/` e faça login.
2. **Novo imóvel** → preencha título, bairro, tipo e **preço** (obrigatórios) + quartos/área/etc.
3. Suba as fotos (otimização automática). Há **geração de descrição por IA**.
4. Salvar → o imóvel entra no site e na **carteira da Ana** automaticamente.

---

## Segurança & LGPD

- Segredos (`.env`, chaves, `*.pem`) e dados pessoais (`data/`, banco com leads, fotos) **não são
  versionados**.
- A IA **nunca inventa** imóvel, preço ou dado — só usa o que existe no banco/fichas.
- Consentimento LGPD registrado no contato; a Ana se identifica como assistente da Priscila.

---

## Status

- [x] Site editorial no ar, lendo imóveis do banco
- [x] Motor de IA (Ana) com anti-invenção, BANT e estágios de conversa
- [x] Qualificação de lead (comprador + vendedor + permuta + intenção)
- [x] WhatsApp conectado (Evolution) + qualificação automática
- [x] Ponte lead-quente → dossiê para a Priscila
- [x] Resposta automática do WhatsApp com **freios de segurança** (modo seguro Evolution)
- [ ] Resposta automática em produção para todos (hoje em modo teste — falta liberar)
- [ ] Meta Lead Ads (anúncios → lead direto no funil) — desenho em `docs/META-LEAD-ADS.md`
- [ ] Modernização visual do site (próxima fase)
