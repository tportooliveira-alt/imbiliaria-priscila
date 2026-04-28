# Plano de Ação — Modernização IA + UX (abril/2026)

> Documento de trabalho. Atualizar checkboxes conforme avança.
> Base: análise dos top sites imobiliários (Zillow, Redfin, Compass, Realtor, Rightmove, Idealista, Immobiliare, QuintoAndar, Loft) + auditoria do nosso site.

---

## 🎯 Objetivo

Trazer ao site da Priscila os **8 padrões de ouro** que separam imobiliárias top do resto do mercado, sem inflar a stack (manter Babel-standalone, FastAPI + SQLite).

**Padrões-alvo:**
1. Busca semântica em linguagem natural
2. AVM com IC visível (faixa min/média/máx + fatores)
3. Match score personalizado por busca
4. Alertas inteligentes (novo imóvel / queda de preço)
5. Mapa de calor + draw polygon
6. Tour 3D
7. Co-pilot do corretor
8. Descrição editorial gerada por IA

---

## 📊 Diagnóstico atual (resumo)

| Categoria | Status | Observação |
|---|---|---|
| Frontend | ✅ Completo | V3 Editorial, 12+ componentes React, hash routing, PWA |
| Backend | ✅ Funcional | FastAPI + SQLite, roteador IA 6 vias |
| IA conversacional | 🟡 MVP | Cascade Gemini/Claude, persona Priscila, sem embeddings |
| Admin/CRM | ✅ Operacional | CRUD + análise lead, falta UI de co-pilot e gerar descrição |
| SEO | 🟡 Básico | title/desc dinâmico, falta OG/Twitter/Schema.org |
| Performance | 🟡 Bom | lazy load, srcSet, SW cache |
| Acessibilidade | 🟡 Parcial | falta ARIA live, focus management |
| Dados | 🔴 Mock | `data.jsx` hardcoded; precisa puxar `/api/imoveis` |

---

## 🌊 Ondas de implementação

### 🔥 Onda A — Quick Wins ✅ **CONCLUÍDA**

**Objetivo:** alto impacto + baixo risco, todas as mudanças no front + 1 endpoint pequeno.
**Status final:** 178 testes passando, sem regressão.

- [x] **A.1** — Match score dinâmico nos cards
- [x] **A.2** — Favoritos com persistência localStorage
  - [x] Hook `useFavoritos` + `BotaoFavoritar`
  - [x] Contador no nav (`ContadorFavoritosNav`)
  - [x] Página `#/favoritos` integrada ao roteador
  - [x] Botão integrado em `PropertyGrid` e `PaginasDetalhe`
- [x] **A.3** — Comparador de até 3 imóveis
  - [x] Drawer + tabela lado a lado (10 atributos)
  - [x] Botão `BotaoComparar` no card
  - [x] FAB flutuante quando há itens
  - [x] `<ComparadorDrawer/>` montado nas 4 rotas (home, imóvel, bairro, favoritos)
  - [x] Footer com WhatsApp para pedir opinião da Priscila
- [x] **A.4** — AVM régua min/central/máx com 3 marcadores posicionados + tooltips
- [x] **A.5** — SEO completo
  - [x] Meta description, keywords, canonical no `index.html`
  - [x] Open Graph + Twitter Card
  - [x] JSON-LD `RealEstateAgent` estático no `index.html`
  - [x] JSON-LD `RealEstateListing` dinâmico em `PaginasDetalhe` (injetado/removido com `useEffect`)
- [x] **A.6** — Validação
  - [x] `pytest -q` → **178 passed**
  - [ ] Smoke manual `/v3-editorial/` (a executar pelo usuário)

**Arquivos novos:**
- `shared/Favoritos.jsx` (~165 linhas)
- `shared/Comparador.jsx` (~210 linhas)
- `shared/favoritos-comparador.css` (~290 linhas)

