# 🗓️ PLANO DE AMANHÃ — 15/06/2026 (combinado na madrugada · **todos os horários = Brasília, UTC-3**)

Âncora durável (no git) do que vamos atacar dia 15/06. Pra retomar: *"continua o plano de amanhã"*.
> O lembrete agendado é só da sessão (pode não disparar). **Este arquivo é a garantia.**

## A) 💰 Ads — quanto investir (Google + Meta)
- [ ] **Pesquisa**: quanto investir em Google Ads + Meta Ads dado NOSSO cenário (inventário 5-7 imóveis, cidade de
      interior, orçamento enxuto) — budget mínimo por canal, CPL esperado, nº de leads por faixa de investimento.
- [ ] **Calculadora de investimento em ads**: entra o orçamento → estima **leads, custo por lead e retorno potencial**,
      por canal (usa dados de `docs/PESQUISA-LEADS-2026.md`). No admin ou página/doc.
- [ ] **Por imóvel** (consultar tabela `imoveis`): listar **palavras-chave** (keywords de intenção: bairro+tipo+atributo)
      e **palavras negativas** (negative keywords) a excluir — uma lista por imóvel ativo.

## B) 📸 Instagram — integração + conteúdo + seguidores
- [ ] **Integração** do Instagram (publicar/agendar) — avaliar via conector/Meta Graph API; o que dá pra automatizar. **Ver `docs/INTEGRACOES-INSTAGRAM-METAADS.md`** (material do Thiago: Upload-Post p/ IG; Graph API na VPS p/ Meta Ads = Método 2, nosso caso).
- [ ] **Carrosséis**: modelos prontos (por imóvel, por bairro, "quanto vale seu imóvel") — conteúdo salvável/compartilhável
      (a pesquisa de leads mostrou que **saves/shares > curtidas** em 2026).
- [ ] **Notícias diárias relevantes** do mercado imobiliário / VDC — uma **Rotina** que traz o assunto do dia pra postar.
- [ ] **Crescer seguidores da Priscila**: o que fazer (frequência, formatos, conteúdo local, CTA) — plano prático.

## D) 🤝 Cowork ↔ Claude Code (VPS) — agente que conversa comigo + WhatsApp
- [ ] **WhatsApp de lembrete JÁ FUNCIONA** (Evolution API configurada, `whatsapp.disponivel()=True`; endpoint
      `/agenda/lembretes/enviar` + botão admin "📱 Enviar lembretes 24h"). Falta só **validar e tirar do modo teste**
      (`WHATSAPP_TEST_NUMBER`/cap) → produção. Combinar: lembrete automático de visita pro lead.
- [ ] **Expor o backend da VPS como servidor MCP** pra o agente do Cowork AGIR no sistema (mandar WhatsApp, marcar
      agenda, deploy) conversando comigo. Sai da pesquisa "nobres integrações". É o que o Thiago quer: Cowork ↔ VPS.

## C) 🌐 Ações pro site (cada melhoria)
- [ ] Lista priorizada de melhorias por página (ligado ao `PENDENCIAS.md`): pixels/rastreamento (🔴), depoimentos/vídeo
      (sai da pesquisa de 360°), padronização final de botões, etc.

## Ordem sugerida (degrau a degrau, custo baixo)
1. Olhar os relatórios que já terão caído (360°/vídeo, nobres integrações) + disparar a pesquisa de **budget de ads**.
2. Construir a **calculadora de ads** + **keywords por imóvel** (entrega concreta nº 1).
3. Plano de **Instagram** (carrossel + rotina de notícias + crescimento) e avaliar a integração de publicação.
4. Aplicar as **ações no site** que saírem das pesquisas.

_Tudo salvo em git + memória. Relacionados: `PENDENCIAS.md`, `PESQUISA-LEADS-2026.md`, `METODO-ESTUDO.md`,
`COMO-USAR-COWORK.md`._
