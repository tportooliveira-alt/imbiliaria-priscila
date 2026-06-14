"""Classificacao de comodos por imagem (Gemini Vision).

Usado pelo Studio (W3) para auto-organizar a galeria de um imovel:
identifica fachada/sala/cozinha/quarto/banheiro/area_externa em cada foto
e devolve um dos tipos validos do schema (`imagens.tipo`).

Sem GOOGLE_API_KEY, retorna `None` (caller fica com o tipo atual).
"""
from __future__ import annotations

import os
from pathlib import Path

# Tipos validos no schema (ver app/imoveis.py atualizar_imagem)
TIPOS_VALIDOS = {"capa", "sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"}

# Ordem editorial canonica (foto principal primeiro)
ORDEM_EDITORIAL = ["capa", "sala", "cozinha", "quarto", "banheiro", "area_externa", "planta"]

_PROMPT = (
    "Voce e um classificador de fotos imobiliarias. Olhe a imagem anexada e "
    "responda APENAS com UMA palavra entre as opcoes abaixo, sem pontuacao "
    "nem explicacao:\n"
    "- fachada (vista externa frontal do imovel, portao, garagem)\n"
    "- sala (sala de estar, jantar, ambiente social)\n"
    "- cozinha (cozinha, copa, area gourmet)\n"
    "- quarto (dormitorio, suite, com cama)\n"
    "- banheiro (banheiro, lavabo)\n"
    "- area_externa (quintal, piscina, jardim, varanda, area de servico)\n"
    "- planta (planta baixa, mapa, desenho tecnico)\n"
    "- outro (nao se encaixa em nenhum acima)\n"
    "\n"
    "Resposta esperada: uma unica palavra exatamente como acima."
)


def disponivel() -> bool:
    # Gemini (preferido) OU Claude (visao) — qualquer um habilita o auto-organizar.
    return bool(os.getenv("GOOGLE_API_KEY")) or bool(os.getenv("ANTHROPIC_API_KEY"))


def _normalizar(resposta: str) -> str | None:
    """Mapeia a resposta do modelo para um tipo valido do schema."""
    if not resposta:
        return None
    palavra = resposta.strip().lower().split()[0].rstrip(".,;:!?")
    if palavra == "fachada":
        return "capa"  # fachada vira capa no schema
    if palavra in TIPOS_VALIDOS:
        return palavra
    if palavra in {"externa", "varanda", "piscina", "quintal", "jardim"}:
        return "area_externa"
    if palavra in {"suite", "dormitorio"}:
        return "quarto"
    if palavra in {"lavabo"}:
        return "banheiro"
    return None


def classificar_comodo(arquivo_path: str | Path, *, modelo: str = "gemini-2.0-flash") -> str | None:
    """Classifica o comodo de uma imagem. Retorna None se IA indisponivel ou erro."""
    if not disponivel():
        return None
    caminho = Path(arquivo_path)
    if not caminho.exists():
        return None
    ext = caminho.suffix.lower().lstrip(".")
    mime = "image/jpeg" if ext in {"jpg", "jpeg"} else f"image/{ext or 'jpeg'}"

    # 1) Gemini Vision (preferido, se houver chave)
    if os.getenv("GOOGLE_API_KEY"):
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
            with caminho.open("rb") as f:
                dados = f.read()
            resp = client.models.generate_content(
                model=modelo,
                contents=[types.Part.from_bytes(data=dados, mime_type=mime), _PROMPT],
            )
            tipo = _normalizar(resp.text or "")
            if tipo:
                return tipo
        except Exception:
            pass  # cai para o Claude

    # 2) Claude Vision (Haiku — barato) quando o Gemini nao esta disponivel/falhou
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            from app.clients import ClienteClaude
            with caminho.open("rb") as f:
                dados = f.read()
            texto = ClienteClaude("claude-haiku-4-5").classificar_imagem(_PROMPT, dados, mime)
            return _normalizar(texto or "")
        except Exception:
            return None
    return None


def ordenar_editorial(imagens: list[dict]) -> list[int]:
    """Devolve lista de IDs ordenada editorialmente (capa → sala → ...).

    Dentro de cada bucket de tipo, mantem a ordem atual (estavel).
    """
    buckets: dict[str, list[dict]] = {t: [] for t in ORDEM_EDITORIAL}
    outros: list[dict] = []
    for img in imagens:
        tipo = img.get("tipo") or "sala"
        if tipo in buckets:
            buckets[tipo].append(img)
        else:
            outros.append(img)
    resultado: list[int] = []
    for tipo in ORDEM_EDITORIAL:
        for img in buckets[tipo]:
            resultado.append(int(img["id"]))
    for img in outros:
        resultado.append(int(img["id"]))
    return resultado
