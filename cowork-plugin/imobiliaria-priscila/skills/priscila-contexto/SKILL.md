---
name: priscila-contexto
description: >-
  Carrega o CONTEXTO do projeto da imobiliária Priscila Vasconcelos (Vitória da Conquista/BA):
  quem é o cliente, a arquitetura do sistema (site FastAPI + agentes Ana/João + CRM + MCP), onde
  ficam as coisas, e as REGRAS DE OURO. Use SEMPRE no início de qualquer trabalho neste projeto —
  desenvolvimento, marketing, CRM, conteúdo, automação — pra agir já orientado e sem errar as regras.
---

# Contexto — Imobiliária Priscila Vasconcelos

Use no começo de qualquer tarefa do projeto. Casa com a skill [[orquestrar-com-ia]] (como construir automação).

## Quem
- **Priscila Vasconcelos** — corretora de imóveis, **CRECI/BA 29.231**, **Vitória da Conquista/BA** (interior). Marca pessoal.
- **Thiago** — dev, esposo e sócio (faz a parte técnica). Priscila é a corretora de verdade.
- Site: **pvscelosimobiliaria.com** (soft-launch, ainda com `noindex`). Ticket ~R$1 mi, comissão ~6% (~R$60k/venda).

## O sistema (o que já existe)
- **Site**: FastAPI (uvicorn 127.0.0.1:8001) + nginx + **SQLite** (`data/site.db`); front estático em `v3-editorial/`,
  painel **admin** em React/Babel (`admin/admin.jsx`). Roda na VPS via systemd `imobiliaria`.
- **Ana** (IA de atendimento ao cliente no WhatsApp): qualifica (BANT), oferta SÓ imóveis reais da carteira, fala da
  Priscila em 3ª pessoa. **Nunca se passa pela Priscila.**
- **João** (IA de agenda da Priscila por WhatsApp): só responde ao número dela + palavra "joão"; confirma em áudio.
- **CRM** com score/temperatura/origem; **calculadora de avaliação** (capta vendedor) e **calculadora de ads**.
- **Empreendimentos**: módulo de lançamentos de construtora (pai + tipologias) — admin + páginas no site.
- **MCP da VPS**: o Cowork lê o sistema AO VIVO (leads, agenda, imóveis, financeiro) — ferramentas de LEITURA.

## 🔒 REGRAS DE OURO (não violar)
1. **NUNCA inventar dado.** Imóvel, preço, bairro, m² — só o que está no banco/fonte real. Sem dado → diz que não sabe.
2. **Fuso horário = Brasília (UTC-3).** Toda data/hora de compromisso considera isso.
3. **Nunca push direto na `main`.** O trabalho vai na branch `feat/calibracao-design-skills`.
4. **Segredos fora do git** (`.env`, chaves, `data/`, fotos). Nunca commitar token/senha.
5. **Imóvel: nunca hard-delete** — usar `desativar` (`ativo=0`).
6. **Mudança de rede/infra exige autorização direta do dono.**
7. **Começar barato e simples** (ver skill [[orquestrar-com-ia]]): workflow antes de agente; treinar agentes ≤3 por vez.

## Onde achar as coisas (docs/)
- `docs/ROTA-PROXIMA.md` — o próximo passo planejado.
- `docs/PLANO-ORQUESTRACAO-EMPRESA.md` — roadmap priorizado de automação (impacto × esforço).
- `docs/ESTUDO-PROJETO-360.md` — auditoria (segurança, agentes, funil, infra).
- `docs/PLANO-MARKETING-CALIBRADO.md` — funil + taxas verificadas (alavancas: resposta instantânea, indicação 10-20×).
- `docs/CAMPANHA-META-1.md` / `docs/CARROSSEIS-INSTAGRAM.md` — campanha e conteúdo prontos.
- `docs/FALTA.md` / `docs/FEITO.md` — estado do projeto.

## Como trabalhar aqui
- Antes de mexer, olhar a `ROTA-PROXIMA.md` e o estado real (via MCP, se conectado).
- Mudou algo no sistema? Confirmar com teste e registrar no git (na branch certa).
- Marketing/conteúdo: honesto, local (VDC), sem prometer o que não dá (financiamento aprovado, laudo grátis).
