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
    "este mes", "esse mes", "ainda esse ano", "esse ano", "ate o fim", "até o fim",
    "ate o ano", "até o ano", "urgente", "com pressa", "logo", "sem pressa",
    "proximo ano", "próximo ano", "proximos meses", "próximos meses",
}
# Vendedor/proprietario: lead valioso (imovel pra captar) — nao pode cair como frio.
# Alinhado com router.PALAVRAS_CAPTACAO pra a rota e o funil concordarem.
SELLER_TOKENS = {
    "quero vender", "vou vender", "gostaria de vender", "pra vender", "para vender",
    "vender minha", "vender meu", "vender a", "vender o", "vendo meu", "vendo minha",
    "colocar a venda", "colocar à venda", "por a venda", "pôr à venda",
    "anunciar meu", "anunciar minha", "anunciar na sua carteira", "anunciar na carteira",
    "cadastrar meu", "cadastrar minha", "quanto vale meu", "quanto vale minha",
    "avaliar meu", "avaliar minha", "avaliar meu imovel", "avaliar meu imóvel", "avaliar minha casa",
    "tenho um imovel", "tenho um imóvel", "tenho uma casa", "tenho um terreno",
    "tenho um lote", "tenho um apartamento", "tenho um ape", "tenho um apê",
    "sou proprietario", "sou proprietária", "imovel pra vender", "imóvel pra vender",
}
PERMUTA_TOKENS = {"permuta", "permutar", "trocar por", "troca por", "como parte do pagamento", "dou meu"}
# Sinal de intencao alta / proximo passo (urgencia de fechar).
INTENT_TOKENS = {
    "agendar", "marcar visita", "quero visitar", "quero ver o imovel", "quero ver o imóvel",
    "fazer proposta", "quero fechar", "fechar negocio", "fechar negócio", "comprar agora",
    "fechar agora", "pode marcar", "quero agendar", "posso visitar",
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
    is_rental = _has_any_token(text, {"alug", "locar", "locação", "locacao", "arrend"})

    # Sinais de vendedor/permuta/intencao SO no que o CLIENTE disse (nao no texto da Ana),
    # pra a resposta da assistente nao disparar falso positivo.
    user_text = " ".join(
        [h.get("content", "") for h in (history or []) if (h.get("role") or "user") == "user"]
        + [message]
    ).lower()
    user_turns = sum(1 for h in (history or []) if (h.get("role") or "") == "user") + 1
    is_seller = _has_any_token(user_text, SELLER_TOKENS)
    is_permuta = _has_any_token(user_text, PERMUTA_TOKENS)
    has_intent = _has_any_token(user_text, INTENT_TOKENS)

    score = 0
    if has_neighborhood:
        score += 20
    if has_budget:
        score += 25
    if has_timeline:
        score += 20
    if has_phone:
        score += 25  # telefone sozinho nao deve inflar (curioso/troll vira quente)
    # Locacao tem funil proprio: intencao clara de aluguel conta como interesse,
    # pra o lead de locacao nao cair em frio/0 so por nao citar orcamento de compra.
    if is_rental and score < 40:
        score += 20
    # Vendedor = imovel pra captar (lead valioso): garante pelo menos "quente".
    if is_seller:
        score += 40
    # Permuta = cliente engajado (vende E compra).
    if is_permuta:
        score += 35
    # Intencao alta (quer visita/proposta/fechar) sobe a temperatura.
    if has_intent:
        score += 20
    # Engajamento: quem volta a conversar demonstra mais interesse.
    if user_turns >= 3:
        score += 10
    score = min(100, score)

    # pronto_proposta exige orcamento real (evita stage alto so por telefone+bairro).
    # Pra vendedor, o "orcamento" e o preco que ele pede (has_budget pega "180 mil").
    if score >= 80 and (has_budget or is_seller):
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

    if is_seller:
        if not has_neighborhood:
            next_question = "Em qual bairro fica o imovel que voce quer vender?"
        elif not has_budget:
            next_question = "Quanto voce espera pelo imovel? Posso te dar uma referencia de mercado."
        elif not has_phone:
            next_question = "Pra Priscila avaliar e te passar um valor, qual o melhor numero pra falar com voce?"
        else:
            next_question = "Perfeito. Posso pedir pra Priscila te ligar e agendar a avaliacao?"
    elif not has_neighborhood:
        next_question = "Qual bairro de Vitoria da Conquista voce prefere?"
    elif not has_budget:
        next_question = (
            "Qual valor de aluguel cabe no seu orcamento?" if is_rental
            else "Qual faixa de investimento fica confortavel para voce?"
        )
    elif not has_timeline:
        next_question = (
            "Pra quando voce precisa mudar?" if is_rental
            else "Voce pretende comprar em qual prazo?"
        )
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
            "vendedor": is_seller,
            "permuta": is_permuta,
            "intencao": has_intent,
            "aluguel": is_rental,
        },
    )


def track_stage(stage: str) -> None:
    FUNIL_COUNTER[stage] += 1
