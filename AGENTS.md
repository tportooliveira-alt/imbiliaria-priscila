# AGENTS.md — Convenções para agentes que editam este projeto

Site da corretora **Priscila Vasconcelos** (CRECI/BA 29.231) em Vitória da Conquista — BA.
FastAPI + SQLite + React via Babel-standalone (sem build step). PT-BR em tudo.

---

## Stack

- Python 3.14, FastAPI, uvicorn, SQLite (`data/site.db`)
- Pillow + pillow-heif para imagens (pipeline 5 versões)
- bcrypt + PyJWT para auth
- Anthropic (Claude) + google-genai (Gemini) — roteador em `app/dispatcher.py`
- React 18 via CDN no HTML, JSX transpilado pelo Babel no navegador
- numpy / pandas / reportlab (financeiro + PDF)

## Comandos

```powershell
.\dev.ps1                 # sobe servidor + abre navegador
.\dev.ps1 -Test           # roda pytest -q
.\dev.ps1 -NoBrowser      # só backend
pytest -q                 # testes
```

## Estrutura

```
app/                # backend (módulos por responsabilidade)
  router.py         # roteador IA (Gemini Flash classifica)
  dispatcher.py     # despacha para Gemini/Claude
  routes_admin.py   # /api/auth/*, /api/admin/*
  routes_publicas.py
  routes_crm.py
  imagens.py        # pipeline Pillow → 4 webp + original
  financiamento.py  # SAC + PRICE
  avaliacao.py      # AVM heurístico
  m2_vdc.py         # tabela m² por bairro
  db.py             # schema SQLite + migrações idempotentes
  auth.py           # bcrypt + JWT + rate limit
shared/             # componentes React JSX (servidos como /shared)
v3-editorial/       # site público (index.html + app.jsx + v3.css)
admin/              # painel /admin/ (index.html + admin.jsx + admin.css)
assets/imoveis/     # uploads ({slug}/{uuid}/{tamanho}.webp)
data/site.db        # SQLite (NÃO commitar)
tests/              # pytest
scripts/            # utilitários (seed, smoke)
```

## Rotas

- `/`                      → redirect `/v3-editorial/`
- `/v3-editorial/`         → site público (vitrine + simulador + avaliação + chat)
- `/admin/`                → painel da Priscila (JWT obrigatório, exceto `DEV_OPEN_ADMIN=1`)
- `/api/health`            → status público
- `/api/admin/health`      → status detalhado (autenticado)
- `/api/chat`              → IA cascade
- `/api/simular-financiamento`, `/api/avaliar-imovel`, `/api/funnel`
- `/api/auth/login`, `/api/auth/me`
- `/api/admin/*`           → CRUD imóveis + imagens (admin)
- `/api/imoveis`, `/api/imoveis/{slug}` (público)

## Convenções de código

- **PT-BR** em nomes (variáveis, funções, mensagens, commits) — exceto APIs externas.
- **Sem acento em chaves de DB/JSON**. Texto exibido com acento normalmente.
- **Snake_case** em Python; **camelCase** em JS; **kebab-case** em CSS/URL.
- Classes CSS no v3 usam prefixo `H` (ex: `.cardH`, `.heroH`). Manter.
- Toda rota nova: adicionar teste em `tests/test_*.py` correspondente.
- Migrations: editar `SCHEMA` em `app/db.py` (idempotente) — não criar Alembic.
- Imagens NUNCA salvas com nome original; sempre `{uuid}/{tamanho}.webp` + `original.jpg`.
- `.env` real nunca commitado. Sempre atualizar `.env.exemplo` quando criar var nova.

## Variáveis de ambiente

| Var                    | Função                                        |
|------------------------|-----------------------------------------------|
| `GOOGLE_API_KEY`       | Gemini (router + Pro + Search grounding)      |
| `ANTHROPIC_API_KEY`    | Claude (Sonnet/Haiku)                         |
| `JWT_SECRET`           | Segredo HS256 — gerar com `secrets.token_urlsafe(64)` |
| `ADMIN_BOOTSTRAP_EMAIL`| Cria admin no primeiro boot se não existir    |
| `ADMIN_BOOTSTRAP_SENHA`| ↑ idem                                        |
| `DEV_OPEN_ADMIN`       | `=1` aceita qualquer login (DEV ONLY)         |
| `SITE_DB_PATH`         | Sobrescrever path do SQLite (testes)          |

## Antes de finalizar uma tarefa

1. `pytest -q` deve passar (≥ os testes existentes).
2. Se mexeu em DB → rodar `python scripts/seed.py --reset` para confirmar schema.
3. Se mexeu no frontend → recarregar `/v3-editorial/` e `/admin/` no browser.
4. `.env.exemplo` atualizado se criou variável nova.
5. Não criar arquivos markdown de "documentação da mudança" — atualizar `PLANO-DE-ACAO.md` se for marco.

## Armadilhas conhecidas

- Pasta no OneDrive: pode travar arquivos abertos. Excluir `venv/`, `data/`, `assets/imoveis/`, `logs/` da sync.
- Pillow: imagens RGBA precisam ser flatten antes de salvar JPEG (já tratado em `imagens.py`).
- `--reload` do uvicorn observa `data/`, `assets/imoveis/` e `logs/` por padrão; `dev.ps1` já exclui.
- Email regex em `LoginRequest` exige TLD (`dev@local` falha; usar `dev@local.dev`).
- JWT_SECRET ausente → cada `--reload` invalida tokens. Sempre setar no `.env`.
