"""Backup consistente do banco (data/site.db) + rotacao.

Usa a API de backup do sqlite (lida com WAL com seguranca, sem corromper enquanto o site
escreve), compacta e mantem so as N copias mais novas. Pensado pra rodar no cron diario.
NAO toca no banco de producao alem de ler.
"""
from __future__ import annotations

import gzip
import shutil
import sqlite3
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DB = RAIZ / "data" / "site.db"
DEST = RAIZ / "backups"
MANTER = 14  # copias mais novas a preservar (1 por dia => ~2 semanas)


def main() -> None:
    DEST.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M")
    tmp = DEST / f"site-{stamp}.db"

    # backup consistente (somente leitura na origem)
    src = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    dst = sqlite3.connect(str(tmp))
    try:
        with dst:
            src.backup(dst)
    finally:
        src.close()
        dst.close()

    # compacta e remove o .db cru
    with open(tmp, "rb") as f, gzip.open(f"{tmp}.gz", "wb") as g:
        shutil.copyfileobj(f, g)
    tmp.unlink()

    # rotacao: mantem so as MANTER mais novas
    copias = sorted(DEST.glob("site-*.db.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    for velha in copias[MANTER:]:
        velha.unlink()

    print(f"backup ok: site-{stamp}.db.gz  ({min(len(copias), MANTER)} copias mantidas)")


if __name__ == "__main__":
    main()
