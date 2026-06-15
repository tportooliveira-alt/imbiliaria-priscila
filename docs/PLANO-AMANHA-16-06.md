# 🗓️ PLANO DE AMANHÃ (16/06/2026) — pro agente continuar

Contexto: sessão 15/06 montou a operação Postiz (VPS+PC), a ponte SSH PC↔VPS, e fez hardening de segurança.
Abaixo o que ficou aberto, em ordem de prioridade. **Regras de sempre:** fuso Brasília (UTC-3); nunca push na `main`
(branch = `feat/calibracao-design-skills`); segredos fora do git; mudança de infra = avisar o dono; não ligar o
`codigo-da-virada` (parado de propósito).

## 🔴 DECISÃO PENDENTE nº1 — Postiz (bloqueador)
O Postiz `:latest` (v2.21 / app v1.47) **não roda nesta VPS**: exige Temporal + **Elasticsearch** + 2º Postgres
(~2-3 GB RAM). O backend (porta 3000) fica **caído** → cadastro dá **502** (nem o Thiago nem o agente conseguem criar conta).
Os 3 containers leves (`postiz`, `postiz-postgres`, `postiz-redis`) sobem, mas o app não funciona sem o backend.

**Escolher 1 dos 2 caminhos (perguntar ao Thiago):**
- **A) Fixar versão LEVE do Postiz** (pré-Temporal): achar a tag onde o `docker-compose.yaml` do repo ainda NÃO tem
  `temporal` (bisseccionar tags em `raw.githubusercontent.com/gitroomhq/postiz-app/<tag>/docker-compose.yaml`).
  Trocar a `image:` em `/root/postiz/docker-compose.yml`, `docker compose up -d`, validar `/api/auth/register` != 502.
  ⚠️ Versão antiga = menos recursos/possíveis bugs.
- **B) Metricool (hospedado, grátis)** — zero carga na VPS, funciona na hora, agenda 24/7 na nuvem deles. Foi a
  recomendação original antes do Thiago pedir VPS. Se for por aqui: **derrubar o Postiz da VPS** (`cd /root/postiz &&
  docker compose down`) pra liberar RAM, e manter o subdomínio/SSL ou remover.

Depois que o Postiz (ou Metricool) funcionar:
- 🔒 **Trancar cadastro do Postiz** (`DISABLE_REGISTRATION=true` + `up -d`) assim que a conta admin existir.
- Conectar **Instagram Business + Página Facebook** da Priscila.
- ⚠️ **O Postiz do PC tem o MESMO problema** (PC-Claude instalou `:latest`) — aplicar a mesma decisão lá.

## 🟠 Marketing / leads (o combustível)
- 📣 **Subir a 1ª campanha Meta** (`docs/CAMPANHA-META-1.md` — 2 criativos prontos). Falta a ARTE (imagem) + a conta de anúncios.
- 🎨 **Gerar os 10 carrosséis** (`docs/CAMPANHA-INSTAGRAM-PRISCILA.md`) — conteúdo pronto pro Canva/agendador.
- 📊 **GA4 ID** ainda vazio no `.env` (Meta Pixel já está: `META_PIXEL_ID=27844979038460971`).
- 🤝 **Coletar depoimentos reais** (textos prontos em `docs/PEDIR-DEPOIMENTOS.md`) — alavanca 10-20×.

## 🟢 Sistema
- ✅ **Hardening feito hoje:** ChromaDB (8000) e motor_ia (8080) estavam **abertos pra internet sem senha** →
  prendidos em `127.0.0.1` (`/root/imobiliaria_ai_agents/docker-compose.yml`). **Sem firewall (ufw inativo)** —
  avaliar ligar ufw deixando 22/80/443.
- 🔑 **Ponte SSH PC→VPS** ativa (`vps-paperclip`, chave `claude-pc-vps-paperclip` em authorized_keys).
- 🔧 **Paperclip** — PC-Claude está destravando via SSH (tirar `ANTHROPIC_API_KEY` do pm2 + `--dangerously-skip-permissions`).
- 🛡️ **Trocar a senha do Facebook** (foi exposta no chat numa sessão anterior).
- Ligar **follow-up de lead morno** (`FOLLOWUP_ENABLED=1`) só quando houver leads REAIS.

## 📚 Entregar amanhã
- O **estudo aprofundado do projeto** (gerado nesta sessão — ver `docs/ESTUDO-PROJETO-360.md`) → virar plano de execução.
