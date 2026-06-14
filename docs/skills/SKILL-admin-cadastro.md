# 🔧 SKILL — Admin / Cadastro de imóvel

## O que faz
Painel onde a **Priscila cadastra e gerencia imóveis** (foto, descrição por IA, sugerir preço,
auto-organizar fotos), além de leads/CRM, agenda e financeiro.

## Acesso
- URL: **pvscelosimobiliaria.com/admin/**
- Login: `tportooliveira@gmail.com` ou `thiago@admin.com` · senha **233024** (temporária — trocar depois).
- Continua acessível mesmo com o site público em soft-launch.

## Onde está o código
- `admin/admin.jsx` — a interface (React via Babel no navegador) · `admin/admin.css` · `admin/index.html`.
- `app/routes_admin.py` — endpoints:
  - `POST /api/admin/imoveis` (criar) · `PUT/DELETE` (editar/desativar)
  - `POST /api/admin/imoveis/gerar-descricao` (IA escreve a descrição — Sonnet)
  - `POST /api/admin/imoveis/{id}/imagens` (upload) · `.../auto-organizar` (classifica fotos por IA)
  - `POST /api/auth/login` · `GET /api/auth/me`
- `app/visao.py` — classifica cômodo da foto (fachada/sala/quarto…). Usa **Gemini OU Claude** (visão).
  Como GOOGLE_API_KEY está vazia, roda pelo **Claude** (`ClienteClaude.classificar_imagem`).
- `app/auth.py` — login com **bcrypt** + JWT (`hash_senha`, `autenticar`, `criar_usuario`).
- `app/imoveis.py` / `app/imagens.py` — regras de imóvel/imagem no banco.
- "💰 Sugerir preço" no formulário chama `POST /api/avaliar-imovel` (a calculadora calibrada).

## Fluxo de cadastro (passo a passo p/ Priscila)
Imóveis → Novo → preencher → 💰 Sugerir preço → ✨ Gerar descrição → Salvar → arrastar fotos →
Auto-organizar → marcar destaque + ativo → aparece no site.

## Resetar senha
```bash
./venv/bin/python -c "
from app.auth import hash_senha; from app.db import db_session
with db_session() as c: c.execute('UPDATE usuarios SET senha_hash=? WHERE email=?', (hash_senha('NOVASENHA'),'email@x'))"
```

## Erros comuns
- **Não loga** → senha errada (bcrypt, não dá pra ler — só resetar). Ou rate-limit (15 min após muitas tentativas).
- **Auto-organizar não faz nada** → precisa de `ANTHROPIC_API_KEY` (ou GOOGLE) no `.env`; senão retorna `fallback:true`.
- **Gerar descrição vazia** → `ANTHROPIC_API_KEY` ausente.
- **Foto não sobe** → máx. 30 por vez; tem que ser `image/*`.
- **Imóvel não aparece no site** → conferir `ativo=1` e `destaque=1`.
