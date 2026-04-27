"""Testes do componente OpeningVideo (sequência cinematográfica em 4 fases).

Como o JSX não roda em Python, testamos por análise textual:
todas as fases declaradas, todos os vídeos referenciados, fluxo `onEnded`
correto.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def opening_src(shared_dir: Path) -> str:
    return (shared_dir / "OpeningVideo.jsx").read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Fases declaradas (3 reais: kenburns → video-ia → video-priscila → done)
# ─────────────────────────────────────────────────────────────────────────────
FASES = ("kenburns", "video-ia", "video-priscila", "done")


@pytest.mark.parametrize("fase", FASES)
def test_fase_declarada(opening_src: str, fase: str) -> None:
    assert f'"{fase}"' in opening_src, f"Fase '{fase}' ausente em OpeningVideo.jsx"


# ─────────────────────────────────────────────────────────────────────────────
# Vídeos referenciados (sem ia-casa.mp4 — fase descontinuada)
# ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "video",
    ["ia-falando.mp4", "priscila-fala.mp4"],
)
def test_video_referenciado(opening_src: str, video: str) -> None:
    assert video in opening_src, f"Vídeo '{video}' não referenciado"


# ─────────────────────────────────────────────────────────────────────────────
# Encadeamento das fases
# ─────────────────────────────────────────────────────────────────────────────
def test_kenburns_avanca_para_video_ia(opening_src: str) -> None:
    assert 'phase === "kenburns"' in opening_src
    assert 'setPhase("video-ia")' in opening_src


def test_video_ia_avanca_para_priscila_ou_done(opening_src: str) -> None:
    assert 'handleVideoIaEnded' in opening_src
    assert 'hasPriscilaVideo ? "video-priscila" : "done"' in opening_src


def test_video_priscila_avanca_para_done(opening_src: str) -> None:
    assert 'handleVideoPriscilaEnded' in opening_src
    assert 'setPhase("done")' in opening_src


# ─────────────────────────────────────────────────────────────────────────────
# Botão Pular (3: kenburns skip + video-ia skip + video-priscila skip)
# ─────────────────────────────────────────────────────────────────────────────
def test_botao_skip_em_todas_fases(opening_src: str) -> None:
    # 3 botões skip: ken burns + video-ia + video-priscila
    assert opening_src.count('className="ov-skip"') >= 3
