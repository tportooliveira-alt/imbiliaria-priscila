# 📋 PENDÊNCIAS — tudo que falta (checklist mestre)

Lista viva de **tudo que ainda falta** no projeto da Priscila. Atualizado em 14/06/2026.
Marque `[x]` quando concluir. Prioridade: 🔴 alta · 🟡 média · 🟢 quando der.

---

## 🔄 Rodando agora (background — não precisa fazer nada)
- [x] ~~**Pesquisa: Claude Code + MCP + automação**~~ ✅ pronta (25/25 confirmadas) → virou `SETUP-DOIS-LADOS.md`
- [x] ~~**Pesquisa: 360° + vídeo + depoimentos**~~ ✅ `PESQUISA-360-VIDEO-DEPOIMENTOS.md` — veredito: 360 é "bom ter"
  (não converte sozinho); **PROVA SOCIAL/depoimentos é a alavanca**; priorizar fotos+descrição. Vários "números" derrubados.
- [x] ~~**Pesquisa: nobres integrações (MCP/conectores)**~~ ✅ `PESQUISA-INTEGRACOES-2026.md` — expor VPS como custom
  MCP (plano F) é o caminho; Calendar/Gmail conectam no claude.ai; WhatsApp MCP é imaturo (seguir Evolution direta).
- _Resultados empurrados no chat._

## 🖥️ Setup "dois lados" + acesso direto (o objetivo: Claude lê/age sozinho, sem alimentar na mão)
- [x] ~~**`docs/SETUP-DOIS-LADOS.md`** — guia passo a passo~~ ✅ montado (rascunho pronto pra executar junto)
- [ ] 🔴 **Clonar a pasta no PC** (Windows): `git clone` do repo → projeto salvo no seu computador
- [ ] 🔴 **Conectar Google Drive** ao app do Claude (ainda NÃO está conectado nesta sessão)
- [ ] 🟡 Confirmar/usar conectores já disponíveis: Box, Microsoft 365, Slack, monday, Gamma, Metaview (precisam de login)
- [ ] 🟡 **MCP de arquivos/GitHub/banco** no Cowork — definir quais valem (sai da pesquisa)
- [ ] 🟡 **Instalar agent-browser no PC** (não na VPS) → extrair dados OLX/QA do site. Ver docs/FERRAMENTA-AGENT-BROWSER.md
- [x] ~~`deploy.sh` na VPS~~ (pronto) · [x] ~~`scripts/build_home.py`~~ (pronto e testado)
- [ ] 🟡 Testar o fluxo completo PC→push→VPS `./deploy.sh` de ponta a ponta

## 📈 Leads & Ads (do `docs/PESQUISA-LEADS-2026.md` + `ROTA-PROXIMA.md`)
- [ ] 🔴 **Rastreamento/pixels** (Meta Pixel + Google Tag) com conversões nomeadas: `calculadora_concluida`, `lead_anunciar`, `clique_whatsapp`, `agendar_visita` — **pré-requisito de qualquer anúncio**
- [x] ~~**1 pergunta qualificadora** na avaliação ("vende em quanto tempo?")~~ ✅ feita → vira urgência (alta/normal/baixa) + score (45-78) no lead (BANT)
- [ ] 🟡 **1º teste Meta Ads** (criativo local, geo 5-10 km p/ vendedor, orçamento pequeno)
- [ ] 🟢 **Instagram orgânico**: posts salváveis (guia de bairros, "m² no seu bairro" — usar nossos dados)
- [ ] 🟢 **Google Ads** (só se houver volume de busca local; keywords transacionais)
- [ ] 🟢 Acumular **~150 clientes fechados** no CRM → lookalike value-based no Meta

## 💰 Financeiro (admin)
- [ ] 🟡 **Lançar despesas reais** (VPS, domínio, anúncios, APIs de IA, CRECI, combustível) em Admin→Contas
- [ ] 🟡 **Lançar comissões** quando houver venda → fluxo de caixa e ROI ganham vida no dashboard
- [ ] 🟢 Cruzar gasto de ads × leads gerados = **CPL real local**
- [x] ~~Dashboard com gráficos + fluxo de caixa + pipeline da carteira~~ (feito)

## 🎨 Design / Confiança
- [x] ~~**Estrutura de DEPOIMENTOS**~~ ✅ feita: tabela + admin (aba Depoimentos) + seção no site (estrelas+média,
  escondida se vazia). **Falta**: Priscila COLETAR os reais (≥20, 4,5+) e cadastrar no admin. Textinho de pedido pronto.
- [ ] 🟢 Priorizar **fotos + descrições** dos imóveis (mais impacto que tour). 360° fica como opção (não investir pesado).
- [ ] 🟢 Padronizar **botões secundários** (3ª da crítica — o principal, CTA dourado, já foi)

