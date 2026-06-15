# 📸 Pesquisa — Postar no Instagram + Facebook (Claude + Priscila) 2026

Síntese do /deep-research (105 agentes, fontes oficiais Meta + ferramentas reais). **Veredito: TEM caminho maduro e seguro.**

## ✅ O que dá pra postar pelas APIs OFICIAIS da Meta
- **Instagram Content Publishing API** (conta **Business**): foto, **carrossel**, vídeo, **Reels** e **Stories**. Limite real
  **100 posts/24h** (não os antigos 25/dia). Fluxo: cria "container" → publica. Pré-requisito: **IG Business vinculado à Página FB**.
- **Facebook Pages API + Video API**: feed, foto, vídeo, Reels e Stories na Página.
- ⚠️ **Gargalo real:** publicar pela SUA própria API exige **App Review da Meta** (verificação de negócio + screencasts) →
  demora. **Atalho:** usar uma ferramenta **já aprovada** (Postiz/Upload-Post/Metricool) que usa o OAuth oficial.

## 🏆 RECOMENDAÇÃO: **Postiz** (encaixa perfeito no nosso setup)
- **Open-source, auto-hospedável na NOSSA VPS** (Ubuntu) — controle total.
- Tem **servidor MCP OFICIAL** com comando pronto **`claude mcp add`** → o **Claude posta/agenda** (Cowork e Code).
- **30+ redes** incluindo IG e FB **via OAuth aprovado pela Meta** (sem dor de App Review).
- Tem **painel** → a **Priscila posta sozinha** também.
- _Ou seja: Claude automatiza + Priscila usa o painel, ambos na mesma ferramenta, segura._

**Alternativas** (se não quiser self-host):
- **Upload-Post** — API REST unificada + SDKs Python/Node + MCP hospedado.
- **Metricool** — **free** (1 marca, MCP, posts limitados); auto-publicação de IG/FB/Reels só no **pago**.

## 🔒 Segurança (regra forte da pesquisa)
- **SEMPRE** OAuth/API **oficial** da Meta (direto OU via Postiz/Upload-Post/Metricool — todos usam fluxo aprovado).
- ❌ **NUNCA** ferramentas não-oficiais que automatizam o app/web do Instagram → **violam os termos e arriscam BAN da conta**.
- Tokens: escopos mínimos (`instagram_business_content_publish`, `pages_manage_posts`), **fora do git** (.env).

## 🎯 Plano de aplicação (no nosso caso)
1. **Pré-requisito (Thiago/Priscila):** IG da Priscila como **Business** + vinculado à **Página do Facebook**.
2. **Instalar o Postiz na VPS** (Docker) → conectar IG + FB pelo OAuth oficial.
3. **`claude mcp add` do Postiz** → no Cowork, eu **gero o carrossel + posto/agendo**.
4. **Priscila** usa o painel do Postiz pra postar/agendar quando quiser.
5. **Workflow primeiro** (a dica da aula): definir o passo a passo do post (gancho → arte → legenda → CTA pra calculadora) ANTES de automatizar.

## ⚠️ Ressalvas (honestidade)
- Tudo muda rápido (Meta mudou limites e permissões em 2024-2025) — **revalidar versão da Graph API antes de implementar**.
- MCP do Upload-Post: anunciado no marketing, mas **ausente dos docs técnicos** — preferir Postiz (MCP oficial documentado).
- Stories por API é mais frágil que feed/Reels — testar.

_Fontes: developers.facebook.com (IG Content Publishing, Pages API), Postiz docs/MCP, Upload-Post, Metricool. Cruzar com
`INTEGRACOES-INSTAGRAM-METAADS.md` (Composio/Windsor/Unipile da aula)._
