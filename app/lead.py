"""Qualificacao comercial de leads para atendimento imobiliario.

Regras:
- captura progressiva (sem insistencia);
- score simples e explicavel (0..100);
- funil em memoria para dashboard rapido.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass


PHONE_RE = re.compile(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9\d{4}|\d{4})[-\s]?\d{4}")

ORCAMENTO_TOKENS = {
    "r$", "mil", "milhao", "milhoes", "orcamento", "entrada", "financiamento", "parcela"
}
Bairro_TOKENS = {
    "candeias", "boa vista", "recreio", "patagonia", "patagônia", "centro", "ibirapuera",
    "alto maron", "guarani", "felicia", "felícia", "vitoria da conquista", "vitória da conquista", "vdc"
}
PRAZO_TOKENS = {
    "este mes", "esse mes", "ainda esse ano", "ate", "até", "urgente", "logo", "sem pressa", "proximo ano"
}


@dataclass(frozen=True)
class LeadSnapshot:
    score: int
    stage: str
    has_phone: bool
    asked_phone: bool
    next_question: str
    fields: dict[str, bool]


FUNIL_COUNTER = Counter()


def _has_any_token(text: str, tokens: set[str]) -> bool:
    return any(t in text for t in tokens)


def detect_phone(text: str) -> str | None:
    m = PHONE_RE.search(text)
    if not m:
        return None
    digits = re.sub(r"\D", "", m.group(0))
    if len(digits) < 8:
        return None
    return digits


def qualify_lead(message: str, history: list[dict] | None = None) -> LeadSnapshot:
    joined = " ".join([h.get("content", "") for h in (history or [])] + [message])
    text = joined.lower()

    has_phone = detect_phone(text) is not None
    has_budget = _has_any_token(text, ORCAMENTO_TOKENS)
    has_neighborhood = _has_any_token(text, Bairro_TOKENS)
    has_timeline = _has_any_token(text, PRAZO_TOKENS)

    score = 0
    if has_neighborhood:
        score += 20
    if has_budget:
        score += 25
    if has_timeline:
        score += 20
    if has_phone:
        score += 35
    score = min(100, score)

    if score >= 80:
        stage = "pronto_proposta"
    elif score >= 60:
        stage = "pronto_visita"
    elif score >= 40:
        stage = "quente"
    elif score >= 20:
        stage = "morno"
    else:
        stage = "frio"

    asked_phone = ("telefone" in text) or ("whatsapp" in text) or ("numero" in text)

    if not has_neighborhood:
        next_question = "Qual bairro de Vitoria da Conquista voce prefere?"
    elif not has_budget:
        next_question = "Qual faixa de investimento fica confortavel para voce?"
    elif not has_timeline:
        next_question = "Voce pretende comprar em qual prazo?"
    elif not has_phone:
        next_question = (
            "Se quiser, te envio as melhores opcoes no WhatsApp com mapa e pontos fortes. "
            "Qual numero voce prefere usar?"
        )
    else:
        next_question = "Perfeito. Posso te propor 2 horarios para visita?"

    return LeadSnapshot(
        score=score,
        stage=stage,
        has_phone=has_phone,
        asked_phone=asked_phone,
        next_question=next_question,
        fields={
            "bairro": has_neighborhood,
            "orcamento": has_budget,
            "prazo": has_timeline,
            "telefone": has_phone,
        },
    )


def track_stage(stage: str) -> None:
    FUNIL_COUNTER[stage] += 1


def funnel_summary() -> dict:
    stages = ["frio", "morno", "quente", "pronto_visita", "pronto_proposta"]
    total = sum(FUNIL_COUNTER.values())
    return {
        "total": total,
        "stages": {s: int(FUNIL_COUNTER.get(s, 0)) for s in stages},
    }
