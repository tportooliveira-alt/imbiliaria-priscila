"""Fator de rua: classifica a rua dentro do bairro (premium / popular) e diz se a
via e um corredor COMERCIAL, a partir do mapa calibrado em calibracao/ruas_vdc.json.

Quando a rua nao e reconhecida, retorna None -> a calculadora usa so a base do
bairro (neutro). As avenidas/condominios mais caros ja estao mapeados, entao a
maioria dos imoveis de valor cai num tier conhecido."""
from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path

_RUAS_PATH = Path(__file__).resolve().parent.parent / "calibracao" / "ruas_vdc.json"

_PREFIXOS = (
    "avenida ", "av. ", "av ", "rua ", "r. ", "travessa ", "trav ", "praca ",
    "condominio ", "cond ", "loteamento ", "lot ", "residencial ", "res ",
    "edificio ", "ed ", "1a ", "2a ", "3a ",
)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().strip()
    mudou = True
    while mudou:  # remove prefixos encadeados (ex.: "cond residencial X")
        mudou = False
        for p in _PREFIXOS:
            if s.startswith(p):
                s = s[len(p):]
                mudou = True
    return " ".join(s.split())


@lru_cache(maxsize=1)
def _mapa() -> dict:
    try:
        with open(_RUAS_PATH, encoding="utf-8") as f:
            return json.load(f).get("bairros", {})
    except (OSError, ValueError):
        return {}


def _casa_em(alvo: str, lista) -> bool:
    """Casa a rua com a lista. Nome curto (ex.: 'Rua H' -> 'h') so casa por igualdade
    EXATA — substring de 1-2 letras dava falso-positivo (ex.: 'h' dentro de 'pinheiros')."""
    if not alvo:
        return False
    for via in lista or []:
        v = _norm(via)
        if not v:
            continue
        if v == alvo:
            return True
        # substring so com nomes longos dos dois lados (evita match espurio de 1-2 letras)
        if len(alvo) >= 4 and len(v) >= 4 and (v in alvo or alvo in v):
            return True
    return False


def tier_da_rua(bairro_key: str, rua: str | None) -> str | None:
    """'premium' | 'popular' | None — ranking da rua p/ imovel RESIDENCIAL.
    (Rua que e so corredor comercial nao vira premium residencial.)"""
    if not rua:
        return None
    b = _mapa().get(bairro_key)
    if not b:
        return None
    alvo = _norm(rua)
    if _casa_em(alvo, b.get("premium")):
        return "premium"
    if _casa_em(alvo, b.get("popular")):
        return "popular"
    return None


def rua_eh_comercial(bairro_key: str, rua: str | None) -> bool:
    """True se a via e um corredor comercial conhecido do bairro."""
    if not rua:
        return False
    b = _mapa().get(bairro_key)
    if not b:
        return False
    return _casa_em(_norm(rua), b.get("comercial"))
