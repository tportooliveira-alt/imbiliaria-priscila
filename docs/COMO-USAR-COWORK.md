# 🤝 COMO USAR O COWORK — passo a passo (Thiago)

Guia rápido pra usar o **Cowork** (modo agente do app do Claude, atalho **Ctrl+2**) no dia a dia do negócio da
Priscila. Cowork = o Claude trabalhando JUNTO contigo em tarefas; **Code** (`</> Code`) = mexer no projeto/código.

---

## 1) Os dois modos (quando usar cada um)
| Modo | Atalho | Pra quê |
|---|---|---|
| **Cowork** | Ctrl+2 | Tarefas do dia: agenda, leads, e-mails, pesquisa, automações (Rotinas), usar conectores |
| **Code** | `</> Code` | Editar o site/sistema (o projeto clonado), com a ponte git pra VPS |

## 2) Conectar suas ferramentas (uma vez só) — é isso que me dá "mãos"
No app: **Configurações → Conectores** (Connectors). Conecte e autorize com a conta certa:
- 📅 **Google Calendar** — marcar/mover/ler visitas e compromissos
- 📁 **Google Drive / Docs** — contratos, fotos, modelos
- ✉️ **Gmail** — e-mails de lead (ler/rascunhar resposta)
- 📊 **Google Sheets** — planilhas (carteira, controle)
- _(outros que aparecem: Box, Microsoft 365, Slack, monday, Gamma)_

> Depois de conectar, **eu uso direto** — você não precisa subir print nem copiar/colar. Era esse o objetivo.

## 3) Como pedir uma tarefa no Cowork (exemplos reais)
Abra o Cowork (Ctrl+2) e fale natural. Exemplos pro nosso negócio:
- 📅 *"Marca uma visita amanhã 15h com o lead João no apê de Candeias."*
- 📅 *"O que a Priscila tem na agenda essa semana?"*
- 👥 *"Resume os leads novos do CRM de hoje e diz quais estão quentes."*
- ✉️ *"Rascunha uma resposta pro e-mail do cliente que pediu a avaliação."*
- 📄 *"Cria um Doc no Drive com a proposta do imóvel do Recreio."*
- 🔎 *"Pesquisa quanto está o m² em Candeias agora e compara com a nossa calculadora."*

## 4) Rotinas (automação que roda sozinha)
No Cowork tem a aba **Rotinas** — tarefas que se repetem. Ideias:
- 🌅 *Toda manhã:* "resuma os leads novos e os compromissos do dia".
- 📱 *Diário 18h:* "liste leads quentes sem retorno e sugira a próxima ação".
- 🗓️ *Segunda:* "monte a agenda da semana e confira conflitos no Google Calendar".
> Configura uma vez, e ela te entrega o resultado sozinha (toca no celular).

## 5) Ligar o Cowork ao PROJETO (site da Priscila)
- No **Code**, abra a pasta clonada (`git clone` — ver `SETUP-DOIS-LADOS.md`).
- Fluxo: você pede → eu edito → `git push` → na VPS roda `./deploy.sh` (puxa + reinicia).
- Assim o Cowork (tarefas) e o Code (projeto) trabalham os dois lados, ligados pelo git.

## 6) Permissões e segurança
- Pra eu agir sem te pedir a cada passo: ligue o **modo autônomo/"aceitar tudo"** em `/permissions` (ou Shift+Tab no
  terminal). É um ajuste **seu**, só o dono liga.
- **Deny rules** bloqueiam ações perigosas **mesmo no modo autônomo** — dá pra blindar o que eu nunca devo tocar.
- Segredos nunca vão pro git; conectores guardam o login no app, com segurança.

---

### TL;DR pra começar agora
1. **Ctrl+2** abre o Cowork.
2. **Configurações → Conectores → Google Calendar** (e Drive/Gmail) → autorizar.
3. Me peça: *"marca um teste amanhã 9h"* → eu crio no Google Agenda.
4. Curtiu? Cria uma **Rotina** ("resumo de leads toda manhã").

_Relacionados: `SETUP-DOIS-LADOS.md` (PC↔VPS + MCP), `PENDENCIAS.md`. As MELHORES integrações pra ligar saem da
pesquisa "nobres integrações" (rodando agora) — atualizo este guia quando o relatório cair._
