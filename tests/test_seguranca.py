"""Etapa 0 — Higiene & segurança.

Testa que:
- as chaves de API estão fora de pastas sincronizadas em nuvem (OneDrive);
- `.gitignore` protege os padrões críticos de segredo;
- arquivos sensíveis não foram commitados.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Notas / chaves
# ─────────────────────────────────────────────────────────────────────────────
def test_notas_em_local_seguro(segredos_dir: Path) -> None:
    """notas.txt deve existir em C:\\segredos (fora do OneDrive)."""
    notas = segredos_dir / "notas.txt"
    assert notas.exists(), f"notas.txt não encontrado em {segredos_dir}"
    assert notas.stat().st_size > 0, "notas.txt está vazio — copia falhou?"


def test_segredos_fora_do_onedrive(segredos_dir: Path) -> None:
    """Confirma que C:\\segredos NÃO está dentro do OneDrive."""
    resolved = str(segredos_dir.resolve()).lower()
    assert "onedrive" not in resolved, (
        f"Pasta de segredos dentro do OneDrive! Caminho: {resolved}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# .gitignore
# ─────────────────────────────────────────────────────────────────────────────
PADROES_OBRIGATORIOS = [
    ".env",
    "notas.txt",
    "*.key",
    "*.pem",
    "**/secrets/**",
    "**/chaves/**",
]


def test_gitignore_existe(proj_dir: Path) -> None:
    assert (proj_dir / ".gitignore").exists()


def test_gitignore_cobre_padroes_criticos(proj_dir: Path) -> None:
    conteudo = (proj_dir / ".gitignore").read_text(encoding="utf-8")
    faltando = [p for p in PADROES_OBRIGATORIOS if p not in conteudo]
    assert not faltando, f".gitignore não cobre: {faltando}"


def test_gitignore_permite_env_exemplo(proj_dir: Path) -> None:
    """Bloquear .env mas liberar .env.exemplo (template público)."""
    conteudo = (proj_dir / ".gitignore").read_text(encoding="utf-8")
    assert "!.env.exemplo" in conteudo


# ─────────────────────────────────────────────────────────────────────────────
# Repo git — nada sensível foi commitado
# ─────────────────────────────────────────────────────────────────────────────
def _git_ls(proj_dir: Path) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"],
        cwd=proj_dir,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.splitlines()


def test_repo_nao_contem_arquivos_sensiveis(proj_dir: Path) -> None:
    arquivos = _git_ls(proj_dir)
    proibidos = [f for f in arquivos if f in {".env", "notas.txt", "apis.txt"}]
    assert not proibidos, f"Arquivos sensíveis no git: {proibidos}"
