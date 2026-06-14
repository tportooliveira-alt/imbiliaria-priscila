# 🤖 SKILL — Ana (IA de atendimento)

## O que faz
A **Ana** atende o cliente no site (chat flutuante + busca do hero) e no WhatsApp. Conversa em
português baiano, usa SÓ os imóveis reais da carteira, faz simulação e conecta com a Priscila.

## Onde está o código
- `app/dispatcher.py` — cérebro:
  - `responder(...)` — pipeline: classifica rota → cascata Gemini→Claude→fallback → devolve resposta.
  - `_montar_contexto_carteira()` — injeta os imóveis REAIS com **valores EXATOS** + descrição completa
    (foi onde corrigimos a Ana "arredondar" preço; agora R$ 6.500 é R$ 6.500, não "6 mil").
  - `_sem_markdown()` — limpa `**`/`#` da resposta (chat não renderiza markdown).
- `app/prompts.py` — `PRISCILA_PERSONA` (tom, regras: nunca inventar imóvel, valores exatos, sem markdown,
  financiamento é SIMULAÇÃO não promessa) + `SYSTEM_PROMPTS` por rota.
- `app/router.py` — classifica a mensagem em rota (TRIAGEM/NEGOCIACAO/INFO_VDC/VISAO/…).
- `app/clients.py` — `ClienteClaude` (texto + `classificar_imagem` p/ visão), `ClienteGemini`, `ClienteFallback`.
- Endpoint: `POST /api/chat` (em routes_publicas) — body `{message, history}` → `{resposta, lead_score, lead_stage…}`.

## Modelos (custo)
Sonnet pra rotas de qualidade (negociação, descrição); Haiku pra operação (triagem, followup) — barato.
Chaves no `.env`: `ANTHROPIC_API_KEY` (texto+visão), `GROQ_API_KEY` (transcrição de áudio), `ELEVENLABS_API_KEY` (voz). `GOOGLE_API_KEY` está VAZIA (Gemini desativado).

## Como testar
```bash
curl -s -X POST https://pvscelosimobiliaria.com/api/chat -H "Content-Type: application/json" \
  -d '{"message":"me fala do ponto comercial da Felicia","history":[]}'
# ver o contexto que a Ana recebe:
./venv/bin/python -c "from app.dispatcher import _montar_contexto_carteira; print(_montar_contexto_carteira())"
```

## Erros comuns
- **Ana fala valor/dado errado** → quase sempre é o CONTEXTO em `_montar_contexto_carteira()` (não a IA).
  Conferir o que ela recebe com o comando acima.
- **Aparece `**` na resposta** → `_sem_markdown()` não foi aplicado; conferir `responder()` retorno "resposta".
- **Ana "não sabe" um imóvel** → ele precisa estar `ativo=1` e `destaque=1` no banco pra entrar no contexto.
- **Ana inventou imóvel** → reforçar regra em `PRISCILA_PERSONA` (REGRA ABSOLUTA) — proibido.
- **Sem resposta / fallback** → conferir `ANTHROPIC_API_KEY` no `.env` (`ClienteClaude.available()`).
