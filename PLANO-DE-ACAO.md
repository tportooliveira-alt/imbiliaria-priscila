# Plano de Ação — Site Priscila Vasconcelos Imóveis

> Documento vivo. Atualize conforme avançar. Cada passo tem checkbox.

**Cliente:** Priscila Vasconcelos · CRECI/BA 29.231
**Praça:** Vitória da Conquista — BA
**Pasta do projeto:** `C:\Users\Thiago Porto\OneDrive\Desktop\site-imobiliaria\`
**Branch git:** `main` (local, sem remote ainda)

---

## 🎯 Objetivo final

Site editorial com **IA híbrida (Gemini + Claude)** que:

1. Abre com vídeo cinematográfico (vídeo prédios → vídeo Priscila falando → IA ativa)
2. Capta lead via chat real plugado em modelos de IA
3. Faz triagem + qualificação + busca de imóvel + negociação
4. Roda local em `http://localhost:8000` agora; depois sobe para VPS

---

## 🧠 Arquitetura de IA (model routing)

```
Mensagem chega
   ↓
[Roteador — Gemini Flash, ~3ms]
   ├─ Triagem simples       → Gemini Flash       (R$ 0,30/1M tok)
   ├─ Pergunta sobre VDC    → Gemini Pro+Search  (info Google em tempo real)
   ├─ Negociar lead quente  → Claude Sonnet      (PT-BR formal, fechamento)
   ├─ Avaliar imóvel        → Gemini Pro Vision  (foto + preço)
   ├─ Descrição editorial   → Claude Sonnet      (texto rico, tom revista)
   └─ Follow-up frio        → Claude Haiku       (barato, cordial)
```

**Custo estimado:** ~R$ 170/mês para 3.000 conversas (vs R$ 400 só Claude).

**Chaves necessárias:**
- `GOOGLE_API_KEY=AIza...` (https://aistudio.google.com/apikey — grátis, 1.500 req/dia)
- `ANTHROPIC_API_KEY=sk-ant-...` (https://console.anthropic.com — US$ 10 de crédito)

---

## 📁 Estado atual do projeto

```
site-imobiliaria/
├── .git/                          ✅ commit c16b9fb + 83d8bc8
├── .gitignore                     ✅ protege chaves, .env, node_modules
├── README.md                      ✅
├── requirements.txt               ✅ fastapi, uvicorn, anthropic, google-genai, pydantic
└── v3-editorial/
    ├── index.html                 ✅ 64 KB / 927 linhas
    └── assets/
        ├── AI_in_daily_*.mp4      ⚠️  renomeado (era abertura.mp4)
        ├── predios.mp4            ❌ removido (precisa restaurar?)
        ├── priscila-new-hero.jpeg ❌ removido (precisa restaurar?)
        └── priscila-sobre.jpg     ✅
```

**Versão de referência adicional encontrada:**
`C:\Users\Thiago Porto\Downloads\modelos-sites-extraido\...\project\v2-cinema\`
(tem index.html + app.jsx + v2.css — variação "cinema dark/neon" para inspiração)

**Ambiente verificado:**
- Python 3.14.4 ✅
- Git 2.54.0 ✅
- Node v24.15.0 ✅
- npm 11.12.1 ✅

---

## 📍 PASSO A PASSO

### Etapa 0 — Higiene & segurança
- [ ] Mover `notas.txt` (chaves de API) de `Desktop` (OneDrive) para `C:\segredos\notas.txt` (fora da nuvem)
- [ ] Confirmar que `.gitignore` cobre `.env`, `notas.txt`, `chave*`, `secrets/`
- [ ] Resolver resíduos do IObit Uninstaller (pasta + serviço `IObitUnSvr` parado)

### Etapa 1 — Restaurar mídias da abertura
- [ ] Decidir nomes finais: `predios.mp4` → `priscila-fala.mp4` → (futuro) `ia-falando.mp4`
- [ ] Restaurar `predios.mp4` e `priscila-new-hero.jpeg` se forem necessários
- [ ] Adicionar **vídeo da IA falando** logo depois do vídeo da Priscila (pedido explícito)
- [ ] Garantir encadeamento: prédios → Priscila → IA → site fica visível

### Etapa 2 — Backend (server.py)
- [ ] Criar `.env.exemplo` com `GOOGLE_API_KEY=` e `ANTHROPIC_API_KEY=`
- [ ] Criar `server.py` (FastAPI) com:
  - [ ] Endpoint `POST /api/chat` recebendo `{message, history}`
  - [ ] Função `roteador()` que classifica a mensagem (triagem/vdc/negociacao/visao/descricao/followup)
  - [ ] Cliente Gemini (Flash + Pro com Search)
  - [ ] Cliente Claude (Sonnet + Haiku)
  - [ ] Fallback automático se uma chave estiver faltando
  - [ ] CORS liberado para `localhost`
  - [ ] Servir arquivos estáticos de `v3-editorial/`
- [ ] Criar `python-dotenv` carregando `.env`

### Etapa 3 — Frontend conectado
- [ ] Localizar widget de chat no `v3-editorial/index.html`
- [ ] Substituir mock por `fetch('/api/chat', ...)` real
- [ ] Streaming opcional (SSE) para resposta token-a-token
- [ ] Tratar erros (rate limit, chave inválida, modelo offline)

### Etapa 4 — Dados de Vitória da Conquista
- [ ] Tabela de bairros (Candeias, Boa Vista, Recreio, Patagônia, Centro, etc.)
- [ ] Catálogo inicial de imóveis (mock JSON ou tabela simples)
- [ ] Prompts do sistema com tom da Priscila

### Etapa 5 — Rodar local
- [ ] `python -m venv venv && .\venv\Scripts\Activate.ps1`
- [ ] `pip install -r requirements.txt`
- [ ] Renomear `.env.exemplo` → `.env` e colar as 2 chaves
- [ ] `python server.py` → abrir `http://localhost:8000`
- [ ] Testar 5 fluxos: oi / preço / "como é Candeias?" / "quero ver foto" / "tô interessado"

### Etapa 6 — Versionamento
- [ ] Commits incrementais por etapa
- [ ] Criar repositório no GitHub (privado) e fazer push
- [ ] Adicionar README com instruções de setup

### Etapa 7 — Deploy (semana que vem)
- [ ] Escolher VPS (Hostinger / DigitalOcean / Contabo)
- [ ] Domínio + HTTPS (Caddy ou nginx + Certbot)
- [ ] PM2 ou systemd para manter `server.py` rodando
- [ ] Logs + monitoramento básico

---

## 🎬 Pedido pendente do usuário

> "quero arrumar a entrada de video — não era essa versão, é v2"
> "quero que coloque o vídeo dela em IA falando logo depois do que já tem"

**Tradução:** a abertura atual está usando uma versão errada de vídeo. Trocar pela v2 e adicionar logo depois um vídeo da Priscila gerado por IA.

---

## 🚧 Decisões pendentes

1. Caminho A (só Claude pago) / B (só Gemini grátis) / **C (híbrido)** ← recomendado
2. Tom dos prompts (formal editorial vs casual conquistense)
3. Volume inicial esperado (vai influenciar limites de rate)
4. CRM/lead capture (Google Sheets? Notion? banco SQLite local?)

---

## 📝 Histórico de commits

- `c16b9fb` — Inicial: site v3-editorial com vídeos de abertura encadeados
- `83d8bc8` — chore: adiciona requirements.txt (FastAPI + Anthropic + Gemini)
