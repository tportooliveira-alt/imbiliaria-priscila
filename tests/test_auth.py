"""Testes do modulo de autenticacao (bcrypt + JWT + rate limit)."""
from __future__ import annotations

import gc
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def db_temporario(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Roteia o DB para um arquivo temporario isolado."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("SITE_DB_PATH", str(db_path))
    monkeypatch.setenv(
        "JWT_SECRET",
        "secret-de-teste-com-tamanho-suficiente-para-hmac-sha256-xxxxxx",
    )

    from app import db as db_mod
    importlib.reload(db_mod)
    from app import auth as auth_mod
    importlib.reload(auth_mod)

    db_mod.init_db()
    yield auth_mod, db_mod
    gc.collect()


def test_hash_e_verificacao_de_senha(db_temporario):
    auth, _ = db_temporario
    h = auth.hash_senha("senha-forte-123")
    assert h != "senha-forte-123"
    assert auth.verifica_senha("senha-forte-123", h) is True
    assert auth.verifica_senha("senha-errada", h) is False


def test_token_jwt_round_trip(db_temporario):
    auth, _ = db_temporario
    token = auth.gerar_token(1, "test@x.com", "admin")
    payload = auth.decodar_token(token)
    assert payload is not None
    assert payload["email"] == "test@x.com"
    assert payload["role"] == "admin"
    assert payload["sub"] == "1"


def test_token_invalido_retorna_none(db_temporario):
    auth, _ = db_temporario
    assert auth.decodar_token("token-invalido.aaa.bbb") is None
    assert auth.decodar_token("") is None


def test_criar_e_autenticar_usuario(db_temporario):
    auth, _ = db_temporario
    uid = auth.criar_usuario("priscila@vdc.com", "minha-senha-123", role="admin")
    assert uid > 0

    user = auth.autenticar("priscila@vdc.com", "minha-senha-123")
    assert user is not None
    assert user["email"] == "priscila@vdc.com"
    assert user["role"] == "admin"

    assert auth.autenticar("priscila@vdc.com", "errada") is None
    assert auth.autenticar("nao-existe@x.com", "qualquer") is None


def test_email_normalizado_lowercase(db_temporario):
    auth, _ = db_temporario
    auth.criar_usuario("PriScilA@Vdc.Com", "senha-123", role="admin")
    assert auth.autenticar("priscila@vdc.com", "senha-123") is not None
    assert auth.autenticar("PRISCILA@VDC.COM", "senha-123") is not None


def test_script_criar_admin_existe(proj_dir: Path) -> None:
    src = (proj_dir / "scripts" / "criar_admin.py").read_text(encoding="utf-8")
    assert "auth.criar_usuario" in src
    assert "UPDATE usuarios SET senha_hash" in src
    assert "secrets.token_urlsafe" in src


def test_rate_limit_bloqueia_apos_5_tentativas(db_temporario):
    auth, _ = db_temporario
    ip = "192.168.0.10"
    for _ in range(5):
        auth.registrar_tentativa(ip)
    assert auth.excedeu_limite(ip) is True
    assert auth.excedeu_limite("outro-ip") is False
