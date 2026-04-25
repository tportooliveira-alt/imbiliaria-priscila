"""Etapa 1 — Estrutura do projeto e mídias da abertura."""
from __future__ import annotations

from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Layout de pastas
# ─────────────────────────────────────────────────────────────────────────────
def test_pastas_principais_existem(proj_dir: Path) -> None:
    for nome in ("assets", "shared", "v3-editorial", "tests"):
        assert (proj_dir / nome).is_dir(), f"Pasta ausente: {nome}"


# ─────────────────────────────────────────────────────────────────────────────
# Vídeos da abertura
# ─────────────────────────────────────────────────────────────────────────────
def test_video_ia_falando_existe(assets_dir: Path) -> None:
    v = assets_dir / "ia-falando.mp4"
    assert v.exists() and v.stat().st_size > 100_000


def test_video_ia_casa_existe(assets_dir: Path) -> None:
    v = assets_dir / "ia-casa.mp4"
    assert v.exists() and v.stat().st_size > 100_000


def test_fotos_priscila_existem(assets_dir: Path) -> None:
    esperadas = ["priscila-new-hero.jpeg", "priscila-sobre.jpg"]
    faltando = [f for f in esperadas if not (assets_dir / f).exists()]
    assert not faltando, f"Fotos faltando: {faltando}"


# ─────────────────────────────────────────────────────────────────────────────
# Componentes shared
# ─────────────────────────────────────────────────────────────────────────────
COMPONENTES_SHARED = [
    "OpeningVideo.jsx",
    "AIChat.jsx",
    "BuscaBairros.jsx",
    "PropertyGrid.jsx",
    "data.jsx",
]


def test_componentes_shared_existem(shared_dir: Path) -> None:
    faltando = [c for c in COMPONENTES_SHARED if not (shared_dir / c).exists()]
    assert not faltando, f"Componentes faltando: {faltando}"


def test_v3_index_carrega_componentes(v3_dir: Path) -> None:
    html = (v3_dir / "index.html").read_text(encoding="utf-8")
    for c in COMPONENTES_SHARED:
        assert c in html, f"index.html não referencia {c}"
