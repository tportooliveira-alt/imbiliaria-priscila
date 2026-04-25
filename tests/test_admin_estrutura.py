"""Testes estruturais do Lightbox/Galeria e do painel admin."""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def proj() -> Path:
    return Path(__file__).resolve().parent.parent


def test_lightbox_jsx_existe_com_componentes(proj: Path):
    arq = proj / "shared" / "Lightbox.jsx"
    assert arq.exists()
    src = arq.read_text(encoding="utf-8")
    assert "function Lightbox(" in src
    assert "function GaleriaImovel(" in src
    assert "ArrowRight" in src and "ArrowLeft" in src and "Escape" in src
    assert "srcSet" in src  # multi-resolucao
    assert "lbx-thumb" in src  # miniaturas


def test_lightbox_css_existe(proj: Path):
    arq = proj / "shared" / "lightbox.css"
    assert arq.exists()
    css = arq.read_text(encoding="utf-8")
    for sel in [".lbx", ".lbx-stage", ".lbx-thumbs", ".gal-trigger"]:
        assert sel in css


def test_admin_index_html_existe(proj: Path):
    arq = proj / "admin" / "index.html"
    assert arq.exists()
    html = arq.read_text(encoding="utf-8")
    assert "noindex,nofollow" in html  # nao indexavel
    assert "admin.jsx" in html


def test_admin_jsx_tem_login_e_crud(proj: Path):
    arq = proj / "admin" / "admin.jsx"
    assert arq.exists()
    src = arq.read_text(encoding="utf-8")
    assert "function Login" in src
    assert "function FormImovel" in src
    assert "function GerenciadorImagens" in src
    assert "/api/auth/login" in src
    assert "/api/admin/imoveis" in src


def test_admin_css_existe(proj: Path):
    arq = proj / "admin" / "admin.css"
    assert arq.exists()


def test_servidor_serve_pasta_admin(proj: Path):
    src = (proj / "server.py").read_text(encoding="utf-8")
    assert '/admin' in src
    assert "admin_dir" in src
