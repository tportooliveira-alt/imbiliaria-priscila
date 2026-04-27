"""Configuração de logging — arquivo rotativo + console."""
from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "logs"


def setup_logging(level: int = logging.INFO) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    root = logging.getLogger()
    if any(getattr(h, "_pv_site", False) for h in root.handlers):
        return  # idempotente

    arquivo = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    arquivo.setFormatter(logging.Formatter(fmt, datefmt))
    arquivo._pv_site = True  # marcador

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt, datefmt))
    console._pv_site = True

    root.setLevel(level)
    root.addHandler(arquivo)
    root.addHandler(console)
