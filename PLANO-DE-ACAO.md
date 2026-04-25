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

## 🧮 Plano primordial — Simulador de financiamento + Avaliação de imóvel

> Dois módulos comerciais que multiplicam a captura: o cliente sai do site sabendo "quanto vai pagar por mês" e "quanto a casa dele vale". Ambos viram lead automático.

### Módulo A — Simulador de financiamento

**Objetivo:** o visitante digita preço do imóvel + entrada + prazo e recebe parcela mensal estimada (SAC e PRICE), CET aproximado e quanto precisa de renda.

**Como funciona em 3 níveis:**

1. **MVP local (sem API externa) — semana 1** ✅ FEITO 25/04/2026
   - [x] Calculadora 100% Python no backend (`app/financiamento.py`):
     - SAC: amortização constante, parcela decrescente
     - PRICE (Tabela Price): parcela fixa, juros decrescentes
     - Entrada: `valor_imovel`, `entrada`, `prazo_meses`, `taxa_anual`
     - Saída: `parcela_inicial`, `parcela_final`, `total_pago`, `total_juros`, `renda_minima`
   - [x] Endpoint `POST /api/simular-financiamento`
   - [x] Componente React `<SimuladorFinanciamento/>` no v3-editorial:
     - Sliders para preço, entrada %, prazo (120/240/360 meses)
     - Toggle SAC ↔ PRICE
     - Gráfico simples de evolução das parcelas
     - Botão "Quero falar com a Priscila" → joga no chat já preenchido
   - [x] Tabela de taxas-base por banco (Caixa SBPE, Pró-Cotista, BB, Itaú, Bradesco, Santander) em `app/financiamento.py::TAXAS_BANCOS`

2. **Integração SBPE/Caixa — semana 2**
   - [ ] Replicar regras do **Pró-Cotista / SBPE / Casa Verde e Amarela** (faixas de renda, % máx. financiável, idade máxima do mutuário)
   - [ ] Validador: comparar parcela com 30% da renda informada → flag "comprometimento ok/alto"
   - [ ] Buscar taxas atualizadas via grounding Gemini (rota `INFO_VDC` já tem Google Search) com cache diário em arquivo JSON

3. **Pré-aprovação real (médio prazo)**
   - [ ] Avaliar parceria com correspondente bancário local (CrediHome / Melhortaxa / direto Caixa)
   - [ ] Formulário curto pré-aprovação (CPF, renda, score Serasa via API paga)
   - [ ] Webhook do parceiro devolvendo "aprovado / análise / reprovado" no chat

**Métricas-alvo:**
- Tempo médio simulação → contato: < 2 min
- Conversão simulação → lead qualificado: > 25%
- Lead com renda informada vira automaticamente `stage = quente`

---

### Módulo B — Avaliação de imóvel (AVM editorial)

**Objetivo:** dono que quer vender informa endereço/bairro + características e recebe faixa de valor estimada + relatório curto. Captura lead vendedor (lado mais escasso da imobiliária).

**Como funciona em 3 níveis:**

1. **MVP heurístico — semana 1** ✅ FEITO 25/04/2026
   - [x] Base de m² médio por bairro de VDC em `app/m2_vdc.py` (14 bairros: Candeias, Boa Vista, Recreio, Patagônia, Centro, Ibirapuera, Alto Maron, Guarani, Primavera, Felícia, Urbis, Brasil, Panorama, Bateias)
   - [x] Fórmula: `valor = m2_bairro × area × fator_padrão × fator_idade × fator_estado × fator_extras`
     - `fator_padrão`: simples / médio / alto / luxo
     - `fator_idade`: novo / 0-10 / 10-20 / 20+
     - `fator_estado`: reformado / bom / regular / precisa reforma
     - `fator_extras`: suíte +3%, vaga +2-4%, área externa +5%, 4+ quartos +4%
   - [x] Endpoint `POST /api/avaliar-imovel`
   - [x] Componente `<AvaliacaoImovel/>` com:
     - Stepper de 5 perguntas (bairro, área, quartos+suítes+vagas, padrão+estado, idade+área externa)
     - Resultado: faixa mínima/máxima + texto editorial (fallback estático, Claude na semana 2)
     - "Quer avaliação presencial?" → vira lead de captação via chat

2. **Análise multimodal — semana 2**
   - [ ] Upload de até 5 fotos do imóvel
   - [ ] Gemini 2.5 Pro (rota `VISAO`) descreve o que vê: padrão de acabamento, estado de conservação, pontos fortes/fracos
   - [ ] Ajusta os fatores automaticamente com base na análise da imagem
   - [ ] Gera mini-relatório PDF (ReportLab) com fotos + faixa de valor + texto

3. **Comparativo de mercado — médio prazo**
   - [ ] Scraper leve em imóveis ativos da própria Priscila + portais (OLX/Vivareal/Zap) com `httpx` + parser
   - [ ] Banco SQLite com histórico de preços por bairro
   - [ ] Modelo de regressão simples (`scikit-learn`) treinado com 100-200 imóveis reais
   - [ ] Atualização semanal automática

