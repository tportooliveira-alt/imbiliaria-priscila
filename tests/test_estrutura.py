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


def test_busca_natural_alimenta_grade(shared_dir: Path, v3_dir: Path) -> None:
    app = (v3_dir / "app.jsx").read_text(encoding="utf-8")
    grid = (shared_dir / "PropertyGrid.jsx").read_text(encoding="utf-8")
    busca = (shared_dir / "BuscaNatural.jsx").read_text(encoding="utf-8")

    assert "aplicarBuscaNatural" in app
    assert "resultadoBuscaNatural" in app
    assert "onResultado={aplicarBuscaNatural}" in app
    assert "resultadoBusca={resultadoBuscaNatural}" in app
    assert "resultadoBusca?.imoveis" in grid
    assert "normalizarImovelPublico" in grid
    assert "busca-natural:resultado" in busca


def test_deploy_tem_agente_24_7(proj_dir: Path) -> None:
    agente = (proj_dir / "scripts" / "agente_lembretes.py").read_text(encoding="utf-8")
    service = (proj_dir / "deploy" / "imobiliaria-agente.service").read_text(encoding="utf-8")
    env = (proj_dir / ".env.exemplo").read_text(encoding="utf-8")

    assert "def executar_ciclo" in agente
    assert "agenda_repo.lembretes_a_enviar" in agente
    assert "Restart=always" in service
    assert "AGENTE_LEMBRETES_INTERVALO_SEGUNDOS" in env
