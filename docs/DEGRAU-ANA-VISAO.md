# Degrau — Ana enxergar imagens (visão multimodal)

**Status:** planejado, NÃO implementado. Aberto 17/06/2026.
**Regra do método:** ≤3 ajustes por vez · event-driven · barato. Este é **1 degrau só**.

## Problema (real, recorrente nas conversas)
A Ana responde "[mídia recebida]" e fica cega. Quando o lead manda imagem, ela entra em
loop "não consigo ver, me explica" e o lead **esfria**. Casos reais já vistos:
- Ane Caroline → print da **simulação da Caixa** (capacidade de financiamento)
- Jorge → **anúncio de imóvel** de outro lugar
- Priscila → fotos de **fachada/ambientes** (material de treino)

## Degrau proposto (mínimo, barato)
Quando — e SÓ quando — chegar mídia (`[midia recebida]`), rodar **1 chamada de visão**
(Claude multimodal) com um prompt curto que classifica + extrai o essencial:
- **Tipo:** simulação Caixa / anúncio de imóvel / documento / foto de imóvel / outro
- **Campos úteis** por tipo (ex.: simulação → valor aprovado, entrada, parcela; anúncio →
  bairro, valor, m²) — sempre com "não sei dizer" quando ilegível (NUNCA inventar).
- Devolve um resumo de 1-2 linhas que a Ana usa pra **continuar a conversa** em vez de travar.

## Limites (pra ficar barato e seguro)
- 1 imagem por vez, só no evento de mídia (não fica "olhando" nada sem gatilho).
- Cache/idempotência por `chave_mensagem` (não reprocessa a mesma mídia).
- Sem OCR pesado/serviço externo novo: usa o modelo que já temos.
- Se a visão falhar, cai no comportamento atual (pede pra pessoa descrever) — não quebra.

## Onde mexe (a confirmar na implementação)
- Pipeline de entrada do WhatsApp (onde hoje gera "[midia recebida]").
- Provavelmente `app/visao.py` (já existe `disponivel_sem_chave` nos testes) + o handler da Ana.

## Verificação
- 1 print de simulação da Caixa → Ana extrai valor aprovado e segue a conversa.
- 1 anúncio → Ana identifica bairro/valor.
- Mídia ilegível → Ana diz que não deu pra ler e pede o dado, sem inventar.
- Custo por mídia medido e logado (manter barato).

## Fora deste degrau (próximos)
- Responder com áudio na voz da Priscila sobre o que viu.
- Integração Google Calendar (ver `INTEGRACAO-GOOGLE-CALENDAR.md`).
