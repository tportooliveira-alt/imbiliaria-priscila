"""Testes da ponte Instagram/Meta.

O foco aqui e garantir falha fechada: sem credenciais ou com midia local,
o cliente nao deve tentar chamar a Graph API nem publicar nada.
"""
from __future__ import annotations

from app import instagram


def _bloquear_rede(monkeypatch):
    def fake_urlopen(*_args, **_kwargs):
        raise AssertionError("nao deveria chamar a Graph API neste teste")

    monkeypatch.setattr(instagram.urllib.request, "urlopen", fake_urlopen)


def test_instagram_indisponivel_sem_env(monkeypatch):
    monkeypatch.delenv("META_PAGE_TOKEN", raising=False)
    monkeypatch.delenv("IG_BUSINESS_ACCOUNT_ID", raising=False)

    assert instagram.disponivel() is False


def test_status_config_sem_env_mostra_faltantes_sem_segredos(monkeypatch):
    monkeypatch.delenv("META_PAGE_TOKEN", raising=False)
    monkeypatch.delenv("IG_BUSINESS_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("META_GRAPH_VERSION", raising=False)
    monkeypatch.delenv("MCP_IG_PUBLISH_ENABLED", raising=False)

    status = instagram.status_config()

    assert status["disponivel"] is False
    assert status["credenciais"] == {
        "META_PAGE_TOKEN": False,
        "IG_BUSINESS_ACCOUNT_ID": False,
    }
    assert set(status["faltando"]) == {"META_PAGE_TOKEN", "IG_BUSINESS_ACCOUNT_ID"}
    assert status["graph_version_configurada"] is False
    assert status["avisos"]
    assert status["mcp_publicacao_habilitada"] is False
    assert status["segredos_expostos"] is False


def test_status_config_com_env_nao_expoe_token(monkeypatch):
    token_fake = "token-super-secreto"
    monkeypatch.setenv("META_PAGE_TOKEN", token_fake)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_GRAPH_VERSION", "v99.0")
    monkeypatch.setenv("MCP_IG_PUBLISH_ENABLED", "1")

    status = instagram.status_config()

    assert status["disponivel"] is True
    assert status["graph_version"] == "v99.0"
    assert status["graph_version_configurada"] is True
    assert status["credenciais"] == {
        "META_PAGE_TOKEN": True,
        "IG_BUSINESS_ACCOUNT_ID": True,
    }
    assert status["faltando"] == []
    assert status["avisos"] == []
    assert status["mcp_publicacao_habilitada"] is True
    assert token_fake not in repr(status)


def test_leitura_sem_ig_id_falha_sem_rede(monkeypatch):
    _bloquear_rede(monkeypatch)
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")
    monkeypatch.delenv("IG_BUSINESS_ACCOUNT_ID", raising=False)

    r = instagram.perfil()

    assert r.ok is False
    assert r.erro == "IG_BUSINESS_ACCOUNT_ID ausente"


def test_leitura_sem_token_falha_sem_rede(monkeypatch):
    _bloquear_rede(monkeypatch)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.delenv("META_PAGE_TOKEN", raising=False)

    r = instagram.listar_midias()

    assert r.ok is False
    assert r.erro == "META_PAGE_TOKEN ausente no .env"


def test_publicar_foto_rejeita_url_nao_publica_sem_rede(monkeypatch):
    _bloquear_rede(monkeypatch)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")

    r = instagram.publicar_foto("C:/Users/Thiago/foto.jpg", "legenda")

    assert r.ok is False
    assert "URL pública HTTPS" in (r.erro or "")


def test_publicar_foto_rejeita_ip_privado_sem_rede(monkeypatch):
    _bloquear_rede(monkeypatch)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")

    r = instagram.publicar_foto("https://192.168.0.10/foto.jpg", "legenda")

    assert r.ok is False
    assert "URL pública HTTPS" in (r.erro or "")


def test_publicar_carrossel_rejeita_quantidade_sem_rede(monkeypatch):
    _bloquear_rede(monkeypatch)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")

    r = instagram.publicar_carrossel(["https://pvscelosimobiliaria.com/a.jpg"], "legenda")

    assert r.ok is False
    assert "2 a 10" in (r.erro or "")


def test_publicar_reel_rejeita_capa_local_sem_rede(monkeypatch):
    _bloquear_rede(monkeypatch)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")

    r = instagram.publicar_reel(
        "https://pvscelosimobiliaria.com/reel.mp4",
        "legenda",
        capa_url="http://localhost/capa.jpg",
    )

    assert r.ok is False
    assert "capa_url" in (r.erro or "")
