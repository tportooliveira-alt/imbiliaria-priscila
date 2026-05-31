# Priscila Vasconcelos Imóveis

Plataforma imobiliária completa para Vitória da Conquista (BA), com:

- site público editorial (`/v3-editorial/`)
- painel administrativo (`/admin/`)
- CRM de leads e agenda
- operação de IA multiagente (procuradora, rastreadora, leads, marketing, orquestrador e corretor)
- simulação de financiamento, avaliação de imóvel e automações de WhatsApp

Backend em FastAPI + SQLite, frontend em React via CDN/Babel (sem build step).

## Stack

- Python 3.14
- FastAPI + Uvicorn
- SQLite (`data/site.db`)
- React 18 + Babel standalone
- IA: Google GenAI (Gemini) + Anthropic (Claude)
- Auth: bcrypt + JWT
- Imagens: Pillow + pillow-heif
- Financeiro/PDF: numpy + pandas + reportlab
- Testes: pytest + httpx

## Estrutura do projeto

```text
site-imobiliaria/
├─ app/                    # backend modular (rotas, IA, CRM, financeiro, auth)
├─ admin/                  # painel administrativo (/admin/)
├─ v3-editorial/           # site público (/v3-editorial/)
├─ shared/                 # componentes JSX compartilhados
├─ scripts/                # utilitários (seed, agente 24/7, operações IA)
├─ tests/                  # suíte automatizada
├─ deploy/                 # arquivos de deploy systemd/nginx/VPS
├─ assets/                 # mídias públicas
└─ data/                   # banco SQLite local (não comitar)
```

## Subir localmente

### Opção rápida (recomendada)

```powershell
.\dev.ps1
```

Comandos úteis:

```powershell
.\dev.ps1 -NoBrowser     # sobe só backend
.\dev.ps1 -Test          # roda testes e sai
```

### Opção manual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.exemplo .env
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

## URLs locais

- Site público: `http://127.0.0.1:8000/v3-editorial/`
- Central de vendas (listagem): `http://127.0.0.1:8000/v3-editorial/#imoveis`
- Admin: `http://127.0.0.1:8000/admin/?reset=1`
- Health check: `http://127.0.0.1:8000/api/health`

## Variáveis de ambiente

Copie `.env.exemplo` para `.env` e preencha:

- `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `JWT_SECRET`
- `ADMIN_BOOTSTRAP_EMAIL`
- `ADMIN_BOOTSTRAP_SENHA`
- `EVOLUTION_API_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCIA`

Importante:

- `DEV_OPEN_ADMIN=1` é só para desenvolvimento.
- Nunca subir `.env` real para o Git.

## Testes

Rodar suíte completa:

```powershell
python -m pytest -q --basetemp=.tmp-pytest-run
```

A suíte atual cobre backend, rotas públicas/admin, CRM, financeiro, agenda, documentos, IA e WhatsApp.

## Principais módulos e capacidades

- `app/routes_publicas.py`: busca natural, simulação, avaliação, captação de vendedor, agendamento, consentimento
- `app/routes_admin.py`: autenticação, CRUD de imóveis, upload/ordenação de imagens, geração de descrição
- `app/routes_crm.py`: dashboard, leads, alertas, agenda, documentos, financeiro, operação IA
- `app/operacao_ia.py`: fila de tarefas de IA, subagentes, feedback, conhecimentos e relatórios
- `app/whatsapp.py`: integração com Evolution API com fallback seguro

## Deploy (Hostinger VPS)

Guia completo em:

- `deploy/README.md`

Inclui:

- setup Ubuntu
- systemd (`imobiliaria` e `imobiliaria-agente`)
- nginx + certbot
- backup e monitoramento

## Segurança

- Arquivos sensíveis ficam fora do versionamento (`.env`, chaves, banco local e uploads privados)
- Respostas admin recebem `X-Robots-Tag: noindex, nofollow`
- CSP e headers de segurança ativos no `server.py`
- JWT assinado com `HS256` e segredo configurável

## Operação diária (resumo)

- Atualizar código:
  ```powershell
  git pull --ff-only
  ```
- Rodar testes:
  ```powershell
  python -m pytest -q --basetemp=.tmp-pytest-run
  ```
- Subir local:
  ```powershell
  .\dev.ps1
  ```
