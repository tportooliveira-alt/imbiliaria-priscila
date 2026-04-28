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
    monkeypatch.setenv("DEV_OPEN_ADMIN", "0")
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


# ─── W3 Studio: auto-organizar imagens ───────────────────────────────────────
def _criar_imovel_com_3_fotos(cliente, tok) -> int:
    r = cliente.post(
        "/api/admin/imoveis",
        json={"titulo": "Casa Studio", "bairro": "Centro", "tipo": "Casa", "preco": 700000},
        headers=_headers(tok),
    )
    imovel_id = r.json()["id"]
    for cor in [(200, 100, 100), (100, 200, 100), (100, 100, 200)]:
        img = Image.new("RGB", (800, 600), color=cor)
        buf = io.BytesIO(); img.save(buf, format="JPEG", quality=85); buf.seek(0)
        cliente.post(
            f"/api/admin/imoveis/{imovel_id}/imagens",
            files=[("files", ("f.jpg", buf, "image/jpeg"))],
            headers=_headers(tok),
        )
    return imovel_id


def test_auto_organizar_fallback_sem_chave(cliente, monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    tok = _login(cliente)
    iid = _criar_imovel_com_3_fotos(cliente, tok)
    r = cliente.post(
        f"/api/admin/imoveis/{iid}/imagens/auto-organizar",
        headers=_headers(tok),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fallback"] is True
    assert "imagens" in body


def test_auto_organizar_404_sem_imagens(cliente):
    tok = _login(cliente)
    r = cliente.post(
        "/api/admin/imoveis",
        json={"titulo": "Sem fotos", "bairro": "Centro", "tipo": "Casa", "preco": 100},
        headers=_headers(tok),
    )
    iid = r.json()["id"]
    r = cliente.post(
        f"/api/admin/imoveis/{iid}/imagens/auto-organizar",
        headers=_headers(tok),
    )
    assert r.status_code == 404


def test_auto_organizar_classifica_e_ordena(cliente, monkeypatch):
    """Mocka classificacao para verificar atualizacao + reordenacao."""
    monkeypatch.setenv("GOOGLE_API_KEY", "fake")
    tok = _login(cliente)
    iid = _criar_imovel_com_3_fotos(cliente, tok)

    # primeira foto vira capa (upload define capa para a primeira), entao
    # aqui simulamos detector dizendo: 1=quarto, 2=fachada (vira capa, mas
    # ja existe → vira sala), 3=cozinha
    respostas = iter(["quarto", "fachada", "cozinha"])
    from app import visao
    monkeypatch.setattr(visao, "classificar_comodo", lambda p, **kw: next(respostas, None))

    r = cliente.post(
        f"/api/admin/imoveis/{iid}/imagens/auto-organizar",
        headers=_headers(tok),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fallback"] is False
    assert body["classificadas"] >= 2
    tipos = [im["tipo"] for im in body["imagens"]]
    # ordem editorial: capa primeiro (se houver) ou sala
    assert tipos[0] in ("capa", "sala")
    assert "cozinha" in tipos or "quarto" in tipos


def test_auto_organizar_exige_admin(cliente):
    r = cliente.post("/api/admin/imoveis/1/imagens/auto-organizar")
    assert r.status_code == 401

    assert "strict-origin" in r.headers.get("Referrer-Policy", "")


def test_gerar_descricao_sem_chave_retorna_fallback(cliente, monkeypatch):
    """B.3: gera-descricao devolve fallback gracioso sem ANTHROPIC_API_KEY."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    tok = _login(cliente)
    r = cliente.post(
        "/api/admin/imoveis/gerar-descricao",
        json={
            "titulo": "Casa moderna no Candeias",
            "bairro": "Candeias",
            "tipo": "Casa",
            "quartos": 3,
            "suites": 1,
            "vagas": 2,
            "area_util": 180,
            "preco": 850000,
            "caracteristicas": ["piscina", "churrasqueira"],
        },
        headers=_headers(tok),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["fallback"] is True
    assert "mensagem_fallback" in body


def test_gerar_descricao_exige_admin(cliente):
    r = cliente.post(
        "/api/admin/imoveis/gerar-descricao",
        json={"titulo": "X", "bairro": "Y", "tipo": "Casa"},
    )
    assert r.status_code == 401


def test_gerar_descricao_validacao_payload(cliente):
    tok = _login(cliente)
    r = cliente.post(
        "/api/admin/imoveis/gerar-descricao",
        json={"titulo": "ab", "bairro": "X", "tipo": "Casa"},  # titulo < 3
        headers=_headers(tok),
    )
    assert r.status_code == 422
