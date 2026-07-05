"""Testes do publicador seguro de lote Instagram."""
from __future__ import annotations

import json

from app.instagram import RespostaIG
from scripts import publicar_instagram_lote


def test_lote_dry_run_monta_fila_premium_sem_publicar(monkeypatch, capsys):
    monkeypatch.delenv("META_PAGE_TOKEN", raising=False)
    monkeypatch.delenv("IG_BUSINESS_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("META_GRAPH_VERSION", raising=False)
    monkeypatch.delenv("MCP_IG_PUBLISH_ENABLED", raising=False)

    chamado = False

    def fake_publicar_foto(*_args, **_kwargs):
        nonlocal chamado
        chamado = True
        return RespostaIG(True, dados={"id": "1"})

    monkeypatch.setattr(publicar_instagram_lote.instagram, "publicar_foto", fake_publicar_foto)

    rc = publicar_instagram_lote.main(["--no-env", "--json"])

    dados = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert chamado is False
    assert dados["modo"] == "conferencia"
    assert dados["pronto_para_publicar"] is False
    assert len(dados["fila"]) == 12
    assert dados["fila"][0]["slug"] == "casa-a-venda-caminho-do-parque-caminho-do-parque-bela-vista"
    assert dados["fila"][0]["image_url"].endswith("/original.jpg")


def test_lote_confirmar_exige_flag_publicacao(monkeypatch, capsys):
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_GRAPH_VERSION", "v99.0")
    monkeypatch.setenv("MCP_IG_PUBLISH_ENABLED", "0")

    rc = publicar_instagram_lote.main(["--no-env", "--confirmar", "--json", "--limite", "1"])

    dados = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert dados["modo"] == "bloqueado"
    assert dados["pronto_para_publicar"] is False
    assert dados["status"]["mcp_publicacao_habilitada"] is False


def test_lote_confirmado_chama_cliente_instagram(monkeypatch, capsys):
    chamadas: list[tuple[str, str]] = []
    monkeypatch.setenv("META_PAGE_TOKEN", "token-fake")
    monkeypatch.setenv("IG_BUSINESS_ACCOUNT_ID", "17841400000000000")
    monkeypatch.setenv("META_GRAPH_VERSION", "v99.0")
    monkeypatch.setenv("MCP_IG_PUBLISH_ENABLED", "1")

    def fake_publicar_foto(image_url: str, legenda: str) -> RespostaIG:
        chamadas.append((image_url, legenda))
        return RespostaIG(True, dados={"id": "post-1"})

    monkeypatch.setattr(publicar_instagram_lote.instagram, "publicar_foto", fake_publicar_foto)

    rc = publicar_instagram_lote.main(
        ["--no-env", "--confirmar", "--json", "--limite", "1", "--intervalo", "0"]
    )

    dados = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert dados["modo"] == "publicacao"
    assert len(chamadas) == 1
    assert chamadas[0][0].endswith("/original.jpg")
    assert "Valor: R$ 2.600.000" in chamadas[0][1]
