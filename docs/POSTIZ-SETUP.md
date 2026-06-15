# 📸 Postiz — agendador de redes (setup 15/06/2026)

Postiz = ferramenta open-source pra criar e **agendar posts** (Instagram, Facebook, etc.). Instalado em DOIS lugares,
independentes, pra dividir carga:

| Onde | URL | Pra quê | Liga 24h? |
|---|---|---|---|
| 🖥️ **VPS** (produção) | https://postiz.pvscelosimobiliaria.com | **agenda e publica sozinho** | ✅ sim |
| 💻 **PC do Thiago** (local) | http://localhost:5000 | criar/testar sem pesar a VPS | ❌ só com PC ligado |

## 🐳 VPS — como roda
- Docker Compose em `/root/postiz/docker-compose.yml` (3 containers: `postiz`, `postiz-postgres`, `postiz-redis`).
- **Limites de RAM** (pra nunca derrubar o site): postiz 900m · postgres 256m · redis 128m. Usa swap se apertar; o
  serviço `imobiliaria` (site/Ana/João) tem prioridade.
- Porta exposta **só em `127.0.0.1:5000`** — o nginx faz o proxy público (não fica aberto direto na internet).
- **Segredos** (JWT + senha do Postgres) ficam em `/root/postiz/.secrets` (chmod 600) e dentro do `docker-compose.yml`
  local da VPS — **NUNCA no git**.

## 🌐 nginx + SSL
- Config: `/etc/nginx/sites-available/postiz` → proxy pra `127.0.0.1:5000` (WebSocket habilitado, body 100M).
- Subdomínio **DNS A** `postiz.pvscelosimobiliaria.com` → `187.77.252.91` (criado no Hostinger).
- **SSL Let's Encrypt** via certbot (renova sozinho), redirect 80→443.

## 🔧 Comandos úteis (na VPS)
```bash
cd /root/postiz
docker compose ps                 # status dos 3 containers
docker compose logs -f postiz     # logs
docker compose restart postiz     # reiniciar só o app
docker compose down / up -d       # parar / subir tudo
docker stats --no-stream postiz   # uso de RAM
```

## 🔒 Pendência de segurança (IMPORTANTE)
- `DISABLE_REGISTRATION` está **`false`** → enquanto assim, **qualquer um** que abrir a URL pode criar conta.
  → **Depois que o Thiago criar a conta admin, trocar pra `true`** e `docker compose up -d` (tranca o cadastro).

## 🔑 Ponte PC→VPS (SSH)
- O Claude Code do PC acessa a VPS sozinho via chave dedicada `~/.ssh/vps_paperclip` (host `vps-paperclip`).
- Chave pública instalada em `/root/.ssh/authorized_keys` (label `claude-pc-vps-paperclip`).
- Junto com **git** (arquivos mão-dupla) e **MCP** (PC lê a VPS), fecha a "mesa-redonda" PC↔VPS.

## ⏭️ Próximos passos
1. Criar conta admin no Postiz da VPS → **trancar o cadastro** (`DISABLE_REGISTRATION=true`).
2. Conectar **Instagram Business + Página do Facebook** da Priscila.
3. Gerar os 10 carrosséis → agendar pelo Postiz.
