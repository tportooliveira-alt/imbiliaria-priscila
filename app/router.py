"""Roteador de intenções — classifica a mensagem do usuário em uma de 6 rotas.

A classificação é puramente local (regras + heurísticas) para ser:
1. Rápida (sem chamada LLM, ~µs)
2. Determinística (testável)
3. Gratuita (não consome cota)

Se a regra não tem certeza, o fallback é "triagem" (Gemini Flash).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Rota(str, Enum):
    TRIAGEM = "triagem"           # cumprimento, dúvida geral curta
    INFO_VDC = "info_vdc"         # pergunta sobre Vitória da Conquista / bairro
    NEGOCIACAO = "negociacao"     # lead quente, intenção de compra
    VISAO = "visao"               # imagem anexada
    DESCRICAO = "descricao"       # gerar descrição editorial de imóvel
    FOLLOWUP = "followup"         # cliente frio, lembrete, retomada


@dataclass(frozen=True)
class Classificacao:
    rota: Rota
    confianca: float  # 0..1
    motivo: str


# ─────────────────────────────────────────────────────────────────────────────
# Léxico
# ─────────────────────────────────────────────────────────────────────────────
PALAVRAS_NEGOCIACAO = {
    "comprar", "compro", "fechar", "proposta", "negociar", "financiar",
    "financiamento", "entrada", "parcelar", "parcela", "interessado",
    "interessada", "quero esse", "quero este", "tô pronto", "estou pronto",
    "fechamos", "vamos fechar", "preço final", "desconto", "abaixar",
}

PALAVRAS_DESCRICAO = {
    "descrição", "descricao", "anúncio", "anuncio", "texto do imóvel",
    "texto do imovel", "redação", "redacao", "editorial", "tom de revista",
    "como anunciar",
}

PALAVRAS_FOLLOWUP = {
    "depois eu vejo", "depois te falo", "vou pensar", "qualquer coisa",
    "se eu lembrar", "talvez", "sem pressa",
}

# Bairros e referências geográficas de Vitória da Conquista
BAIRROS_VDC = {
    "candeias", "boa vista", "recreio", "patagônia", "patagonia",
    "centro", "ibirapuera", "alto maron", "guarani", "primavera",
    "felícia", "felicia", "urbis", "vitória da conquista", "vitoria da conquista",
    "vdc", "conquista",
}

PALAVRAS_INFO_VDC = {
    "bairro", "bairros", "regiao", "região", "zona", "localizacao",
    "localização", "mercado", "valorizado", "valorizada", "valorizacao",
    "valorização", "seguranca", "segurança", "escola", "escolas",
    "mobilidade", "infraestrutura", "condominio", "condomínio",
    "apartamento", "apartamentos", "casa", "casas",
}

PADRAO_PRECO = re.compile(r"\b(r\$|reais?|mil|milh[ãa]o|milh[õo]es)\b", re.IGNORECASE)
PADRAO_IMAGEM = re.compile(r"\b(foto|imagem|anexo|anexei|olha essa|esta foto)\b", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────────
# Classificador
# ─────────────────────────────────────────────────────────────────────────────
def classificar(mensagem: str, *, tem_imagem: bool = False) -> Classificacao:
    """Classifica uma mensagem do usuário em uma das 6 rotas.

    Args:
        mensagem: texto digitado pelo usuário.
        tem_imagem: True se o usuário anexou uma imagem.

    Returns:
        Classificacao com rota, confiança e motivo.
    """
    if not isinstance(mensagem, str):
        raise TypeError("mensagem deve ser str")

    texto = mensagem.lower().strip()

    if tem_imagem:
        return Classificacao(Rota.VISAO, 1.0, "imagem anexada")

    if not texto:
        return Classificacao(Rota.TRIAGEM, 0.5, "mensagem vazia")

    # Descrição editorial (uso interno da Priscila)
    if any(p in texto for p in PALAVRAS_DESCRICAO):
        return Classificacao(Rota.DESCRICAO, 0.85, "pedido de redação")

    # Follow-up (lead esfriando)
    if any(p in texto for p in PALAVRAS_FOLLOWUP):
        return Classificacao(Rota.FOLLOWUP, 0.75, "sinal de adiamento")

    # Pergunta sobre VDC (bairro, escola, segurança, mercado)
    if any(b in texto for b in BAIRROS_VDC):
        return Classificacao(Rota.INFO_VDC, 0.8, "menção a bairro/cidade")

    if any(p in texto for p in PALAVRAS_INFO_VDC) and any(c in texto for c in {"vitoria da conquista", "vitória da conquista", "vdc", "conquista"}):
        return Classificacao(Rota.INFO_VDC, 0.78, "pergunta de mercado/localidade em VDC")

    # Negociação tem prioridade alta, mas depois das perguntas de contexto local.
    if any(p in texto for p in PALAVRAS_NEGOCIACAO):
        return Classificacao(Rota.NEGOCIACAO, 0.9, "léxico de negociação")

    # Pergunta envolvendo preço sem intenção clara → triagem
    if PADRAO_PRECO.search(texto):
        return Classificacao(Rota.TRIAGEM, 0.6, "menção a valor")

    # Default
    return Classificacao(Rota.TRIAGEM, 0.5, "fallback")
