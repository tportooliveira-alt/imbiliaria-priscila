# 📋 PENDÊNCIAS — tudo que falta (checklist mestre)

Lista viva de **tudo que ainda falta** no projeto da Priscila. Atualizado em 14/06/2026.
Marque `[x]` quando concluir. Prioridade: 🔴 alta · 🟡 média · 🟢 quando der.

---

## 🔄 Rodando agora (background — não precisa fazer nada)
- [x] ~~**Pesquisa: Claude Code + MCP + automação**~~ ✅ pronta (25/25 confirmadas) → virou `SETUP-DOIS-LADOS.md`
- [ ] **Pesquisa: 360° + vídeo + depoimentos na conversão** (task `wscezwr75`) → vira melhorias do site
- _Resultado de cada uma será empurrado aqui no chat quando terminar._

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

## 🎨 Design
- [ ] 🟢 Padronizar **botões secundários** (3ª da crítica — o principal, CTA dourado, já foi)
- [ ] 🟢 Aplicar o que a **pesquisa de 360°/vídeo/depoimentos** recomendar (seção de depoimentos, vídeo na home, etc.)

## 🧮 Calculadora de avaliação
- [ ] 🟢 **DEGRAU 2**: Método Evolutivo p/ casas de alto padrão (CUB/BA R-8 + depreciação Ross-Heidecke + fator de comercialização) — crava casa de alto padrão
- [x] ~~Calibração com 1.016 anúncios OLX (±0,1%)~~ (feito) · [x] ~~skill de teste~~ (feito)

## 📅 Google Agenda (integração)
- [x] ~~**Nível 1**: botão "📅 Google" em cada compromisso do admin~~ ✅ abre o Google Agenda preenchido (sem credencial)
- [ ] 🟡 **Nível 2 (auto-sync)**: criar/editar eventos direto na agenda da Priscila via Google Calendar API — exige **OAuth/credencial do Google do Thiago** (ou conector Google Calendar no Cowork). Decidir conta + autorizar.

## 🤖 Ana / WhatsApp / IA
- [ ] 🟡 **Resposta automática do WhatsApp**: validar em modo teste → produção
- [ ] 🟡 **Meta Lead Ads** → lead direto no funil
- [ ] 🟢 **GOOGLE_API_KEY vazia** — hoje a visão/classificação usa Claude (ok); só ligar Gemini se quiser baratear
- [ ] 🟢 Bug de boot inofensivo: `UNIQUE constraint usuarios.email` no restart (corrigir com `if not exists`)

## 🚀 Lançamento oficial
- [ ] 🔴 **Remover `noindex`** do `server.py` quando a Priscila aprovar (hoje o site está soft-launch, fora do Google)
- [ ] 🟡 Trocar a **senha temporária** do admin (`233024`) por uma definitiva
- [ ] 🟢 Depoimentos reais, vídeo, blog VDC, prospecção ativa

## ❓ Perguntas em aberto (decidir / pesquisar)
- [ ] Volume real de busca no Google em VDC justifica Google Ads, ou foco total em Meta?
- [ ] CPL/CPC real na microrregião (nenhuma fonte trouxe dado local)
- [ ] O que é "cowork" no fluxo: confirmado = modo **Cowork (Ctrl+2)** do app do Claude

---

### Como usar este arquivo
É o nosso **mapa do que falta**. Quando a gente sentar pra trabalhar, abre aqui, escolhe um 🔴 e ataca.
Eu mantenho atualizado a cada sessão. Relacionados: `ROTA-PROXIMA.md` (ordem priorizada),
`PESQUISA-LEADS-2026.md` (ads), `PLANO-MESTRE.md` (auditoria).
