#!/usr/bin/env bash
# Deploy da VPS: puxa o que veio do git (editado no PC), reconstrói a home e reinicia.
# Uso: ./deploy.sh    (rodar DENTRO de /var/www/imobiliaria, na VPS)
set -euo pipefail
cd "$(dirname "$0")"

BRANCH="feat/calibracao-design-skills"
echo "── Deploy imobiliária ─────────────────────────────"

echo "→ 1/5 puxando do GitHub (branch $BRANCH)…"
git fetch --quiet origin "$BRANCH"
if ! git pull --ff-only origin "$BRANCH"; then
  echo "❌ pull não foi limpo (a VPS tem mudanças não enviadas, ou houve conflito)."
  echo "   Resolva com: git status   — e evite editar os dois lados ao mesmo tempo."
  exit 1
fi

echo "→ 2/5 validando o código (py_compile — aborta se houver erro de sintaxe)…"
PY="venv/bin/python"; [ -x "$PY" ] || PY="python3"
if ! "$PY" -m py_compile server.py app/*.py; then
  echo "❌ erro de sintaxe no Python — deploy ABORTADO (nada foi reiniciado)."
  exit 1
fi

echo "→ 3/5 reconstruindo a home (assets/preview.html → v3-editorial)…"
python3 scripts/build_home.py

echo "→ 4/5 reiniciando o serviço…"
sudo systemctl restart imobiliaria.service
sleep 2

echo "→ 5/5 conferindo…"
ST=$(systemctl is-active imobiliaria.service || true)
CODE=$(curl -s -o /dev/null -w '%{http_code}' https://pvscelosimobiliaria.com/ || true)
echo "   serviço: $ST | site: HTTP $CODE"
[ "$ST" = "active" ] && [ "$CODE" = "200" ] && echo "✅ deploy concluído com sucesso." || { echo "⚠ algo fora do esperado — verifique os logs: journalctl -u imobiliaria -n 50"; exit 1; }
