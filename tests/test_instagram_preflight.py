"""Testes do preflight seguro Instagram/Meta."""
from __future__ import annotations

import json

from scripts import verificar_instagram_meta


def test_preflight_json_pronto_nao_expoe_token(monkeypatch, capsys):
    token_fake = "token-que-nao-pode-sair"
    monkeypatch.setenv("META_PAGE_TOKEN", token_fake)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_GRAPH_VERSION", "v99.0")
    monkeypatch.setenv("MCP_IG_PUBLISH_ENABLED", "0")

    rc = verificar_instagram_meta.main([
        "--no-env",
        "--json",
        "--media-url",
        "https://pvscelosimobiliaria.com/ig-media/reel.mp4",
    ])

    saida = capsys.readouterr().out
    dados = json.loads(saida)
    assert rc == 0
    assert dados["preflight_ok"] is True
    assert dados["midias"] == [
        {"url": "https://pvscelosimobiliaria.com/ig-media/reel.mp4", "ok": True}
    ]
    assert token_fake not in saida


def test_preflight_pendente_com_midia_privada(monkeypatch, capsys):
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_GRAPH_VERSION", "v99.0")

    rc = verificar_instagram_meta.main([
        "--no-env",
        "--media-url",
        "https://10.0.0.5/reel.mp4",
    ])

    saida = capsys.readouterr().out
    assert rc == 2
    assert "REJEITADA" in saida
    assert "Resultado: PENDENTE" in saida


def test_preflight_allow_pending_retorna_sucesso(monkeypatch, capsys):
    monkeypatch.delenv("META_PAGE_TOKEN", raising=False)
    monkeypatch.delenv("IG_BUSINESS_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("META_GRAPH_VERSION", raising=False)

    rc = verificar_instagram_meta.main(["--no-env", "--allow-pending"])

    saida = capsys.readouterr().out
    assert rc == 0
    assert "Resultado: PENDENTE" in saida


def test_relatorio_html_usa_marca_e_nao_expoe_token(monkeypatch):
    token_fake = "token-visual-nao-vaza"
    monkeypatch.setenv("META_PAGE_TOKEN", token_fake)
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_GRAPH_VERSION", "v99.0")

    status = verificar_instagram_meta._preflight([
        "https://pvscelosimobiliaria.com/ig-media/reel.mp4"
    ])
    html = verificar_instagram_meta._html_relatorio(
        status,
        "../../assets/marketing/logo-mono-offwhite.png",
    )

    assert "Priscila Social API" in html
    assert "logo-mono-offwhite.png" in html
    assert "Preflight Instagram e Meta" in html
    assert "Operação Multiplace" in html
    assert "Proteções ativas" in html
    assert token_fake not in html
