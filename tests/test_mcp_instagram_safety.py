"""Garantias estáticas da exposição Instagram no MCP.

O ambiente local de teste pode não ter `fastmcp` instalado. Mesmo assim,
conseguimos validar a regra crítica: ferramentas de publicação só existem
dentro do bloco habilitado por `MCP_IG_PUBLISH_ENABLED=1`.
"""
from __future__ import annotations

import ast
from pathlib import Path


def _mcp_tree(proj_dir: Path) -> ast.Module:
    return ast.parse((proj_dir / "app" / "mcp_server.py").read_text(encoding="utf-8"))


def test_mcp_instagram_publicacao_fica_atras_da_flag(proj_dir: Path) -> None:
    tree = _mcp_tree(proj_dir)
    funcoes_publicacao = {"ig_publicar_foto", "ig_publicar_carrossel", "ig_publicar_reel"}

    top_level = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in funcoes_publicacao
    }
    assert top_level == set()

    blocos_ig_publish = [
        node for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Name)
        and node.test.id == "IG_PUBLISH"
    ]
    assert len(blocos_ig_publish) == 1

    protegidas = {
        node.name
        for node in blocos_ig_publish[0].body
        if isinstance(node, ast.FunctionDef)
    }
    assert funcoes_publicacao <= protegidas


def test_mcp_instagram_leitura_fica_disponivel_no_topo(proj_dir: Path) -> None:
    tree = _mcp_tree(proj_dir)
    funcoes_top_level = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }

    assert {"ig_status", "ig_perfil", "ig_listar_midias", "ig_insights"} <= funcoes_top_level
    assert "status_ecossistema" in funcoes_top_level


def test_mcp_instagram_publicacao_default_off(proj_dir: Path) -> None:
    fonte = (proj_dir / "app" / "mcp_server.py").read_text(encoding="utf-8")

    assert 'os.getenv("MCP_IG_PUBLISH_ENABLED", "0") == "1"' in fonte
