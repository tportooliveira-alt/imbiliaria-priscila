from __future__ import annotations

import gc
import importlib
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente(monkeypatch: pytest.MonkeyPatch):
    raiz = Path(__file__).resolve().parents[1]
    workdir = raiz / ".tmp-test-url-policies"
    workdir.mkdir(exist_ok=True)
    db_path = workdir / "test.db"
    if db_path.exists():
        db_path.unlink()
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv("DEV_OPEN_ADMIN", "0")
    monkeypatch.setenv(
        "JWT_SECRET",
        "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa",
    )

    from app import db as db_mod
    importlib.reload(db_mod)
    from app import auth as auth_mod
    importlib.reload(auth_mod)
    from app import leads as leads_mod
    importlib.reload(leads_mod)
    from app import imoveis as imoveis_mod
    importlib.reload(imoveis_mod)
    from app import routes_admin as ra
    importlib.reload(ra)
    from app import routes_crm as rc
    importlib.reload(rc)
    from app import routes_publicas as rp
    importlib.reload(rp)

    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")

    import server as server_mod
    importlib.reload(server_mod)

    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()
    if db_path.exists():
        db_path.unlink()
    shutil.rmtree(workdir, ignore_errors=True)


def _login(cli: TestClient) -> dict[str, str]:
    r = cli.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "senha-segura-123"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_robots_txt_bloqueia_admin_e_exibe_sitemap(cliente: TestClient) -> None:
    r = cliente.get("/robots.txt")
    assert r.status_code == 200
    texto = r.text
    assert "Disallow: /admin/" in texto
    assert "Disallow: /api/admin/" in texto
    assert "/sitemap.xml" in texto


def test_sitemap_xml_lista_paginas_publicas(cliente: TestClient) -> None:
    r = cliente.get("/sitemap.xml")
    assert r.status_code == 200
    xml = r.text
    assert "<loc>http://testserver/</loc>" in xml
    assert "<loc>http://testserver/v3-editorial/</loc>" in xml
    assert "<loc>http://testserver/v3-editorial/privacidade.html</loc>" in xml
    assert "/admin/" not in xml
    assert "/api/admin/" not in xml


def test_admin_respostas_carregam_noindex(cliente: TestClient) -> None:
    h = _login(cliente)

    r = cliente.get("/admin/?reset=1")
    assert r.status_code == 200
    assert r.headers.get("X-Robots-Tag") == "noindex, nofollow"

    r = cliente.get("/api/admin/dashboard", headers=h)
    assert r.status_code == 200
    assert r.headers.get("X-Robots-Tag") == "noindex, nofollow"
