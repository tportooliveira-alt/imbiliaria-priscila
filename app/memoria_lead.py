"""Ficha viva do lead — a memória da Ana que ATRAVESSA conversas.

Monta, a partir do que o sistema JÁ persiste (sem custo de IA), um resumo do que a Ana
já sabe sobre o cliente: situação, anotações, marcadores e o que ele já disse. Assim ela
não recomeça do zero quando a pessoa volta dias depois.

É lido em tempo real no atendimento (dispatcher.responder) — sempre fresco, nada de job
de fundo nem chamada de modelo só pra isso.
"""
from __future__ import annotations

from app import leads as leads_repo

# tags que ajudam a Ana a lembrar do interesse (bairro, imóvel, faixa, etc.)
_TAGS_PREFIX_UTEIS = ("bairro:", "imovel:", "interesse:", "faixa:", "tipo:")
_TAGS_FLAG = {"agendou_visita", "quer_alugar", "quer_comprar", "investidor"}


def ficha_viva(lead_id: int | None) -> str:
    """Devolve um bloco de texto com o que a Ana já sabe do lead (ou '' se não houver nada útil)."""
    if not lead_id:
        return ""
    try:
        d = leads_repo.detalhar(lead_id)
    except Exception:
        return ""
    if not d:
        return ""

    linhas: list[str] = []

    # Situação (temperatura / estágio)
    cab = []
    if d.get("temperatura"):
        cab.append(f"temperatura {d['temperatura']}")
    if d.get("estagio") and d["estagio"] not in ("novo", "teste"):
        cab.append(f"estágio {d['estagio']}")
    if cab:
        linhas.append("Situação: " + ", ".join(cab) + ".")

    # Anotações livres (handoff/anamnese da Priscila ou notas)
    obs = (d.get("observacoes") or "").strip()
    if obs:
        linhas.append("Anotações: " + obs[:400])

    # Marcadores úteis
    tags = d.get("tags") or []
    uteis = [t for t in tags if t in _TAGS_FLAG or any(t.startswith(p) for p in _TAGS_PREFIX_UTEIS)]
    if uteis:
        linhas.append("Marcadores: " + ", ".join(uteis[:8]))

    # O que o cliente já te disse (só mensagens recebidas, ignora mídia/sistema)
    recebidas = [
        (i.get("descricao") or "").strip()
        for i in (d.get("interacoes") or [])
        if i.get("tipo") == "whatsapp_recebido"
        and (i.get("descricao") or "").strip()
        and not (i.get("descricao") or "").startswith("[")
    ]
    if recebidas:
        ult = " | ".join(recebidas[:5])  # interacoes vêm do mais recente pro mais antigo
        linhas.append("Já te falou (recente→antigo): " + ult[:500])

    if not linhas:
        return ""

    nome = (d.get("nome") or "").strip()
    quem = f" ({nome})" if nome else ""
    return (
        f"O QUE VOCÊ JÁ SABE DESTE CLIENTE{quem} — use com JOGO DE CINTURA: não jogue na "
        "cara como se fosse do agora, confirme com leveza antes de assumir:\n- "
        + "\n- ".join(linhas)
    )
