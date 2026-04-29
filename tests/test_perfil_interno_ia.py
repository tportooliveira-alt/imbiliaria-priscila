"""Perfil interno da IA deve ficar no CRM, nao no frontend publico."""
from __future__ import annotations


def test_chat_cria_perfil_interno_sem_descricao_exposta() -> None:
    from app.conversas import _perfil_interno

    perfil = _perfil_interno(
        texto_contexto="Quero comprar casa em Candeias ainda esse mes",
        lead_stage="pronto_visita",
        lead_score=70,
        rota="negociacao",
    )

    assert perfil["visivel_cliente"] is False
    assert perfil["intencao"] == "comprar"
    assert perfil["jornada"] == "interesse_ativo"
    assert perfil["urgencia"] == "alta"
    assert perfil["proximo_passo"] == "encaminhar para atendimento humano"


def test_chat_publico_nao_usa_termos_operacionais(shared_dir) -> None:
    src = (shared_dir / "AIChat.jsx").read_text(encoding="utf-8").lower()
    termos_bloqueados = [
        "cliente frio",
        "lead frio",
        "lead quente",
        "score",
        "rota / modelo",
        "grounding",
    ]
    for termo in termos_bloqueados:
        assert termo not in src
