"""Publicador seguro de lote para Instagram/Meta.

Por padrao roda em modo conferencia: monta a fila, valida travas e nao publica.
Para publicar de verdade exige:

    1. META_PAGE_TOKEN no .env
    2. IG_BUSINESS_ACCOUNT_ID no .env
    3. META_GRAPH_VERSION no .env
    4. MCP_IG_PUBLISH_ENABLED=1 no .env
    5. argumento --confirmar

Nunca imprime tokens ou segredos.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - ambiente minimo
    load_dotenv = None

from app import instagram  # noqa: E402

MANIFEST_PADRAO = ROOT / "_marketing_ia" / "criativos" / "instagram-upload-imoveis" / "manifest.json"
LEGENDAS_PADRAO = ROOT / "_marketing_ia" / "criativos" / "2026-07-01-instagram-premium-vitrine-priscila.md"

ORDEM_PREMIUM = [
    "casa-a-venda-caminho-do-parque-caminho-do-parque-bela-vista",
    "casa-terrea-a-venda-parque-dos-ipes-i-boa-vista",
    "casa-duplex-a-venda-boa-vista",
    "casa-terrea-a-venda-alphaville-i-primavera",
    "apartamento-a-venda-bairro-candeias-candeias",
    "apartamento-a-venda-candeias",
    "casa-terrea-a-venda-horto-premier-primavera",
    "apartamento-a-venda-bairro-candeias-candeias-2",
    "terreno-a-venda-av-brasil-candeias",
    "terreno-de-esquina-a-venda-haras-camping-club-rodovia-conquista-ba-415-barra-do-choca",
    "terreno-a-venda-haras-camping-club-rodovia-conquista-ba-415-barra-do-choca",
    "ponto-comercial-multiplace-para-locacao-felicia",
]

TITULO_LEGENDA_POR_SLUG = {
    "casa-a-venda-caminho-do-parque-caminho-do-parque-bela-vista": "Casa Caminho do Parque",
    "casa-terrea-a-venda-parque-dos-ipes-i-boa-vista": "Casa Parque dos Ipes I",
    "casa-duplex-a-venda-boa-vista": "Casa Duplex Boa Vista",
    "casa-terrea-a-venda-alphaville-i-primavera": "Casa Alphaville I",
    "apartamento-a-venda-bairro-candeias-candeias": "Apartamento Mansao Joaquim Gusmao Sales",
    "apartamento-a-venda-candeias": "Apartamento Mansao Leonardo da Vinci",
    "casa-terrea-a-venda-horto-premier-primavera": "Casa Horto Premier",
    "apartamento-a-venda-bairro-candeias-candeias-2": "Apartamento Maison du Soleil",
    "terreno-a-venda-av-brasil-candeias": "Terreno Av. Brasil",
    "terreno-de-esquina-a-venda-haras-camping-club-rodovia-conquista-ba-415-barra-do-choca": "Terreno de esquina Haras Camping Club",
    "terreno-a-venda-haras-camping-club-rodovia-conquista-ba-415-barra-do-choca": "Terreno Haras Camping Club",
    "ponto-comercial-multiplace-para-locacao-felicia": "Ponto Comercial Multiplace",
}


def _carregar_env(no_env: bool) -> None:
    if no_env or load_dotenv is None:
        return
    load_dotenv(ROOT / ".env")


def _normalizar_legenda(texto: str) -> str:
    linhas: list[str] = []
    for linha in texto.strip().splitlines():
        limpa = linha.strip()
        if limpa.startswith("`") and limpa.endswith("`"):
            limpa = limpa.strip("`")
        linhas.append(limpa)
    return "\n".join(linhas).strip()


def extrair_legendas(caminho: Path = LEGENDAS_PADRAO) -> dict[str, str]:
    texto = caminho.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^###\s+\d+\.\s+(?P<titulo>.+?)\s*$", texto, re.MULTILINE))
    legendas: dict[str, str] = {}

    for indice, match in enumerate(headings):
        titulo = match.group("titulo").strip()
        inicio = match.end()
        fim = headings[indice + 1].start() if indice + 1 < len(headings) else len(texto)
        bloco = texto[inicio:fim]
        if "**Legenda:**" not in bloco:
            continue
        legenda = bloco.split("**Legenda:**", 1)[1]
        legenda = legenda.split("**Comentario fixado:**", 1)[0]
        legendas[titulo] = _normalizar_legenda(legenda)

    return legendas


def _url_jpeg_publica(item: dict[str, Any]) -> str:
    url = str(item["url"])
    if url.endswith("/1200.webp"):
        return url.rsplit("/", 1)[0] + "/original.jpg"
    return url


def montar_fila(
    manifest_path: Path = MANIFEST_PADRAO,
    legendas_path: Path = LEGENDAS_PADRAO,
    somente_casas: bool = False,
    limite: int | None = None,
) -> list[dict[str, Any]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    por_slug = {item["slug"]: item for item in manifest}
    legendas = extrair_legendas(legendas_path)
    fila: list[dict[str, Any]] = []

    for slug in ORDEM_PREMIUM:
        if somente_casas and not slug.startswith("casa-"):
            continue
        item = por_slug[slug]
        titulo_legenda = TITULO_LEGENDA_POR_SLUG[slug]
        legenda = legendas[titulo_legenda]
        fila.append(
            {
                "ordem": len(fila) + 1,
                "slug": slug,
                "titulo": item["titulo"],
                "titulo_legenda": titulo_legenda,
                "image_url": _url_jpeg_publica(item),
                "legenda": legenda,
            }
        )
        if limite is not None and len(fila) >= limite:
            break

    return fila


def _preflight(fila: list[dict[str, Any]]) -> dict[str, Any]:
    status = instagram.status_config()
    midias: list[dict[str, Any]] = []
    for item in fila:
        url = item["image_url"]
        jpeg = url.lower().endswith((".jpg", ".jpeg"))
        publica = instagram.validar_url_midia_publica(url)
        midias.append(
            {
                "slug": item["slug"],
                "url": url,
                "jpeg": jpeg,
                "publica": publica,
                "ok": jpeg and publica,
            }
        )

    status["midias"] = midias
    status["fila_total"] = len(fila)
    status["preflight_ok"] = (
        bool(fila)
        and status["disponivel"]
        and status["graph_version_configurada"]
        and status["mcp_publicacao_habilitada"]
        and all(item["ok"] for item in midias)
    )
    return status


def _saida_json(
    modo: str,
    status: dict[str, Any],
    fila: list[dict[str, Any]],
    resultados: list[dict[str, Any]] | None = None,
) -> str:
    fila_segura = [
        {
            "ordem": item["ordem"],
            "slug": item["slug"],
            "titulo": item["titulo"],
            "image_url": item["image_url"],
            "legenda_chars": len(item["legenda"]),
            "legenda_preview": item["legenda"][:180],
        }
        for item in fila
    ]
    return json.dumps(
        {
            "modo": modo,
            "pronto_para_publicar": status["preflight_ok"],
            "status": status,
            "fila": fila_segura,
            "resultados": resultados or [],
        },
        ensure_ascii=False,
        indent=2,
    )


def _saida_texto(modo: str, status: dict[str, Any], fila: list[dict[str, Any]]) -> str:
    linhas = [
        "Instagram/Meta - publicador de lote",
        f"Modo: {modo}",
        f"Fila: {len(fila)} publicacoes",
        f"Credenciais: {'OK' if status['disponivel'] else 'PENDENTE'}",
        f"Graph version: {'OK' if status['graph_version_configurada'] else 'PENDENTE'} ({status['graph_version']})",
        f"Publicacao liberada: {'SIM' if status['mcp_publicacao_habilitada'] else 'NAO'}",
        f"Resultado: {'PRONTO' if status['preflight_ok'] else 'CONFERENCIA/PENDENTE'}",
        "",
        "Fila:",
    ]
    for item in fila:
        linhas.append(f"{item['ordem']:02d}. {item['titulo_legenda']} - {item['image_url']}")
    if not status["preflight_ok"]:
        faltando = ", ".join(status["faltando"]) if status["faltando"] else "nenhum"
        linhas.extend(["", f"Faltando: {faltando}"])
        if not status["mcp_publicacao_habilitada"]:
            linhas.append("Trava: MCP_IG_PUBLISH_ENABLED precisa estar igual a 1.")
    return "\n".join(linhas)


def publicar_fila(fila: list[dict[str, Any]], intervalo_s: float) -> list[dict[str, Any]]:
    resultados: list[dict[str, Any]] = []
    for item in fila:
        resposta = instagram.publicar_foto(item["image_url"], item["legenda"])
        resultados.append(
            {
                "ordem": item["ordem"],
                "slug": item["slug"],
                "ok": resposta.ok,
                "dados": resposta.dados,
                "erro": resposta.erro,
            }
        )
        if not resposta.ok:
            break
        if intervalo_s > 0:
            time.sleep(intervalo_s)
    return resultados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publica lote seguro de imoveis no Instagram via Meta Graph API.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PADRAO)
    parser.add_argument("--legendas", type=Path, default=LEGENDAS_PADRAO)
    parser.add_argument("--casas", action="store_true", help="Usa apenas as casas da fila premium.")
    parser.add_argument("--limite", type=int, help="Limita a quantidade de posts da fila.")
    parser.add_argument("--intervalo", type=float, default=3.0, help="Intervalo em segundos entre publicacoes.")
    parser.add_argument("--confirmar", action="store_true", help="Publica de verdade se todas as travas estiverem OK.")
    parser.add_argument("--json", action="store_true", help="Imprime saida em JSON seguro.")
    parser.add_argument("--no-env", action="store_true", help="Nao carrega .env local.")
    args = parser.parse_args(argv)

    _carregar_env(args.no_env)
    fila = montar_fila(args.manifest, args.legendas, args.casas, args.limite)
    status = _preflight(fila)

    if not args.confirmar:
        saida = _saida_json("conferencia", status, fila) if args.json else _saida_texto("conferencia", status, fila)
        print(saida)
        return 0

    if not status["preflight_ok"]:
        saida = _saida_json("bloqueado", status, fila) if args.json else _saida_texto("bloqueado", status, fila)
        print(saida)
        return 2

    resultados = publicar_fila(fila, args.intervalo)
    houve_erro = any(not item["ok"] for item in resultados)
    if args.json:
        print(_saida_json("publicacao", status, fila, resultados))
    else:
        print(_saida_texto("publicacao", status, fila))
        for item in resultados:
            print(f"{item['ordem']:02d}. {item['slug']}: {'OK' if item['ok'] else item['erro']}")
    return 2 if houve_erro else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