**Métricas-alvo:**
- Cada avaliação online vira contato em até 48h
- Captação de imóveis para vender: meta 5 novos/mês via canal digital
- Relatório PDF entregue como brinde mesmo se o lead não converter (marketing orgânico)

---

### Ordem sugerida de execução

1. **Semana 1** — Simulador MVP (calculadora pura) + Avaliação MVP (heurística por bairro)
   - Os dois ficam prontos no mesmo sprint pois compartilham a base de dados de VDC.
2. **Semana 2** — Multimodal nas duas pontas (Gemini Pro com Search no simulador, Gemini Pro com fotos na avaliação)
3. **Semana 3** — Tracking integrado: cada simulação/avaliação alimenta o `/api/funnel` com novo estágio `simulou_financiamento` e `pediu_avaliacao`
4. **Semana 4** — Geração de PDF + envio por e-mail/WhatsApp
5. **Mês 2** — Pré-aprovação real e scraper de comparativos

### Dependências técnicas novas

- [ ] `numpy` + `pandas` (cálculo financeiro e dataset de m²)
- [ ] `reportlab` (PDF do relatório de avaliação)
- [ ] `recharts` ou `chart.js` no frontend (gráfico do simulador)
- [ ] Tabela `simulacoes` e `avaliacoes` no banco SQLite local

### Testes obrigatórios (regra do projeto: sempre testar)

- [ ] `tests/test_financiamento.py`: SAC vs PRICE, casos de borda (entrada 0%, prazo mínimo, taxa zero)
- [ ] `tests/test_avaliacao.py`: cada bairro retorna faixa coerente, fatores aplicam corretamente
- [ ] `tests/test_server_simulacao.py`: endpoints respondem 200 + payload validado

---

## 🔐 Painel admin da Priscila + galeria/carrossel + políticas de URL

> Hoje o catálogo de imóveis é estático em `shared/data.jsx`. Para escalar, a Priscila precisa de uma área logada onde ela mesma cadastra/edita imóveis com várias fotos preservando a qualidade, e o site precisa de URLs amigáveis e seguras.

### Módulo C — Área de login da corretora

**Objetivo:** Priscila acessa `/admin`, faz login e cadastra/edita imóveis sem mexer em código.

1. **Autenticação — semana 1**
   - [x] Tabela `usuarios` em SQLite (`app/db.py`): `id`, `email`, `senha_hash` (bcrypt), `role` (`admin` | `corretor`), `criado_em`
   - [x] Endpoints:`r`n     - `POST /api/auth/login` → JWT (`PyJWT`) com expiração de 8h
     - `POST /api/auth/logout`
     - `GET /api/auth/me`
   - [ ] Middleware `requer_admin` para proteger rotas `/api/admin/*`
   - [ ] Rate limit no login (5 tentativas / 15 min) para evitar brute force
   - [ ] Variável `.env`: `JWT_SECRET=` (gerada com `secrets.token_urlsafe(64)`)

2. **CRUD de imóveis — semana 1**
   - [ ] Tabela `imoveis`: `id`, `slug`, `titulo`, `bairro`, `tipo`, `quartos`, `suites`, `vagas`, `area_util`, `preco`, `descricao`, `caracteristicas` (JSON), `destaque` (bool), `ativo` (bool), `criado_em`, `atualizado_em`
   - [ ] Tabela `imagens`: `id`, `imovel_id` (FK), `arquivo`, `legenda`, `ordem`, `tipo` (`capa` | `sala` | `cozinha` | `quarto` | `banheiro` | `area_externa` | `planta`)
   - [ ] Endpoints:
     - `GET /api/imoveis` (público, com filtros)
     - `GET /api/imoveis/{slug}` (público)
     - `POST /api/admin/imoveis` (cria)
     - `PUT /api/admin/imoveis/{id}` (edita)
     - `DELETE /api/admin/imoveis/{id}` (soft delete via `ativo=false`)
     - `POST /api/admin/imoveis/{id}/imagens` (upload múltiplo)
     - `PUT /api/admin/imoveis/{id}/imagens/ordem` (reordenar)
     - `DELETE /api/admin/imagens/{id}`

3. **Painel React em `/admin` — semana 2**
   - [ ] Tela de login editorial (mesmo tom do site)
   - [ ] Lista de imóveis com busca + ordenação + toggle ativo/destaque
   - [ ] Formulário de imóvel com:
     - Campos básicos (título, preço, bairro, etc.)
     - Drop zone de imagens (drag-drop múltiplo, preview, reordenar arrastando)
     - Editor de descrição com botão "✨ Reescrever com IA" (chama Claude Sonnet)
     - Sugestão automática de tags pela IA com base nas fotos (Gemini Pro Vision)
   - [ ] "Visualizar como visitante" antes de publicar

### Módulo D — Galeria + carrossel ao clicar na foto

**Objetivo:** visitante vê o card do imóvel, clica na foto → abre lightbox em tela cheia com carrossel mostrando todos os cômodos (sala, quarto, banheiro, cozinha, área externa, planta).

1. **Galeria simples no card — semana 1**
   - [x] Card de imóvel com foto principal + indicador "📸 12 fotos"
   - [ ] Hover desktop: troca lenta entre 3 primeiras fotos (preview animado)

