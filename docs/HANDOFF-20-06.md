# 📋 Handoff — 20/06/2026 (madrugada): Calibração da Ana + Deploy

## Resumo
Sessão longa de **calibração da Ana** (assistente IA do site + WhatsApp), feita em cima de uma
simulação de 14 personas + estudo do Gemini (design conversacional imobiliário). **No fim do dia a
Ana calibrada foi pro ar** (`systemctl restart imobiliaria`, com OK do dono e backup antes).

## Contexto: dois Claudes em paralelo
O Thiago tinha um **segundo Claude no PC** (clone `Downloads/imbiliaria-priscila`, base `main` antiga)
calibrando a Ana ao mesmo tempo. Risco de um atropelar o outro. Combinamos: **a VPS é a fonte única**
(produção roda `feat/calibracao-design-skills`, deploy por restart, NÃO git pull). O Claude do PC
mandou o `git diff` dele e EU integrei **à mão** aqui (Claude, não Gemini; persona calibrada) —
pegando só as 3 contribuições novas dele (captação/handoff, carteira completa, busca real) e
descartando o que já existia ou divergia (Gemini, persona antiga).

## O que foi calibrado (commits em `feat/calibracao-design-skills`)
- **router.py** — rotas `CAPTACAO` (vendedor) + `HANDOFF` (pedido de humano).
- **dispatcher.py** — carteira **COMPLETA** no contexto (acabou o "não tenho" falso: o Maison du Soleil
  R$ 500k estava escondido); `busca_natural` ligada ao chat; fábricas Claude p/ as rotas novas;
  **removida a prosa de marketing** das descrições (vinha com "sofisticado/alto padrão" e a Ana repetia).
- **lead.py** — telefone 35→25 (não infla score sozinho); `pronto_proposta` exige orçamento; tirou
  "ate" solto do PRAZO; léxico de vendedor alinhado com o router.
- **prompts.py** (persona) — TRAVAS e regras fortes:
  - 🔒 **Financiamento:** não chuta taxa/parcela/ITBI — manda pro **simulador do site** (estimativa) e/ou
    Priscila, sempre deixando claro que é estimativa. Gentil, mas não fala o que não deve.
  - 🔒 **Avaliação:** não chuta metragem/valor de imóvel de terceiro (Priscila avalia).
  - 🤝 **Atende TUDO** (do popular ao alto) — NUNCA rotula "alto padrão", NUNCA diminui a renda do cliente
    (cliente que se sente menor foge / vira problema).
  - ❤️ **Cuidado com a pessoa** (princípio acima de tudo): cliente magoado vira problema pra Priscila.
  - 📏 **Brevidade** com teto de palavras (~40, máx 60), 1 pergunta, imóvel em ≤3 pontos + oferece fotos.
  - 🔁 **Handoff** em: pedido de humano, desconto, jurídico/documentação, "ver agora", impaciência.
  - Acento pt-BR; não inventar telefone da Priscila.
- **conversas.py** — evento `handoff.solicitado` + tag no lead.
- **routes_publicas.py** — simulador retorna `aviso_estimativa` bem claro ("⚠️ ESTIMATIVA — o banco confirma").

## Verificação
- **25 testes de IA** (dispatcher/router/lead/busca/calibração/persistência) passando. (4 falhas pré-existentes
  são de frontend v3 / caminho Windows / health-Gemini — não relacionadas.)
- **Simulação final (14 personas, pior caso Haiku)** + auditoria por **agente Haiku**: veredito **pronta pra
  produção**. Provado: não inventa taxa, não chuta avaliação, não diminui cliente, acolhe vendedor, mostra
  imóvel barato, sem rótulo de luxo.
- **Pós-deploy (produção real):** financiamento não cita taxa; vendedor cai em captação. Motor intacto
  (site/api 200, 0 erro no log).

## Ferramenta nova
- `tests/sim_ana.py` — harness de simulação (14 personas, modo `--haiku` pior caso) → `docs/SIM-ANA-*.md`.
  Reusar pra validar futuras mudanças (antes/depois).
- `docs/auditoria-ia-console.html` — console de auditoria do Gemini (guardado pra mexer depois; chave vazia).

## Infra (checado, nada precisou mudar)
- `codigo-da-virada` já **stopped** (de propósito). Paperclip só escuta em `127.0.0.1:3100` e o MCP é
  **só-leitura** (`MCP_WRITE_ENABLED=0`) — já travado de fora. Nenhum Claude rogue na VPS.

## Backups
- `backups/app-PRE-DEPLOY-ana-0824.tar.gz` (antes do restart, reversível).
- `backups/app-calibracao-ana-20260620.tar.gz`.
- Commits no git local (branch `feat/calibracao-design-skills`) — **push pro GitHub pendente** (foi
  bloqueado pela trava "não sobe por aqui"; subir quando o dono liberar, pra sincronizar com o Claude do PC).

## Pendências / próximos passos (segunda)
- **Push pro GitHub** da branch (sincronizar com o Claude do PC).
- Acompanhar a Ana nova com clientes reais (manutenção): ver conversas via MCP (`monitor_site_ao_vivo`,
  `metricas_ia`) e ajustar se aparecer padrão novo.
- Meta Ads (campanha Instagram) — esperando token `EAA...`.
- Google Ads — ler "termos de pesquisa" e afinar negativas.
