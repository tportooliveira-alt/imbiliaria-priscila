#!/usr/bin/env python3
"""Gera palavras-chave (keywords) + negativas por imóvel ativo para Google/Meta Ads.

Baseado na pesquisa de leads (docs/PESQUISA-LEADS-2026.md): keywords de INTENÇÃO
(bairro + tipo + atributo) convertem melhor; negativas cortam clique-lixo e baixam o CPL.
Saída: docs/ADS-KEYWORDS-POR-IMOVEL.md  (uso: python3 scripts/gerar_ads.py)
"""
from __future__ import annotations
import pathlib
import sqlite3

ROOT = pathlib.Path(__file__).resolve().parent.parent
CIDADE = "Vitória da Conquista"
UF = "BA"

# negativas comuns (cortam curioso/errado em qualquer campanha)
NEG_COMUNS = ["grátis", "planta baixa", "como avaliar", "calculadora", "simulador",
              "decoração", "construir", "reformar", "emprego", "vaga de emprego", "concurso"]
NEG_VENDA = ["aluguel", "alugar", "alugo", "locação", "temporada", "minha casa minha vida",
             "leilão", "financiamento caixa"]
NEG_LOCACAO = ["venda", "comprar", "à venda", "financiamento", "comprar imóvel"]


def _fin(im: dict) -> str:
    """venda x locação (comercial barato/preço baixo = aluguel mensal)."""
    if (im["tipo"] or "").lower() == "comercial" and (im["preco"] or 0) < 50000:
        return "locacao"
    if (im["preco"] or 0) < 50000:
        return "locacao"
    return "venda"


def keywords_por_imovel(im: dict) -> dict:
    bairro = (im["bairro"] or "").strip().title()
    tipo = (im["tipo"] or "imóvel").strip().lower()
    q = im["quartos"] or 0
    fin = _fin(im)
    acao = "à venda" if fin == "venda" else "para alugar"
    comprar = "comprar" if fin == "venda" else "alugar"
    kw = [
        f"{tipo} {acao} {bairro}",
        f"{tipo} {acao} {bairro} {CIDADE}",
        f"{comprar} {tipo} {bairro}",
        f"{tipo} {bairro} {CIDADE}",
        f"{tipo} {acao} {CIDADE}",
    ]
    if q:
        kw += [f"{tipo} {q} quartos {bairro}", f"{tipo} {q} quartos {acao} {CIDADE}"]
    if (im["suites"] or 0) >= 3:
        kw.append(f"{tipo} alto padrão {bairro}")
    if tipo == "terreno":
        kw += [f"lote {acao} {bairro}", f"terreno {im['area_util']:.0f}m {bairro}"]
    if tipo == "comercial":
        kw += [f"ponto comercial {bairro} {CIDADE}", f"sala comercial {acao} {bairro}",
               f"loja {acao} {bairro}"]
    # dedup mantendo ordem
    seen, kws = set(), []
    for k in kw:
        kk = " ".join(k.split())
        if kk.lower() not in seen:
            seen.add(kk.lower()); kws.append(kk)
    neg = list(NEG_COMUNS) + (NEG_VENDA if fin == "venda" else NEG_LOCACAO)
    # não negativar o próprio tipo
    neg = [n for n in neg if tipo not in n]
    return {"finalidade": fin, "keywords": kws, "negativas": neg}


def keywords_marca() -> dict:
    """Campanha PRINCIPAL = marca / site inteiro (comprar + vender em VDC + ímãs de lead).

    Faz mais sentido que só por-imóvel: inventário pequeno + marca pessoal + lead magnets
    capturam comprador E vendedor. Por-imóvel vira complemento.
    """
    c = CIDADE
    kw = [
        f"imóveis à venda em {c}", f"apartamento à venda {c}", f"casa à venda {c}",
        f"comprar imóvel {c}", f"comprar apartamento {c}", f"comprar casa {c}",
        f"imobiliária {c}", f"corretora de imóveis {c}", f"Priscila Vasconcelos imóveis",
        # ímãs de lead (vendedor) — alta alavancagem
        f"quanto vale meu imóvel {c}", f"avaliação de imóvel grátis {c}",
        f"vender meu imóvel {c}", f"avaliar imóvel {c}",
    ]
    neg = ["aluguel", "alugar", "locação", "temporada", "emprego", "vaga de emprego",
           "concurso", "curso", "faculdade", "estágio", "planta baixa", "leilão"]
    return {"keywords": kw, "negativas": neg}


def main() -> None:
    con = sqlite3.connect(ROOT / "data/site.db"); con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT slug,titulo,bairro,tipo,quartos,suites,vagas,area_util,preco "
        "FROM imoveis WHERE ativo=1 ORDER BY preco DESC").fetchall()
    out = ["# 🔑 Palavras-chave de Ads — marca/site + por imóvel (Google + Meta)\n",
           "Estratégia: **campanha PRINCIPAL = marca/site inteiro** (comprar/vender em VDC + avaliação grátis); "
           "as keywords **por imóvel** são **complemento** (pros poucos que buscam específico). "
           "Keywords de intenção + negativas (cortam clique-lixo → CPL menor). Ver `docs/PESQUISA-LEADS-2026.md`.\n"]
    m = keywords_marca()
    out.append("## 🎯 CAMPANHA PRINCIPAL — Marca / Site inteiro (comprador + vendedor)")
    out.append("Aponta pra home + calculadora **\"quanto vale meu imóvel\"** (capta VENDEDOR) e /anunciar.\n")
    out.append("**Palavras-chave (intenção):**")
    out += [f"- {kw}" for kw in m["keywords"]]
    out.append("\n**Palavras NEGATIVAS:** " + ", ".join(m["negativas"]) + "\n")
    out.append("---\n### 🏠 Complemento — keywords por imóvel (pros buscadores específicos)\n")
    for r in rows:
        im = dict(r)
        k = keywords_por_imovel(im)
        preco = f"R$ {im['preco']:,.0f}".replace(",", ".")
        out.append(f"## {im['bairro'].strip().title()} · {im['tipo'].title()} · {preco}  ({k['finalidade']})")
        out.append(f"`{im['slug']}`\n")
        out.append("**Palavras-chave (intenção):**")
        out += [f"- {kw}" for kw in k["keywords"]]
        out.append("\n**Palavras NEGATIVAS:** " + ", ".join(k["negativas"]) + "\n")
    (ROOT / "docs/ADS-KEYWORDS-POR-IMOVEL.md").write_text("\n".join(out), encoding="utf-8")
    print(f"✅ docs/ADS-KEYWORDS-POR-IMOVEL.md gerado ({len(rows)} imóveis)")


if __name__ == "__main__":
    main()