2. **Lightbox em tela cheia — semana 1**
   - [x] Componente `<GaleriaImovel/>` com:
     - Backdrop preto 95% + animação editorial de entrada
     - Foto principal grande (cabe na tela, sem cortar)
     - Setas ◄ ► (teclado, swipe mobile, click)
     - Miniaturas embaixo agrupadas por cômodo: `Sala (3) | Cozinha (2) | Quarto 1 (4)…`
     - Contador `5 / 18`
     - Tecla `Esc` fecha
     - [ ] URL muda para `/imovel/{slug}/foto/{n}` (deep link compartilhável)

3. **Pipeline de imagens preservando qualidade — semana 1**
   > Regra: a Priscila joga a foto original do celular/câmera (geralmente 4-12 MB) e o site não pode degradar visualmente.
   - [x] Dependência: `Pillow` + `pillow-heif` (HEIC do iPhone)
   - [x] Ao subir, gerar 4 versões em WebP + 1 original guardada:
     - `original.jpg` (intacto, q=95)
     - `2400.webp` (lightbox/4K, qualidade 85)
     - `1200.webp` (card grande, qualidade 82)
     - `600.webp` (thumb, qualidade 78)
     - `200.webp` (placeholder/blur, qualidade 60)
   - [x] HTML usa `<picture>` com `srcset` + `loading="lazy"` + `decoding="async"`
   - [x] Servir via FastAPI `StaticFiles`
   - [ ] `Cache-Control: public, max-age=31536000, immutable` (a configurar no deploy)
   - [x] Magic-byte validation + EXIF strip + max 15 MB
   - [x] Limite de 30 fotos por upload; pasta `assets/imoveis/{slug}/{uuid}/`

### Módulo E — Políticas de URL e segurança

1. **URLs amigáveis (slugs)**
   - [ ] `/imovel/casa-3-suites-candeias-vdc` (slug = `slugify(titulo + bairro + cidade)`)
   - [ ] Redirect 301 de IDs antigos → slug novo
   - [ ] `/bairro/candeias`, `/bairro/boa-vista` (página por bairro com SEO)
   - [ ] Sitemap automático em `/sitemap.xml`
   - [ ] `robots.txt` permitindo crawl do site público e bloqueando `/admin/*` e `/api/admin/*`

2. **Cabeçalhos de segurança (FastAPI middleware)**
   - [ ] `Content-Security-Policy` (whitelist: self, CDN React/Babel, googleapis, anthropic, fontes Google)
   - [ ] `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` (após HTTPS)
   - [x] `X-Content-Type-Options: nosniff`
   - [x] `X-Frame-Options: DENY`
   - [x] `Referrer-Policy: strict-origin-when-cross-origin`
   - [x] `Permissions-Policy: camera=(), microphone=(), geolocation=()`

3. **Hardening do upload**
   - [ ] Aceitar somente `image/jpeg`, `image/png`, `image/webp`, `image/heic`
   - [ ] Validar magic bytes (não confiar só no `Content-Type`)
   - [ ] Tamanho máximo 15 MB por arquivo, 30 arquivos por upload
   - [ ] Renomear todo arquivo para UUID (nunca usar nome original)
   - [ ] Stripping de EXIF (remove geolocalização da Priscila ou do dono do imóvel — LGPD)

4. **LGPD básico**
   - [ ] Página `/politica-de-privacidade` (cliente Priscila aprova)
   - [ ] Banner de cookies opcional (só se tiver analytics)
   - [ ] Endpoint `POST /api/lead/excluir-meus-dados` (LGPD art. 18)
   - [ ] Logs com retenção de 90 dias e anonimização

### Testes obrigatórios

- [ ] `tests/test_auth.py`: hash bcrypt, JWT válido/expirado, rate limit de login
- [ ] `tests/test_admin_imoveis.py`: CRUD completo + autorização (sem token = 401)
- [ ] `tests/test_upload_imagens.py`: rejeita PDF disfarçado, redimensiona corretamente, mantém aspect ratio, EXIF removido
- [ ] `tests/test_galeria.py` (frontend estrutural): `<GaleriaImovel/>` tem setas, miniaturas, contador, fecha com Esc
- [ ] `tests/test_url_policies.py`: headers de segurança presentes em toda resposta, slugs válidos, sitemap responde 200

### Ordem sugerida (alinhada com simulador/avaliação)

| Sprint | Foco |
|--------|------|
| Semana 1 | Simulador MVP + Avaliação MVP + Auth + CRUD imóveis + Pipeline de imagens + Lightbox |
| Semana 2 | Multimodal (Gemini Pro Vision em fotos) + Painel admin completo + URLs amigáveis |
| Semana 3 | Headers de segurança + LGPD + tracking unificado no funil |
| Semana 4 | PDF de avaliação + e-mail/WhatsApp + sitemap + SEO por bairro |

---

## 📝 Histórico de commits

- `c16b9fb` — Inicial: site v3-editorial com vídeos de abertura encadeados
- `83d8bc8` — chore: adiciona requirements.txt (FastAPI + Anthropic + Gemini)

