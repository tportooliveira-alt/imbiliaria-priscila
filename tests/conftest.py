"""Fixtures compartilhadas para a suite de testes do site Priscila Vasconcelos."""
from __future__ import annotations

from pathlib import Path

import pytest


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
