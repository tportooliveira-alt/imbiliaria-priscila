# Integração Google Calendar ↔ Agenda interna (PENDENTE)

**Status:** não construída ainda. Aberto em 17/06/2026.
**Objetivo:** o que for marcado no site (formulário) **e** o que a Priscila/Ana marcam no
Google Calendar aparecerem nos DOIS lugares, sem digitar duas vezes.

---

## Por que isso virou tarefa

Hoje existem duas agendas separadas que NÃO se falam:

1. **Agenda interna do site** (tabela `agenda` no `data/site.db`) → o painel da corretora.
   Só recebe o que é marcado **pelo formulário do site** (`/api/agendar-visita`, já liga lead → agenda).
2. **Google Calendar de verdade** → onde a Ana/Priscila marcam manualmente (ex.: cliente que
   chega pelo WhatsApp). O site **não enxerga** esses eventos.

Resultado: a visita da **Ane Caroline** (lead quente, veio pelo WhatsApp via Ana) foi marcada no
Google e não aparecia no painel — não sumiu, só não havia ponte. Lançada manualmente em 17/06
como evento `id=9` (com flag "CONFIRMAR HORÁRIO").

---

## O que o Thiago precisa providenciar (depende do dono — chaves/infra)

1. **Ativar a Google Calendar API** no projeto do Google Cloud da imobiliária.
2. **Service Account** (recomendado p/ servidor): gerar o JSON de credencial e **compartilhar o
   calendário** da Priscila com o e-mail da service account (permissão "Fazer alterações em eventos").
   - Alternativa: OAuth (precisa de tela de consentimento + refresh token — mais passos).
3. **ID do calendário** que a Priscila/Ana usam (Configurações do calendário → "ID da agenda",
   normalmente o e-mail dela ou um `...@group.calendar.google.com`).

> Sem isso eu não construo: integração externa + segredo exigem autorização direta do dono e as
> chaves. Segredos vão pro `.env` (gitignored), **nunca** pro git.

---

## O que EU (Claude) faço quando as credenciais chegarem

- `app/gcal.py` (novo): cliente da Calendar API lendo credencial de `GOOGLE_CALENDAR_SA_JSON`
  (path) + `GOOGLE_CALENDAR_ID` no `.env`. Funções `criar_evento()`, `listar_eventos(intervalo)`,
  `atualizar_evento()`, `cancelar_evento()`. Falha sempre em try/except → **nunca quebra** o site.
- **Site → Google:** em `app/agenda.py::criar()` (ou no `/api/agendar-visita`), após gravar no
  banco, espelhar no Google e guardar o `gcal_event_id` numa coluna nova `agenda.gcal_event_id`
  (migração leve). Idempotente (não duplica em retry).
- **Google → painel:** o painel passa a mostrar também os eventos do Google no intervalo
  (merge por `gcal_event_id`), pra Ana ver tudo num lugar só.
- Mapear `turno`/horário ↔ `dateTime` com fuso **America/Bahia (UTC-3)**.
- Testes: criar/atualizar/cancelar com a API mockada; smoke real com 1 evento de teste e apagar.

### Esboço do `.env` (preencher depois)
```
GOOGLE_CALENDAR_ID=xxxxx@group.calendar.google.com
GOOGLE_CALENDAR_SA_JSON=/var/www/imobiliaria/secret/gcal-sa.json   # fora do git
```

---

## Pendência imediata (não depende de integração)

- [ ] Confirmar com a Ana o **dia e hora reais** da visita da **Ane Caroline** e ajustar o evento
      `id=9` (hoje está provisório 09:00/17-06 com flag "CONFIRMAR HORÁRIO").