## 🧮 Calculadora de avaliação
- [ ] 🟢 **DEGRAU 2**: Método Evolutivo p/ casas de alto padrão (CUB/BA R-8 + depreciação Ross-Heidecke + fator de comercialização) — crava casa de alto padrão
- [x] ~~Calibração com 1.016 anúncios OLX (±0,1%)~~ (feito) · [x] ~~skill de teste~~ (feito)

## 📅 Google Agenda (integração)
- [x] ~~**Nível 1**: botão "📅 Google" em cada compromisso do admin~~ ✅ abre o Google Agenda preenchido (sem credencial)
- [x] ~~**Nível 2 (auto-sync) — conector Google Calendar no Cowork**~~ ✅ **TESTADO E FUNCIONANDO (14/06)**: no Cowork,
  pedido "marca teste amanhã 9h" → evento "Teste" criado em 15/06 09h-10h na Google Agenda. No **Cowork** é só pedir que o
  Claude cria/edita/cancela. ⚠️ O conector só existe no **app do Thiago**, NÃO na sessão da VPS (headless).
- [ ] 🟢 **Backend auto-sync (reforço, opção 1 — Thiago pediu OS DOIS)**: site cria evento no Google Calendar sozinho. Precisa: `pip install google-api-python-client` no venv + **service account JSON** (Google Cloud) com o calendário compartilhado. Código a fazer (`app/gcal.py`).

## 🤖 Ana / WhatsApp / IA
- [ ] 🟡 **Resposta automática do WhatsApp**: validar em modo teste → produção
- [ ] 🟡 **Meta Lead Ads** → lead direto no funil
- [ ] 🟢 **GOOGLE_API_KEY vazia** — hoje a visão/classificação usa Claude (ok); só ligar Gemini se quiser baratear
- [ ] 🟢 Bug de boot inofensivo: `UNIQUE constraint usuarios.email` no restart (corrigir com `if not exists`)

## 🔬 Método de estudo (Thiago quer construir em cima)
- [x] ~~Salvar o **MÉTODO de estudo**~~ ✅ `docs/METODO-ESTUDO.md` (pipeline de pesquisa verificada)
- [ ] 🟡 **Criar algo com o método** (combinado p/ retomar): skill/rotina "pesquisa-priscila" + base `docs/estudos/` + cruzar com agent-browser

## 🆕 Decisões 15/06 (capturadas, fazer com o Thiago)
- [ ] 🔴 **Corrigir oferta: avaliação grátis ≠ LAUDO.** Online (calculadora) = GRÁTIS (ímã de lead). **Laudo de
  avaliação = serviço PAGO da Priscila** (profissional CRECI). Site hoje diz "avaliação final GRATUITA feita pela
  Priscila" (`anunciar.html` ~l.153 + textos de captura/okmsg) → MUDAR. Ana NÃO pode prometer laudo grátis.
  Definir: visita presencial p/ captar é grátis? preço do laudo?
- [ ] 🟡 **Campanha de marketing do Instagram da Priscila** — criar: linha editorial (guia de bairros, "quanto vale
  seu imóvel", dicas de VDC, bastidores da Priscila), carrosséis salváveis, calendário de posts, rotina de notícias
  diárias, e plano de captação de vendedores via Insta. Base: `PESQUISA-LEADS-2026.md` (saves/shares > curtidas).

## 🚀 Lançamento oficial
- [ ] 🔴 **Remover `noindex`** do `server.py` quando a Priscila aprovar (hoje o site está soft-launch, fora do Google)
- [ ] 🟡 Trocar a **senha temporária** do admin (`233024`) por uma definitiva
- [ ] 🟢 Depoimentos reais, vídeo, blog VDC, prospecção ativa

- [ ] 🟡 **MEDIR (não chutar):** CPL/CPC/CPM reais de VDC em R$ e % da comissão como CAC saudável — só saem dos
  NOSSOS números (pixel Meta/Google + CRM, 60–90 dias). Usar Google Keyword Planner p/ CPC estimado das keywords em VDC.

## ❓ Perguntas em aberto (decidir / pesquisar)
- [ ] Volume real de busca no Google em VDC justifica Google Ads, ou foco total em Meta?
- [ ] CPL/CPC real na microrregião (nenhuma fonte trouxe dado local)
- [ ] O que é "cowork" no fluxo: confirmado = modo **Cowork (Ctrl+2)** do app do Claude

---

### Como usar este arquivo
É o nosso **mapa do que falta**. Quando a gente sentar pra trabalhar, abre aqui, escolhe um 🔴 e ataca.
Eu mantenho atualizado a cada sessão. Relacionados: `ROTA-PROXIMA.md` (ordem priorizada),
`PESQUISA-LEADS-2026.md` (ads), `PLANO-MESTRE.md` (auditoria).
