# 🗓️ Estudo: Secretária por WhatsApp (Priscila agenda) sem confundir a Ana

Objetivo: a Priscila manda do **número pessoal dela** → "marca visita com a dona Maria sexta 10h" → o sistema cria o
compromisso na agenda e confirma. **Só o número dela** pode. A **Ana (bot cliente) NÃO pode se confundir.**
_Pesquisa rodando (task wqxjqel4b) pra validar; este é o desenho preliminar._

## ⚠️ O risco que o Thiago levantou (e a solução)
**Risco:** um cliente falar algo e o sistema achar que é a Priscila → marcar errado / a Ana se confundir.
**Solução (trava dura):** a decisão é pelo **NÚMERO de quem enviou**, NÃO pelo conteúdo.
- O webhook do Evolution entrega o **número real** do remetente (`remoteJid`).
- `eh_priscila(remote)` compara com `PRISCILA_WHATSAPP` (env). **Só bate o número dela.**
- Cliente (número diferente) → **sempre** segue pra Ana, jamais é tratado como Priscila.

## 🔒 Camadas de segurança (defesa em profundidade)
1. **Número allow-list (principal):** só `PRISCILA_WHATSAPP` dispara a secretária. _É a trava que o Thiago pediu._
2. **(Opcional) palavra-chave:** exigir prefixo (ex.: "Sofia," ou "/agenda") pra acionar — zero ambiguidade mesmo no
   número dela. _A decidir com o Thiago._
3. **Ordem de interceptação:** no webhook, checar Priscila ANTES de qualquer lógica da Ana. Se for ela+comando →
   processa e **retorna** (a Ana nem roda).
4. **Confirmação (eco):** o sistema responde "✅ Marquei: X — sexta 10:00" — ela vê o que foi entendido.
5. **Fallback:** se a data/hora estiver ambígua → "não entendi, manda o dia e a hora" (nunca cria lixo).
6. **Spoofing:** falsificar número no WhatsApp é muito difícil (ligado ao chip/conta); Evolution reporta o JID real.

## 🧠 Interpretação de "sexta às 10h" (PT-BR + fuso Brasília)
- Usar **LLM (Claude) → JSON** com o "agora" de Brasília no prompt (UTC-3). Robusto pra PT-BR coloquial.
- Regras no prompt: "sexta" = próxima sexta; duração 1h se não disser fim; sempre ISO sem timezone.
- (A pesquisa vai comparar LLM vs dateparser/duckling e armadilhas.)

## ✅ O que já está construído (a confirmar/ligar após o estudo)
- `app/secretaria.py`: `eh_priscila()` (número), `eh_comando_agenda()`, `interpretar()` (Claude→JSON), `processar()`
  (cria na agenda + mensagem de confirmação). **Ainda NÃO ligado no webhook** (espera o estudo + o número dela + decisão da palavra-chave).

## ❓ Decisões pendentes (Thiago)
1. **Palavra-chave** sim ou não? (recomendo SIM — "Sofia," — segurança extra, custo zero).
2. **Número pessoal da Priscila** (pra cadastrar em `PRISCILA_WHATSAPP`).
3. Confirmar tirar o WhatsApp do modo teste (pra mandar a confirmação pra ela / lembretes a clientes reais).

_Relacionado: `PLANO-DE-ATAQUE.md`, `admin-priscila-plano` (agente "Sofia"). Finalizar quando a pesquisa cair._
