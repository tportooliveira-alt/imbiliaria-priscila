#!/usr/bin/env bash
# Backup diário do CRM (data/site.db) com rotação. Sem segredos — seguro no git.
# Usa a API de backup do SQLite (consistente mesmo com o app escrevendo).
set -euo pipefail

DB="/var/www/imobiliaria/data/site.db"
DEST="/root/backups"
KEEP=14                      # mantém os últimos 14 backups (~2 semanas)
PY="/var/www/imobiliaria/venv/bin/python"

mkdir -p "$DEST"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$DEST/site-$STAMP.db"

# .backup atômico via API do sqlite3 (não corrompe se o app gravar no meio)
"$PY" - "$DB" "$OUT" <<'PYEOF'
import sqlite3, sys
src, dst = sys.argv[1], sys.argv[2]
s = sqlite3.connect(src); d = sqlite3.connect(dst)
with d:
    s.backup(d)
s.close(); d.close()
PYEOF

gzip -f "$OUT"
chmod 600 "$OUT.gz"

# rotação: apaga os mais antigos além de KEEP
ls -1t "$DEST"/site-*.db.gz 2>/dev/null | tail -n +$((KEEP+1)) | xargs -r rm -f

echo "$(date -Is) backup ok: $OUT.gz ($(du -h "$OUT.gz" | cut -f1))"
