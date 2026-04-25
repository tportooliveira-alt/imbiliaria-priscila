"""Testes end-to-end do CRUD admin via FastAPI TestClient."""
from __future__ import annotations

import gc
import importlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture
def cliente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv(
        "JWT_SECRET",
        "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa",
    )

    # Recarrega modulos que dependem do env do DB
    from app import db as db_mod
    importlib.reload(db_mod)
    from app import auth as auth_mod
    importlib.reload(auth_mod)
    from app import imoveis as imoveis_mod
    importlib.reload(imoveis_mod)
    from app import routes_admin as routes_mod
    importlib.reload(routes_mod)

    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")

    import server as server_mod
    importlib.reload(server_mod)

    client = TestClient(server_mod.app)
    with client:
        yield client
    # forca liberacao de handles do sqlite no Windows antes do cleanup do tmp_path
    gc.collect()


def _login(cli: TestClient) -> str:
    r = cli.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "senha-segura-123"})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_login_sucesso(cliente):
    r = cliente.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "senha-segura-123"})
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "admin"
    assert body["token"]


def test_login_senha_errada(cliente):
    r = cliente.post("/api/auth/login", json={"email": "priscila@vdc.com", "senha": "errada-errada"})
    assert r.status_code == 401


def test_endpoints_admin_exigem_token(cliente):
    r = cliente.post("/api/admin/imoveis", json={"titulo": "x", "bairro": "x", "tipo": "Casa", "preco": 1})
    assert r.status_code == 401


def test_crud_imovel_completo(cliente):
    tok = _login(cliente)

    # criar
    r = cliente.post(
        "/api/admin/imoveis",
        json={"titulo": "Casa elegante", "bairro": "Candeias", "tipo": "Casa", "preco": 750000, "quartos": 3},
        headers=_headers(tok),
    )
    assert r.status_code == 201
    imovel = r.json()
    assert imovel["slug"].startswith("casa-elegante")

    # listar publico
    r = cliente.get("/api/imoveis")
    assert r.status_code == 200
    assert r.json()["total"] == 1

    # detalhe por slug
    r = cliente.get(f"/api/imoveis/{imovel['slug']}")
    assert r.status_code == 200
    assert r.json()["titulo"] == "Casa elegante"

    # atualizar
    r = cliente.put(
        f"/api/admin/imoveis/{imovel['id']}",
        json={"preco": 720000, "destaque": True},
        headers=_headers(tok),
    )
    assert r.status_code == 200
    assert r.json()["preco"] == 720000
    assert r.json()["destaque"] is True

    # desativar
    r = cliente.delete(f"/api/admin/imoveis/{imovel['id']}", headers=_headers(tok))
    assert r.status_code == 204

    # nao aparece mais publico
    r = cliente.get(f"/api/imoveis/{imovel['slug']}")
    assert r.status_code == 404


def test_filtro_por_bairro(cliente):
    tok = _login(cliente)
    cliente.post("/api/admin/imoveis", json={"titulo": "Casa A", "bairro": "Candeias", "tipo": "Casa", "preco": 100}, headers=_headers(tok))
    cliente.post("/api/admin/imoveis", json={"titulo": "Casa B", "bairro": "Centro", "tipo": "Casa", "preco": 100}, headers=_headers(tok))

    r = cliente.get("/api/imoveis?bairro=Candeias")
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["bairro"] == "Candeias"


def test_upload_imagem_completo(cliente):
    tok = _login(cliente)
    r = cliente.post(
        "/api/admin/imoveis",
        json={"titulo": "Casa com fotos", "bairro": "Centro", "tipo": "Casa", "preco": 500000},
        headers=_headers(tok),
    )
    imovel_id = r.json()["id"]

    # gera JPEG real em memoria
    img = Image.new("RGB", (1200, 800), color=(80, 120, 160))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    r = cliente.post(
        f"/api/admin/imoveis/{imovel_id}/imagens",
        files=[("files", ("teste.jpg", buf, "image/jpeg"))],
        data={"tipo": "sala"},
        headers=_headers(tok),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["total"] == 1
    assert body["imagens"][0]["tipo"] == "sala"


def test_upload_rejeita_arquivo_nao_imagem(cliente):
    tok = _login(cliente)
    r = cliente.post("/api/admin/imoveis", json={"titulo": "Casa Z", "bairro": "Centro", "tipo": "Casa", "preco": 100}, headers=_headers(tok))
    imovel_id = r.json()["id"]

    r = cliente.post(
        f"/api/admin/imoveis/{imovel_id}/imagens",
        files=[("files", ("fake.txt", b"isso nao e imagem", "text/plain"))],
        headers=_headers(tok),
    )
    assert r.status_code == 400


def test_headers_de_seguranca_presentes(cliente):
    r = cliente.get("/api/imoveis")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert "strict-origin" in r.headers.get("Referrer-Policy", "")
