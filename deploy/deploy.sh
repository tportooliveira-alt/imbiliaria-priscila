#!/usr/bin/env bash
# deploy.sh — atualiza app em producao
# Uso: bash deploy/deploy.sh

set -euo pipefail

APP_DIR="/var/www/imobiliaria"
SERVICE="imobiliaria"

cd "$APP_DIR"

echo "==> Atualizando codigo..."
git pull --ff-only

echo "==> Atualizando dependencias..."
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

echo "==> Migrando banco..."
./venv/bin/python -c "from app.db import init_db; init_db()"

echo "==> Reiniciando servico..."
sudo systemctl restart "$SERVICE"
sleep 2
sudo systemctl status "$SERVICE" --no-pager | head -15

echo ""
echo "==> Smoke test..."
curl -fsS http://127.0.0.1:8000/api/health || echo "(health indisponivel — verifique logs)"

echo ""
echo "✓ Deploy concluido."