**Arquivos editados:**
- `v3-editorial/index.html` — SEO + scripts novos
- `v3-editorial/app.jsx` — rota favoritos, drawer global, contador no nav
- `shared/PropertyGrid.jsx` — botões favoritar + comparar
- `shared/PaginasDetalhe.jsx` — rota `#/favoritos`, JSON-LD dinâmico
- `shared/AvaliacaoImovel.jsx` — régua com 3 marcadores

**Commit sugerido:**
```
feat(onda-a): favoritos + comparador + SEO Schema.org + AVM régua melhorada

- Wishlist persistente (localStorage) com sync entre abas e contador no nav
- Comparador lateral até 3 imóveis com 10 atributos + CTA WhatsApp
- AVM régua min/central/máx com tooltips
- Open Graph, Twitter Card e JSON-LD (RealEstateAgent + RealEstateListing)
- 178 testes passando
```

---

### ⚙️ Onda B — Diferenciação IA

**Objetivo:** trazer o que os tops do mercado têm e nós não.

- [x] **B.1** — Busca semântica em linguagem natural ✅
  - [x] Módulo `app/busca_natural.py` (heurística regex + refinamento Gemini Flash JSON-only)
  - [x] Endpoint `POST /api/busca-natural` em `routes_publicas.py`
  - [x] Componente `shared/BuscaNatural.jsx` + `shared/busca-natural.css` montado acima do PropertyGrid
  - [x] Fallback gracioso sem `GOOGLE_API_KEY` (apenas heurística)
  - [x] 6 testes novos em `tests/test_busca_natural.py` — todos passando
  - **Frases entendidas:** bairro + tipo + quartos + faixa de preço + área + tags (piscina, churrasqueira, vista, varanda, suíte etc.)
- [ ] **B.2** — Co-pilot do corretor no `/admin`
  - Ao abrir lead, dispara `/api/analisar-lead`
  - Card "Resumo do lead": stage, próximas perguntas, objeções, melhor horário
  - Botão "Sugerir resposta" (chama Claude com contexto)
- [ ] **B.3** — Botão "Gerar descrição editorial" no admin
  - CRUD imóvel → botão usa rota `DESCRICAO` existente
  - Preview + aceitar/regenerar
- [ ] **B.4** — Alertas de novos imóveis por filtro salvo
  - Tabela `alertas_busca` (já mencionada no `AlertaBuscaBtn`) — verificar se existe
  - Cron diário cruza alertas vs. imóveis novos
  - Notificação via WhatsApp (depende de Onda W2 — pode começar com email)

---

### 🚀 Onda C — Avançado

**Objetivo:** features que dependem de pré-requisitos (W2 WhatsApp ou ML real).

- [ ] **C.1** — Mapa de calor de preços por bairro (Leaflet heatmap plugin)
- [ ] **C.2** — Draw polygon (busca por área desenhada no mapa) — Rightmove-style
- [ ] **C.3** — Geolocalização "imóveis perto de mim" (`navigator.geolocation`)
- [ ] **C.4** — Chat por voz (Web Speech API) no `AIChat`
- [ ] **C.5** — Embeddings reais para "imóveis parecidos" (precisa de pgvector ou solução SQLite)
- [ ] **C.6** — Pré-aprovação Caixa (mock inicial → integração depois)
- [ ] **C.7** — Tour 3D Matterport (substitui Pannellum em imóveis premium)

---

## ❌ Não replicar (lições do mercado)

- Carrossel infinito de "imóveis sugeridos" — cansa, não converte
- Bot WhatsApp com menu numerado — burro vs. nosso roteador semântico
- Tour 360 com fotos amadoras — passa amadorismo (esperar fotos profissionais)
- Multi-idioma agora — VDC é mercado local, sem ROI

---

## 🔗 Dependências entre ondas

