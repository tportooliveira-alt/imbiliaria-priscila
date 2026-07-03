# Handoff — Página de Calculadoras (financiamento + avaliação) — 21/06

Página NOVA de teste, **oculta** (`?calc=1`, fora do menu). NADA publicado no menu, NADA reiniciado ainda
(ordem do Thiago: "não coloque na página até ficar pronto"). Tudo buildado no `dist/` (hidden) + backend
editado, mas o serviço **não foi reiniciado** → endpoints novos dão 404 até o restart.

## Acesso de teste (após o restart)
`https://pvscelosimobiliaria.com/?calc=1`

## O que foi feito (construído + testado em processo)
- **Frontend** `design-recebido/pvscelos-imobiliaria/src/Calculadoras.jsx` (novo) + `App.jsx` (`?calc=1`) + `api.js` (helpers).
  - Tema claro/areia, paleta do site (#16284B/#c9943a/#5C7CB8), **logo da Priscila** no topo.
  - Abas: **Financiamento** (perfil completo) e **Avaliação** (AVM).
  - Perfil: nome, WhatsApp, **e-mail**, vínculo (CLT/autônomo/servidor/aposentado), idade, renda, dependentes,
    valor, entrada, novo/usado/planta, bairro, finalidade, prazo, SAC/Price, FGTS+anos, 1º imóvel, nome limpo.
  - 3 cartões: Enquadramento · Taxa · Subsídio. **Alternativas** ("mais perfis").
  - Gráficos **Chart.js**: evolução da parcela (linha) + comparativo de bancos (barras).
  - **Imóveis nossos que casam** com o perfil (carteira real).
  - **Análise do perfil** pelo **agente especializado** (não a Ana genérica).
  - **Marcar horário com a Priscila** (data + turno → /api/agendar-visita).
- **Backend** `app/routes_publicas.py`:
  - `POST /api/perfil-financiamento` — enquadramento/taxa/subsídio (via `recomendar_financiamento`), imóveis
    que casam (`_imoveis_para_perfil`), cadastra lead rico (+e-mail, tags comprador/handoff/fgts/servidor),
    **manda resultado+imóveis no WhatsApp do cliente** (`_enviar_resultado_cliente`, WhatsApp ON).
  - `POST /api/analise-financiamento` — agente especializado (`SYSTEM_CONSULTOR_FINANCIAMENTO`, ClienteClaude
    sonnet→cascata). Explica MCMV/Price/FGTS/SBPE em detalhe, SEMPRE estimativa, passa pra Priscila.
- **Backend** `data/taxas.json`: +Sicredi, +Sicoob, +Banco Inter (comparativo 6→9 linhas).
- **Backend** `app/proposta_pdf.py`: **logo no topo + marca d'água** suave (logo em `app/branding/selo.png`).

## Testado (em processo, sem tocar produção)
- 1830 combinações de faixa/taxa/Pró-Cotista — OK.
- `/api/perfil-financiamento` — HTTP 200, enquadramento+imóveis+lead OK (lead de teste já removido).
- `/api/analise-financiamento` — agente respondeu detalhado e acolhedor (renda baixa), como estimativa.
- PDF da proposta — gerado com logo+marca d'água (válido, 2 págs).

## Pendências / decisões do Thiago
1. **RESTART** (`systemctl restart imobiliaria`) — falta o OK explícito. Sem ele, o "Not Found" persiste.
   Continua OCULTO (fora do menu) mesmo após o restart. ~8s de blip na Ana.
2. **#22 Google Agenda** — integração configurada (`gcal.disponivel()=True`, wiring agendar→agenda→gcal ok),
   MAS o teste de ESCRITA (criar+apagar evento) foi BLOQUEADO 2x pelo classifier por ser escrita no
   calendário real da Priscila. Precisa de OK explícito OU a Priscila compartilhar o calendário com o e-mail
   da service account. NÃO confirmado que marca de verdade.
3. Publicar no MENU — só quando o Thiago aprovar tudo.

## Backups
`/tmp/app-backup-*`, `/tmp/dist-calc-*` (reversível).
