# Plano de Ação — Site Priscila Vasconcelos Imóveis

> Documento vivo. Atualize conforme avançar. Cada passo tem checkbox.

**Cliente:** Priscila Vasconcelos · CRECI/BA 29.231
**Praça:** Vitória da Conquista — BA
**Pasta do projeto:** `C:\Users\Thiago Porto\OneDrive\Desktop\site-imobiliaria\`
**Branch git:** `main` (local, sem remote ainda)

---

## 🎯 Objetivo final

Site editorial com **IA híbrida (Gemini + Claude)** que:

1. Abre com vídeo cinematográfico (Ken Burns → IA falando → IA casa → Priscila opcional → site)
2. Capta lead via chat real plugado em modelos de IA
3. Faz triagem + qualificação + busca de imóvel + negociação
4. Roda local em `http://localhost:8000` agora; depois sobe para VPS

---

## 🧠 Arquitetura de IA (model routing)

```
Mensagem chega
   ↓
[Roteador — Gemini 2.5 Flash, baixa latência]
   ├─ Triagem simples       → Gemini 2.5 Flash
   ├─ Pergunta sobre VDC    → Gemini 2.5 Pro + Search grounding
   ├─ Negociar lead quente  → Claude Sonnet      (PT-BR formal, fechamento)
   ├─ Avaliar imóvel        → Gemini 2.5 Pro     (foto + leitura multimodal)
   ├─ Descrição editorial   → Claude Sonnet      (texto rico, tom revista)
   ├─ Follow-up frio        → Claude Haiku       (barato, cordial)
   └─ Análise pós-conversa  → Gemini 2.5 Pro     (resumo executivo + score do lead)
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
- [x] Copiar `notas.txt` (chaves de API) para `C:\segredos\notas.txt` (fora da nuvem)
- [ ] Apagar `notas.txt` original do OneDrive (`C:\Users\Thiago Porto\OneDrive\Desktop\notas.txt`)
- [x] Confirmar que `.gitignore` cobre `.env`, `notas.txt`, `chave*`, `secrets/`
- [ ] Resolver resíduos do IObit Uninstaller (pasta + serviço `IObitUnSvr` parado)

### Etapa 1 — Restaurar mídias da abertura
- [x] Decidir nomes finais de vídeos atuais: `ia-falando.mp4` + `ia-casa.mp4` + `priscila-fala.mp4` (opcional)
- [x] Restaurar estrutura completa de assets/shared e imagem `priscila-new-hero.jpeg`
- [x] Adicionar vídeo da IA e segundo vídeo na sequência de abertura
- [x] Garantir encadeamento atual: Ken Burns → IA falando → IA casa → Priscila opcional → site

### Etapa 2 — Backend (server.py)
- [x] Criar `.env.exemplo` com `GOOGLE_API_KEY=` e `ANTHROPIC_API_KEY=`
- [x] Criar `server.py` (FastAPI) com:
   - [x] Endpoint `POST /api/chat` recebendo `{message, history}`
   - [x] Função `roteador()` que classifica a mensagem (triagem/vdc/negociacao/visao/descricao/followup)
   - [x] Cliente Gemini (Flash + Pro com Search)
   - [x] Cliente Claude (Sonnet + Haiku)
   - [x] Fallback automático se uma chave estiver faltando
   - [x] CORS liberado para `localhost`
   - [x] Servir arquivos estáticos de `v3-editorial/`
- [x] Criar `python-dotenv` carregando `.env`

### Etapa 3 — Frontend conectado
- [x] Localizar widget de chat no `v3-editorial/index.html`
- [x] Substituir mock por `fetch('/api/chat', ...)` real
- [ ] Streaming opcional (SSE) para resposta token-a-token
- [x] Tratar erros básicos de conexão/offline no chat

### Etapa 4 — Dados de Vitória da Conquista
- [x] Tabela de bairros (Candeias, Boa Vista, Recreio, Patagônia, Centro, etc.)
- [x] Catálogo inicial de imóveis (mock JSON)
- [x] Prompts do sistema com tom da Priscila

### Etapa 5 — Rodar local
- [x] `python -m venv venv && .\venv\Scripts\Activate.ps1`
- [x] `pip install -r requirements.txt`
- [ ] Renomear `.env.exemplo` → `.env` e colar as 2 chaves
- [x] `python server.py` (via uvicorn) e abrir `http://localhost:8000`
- [x] Testar 5 fluxos com chaves reais: oi / preço / "como é Candeias?" / "quero ver foto" / "tô interessado"

### Etapa 6 — Versionamento
- [x] Commits incrementais por etapa
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
