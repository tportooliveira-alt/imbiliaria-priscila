# 🗺️ PLANO DE CONTINUAÇÃO — comece por aqui ao retomar

> Plano vivo pra eu (Claude) continuar de onde paramos, sem esquecer nada. Marca o que **foi
> feito**, o que **vem a seguir** (em degraus), e as **métricas** pra saber se está funcionando.
> Detalhe do dia-a-dia: `docs/HANDOFF-<data>.md`. Estado vivo dos dados: `panorama_geral` (MCP).
> Disciplina de trabalho: skill `disciplina-de-trabalho` + `~/.claude/CLAUDE.md` (verificar antes de
> falar · confirmar antes de executar · ≤3 por vez · registrar tudo · produção real).

---

## ✅ FEITO (madrugada 18→19/06)

- [x] **Ana 100% Claude** (Gemini removido) — Sonnet/Haiku por rota, testado.
- [x] **Captação** reconhecida — contato que OFERECE imóvel não é mais lead frio (acolhe, pede fotos+
  descrição, adianta pra Priscila). Testado ao vivo.
- [x] **Marca d'água** nas 1076 fotos (selo redondo da marca, centralizado, transparente) — originais
  preservados (`original.jpg` + backup tar). No site também.
- [x] **Lembrete ~1h antes pra Priscila** (qualquer compromisso: Ana ou João) — no ar, testado.
- [x] **Paperclip** confirmado recebendo dossiês de lead quente + 5 quentes reescalados. Mantido (RAM ok).
- [x] **Disciplina/organização**: Karpathy global (`~/.claude/CLAUDE.md`), ECC vira referência,
  skill `disciplina-de-trabalho`, `scripts/verificar.sh`.
- [x] **README** reescrito (completo/atual) + backups (pequeno no chat, completo via SSH).
- [x] `codigo-da-virada` desligado · tudo no GitHub (sem segredos).

## 🔜 PRÓXIMOS DEGRAUS (em ordem, um de cada vez)

- [ ] **1. Consertar a VISÃO** (a foto não baixa da Evolution — 0/28). O log `[DIAG-MIDIA]` já está no
  ar; ver o erro real na próxima imagem → corrigir `whatsapp.baixar_midia_base64`. **Depois remover os
  logs temporários** `[DIAG-MIDIA]`/`[DIAG-LID]`.
- [ ] **2. Caso @lid** — confirmar pelo log `[DIAG-LID]` se contato da Priscila some por causa do
  filtro de número (linha ~697 do webhook) → corrigir se for o caso.
- [ ] **3. Ana ENVIAR foto/link do imóvel** (degrau 2). REGRA DE OURO: só se o cliente pedir + mostrar
  interesse; pergunta antes; nunca importunar. WhatsApp = perguntar "link do site ou foto aqui?"; site =
  só mostrar na página. Precisa `whatsapp.enviar_imagem`. **Desenhar e mostrar antes de subir.**
- [ ] **4. Escalonar Haiku→Sonnet por complexidade/tamanho** da conversa (não só por rota). Sinais:
  nº de turnos + temperatura do lead + financiamento/negociação. Mudança no `dispatcher`.
- [ ] **5. Captação: visão Haiku→Sonnet** (descrição mais rica do imóvel pro cadastro).
- [ ] **6. "Colocar na MCP"** (pendência do dono) — definir o quê: tag `contato_priscila`? captação no
  `panorama`?

## 🅿️ Depende do dono (faço a parte técnica quando chegar)
- [ ] Cadastrar tipologias/preços dos 5 empreendimentos · GA4 ID · biometria (1 clique) · DeepSeek (chave).

---

## 📊 MÉTRICAS FUTURAS (acompanhar pra saber se funciona)

> Tudo já dá pra puxar do banco/MCP. Ideal: olhar 1x/semana. Baseline = onde estamos hoje (19/06).

| Métrica | O que mede | Baseline (19/06) | Meta |
|---|---|---|---|
| **Leads novos / semana** | volume de captação | ~14 no total | crescer |
| **% leads quentes** | qualidade do funil | 9 quentes / 14 | acompanhar |
| **Lead → visita agendada** | conversão real | medir | ↑ |
| **Visita → venda** | fechamento (Priscila registra) | — | ↑ |
| **Respostas da Ana não-fallback** | IA saudável (não caiu) | ~100% | ≥99% |
| **Resposta dobrada / re-saudação** | bug de atendimento | 0 (corrigido) | **0** |
| **Imagens lidas pela visão** | visão funcionando | **0/28 (quebrado)** | ≥90% após fix |
| **Captações recebidas** | parceiros oferecendo imóvel | começou hoje | acompanhar |
| **Dossiês no Paperclip** | lead quente organizado | 11 | = nº de quentes |
| **Lembretes 1h enviados / no-show da Priscila** | ela não perder horário | novo | 0 no-show |
| **Opt-outs / teto diário atingido** | saúde do WhatsApp (anti-ban) | baixo | manter baixo |

### Como puxar (rápido)
- `panorama_geral` (MCP) → leads, agenda, financeiro, pendências.
- Conversas da Ana: `listar_conversas_ia` / `metricas_ia` (MCP).
- Funil/temperatura: tabela `leads` (score, temperatura) + `lead_interacoes`.
- Agenda/lembretes: tabela `agenda` (`lembrete_enviado`, `lembrete_1h_enviado`).

---

## 🔒 Invariantes (não re-derivar)
Produção real · nunca inventar dado · imóvel nunca hard-delete (`ativo=0`) · segredos fora do git ·
app roda como `priscila` (não dar chown root) · Brasília UTC−3 · mudança de Ana/infra só com OK do dono ·
verificar de verdade antes de reportar.
