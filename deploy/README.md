# Deploy — Hostinger VPS (Ubuntu 22.04)

Guia rapido para deploy em producao na VPS W8 (Hostinger).

## 1) Preparar VPS

```bash
# como root
apt update && apt upgrade -y
apt install -y python3.12 python3.12-venv python3-pip nginx git certbot python3-certbot-nginx ufw
ufw allow 'Nginx Full'
ufw allow OpenSSH
ufw enable
```

## 2) Criar usuario nao-root

```bash
adduser priscila
usermod -aG sudo priscila
mkdir -p /var/www
chown priscila:priscila /var/www
```

## 3) Clonar projeto

```bash
su - priscila
cd /var/www
git clone <REPO_URL> imobiliaria
cd imobiliaria
python3.12 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
```

## 4) Configurar `.env` de producao

Copiar `.env.example` para `.env` e definir:

```env
JWT_SECRET=<gerar com: python -c "import secrets; print(secrets.token_urlsafe(64))">
ADMIN_BOOTSTRAP_EMAIL=priscila@vasconcelosimoveis.com.br
ADMIN_BOOTSTRAP_SENHA=<senha-forte-inicial>
SITE_DB_PATH=/var/www/imobiliaria/data/site.db
DOCS_DIR=/var/www/imobiliaria/data/docs
CORS_ORIGINS=https://vasconcelosimoveis.com.br
WATERMARK_ATIVO=1
# IMPORTANTE: NAO definir DEV_OPEN_ADMIN em producao
```

Inicializar banco:

```bash
./venv/bin/python -c "from app.db import init_db; init_db()"
```

## 5) Servico systemd

Copiar `deploy/imobiliaria.service` para `/etc/systemd/system/imobiliaria.service`:

```bash
sudo cp deploy/imobiliaria.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable imobiliaria
sudo systemctl start imobiliaria
sudo systemctl status imobiliaria
```

## 6) Nginx

Copiar `deploy/nginx.conf.example` para `/etc/nginx/sites-available/imobiliaria`,
ajustar `server_name`, criar symlink:

```bash
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/imobiliaria
sudo ln -s /etc/nginx/sites-available/imobiliaria /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 7) HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d vasconcelosimoveis.com.br -d www.vasconcelosimoveis.com.br
```

Renovacao automatica ja vem por padrao (`/etc/cron.d/certbot`).

## 8) Backup

Cron diario do banco + docs:

```cron
0 3 * * * tar czf /home/priscila/backups/site_$(date +\%Y\%m\%d).tgz /var/www/imobiliaria/data/
0 4 * * * find /home/priscila/backups -mtime +30 -delete
```

## 9) Atualizacoes

```bash
cd /var/www/imobiliaria
git pull
./venv/bin/pip install -r requirements.txt
./venv/bin/python -c "from app.db import init_db; init_db()"
sudo systemctl restart imobiliaria
```

Ou usar `deploy/deploy.sh`:

```bash
bash deploy/deploy.sh
```

## 10) Logs e monitoramento

```bash
journalctl -u imobiliaria -f          # logs do servico
tail -f /var/log/nginx/access.log     # acessos
tail -f /var/log/nginx/error.log      # erros
```

## Checklist seguranca antes de publicar

- [ ] `DEV_OPEN_ADMIN` removido do `.env`
- [ ] `JWT_SECRET` com 64+ bytes aleatorios (NAO usar default)
- [ ] `ADMIN_BOOTSTRAP_SENHA` trocada apos primeiro login
- [ ] HTTPS ativo (certbot OK)
- [ ] Firewall (ufw) ativo
- [ ] Backup diario configurado
- [ ] CORS restrito ao dominio real
