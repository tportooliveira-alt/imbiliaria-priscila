# Admin da Priscila — Estudo Avançado + Plano (Back-office + Agente Assistente)

> O painel "atrás do site" onde a Priscila trabalha de verdade: imóveis (foto + texto),
> leads/CRM, agenda e fluxo de caixa — com um **agente IA assistente** que faz o trabalho pesado.
> Princípio: refinar em cima do que JÁ existe (o backend é rico), degrau em degrau, barato e honesto.

---

## 1. O que JÁ existe hoje (baseline real — NÃO reconstruir)

**Backend (bem completo — `app/routes_admin.py` + `app/routes_crm.py`):**
- **Imóveis:** criar / editar / excluir (soft-delete), **upload de imagens**, **IA gera descrição**
  (`/gerar-descricao`), **IA auto-organiza as fotos** (`/imagens/auto-organizar`), reordenar, editar/excluir imagem.
- **Leads / CRM:** listar, criar, editar, notas, tags, **copiloto que sugere resposta** (`/copilot/sugerir-resposta`),
  enviar WhatsApp pelo painel.
- **Agenda:** criar / listar / editar / excluir compromissos + **lembretes** (`/agenda/lembretes/enviar`).
- **Financeiro (fluxo de caixa):** **comissões**, **metas**, **contas a pagar/receber** (+ marcar paga),
  **dashboard financeiro** (`/financeiro/dashboard`).
- **Alertas + matches:** casar lead com imóvel automaticamente (`/alertas/matches`).
- **Documentos.** **Operação-IA:** conversas + métricas (monitor da Ana).
- **Auth:** login.

**Interface (`admin/admin.jsx`, ~1.756 linhas):** já tem as seções *dashboard, imóveis, leads, agenda,
financeiro (comissões/metas/contas), documentos, alertas, operação-IA*. Upload de foto e botão de gerar
descrição já aparecem na tela.

➡️ **Conclusão:** a fundação existe. O trabalho é **refinar a usabilidade pra Priscila** e **plugar um agente
assistente** que opere tudo isso conversando com ela.

---

## 2. Estudo avançado — o que os melhores CRMs de corretagem (2026) têm × onde estamos

| Recurso de ponta (mercado) | Status nosso |
|---|---|
| **Gestão de anúncio** (fotos, descrição, publicar) | ✅ tem (com IA) — **refinar o fluxo** |
| **Comissão atrelada ao pipeline** (splits, taxas do corretor) | ✅ tem base — **deixar visual** |
| **Agenda + lembretes** integrados | ✅ tem — **conectar com site/Ana** |
| **Back-office: relatórios e dashboard** | ⚠️ parcial — **simplificar p/ Priscila** |
| **Lead auto-importado, taggeado, roteado + auto-mensagem** | ✅ Ana já alimenta — **fechar o ciclo** |
| **Workflow/checklist por tipo de negócio** (ex.: "venda alto padrão") | ❌ falta — **degrau futuro** |
| **Portal do cliente** (acompanhar a negociação) | ❌ falta — **degrau futuro** |
| **Assistente IA que opera o back-office** | ❌ falta — **é o que vamos criar (seção 5)** |

*Fontes: Ascendix, monday.com, CRM.org, Close (CRMs imobiliários 2026).*

---

## 3. Refinamentos prioritários de UX (pra Priscila trabalhar fácil, do celular)

1. **Cadastro de imóvel sem dor (1 fluxo):** arrastar as fotos → IA **organiza + gera título e descrição**
   → IA **sugere preço** (usa a calculadora de avaliação) → Priscila revisa e **publica**. Tudo numa tela.
2. **Agenda conectada de ponta a ponta:** visita pedida pelo site/WhatsApp (Ana) **cai direto na agenda**
   da Priscila + **lembrete automático** pra ela e pro cliente.
3. **Fluxo de caixa simples e visual** (ela já entende de caixa): card grande com **a receber** (comissões),
   **a pagar** (contas), **saldo do mês** e **meta** — verde/vermelho, sem planilha.
4. **Pipeline de leads claro:** Novo → Qualificado → **Quente** → Visita → Proposta → Fechado, com a Ana
   movendo os cards e o copiloto sugerindo o próximo passo.
5. **Mobile-first:** ela trabalha do celular — botões grandes, foto pela câmera, tudo numa mão.

---

## 4. ⭐ O AGENTE ASSISTENTE DA PRISCILA (a "skill" / copiloto do admin)

**Ideia:** um agente que é o **braço direito administrativo** da Priscila dentro do painel. Ela fala
(texto ou áudio) e ele **executa de verdade** usando os endpoints que já existem.

**Nome sugerido:** *Sofia* (secretária/gerente) — separada da **Ana** (que atende o cliente). A Ana é o
front; a Sofia é o back-office.

**O que ela faz (tudo ligado no que já existe):**
- 📸 **"Cadastra esse imóvel"** (manda fotos + um áudio descrevendo) → cria o imóvel, **auto-organiza as fotos**,
  **gera a descrição**, **sugere o preço** (calculadora de avaliação) e mostra pra Priscila **aprovar antes de publicar**.
- 📅 **"Agenda a visita do João sábado 10h"** → cria na agenda + dispara o lembrete.
- 💰 **"Como tá meu caixa esse mês?"** → resume o dashboard financeiro (a receber, a pagar, saldo, meta).
- 🔥 **"Quais leads estão quentes?"** → lista, resume a conversa de cada um e **sugere o próximo passo** (já tem copiloto).
- ✍️ **"Deixa esse anúncio mais chamativo"** → reescreve a descrição.
- 🔔 **Resumo do dia / follow-ups pendentes** ("3 leads esperando retorno, 2 visitas amanhã, conta de luz vence dia 20").

**Como entra na prática:** uma aba **"Assistente"** no admin (um chat) + **ações rápidas**. Por baixo, um
orquestrador parecido com o copiloto de leads que já existe, expandido pra agir nos `/api/admin/*`.

**Regras (importantes):**
- **Modelo Sonnet** (admin = decisão e qualidade; o atendimento operacional da Ana segue Haiku — barato).
- **Event-driven e econômico** — respeita o "degrau em degrau, no máximo 3 agentes por vez".
- **Confirmação obrigatória** em ações sensíveis: publicar imóvel, excluir, enviar WhatsApp, lançar no financeiro.
- **Nunca inventa dado** (preço, imóvel, número) — sempre puxa do sistema ou pergunta.

---

## 5. Roadmap (degrau em degrau, testando cada um antes do próximo)

- **Degrau A — Cadastro de imóvel turbo:** refinar a tela "arrastar fotos → IA organiza + descreve + sugere preço → publicar". + **agenda conectada** (visita do site cai na agenda com lembrete).
- **Degrau B — Fluxo de caixa pra Priscila:** painel visual simples de a receber / a pagar / saldo / meta.
- **Degrau C — Agente Sofia (assistente):** chat no admin ligado nos endpoints, começando por **3 capacidades**:
  (1) cadastrar imóvel por foto+áudio, (2) resumir o caixa, (3) puxar leads quentes com próximo passo.
- **Degrau D (futuro):** checklists por tipo de negócio + portal do cliente.

---

## 6. Princípios inegociáveis
Honestidade (dados reais, nada inventado) · custo baixo (Haiku operação / Sonnet admin) · mobile-first ·
confirmação em ações sensíveis · construir sobre o que já existe · um degrau por vez.
