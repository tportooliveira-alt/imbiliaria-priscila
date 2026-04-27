"""Popula o banco com dados de exemplo para desenvolvimento.

Uso:
    python scripts/seed.py            # adiciona se vazio
    python scripts/seed.py --reset    # apaga tudo e recria
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import auth, imoveis  # noqa: E402
from app.db import db_session, init_db  # noqa: E402


IMOVEIS_EXEMPLO = [
    {
        "titulo": "Casa moderna 3 suítes — Candeias",
        "bairro": "Candeias",
        "tipo": "casa",
        "quartos": 3,
        "suites": 3,
        "vagas": 2,
        "area_util": 220,
        "preco": 890_000,
        "descricao": "Casa contemporânea em condomínio fechado em Candeias, "
                     "com pé-direito alto, área gourmet integrada e piscina aquecida.",
        "caracteristicas": ["piscina", "área gourmet", "condomínio fechado", "pé-direito alto"],
        "destaque": True,
        "ativo": True,
    },
    {
        "titulo": "Apartamento alto padrão — Boa Vista",
        "bairro": "Boa Vista",
        "tipo": "apartamento",
        "quartos": 3,
        "suites": 1,
        "vagas": 2,
        "area_util": 135,
        "preco": 620_000,
        "descricao": "Apartamento de 3 quartos com varanda gourmet, "
                     "vista para a Serra do Periperi e lazer completo.",
        "caracteristicas": ["varanda gourmet", "vista panorâmica", "lazer completo"],
        "destaque": True,
        "ativo": True,
    },
    {
        "titulo": "Cobertura duplex — Recreio",
        "bairro": "Recreio",
        "tipo": "cobertura",
        "quartos": 4,
        "suites": 2,
        "vagas": 3,
        "area_util": 280,
        "preco": 1_250_000,
        "descricao": "Cobertura duplex com terraço privativo, jacuzzi e churrasqueira.",
        "caracteristicas": ["terraço privativo", "jacuzzi", "duplex", "churrasqueira"],
        "destaque": False,
        "ativo": True,
    },
]


LEADS_EXEMPLO = [
    ("Maria Souza", "(77) 99100-0001", "maria@example.com", "simulador", "qualificado", "quente", 78),
    ("João Pereira", "(77) 99100-0002", "joao@example.com", "chat", "novo", "morno", 45),
    ("Ana Lima", "(77) 99100-0003", None, "site", "novo", "frio", 18),
    ("Carlos Mota", "(77) 99100-0004", "carlos@example.com", "avaliacao", "contatado", "morno", 52),
]


def reset() -> None:
    with db_session() as conn:
        for tabela in [
            "lead_tags", "lead_interacoes", "leads",
            "imagens", "imoveis",
            "simulacoes", "avaliacoes",
            "login_attempts",
        ]:
            try:
                conn.execute(f"DELETE FROM {tabela}")
            except Exception:
                pass


def seed_admin() -> None:
    email = "priscila@vasconcelos.imb"
    if not auth.buscar_usuario_por_email(email):
        auth.criar_usuario(email, "trocar-em-producao", role="admin")
        print(f"  + admin {email} (senha: trocar-em-producao)")


def seed_imoveis() -> int:
    n = 0
    with db_session() as conn:
        existentes = {
            r["titulo"] for r in conn.execute("SELECT titulo FROM imoveis").fetchall()
        }
    for item in IMOVEIS_EXEMPLO:
        if item["titulo"] in existentes:
            continue
        try:
            imoveis.criar_imovel(item)
            n += 1
        except Exception as e:
            print(f"  ! pulou {item['titulo']}: {e}")
    return n


def seed_leads() -> int:
    n = 0
    with db_session() as conn:
        for nome, tel, email, origem, estagio, temp, score in LEADS_EXEMPLO:
            existe = conn.execute(
                "SELECT 1 FROM leads WHERE telefone = ? OR (email IS NOT NULL AND email = ?)",
                (tel, email or ""),
            ).fetchone()
            if existe:
                continue
            conn.execute(
                "INSERT INTO leads (nome, telefone, email, origem, estagio, temperatura, score) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nome, tel, email, origem, estagio, temp, score),
            )
            n += 1
    return n


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="apaga dados antes")
    args = parser.parse_args()

    init_db()
    if args.reset:
        print("[seed] resetando...")
        reset()

    print("[seed] usuário admin:")
    seed_admin()
    print(f"[seed] imóveis: +{seed_imoveis()}")
    print(f"[seed] leads:   +{seed_leads()}")
    print("[seed] ok")


if __name__ == "__main__":
    main()
