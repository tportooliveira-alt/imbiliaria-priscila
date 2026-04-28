"""Busca em linguagem natural — converte texto livre em filtros estruturados.

Estrategia em camadas:
1. Heuristica regex/lexical (sempre roda, gratuita, deterministica).
2. Se houver GOOGLE_API_KEY, refina/expande com Gemini Flash em modo JSON-only.

Retorna sempre um dict de filtros + lista de imoveis ja aplicados.
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from typing import Any

from app import imoveis as imoveis_repo

# Bairros conhecidos (mesma normalizacao do m2_vdc)
_BAIRROS = [
    "candeias", "boa vista", "recreio", "patagonia", "centro",
    "ibirapuera", "alto maron", "guarani", "primavera", "felicia",
    "urbis", "brasil", "panorama", "bateias",
]

_TIPOS = {
    "apartamento": ["apartamento", "apto", "ap"],
    "casa": ["casa"],
    "cobertura": ["cobertura", "duplex"],
    "lote": ["lote", "terreno"],
    "comercial": ["comercial", "sala comercial", "loja"],
    "rural": ["rural", "fazenda", "chacara", "sitio"],
}

_TAGS_CONHECIDAS = [
    "piscina", "churrasqueira", "varanda", "suite", "suíte",
    "academia", "playground", "portaria", "elevador", "mobiliado",
    "vista", "jardim", "garagem", "quintal", "area gourmet",
    "área gourmet", "lavabo", "closet",
]


def _normalizar(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return txt.lower()


def _extrair_preco(texto_norm: str) -> tuple[float | None, float | None]:
    """Extrai preco_min e preco_max do texto normalizado."""
    preco_min = None
    preco_max = None

    # padroes "ate R$ 500 mil", "ate 500k", "ate 500.000"
    m = re.search(r"at[eé]\s*(?:r\$\s*)?([\d\.,]+)\s*(mil|milh[oõ]es?|milhao|k|m)?", texto_norm)
    if m:
        preco_max = _parse_valor(m.group(1), m.group(2))

    # "acima de R$ 300 mil", "a partir de 300k"
    m = re.search(r"(?:acima de|a partir de|mais de)\s*(?:r\$\s*)?([\d\.,]+)\s*(mil|milh[oõ]es?|milhao|k|m)?", texto_norm)
    if m:
        preco_min = _parse_valor(m.group(1), m.group(2))

    # "entre 300 e 500 mil"
    m = re.search(r"entre\s*([\d\.,]+)\s*e\s*([\d\.,]+)\s*(mil|milh[oõ]es?|milhao|k|m)?", texto_norm)
    if m:
        preco_min = _parse_valor(m.group(1), m.group(3))
        preco_max = _parse_valor(m.group(2), m.group(3))

    return preco_min, preco_max


def _parse_valor(numero: str, unidade: str | None) -> float | None:
    try:
        n = float(numero.replace(".", "").replace(",", "."))
    except ValueError:
        return None
    if not unidade:
        # se eh muito pequeno, assume milhares
        if n < 100:
            return n * 1_000_000  # "1.5" sem unidade -> 1.5mi
        if n < 10_000:
            return n * 1_000  # "500" -> 500 mil
        return n
    u = unidade.lower()
    if u in ("mil", "k"):
        return n * 1_000
    if u in ("milhao", "milhoes", "m"):
        return n * 1_000_000
    return n


def _extrair_quartos(texto_norm: str) -> int | None:
    m = re.search(r"(\d+)\s*(?:quartos?|dorms?|dormit[oó]rios?|q\b)", texto_norm)
    if m:
        return int(m.group(1))
    # "tres quartos", "dois quartos"
    mapa = {"um": 1, "dois": 2, "tres": 3, "quatro": 4, "cinco": 5}
    for k, v in mapa.items():
        if re.search(rf"\b{k}\s+(?:quartos?|dorms?)", texto_norm):
            return v
    return None


def _extrair_bairros(texto_norm: str) -> list[str]:
    achados = []
    for b in _BAIRROS:
        if re.search(rf"\b{re.escape(b)}\b", texto_norm):
            achados.append(b)
    return achados


def _extrair_tipo(texto_norm: str) -> str | None:
    for canonico, sinonimos in _TIPOS.items():
        for s in sinonimos:
            if re.search(rf"\b{re.escape(s)}\b", texto_norm):
                return canonico
    return None


def _extrair_tags(texto_norm: str) -> list[str]:
    achadas = []
    for t in _TAGS_CONHECIDAS:
        tn = _normalizar(t)
        if tn in texto_norm and tn not in achadas:
            achadas.append(tn)
    return achadas


def _extrair_area_min(texto_norm: str) -> float | None:
    m = re.search(r"(\d+)\s*m[²2]", texto_norm)
    if m:
        return float(m.group(1))
    return None


def extrair_filtros_heuristica(texto: str) -> dict[str, Any]:
    """Extrai filtros usando regex local. Sempre disponivel."""
    norm = _normalizar(texto)
    pmin, pmax = _extrair_preco(norm)
    return {
        "bairros": _extrair_bairros(norm),
        "tipo": _extrair_tipo(norm),
        "quartos_min": _extrair_quartos(norm),
        "preco_min": pmin,
        "preco_max": pmax,
        "area_min": _extrair_area_min(norm),
        "tags": _extrair_tags(norm),
    }


def _refinar_com_gemini(texto: str, filtros_base: dict) -> dict:
    """Tenta refinar filtros com Gemini Flash. Falha silenciosa retorna filtros_base."""
    if not os.getenv("GOOGLE_API_KEY"):
        return filtros_base
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        sistema = (
            "Voce e um extrator de filtros de busca imobiliaria em Vitoria da Conquista (BA). "
            "Receba a frase do usuario e devolva APENAS um JSON valido com as chaves: "
            "bairros (array de string), tipo (apartamento|casa|cobertura|lote|comercial|rural ou null), "
            "quartos_min (inteiro ou null), preco_min (numero em reais ou null), preco_max (numero em reais ou null), "
            "area_min (numero em m2 ou null), tags (array de string em pt-br sem acentos). "
            "Bairros conhecidos: " + ", ".join(_BAIRROS) + ". "
            "Nao invente. Se nao tiver certeza, devolva null/array vazio."
        )
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Frase: {texto}\nJSON:",
            config=types.GenerateContentConfig(
                system_instruction=sistema,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(resp.text or "{}")
        # mescla: prefere o que veio do Gemini se nao for None/vazio
        merged = dict(filtros_base)
        for k, v in data.items():
            if v in (None, [], "", 0):
                continue
            merged[k] = v
        return merged
    except Exception:
        return filtros_base


def extrair_filtros(texto: str, *, usar_ia: bool = True) -> dict[str, Any]:
    """Extrai filtros estruturados. Combina heuristica + Gemini (se disponivel)."""
    base = extrair_filtros_heuristica(texto)
    if usar_ia:
        return _refinar_com_gemini(texto, base)
    return base


def aplicar_filtros(filtros: dict[str, Any], *, limite: int = 30) -> list[dict]:
    """Aplica filtros nos imoveis ativos. Retorna lista pronta para o frontend."""
    todos = imoveis_repo.listar_imoveis(somente_ativos=True)

    bairros = [_normalizar(b) for b in (filtros.get("bairros") or [])]
    tipo = filtros.get("tipo")
    quartos_min = filtros.get("quartos_min")
    preco_min = filtros.get("preco_min")
    preco_max = filtros.get("preco_max")
    area_min = filtros.get("area_min")
    tags = [_normalizar(t) for t in (filtros.get("tags") or [])]

    def casa(im: dict) -> bool:
        if bairros and _normalizar(im.get("bairro") or "") not in bairros:
            return False
        if tipo and _normalizar(im.get("tipo") or "") != _normalizar(tipo):
            return False
        if quartos_min is not None and (im.get("quartos") or 0) < int(quartos_min):
            return False
        if preco_min is not None and (im.get("preco") or 0) < float(preco_min):
            return False
        if preco_max is not None and (im.get("preco") or 0) > float(preco_max):
            return False
        if area_min is not None and (im.get("area_util") or 0) < float(area_min):
            return False
        if tags:
            blob = _normalizar(
                f"{im.get('descricao') or ''} {' '.join(im.get('caracteristicas') or [])}"
            )
            if not all(t in blob for t in tags):
                return False
        return True

    selecionados = [im for im in todos if casa(im)]
    return selecionados[:limite]


def buscar(texto: str, *, usar_ia: bool = True, limite: int = 30) -> dict[str, Any]:
    """Pipeline completo: extrai filtros + aplica + retorna resumo."""
    texto = (texto or "").strip()
    if not texto:
        return {"filtros": {}, "imoveis": [], "total": 0, "explicacao": "Mensagem vazia."}

    filtros = extrair_filtros(texto, usar_ia=usar_ia)
    imoveis = aplicar_filtros(filtros, limite=limite)

    explicacao_partes = []
    if filtros.get("bairros"):
        explicacao_partes.append(f"bairro {', '.join(filtros['bairros'])}")
    if filtros.get("tipo"):
        explicacao_partes.append(filtros["tipo"])
    if filtros.get("quartos_min"):
        explicacao_partes.append(f"{filtros['quartos_min']}+ quartos")
    if filtros.get("preco_max"):
        explicacao_partes.append(f"ate R$ {filtros['preco_max']/1000:.0f} mil")
    if filtros.get("preco_min"):
        explicacao_partes.append(f"a partir de R$ {filtros['preco_min']/1000:.0f} mil")
    if filtros.get("tags"):
        explicacao_partes.append("com " + ", ".join(filtros["tags"]))

    explicacao = (
        "Buscando " + ", ".join(explicacao_partes)
        if explicacao_partes
        else "Sem filtros identificados — mostrando carteira completa."
    )

    return {
        "filtros": filtros,
        "imoveis": imoveis,
        "total": len(imoveis),
        "explicacao": explicacao,
    }
