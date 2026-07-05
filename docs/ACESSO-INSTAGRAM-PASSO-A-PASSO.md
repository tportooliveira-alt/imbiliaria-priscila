# 📲 Acesso total ao Instagram da Priscila — passo a passo (a executar)

Objetivo do Thiago: **dar ao Claude acesso total ao Instagram da Priscila** pra ler, analisar e
**publicar** (carrossel/reel/story) sem alimentar na mão. Esta é a **peça-chave**: o mesmo app +
tokens destrava de uma vez **Instagram (publicar) + Meta Ads + Meta Lead Ads**.

> ⚠️ Atualizado em 19/06/2026. A Meta **renomeou as permissões** (as antigas `instagram_basic` e
> `instagram_content_publish` foram descontinuadas em **27/01/2025**). Use os nomes novos abaixo.
> Relacionados: `INTEGRACOES-INSTAGRAM-METAADS.md`, `META-LEAD-ADS.md`, `CAMPANHA-INSTAGRAM-PRISCILA.md`.

## 💸 Custo = ZERO (decisão do Thiago: sem custos)
**Todo este caminho é gratuito.** A Meta **não cobra** por: criar o app, Graph API, gerar token,
**publicar** (carrossel/reel/story), ler o Meta Ads, nem pelo App Review. GA4, Google Tag e Meta Pixel
também são grátis. Instagram orgânico é grátis. **Eu gero os carrosséis sem custo.**
- ✅ **Único gasto possível = verba de anúncio** (Meta/Google Ads), e isso é **opcional** — dá pra
  rodar 100% orgânico no Insta.
- ❌ **Evitar (são pagos):** Supermetrics, Windsor.ai, Ryze AI e atalhos tipo Upload-Post. **Não
  precisamos de nenhum** — a **Graph API direta na VPS** (nosso método) faz tudo de graça.

---

## 🧱 Pré-requisitos (sem isso NADA da API funciona)
- [x] **IG da Priscila = conta Profissional (Business)**, não pessoal nem só "Criador".
      ⚠️ Publicação de **Reels via API só funciona em conta Business** — Criador não publica por API.
      (No app do Insta: Configurações → Conta → *Mudar para conta profissional* → **Empresa/Business**.)
- [x] **Página do Facebook** da Priscila criada e **vinculada ao Instagram**
      (no app do Insta: Configurações → *Central de Contas* → vincular a Página do FB).
- [ ] Acesso de **administrador** da Priscila ao **Meta Business Suite** (business.facebook.com).
- [ ] Login da Priscila disponível na hora de criar o app (OAuth/aceite de convite).

> Status 01/07/2026: Thiago confirmou que o Instagram ja e Business e esta vinculado a uma Pagina FB.

---

## 🔑 Passo 1 — Criar o Meta App (uma vez)
1. ✅ Entrar em **developers.facebook.com** com a conta da Priscila (ou um perfil admin do negócio dela).
2. ✅ **Meus Apps → Criar app** → tipo **Negócios/Business** → vincular ao **Meta Business** dela.
3. ✅ App principal criado: `Priscila Social API` (`2485154298661482`) no portfolio `Corretora de imóveis Priscila Vasconcelos`.
4. ⚠️ App duplicado criado no processo: `1028260512990922`. Nao arquivar ate o principal estar validado.
5. ⏳ Proximo clique: adicionar/configurar o produto **Graph API do Instagram**.
6. Depois: adicionar/configurar **API de Marketing** e **Webhooks** — ver `META-LEAD-ADS.md`.

## 🔑 Passo 2 — Permissões a pedir no app (nomes NOVOS de 2026)
- `instagram_business_basic` — ler dados básicos da conta.
- `instagram_business_content_publish` — **criar e publicar** mídia (foto/carrossel/reel/story).
- `pages_show_list`, `pages_read_engagement`, `business_management` — ligar Página/negócio.
- (Para Meta Ads) `ads_read` — ler campanhas/ROAS; (Lead Ads) `leads_retrieval`, `pages_manage_ads`.

## 🔑 Passo 3 — Gerar o token (longa duração)
1. No **Graph API Explorer** (ou *Usuário de Sistema* no Business Suite → mais estável/permanente),
   gerar token com as permissões acima.
2. **Estender** para token de longa duração (≈60 dias) **ou** usar **Usuário de Sistema** (não expira).
3. Anotar: **IG Business Account ID**, **Page ID** e o **token**.

Antes de gerar token real, rodar localmente:

```powershell
python -m pytest tests\test_instagram.py tests\test_mcp_instagram_safety.py -q
```

Esses testes confirmam que a ponte falha fechada sem credenciais e que publicacao no MCP continua desligada por padrao.
Depois de colocar token/IDs no `.env` seguro, o primeiro teste pelo MCP deve ser `ig_status`. Ele mostra somente booleanos e campos faltantes; nao mostra o token.

## 🔑 Passo 4 — Me entregar as credenciais (com segurança)
Colocar no **`.env` do site (VPS)** — **nunca no git** (já protegido pelo `.gitignore`/`.claudeignore`):
```
META_APP_ID=...
META_APP_SECRET=...
META_PAGE_TOKEN=...            # token longo / usuário de sistema
IG_BUSINESS_ACCOUNT_ID=...
META_GRAPH_VERSION=v23.0       # usar a versão atual da Graph API
```
> A partir daí eu leio/publico no Insta e leio o Meta Ads direto, sem você colar nada na mão.

---

## ⏳ App Review (atenção ao prazo)
Publicar via API exige **App Review** da Meta para `instagram_business_content_publish`: submeter um
**screencast** mostrando o fluxo completo. **Leva ~2–4 semanas.** Enquanto não aprova, dá pra testar com
as contas de **administrador/testador** do próprio app (sem review). Então: **submeter o review cedo**.

## 📏 Limites bons de saber
- **100 publicações por API a cada 24h** por conta (soma reels+foto+carrossel+story). Folga total pro nosso volume.
- Fluxo de publicação = **2 chamadas**: cria o "container" da mídia → publica o container.

---

## 🚦 Caminho recomendado (do mais rápido ao completo)
1. ✅ **Confirmar pré-requisitos** (IG Business + Página FB vinculada).
2. ✅ **Criar o app**: `Priscila Social API` (`2485154298661482`).
3. ⏳ Configurar `Graph API do Instagram`, `API de Marketing` e `Webhooks`.
4. ⏳ Gerar token/IDs com segurança (sem colar em chat/Markdown/git). Já testo leitura/publicação com conta de teste.
5. **Submeter o App Review** de `instagram_business_content_publish` (começa o relógio de 2–4 sem).
6. Enquanto o review corre: eu gero os **10 carrosséis** já planejados (`CAMPANHA-INSTAGRAM-PRISCILA.md`).
7. Review aprovado → **publicação automática** (eu posto do Cowork) + **rotina de stories de notícias**.

### Atalho sem App Review — ❌ descartado (tem custo)
Existem serviços (Upload-Post e similares) que publicam sem App Review, mas são **pagos/terceiros**.
Como a decisão é **custo zero**, ficamos na **Graph API direta** (gratuita, sob nosso controle). Enquanto
o review não aprova, publicamos manualmente os carrosséis que eu gerar (também sem custo).
