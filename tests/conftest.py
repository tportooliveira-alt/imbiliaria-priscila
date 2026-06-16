"""Fixtures compartilhadas para a suite de testes do site Priscila Vasconcelos."""
from __future__ import annotations

from pathlib import Path

import pytest


# Chaves externas que a suite assume AUSENTES (testes rodam em modo "sem chave"/fallback).
# O .env real fica carregado em produção; aqui limpamos por teste pra a suite ser confiável.
_CHAVES_EXTERNAS = (
    "GOOGLE_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY",
    "EVOLUTION_WEBHOOK_TOKEN", "EVOLUTION_API_URL", "EVOLUTION_API_KEY",
    "ELEVENLABS_API_KEY", "GROQ_API_KEY", "WHATSAPP_AUTO_REPLY",
)


@pytest.fixture(autouse=True)
def _isolar_env(monkeypatch):
    """Isola o ambiente: remove as chaves externas pra cada teste (evita env leakage do .env real).

    Também neutraliza `load_dotenv` — algumas fixtures fazem `importlib.reload(server)`, que re-roda
    `load_dotenv()` e recolocaria as chaves do .env real depois da limpeza. Com o no-op, a limpeza persiste.
    """
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: None)
    for k in _CHAVES_EXTERNAS:
        monkeypatch.delenv(k, raising=False)


@pytest.fixture(scope="session")
def proj_dir() -> Path:
    """Raiz do projeto site-imobiliaria."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def assets_dir(proj_dir: Path) -> Path:
    return proj_dir / "assets"


@pytest.fixture(scope="session")
def shared_dir(proj_dir: Path) -> Path:
    return proj_dir / "shared"


@pytest.fixture(scope="session")
def v3_dir(proj_dir: Path) -> Path:
    return proj_dir / "v3-editorial"


@pytest.fixture(scope="session")
def segredos_dir() -> Path:
    """Pasta fora do OneDrive onde devem ficar as chaves de API."""
    return Path("C:/segredos")