```
Onda A (front + SEO)         → independente
Onda B.1 (busca semântica)   → independente
Onda B.2 (co-pilot admin)    → API /analisar-lead já existe
Onda B.3 (gerar descrição)   → rota DESCRICAO já existe
Onda B.4 (alertas)           → depende de Onda W2 (WhatsApp Evolution) p/ canal completo
Onda C.5 (embeddings)        → reescrever camada de busca
Onda W2 (WhatsApp)           → roadmap separado, paralelo
```

---

## 📋 Definição de "feito" por onda

Cada onda só é considerada concluída quando:
1. ✅ `pytest -q` passa (≥ testes existentes)
2. ✅ Smoke manual `/v3-editorial/` + `/admin/` no navegador
3. ✅ `.env.exemplo` atualizado se criou variável nova
4. ✅ Schema `app/db.py` atualizado se criou tabela nova
5. ✅ Checkbox marcado neste arquivo

---

## 🗓️ Próximos passos imediatos

1. ✅ Onda A concluída
2. ✅ `pytest -q` → 178 passed
3. **Smoke manual** pelo usuário em `/v3-editorial/` (favoritar card → ir em `#/favoritos` → comparar 3 imóveis → AVM régua)
4. Commit `feat(onda-a): favoritos + comparador + SEO + AVM régua`
5. Decidir entre Onda B.1 (busca semântica) ou retomar W2 (WhatsApp Evolution)

---

## 🔬 Pesquisa de mercado IA imobiliária 2025/2026

> Fonte: subagente de pesquisa rodado em paralelo durante a Onda A.

### Padrões com ROI confirmado

| # | Feature | Conversão | Status no nosso site |
|---|---|---|---|
| 1 | Chat IA com persistência | 70-80% | ✅ Já temos (cascade Gemini/Claude) |
| 2 | Simulador de financiamento | 60% clicam | ✅ Já temos (`SimuladorFinanciamento`) |
| 3 | Avaliação rápida via chat | 40% solicitam completa | ✅ Já temos (`AvaliacaoImovel` + AVM) |
| 4 | Lead scoring (temperatura) | 25-35% recicla | ✅ CRM já tem (interno apenas) |
| 5 | Busca semântica/visual | 30% CTR | 🟡 Onda B.1 |
| 6 | Geração de descrição IA | 15% (hype) | 🟡 Onda B.3 (usar com moderação) |

### Stack recomendada (próxima onda)

- **Embeddings:** Gemini Flash (`$0.075/M tokens`) — melhor custo-benefício
- **Vector store:** `sqlite-vec` (extensão SQLite, sem servidor extra) — ideal para nosso `data/site.db`
- **Visão:** Gemini Pro Vision (`$0.0025/1M pixels`) com cache local
- **AVM ML:** XGBoost com 50-100 features quando tivermos ≥5k imóveis vendidos histórico

### Tendências 2026 que NÃO devemos perseguir agora

- ❌ **Climate risk scores** — Zillow removeu em dez/2025 (assustava compradores)
- ❌ **Generative staging** — risco legal de "foto representativa" mal interpretada
- ❌ **AR/VR off-plan** — só faz sentido para grandes lançamentos
- ❌ **Banco vetorial managed (Pinecone)** — caro, SQLite serve

### Tendências que VALEM a pena no roadmap

- ✅ **Busca semântica multimodal** (texto + foto) — diferencia muito (B.1)
- ✅ **Agentic AI** (follow-up automático WhatsApp) — alinhado com W2
- ✅ **Neighborhood intelligence** (scoring 0-10 por bairro) — encaixa no `BuscaBairros`
- ✅ **Voice search** — Web Speech API grátis, encaixe natural no `AIChat`

### Erros comuns a evitar

| Erro | Como evitamos |
|---|---|
| Chatbot 100% IA sem fallback | Já temos botão WhatsApp em todo lugar |
| AVM sem dados locais | Já usamos `m2_vdc.py` (tabela bairros VDC) |
| Tour 3D em site lento | Pannellum + lazy load |
| Search só por keyword | Onda B.1 corrige isso |
| Generative staging fake | Não vamos implementar |
