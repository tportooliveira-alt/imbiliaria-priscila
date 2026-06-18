#!/usr/bin/env bash
# Verificacao antes de dizer "PRONTO" (verification-loop do ECC, versao Python deste projeto).
# Uso: bash scripts/verificar.sh   — sai 0 se tudo passou, !=0 se falhou.
set -uo pipefail
cd /var/www/imobiliaria
FALHAS=0

echo "== 1) Sintaxe (py_compile) =="
if venv/bin/python -m py_compile app/*.py server.py 2>/tmp/vc.txt; then echo "   OK ✅"
else echo "   FALHOU ❌"; cat /tmp/vc.txt; FALHAS=$((FALHAS+1)); fi

echo "== 2) Testes-chave (subset rapido, timeout 120s) =="
if timeout 120 venv/bin/python -m pytest tests/test_dispatcher.py tests/test_avaliacao.py tests/test_leads.py -q 2>&1 | tail -6; then :
else echo "   pytest com falha/timeout ❌"; FALHAS=$((FALHAS+1)); fi

echo "== 3) Smoke: site no ar + Ana viva (IA real, nao fallback) =="
code=$(curl -s -m6 -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ 2>/dev/null)
echo "   site HTTP $code"; [ "$code" = "200" ] || FALHAS=$((FALHAS+1))
set -a; . ./.env 2>/dev/null; set +a
venv/bin/python3 -c "
from app import dispatcher; import sys
r = dispatcher.responder('oi quero apto em candeias', nome_cliente='V')
print('   Ana ->', r.get('modelo'), '| fallback:', r.get('fallback'))
sys.exit(0 if not r.get('fallback') else 1)" || FALHAS=$((FALHAS+1))

echo
if [ "$FALHAS" = "0" ]; then echo "✅ VERIFICACAO PASSOU — pode dizer 'pronto'."
else echo "❌ $FALHAS bloco(s) com problema — NAO dizer pronto, corrigir antes."; fi
exit $FALHAS
