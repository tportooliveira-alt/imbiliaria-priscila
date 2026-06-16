# 🏗️ ESTUDO DE ARQUITETURA E CÓDIGO (16/06/2026) — a 5ª frente do 360

Revisão profunda da arquitetura/qualidade. **Nota geral: 7/10** — sólido pro estágio (1 dev + IA, corretora única),
acima da média de "projeto de IA improvisado". A dívida é **localizada** em poucos pontos que doem ao escalar.

## ✅ Pontos fortes (reais)
Separação limpa repositório/rotas · cliente LLM com **fallback em cascata** bem desenhado · captura de lead progressiva
e idempotente · **Pydantic** em todas as entradas · upload de imagem seguro (magic bytes + EXIF + watermark) · CSP/headers
· rate-limit de login · **274 testes** · código legível e comentado em PT-BR (explica o "porquê").

## 🔴 Dívida ALTA (corrigir cedo)
1. **Rota duplicada fantasma:** `routes_crm.py:304` e `:387` definem a MESMA rota `sugerir-resposta` — a 2ª sombreia a 1ª
   (≈80 linhas de código morto). Mexer na "errada" não tem efeito. → remover a duplicata.
2. **SQLite sem WAL + 2 workers, sem `busy_timeout`** (`db.py:conectar`) → escritas concorrentes podem dar
   `database is locked` sob carga. Hoje não aparece (volume baixo), mas é o **SPOF nº1** ao crescer. → **fix de 2 linhas** (WAL + busy_timeout).
3. **Transações não-atômicas por design:** uma "interação de lead" são 2-3 commits separados → se cair no meio, estado parcial.
4. **9 de 274 testes falhando** — não é regressão de lógica, é *test rot*: a suíte roda com o `.env` real carregado
   (chaves presentes, `EVOLUTION_WEBHOOK_TOKEN` setado) e os testes assumem ambiente limpo. → isolar env no `conftest.py`.

## 🟠 Dívida MÉDIA
5. **~31 `except Exception` que engolem erro** — vários legítimos (fallback comentado), mas alguns escondem bug
   (Paperclip, WhatsApp, voz param e ninguém vê). → ao menos `logging.exception` nos que importam.
6. **Duplicação imóveis ↔ empreendimentos** (`empreendimentos.py` copia ~60% de imagens/slug de `imoveis.py`). Defensável
   com 2 entidades; vira problema na 3ª. → generalizar uma "Galeria(tabela, fk)" antes de adicionar mais uma.
7. **Admin transpilado no browser** (React+Babel via CDN, 2281 linhas a cada load) — exige `unsafe-eval`, depende da CDN
   estar no ar (CDN cai = admin morre). Tolerável p/ 1 usuária; é fragilidade.
8. Código morto: `FUNIL_COUNTER`/`funnel_summary` (`lead.py`), `CORS_ORIGINS` nunca lido, `detalhe_por_id` (hasattr sempre False).

## 🟡 Dívida BAIXA
`datetime.utcnow()` deprecado (279 warnings) · `time.sleep` síncrono no webhook (segura worker) · `max_tokens=800` fixo
(trunca resposta longa) · backups `.bak`/`.env.bak` poluindo o diretório.

## 🗄️ Banco (resposta direta)
- **Lock com 2 workers:** risco real mas latente → WAL + busy_timeout resolve.
- **Migrações** (`SCHEMA` idempotente + `_migrar_coluna`): robusto p/ ADICIONAR coluna; não cobre renomear/tipo/backfill;
  sem versionamento. Funciona; frágil p/ evolução complexa.
- **Índices:** bem cobertos (~25). 👍 · **FK ON** correto com CASCADE.

## 🧪 Testes (resposta direta)
274 testes, cobertura ampla. **265 passam, 9 falham** por vazamento de ambiente (não lógica). **O `deploy.sh` NÃO roda
os testes** (só smoke curl) → sem CI, validação manual.

## 🎯 Recomendações priorizadas

**Quick wins (alto impacto, baixo esforço — "uma tarde"):**
1. `PRAGMA journal_mode=WAL` + `busy_timeout=5000` em `db.py:conectar()` — mata o risco de lock. _(2 linhas)_
2. Remover a rota duplicada `sugerir_resposta` (`routes_crm.py`). _(deletar ~80 linhas)_
3. Isolar env nos testes (`conftest.py` limpa as chaves) → os 9 testes voltam a verde.
4. Rodar `pytest`/`py_compile` no `deploy.sh` antes do restart.
5. Limpar código morto (`FUNIL_COUNTER`, `CORS_ORIGINS`, `detalhe_por_id`, `.bak` do diretório).

**Médio prazo:** extrair o webhook de 255 linhas p/ uma camada de serviço · trocar `time.sleep` por background ·
generalizar galeria imóveis/empreendimentos · `datetime.now(timezone.utc)` · logar os `except` que importam.

**Longo prazo (só quando crescer):** build real do admin (esbuild/vite, remove `unsafe-eval`) · versionamento de schema ·
avaliar Postgres **só quando o SQLite+WAL doer** (não antes).

> **Veredito:** nada é incêndio. A plataforma está saudável pro estágio. Os itens 1-5 custam uma tarde e removem os
> riscos mais sérios (lock de DB, rota fantasma, suíte de testes não-confiável).
