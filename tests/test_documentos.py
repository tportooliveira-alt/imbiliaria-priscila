"""Testes W5: documentos + consentimentos LGPD + proposta PDF."""
from __future__ import annotations

import gc
import importlib
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def cliente(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "test.db"
    docs_dir = tmp_path / "docs"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv("DOCS_DIR", str(docs_dir))
    monkeypatch.setenv("DEV_OPEN_ADMIN", "0")
    monkeypatch.setenv(
        "JWT_SECRET",
        "test-secret-key-com-tamanho-suficiente-para-hmac-sha256-aaaaaa",
    )
    for mod in ["app.db", "app.auth", "app.imoveis", "app.leads",
                "app.documentos", "app.proposta_pdf",
                "app.routes_admin", "app.routes_publicas", "app.routes_crm"]:
        if mod in importlib.sys.modules:
            importlib.reload(importlib.sys.modules[mod])
        else:
            importlib.import_module(mod)
    from app import db as db_mod, auth as auth_mod
    db_mod.init_db()
    auth_mod.criar_usuario("priscila@vdc.com", "senha-segura-123", role="admin")
    import server as server_mod
    importlib.reload(server_mod)
    client = TestClient(server_mod.app)
    with client:
        yield client
    gc.collect()


def _login(c: TestClient) -> dict:
    r = c.post(
        "/api/auth/login",
        json={"email": "priscila@vdc.com", "senha": "senha-segura-123"},
    )
    return {"Authorization": f"Bearer {r.json()['token']}"}


# ─── unit: repo ──────────────────────────────────────────────────────────────
def test_salvar_e_listar(cliente):
    from app import documentos
    doc = documentos.salvar(
        nome_original="rg.pdf",
        conteudo=b"%PDF-1.4 fake",
        mime="application/pdf",
        tipo="rg",
    )
    assert doc["id"] > 0
    assert doc["nome_original"] == "rg.pdf"
    assert Path(doc["caminho"]).exists()
    items = documentos.listar()
    assert len(items) == 1


def test_salvar_tipo_invalido(cliente):
    from app import documentos
    with pytest.raises(ValueError):
        documentos.salvar(
            nome_original="x.pdf", conteudo=b"x",
            mime="application/pdf", tipo="hackerman",
        )


def test_salvar_arquivo_vazio(cliente):
    from app import documentos
    with pytest.raises(ValueError):
        documentos.salvar(nome_original="x.pdf", conteudo=b"", mime="application/pdf")


def test_salvar_mime_proibido(cliente):
    from app import documentos
    with pytest.raises(ValueError):
        documentos.salvar(
            nome_original="x.exe", conteudo=b"MZ\x90\x00",
            mime="application/x-msdownload",
        )


def test_salvar_excede_tamanho(cliente, monkeypatch):
    from app import documentos
    monkeypatch.setattr(documentos, "TAMANHO_MAX_BYTES", 100)
    with pytest.raises(ValueError):
        documentos.salvar(
            nome_original="big.pdf", conteudo=b"x" * 200,
            mime="application/pdf",
        )


def test_remover_apaga_arquivo(cliente):
    from app import documentos
    doc = documentos.salvar(
        nome_original="x.pdf", conteudo=b"%PDF-1.4 z",
        mime="application/pdf",
    )
    caminho = Path(doc["caminho"])
    assert caminho.exists()
    assert documentos.remover(doc["id"]) is True
    assert not caminho.exists()
    assert documentos.detalhar(doc["id"]) is None


def test_consentimento_repo(cliente):
    from app import documentos
    cid = documentos.registrar_consentimento(
        tipo="contato", aceito=True,
        email="ana@x.com", ip="127.0.0.1", user_agent="ua",
    )
    assert cid > 0
    items = documentos.listar_consentimentos(email="ana@x.com")
    assert len(items) == 1
    assert items[0]["aceito"] == 1


def test_consentimento_tipo_invalido(cliente):
    from app import documentos
    with pytest.raises(ValueError):
        documentos.registrar_consentimento(tipo="invalido")


# ─── endpoints admin ────────────────────────────────────────────────────────
def test_endpoint_upload_e_listar(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/documentos",
        files={"arquivo": ("rg.pdf", b"%PDF-1.4 fake", "application/pdf")},
        data={"tipo": "rg", "observacoes": "teste"},
        headers=h,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["ok"] is True
    assert "caminho" not in body["documento"]
    doc_id = body["documento"]["id"]

    r = cliente.get("/api/admin/documentos", headers=h)
    assert r.json()["total"] == 1

    r = cliente.get(f"/api/admin/documentos/{doc_id}/download", headers=h)
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF")

    r = cliente.delete(f"/api/admin/documentos/{doc_id}", headers=h)
    assert r.status_code == 204


def test_upload_exige_admin(cliente):
    r = cliente.post(
        "/api/admin/documentos",
        files={"arquivo": ("x.pdf", b"x", "application/pdf")},
    )
    assert r.status_code == 401


def test_upload_validacao_422(cliente):
    h = _login(cliente)
    r = cliente.post(
        "/api/admin/documentos",
        files={"arquivo": ("x.exe", b"MZ", "application/x-msdownload")},
        data={"tipo": "outro"},
        headers=h,
    )
    assert r.status_code == 422


def test_consentimento_publico_endpoint(cliente):
    r = cliente.post(
        "/api/consentimento",
        json={"tipo": "contato", "aceito": True, "email": "ana@x.com"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["ok"] is True


def test_proposta_pdf_endpoint(cliente):
    h = _login(cliente)
    from app import imoveis as imoveis_repo
    from app import leads as leads_repo

    imovel = imoveis_repo.criar_imovel({
        "titulo": "Casa Centro", "bairro": "Centro", "tipo": "Casa",
        "quartos": 3, "suites": 1, "vagas": 2, "area_util": 180,
        "preco": 850000, "descricao": "X",
    })
    lead_id = leads_repo.upsert_lead(
        nome="Ana Silva", email="ana@x.com", telefone="77999990000", origem="manual",
    )

    r = cliente.post(
        "/api/admin/proposta-pdf",
        json={
            "imovel_id": imovel["id"],
            "lead_id": lead_id,
            "valor_proposta": 800000,
            "forma_pagamento": "Financiamento Caixa",
            "condicoes": "Sinal de 50k",
        },
        headers=h,
    )
    assert r.status_code == 200, r.text
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")

    # confirma que documento foi salvo
    r2 = cliente.get(f"/api/admin/documentos?lead_id={lead_id}", headers=h)
    items = r2.json()["items"]
    assert any(it["tipo"] == "proposta" for it in items)


def test_proposta_pdf_404_imovel(cliente):
    h = _login(cliente)
    from app import leads as leads_repo
    lid = leads_repo.upsert_lead(nome="X", email="x@x.com", origem="manual")
    r = cliente.post(
        "/api/admin/proposta-pdf",
        json={"imovel_id": 99999, "lead_id": lid, "valor_proposta": 100},
        headers=h,
    )
    assert r.status_code == 404
