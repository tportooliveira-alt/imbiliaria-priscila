#!/usr/bin/env python3
"""Backtest de calibracao da calculadora de avaliacao (AVM) contra anuncios REAIS de VDC.

Coletados por agentes (OLX + imobiliarias locais: Paullo Victor, MGF, Sales...). Preco = PEDIDO (ask),
que costuma estar ~5-15% ACIMA do fechamento; logo, espera-se a estimativa um pouco ABAIXO do pedido.
Salva o dataset acumulado em data/calibracao_olx.csv e imprime erro por anuncio + MAPE por bairro.

Uso: venv/bin/python scripts/calibracao_eval.py
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path

from app.avaliacao import avaliar

CSV = Path("data/calibracao_olx.csv")

# Cada rodada acrescenta itens aqui (mantemos o historico no codigo + no CSV).
# campos: bairro,titulo,tipo,area_util,area_terreno,quartos,suites,vagas,padrao,estado,idade,recem,preco_pedido,fonte
RODADA_1 = [
    # ---- Candeias ----
    ("candeias", "Apto Olivia Flores 74m2", "apartamento", 74, None, 2, 0, 0, "alto", "bom", None, False, 549000, "Paullo Victor"),
    ("candeias", "Apto AP0089 115m2 3q/2ste/2vg", "apartamento", 115, None, 3, 2, 2, "alto", "bom", None, False, 839929, "Paullo Victor"),
    ("candeias", "Casa CA0302 119m2 3q", "casa", 119, None, 3, 0, 0, "medio", "bom", None, False, 600000, "Paullo Victor"),
    ("candeias", "Casa CA0172 257m2 4q/3ste/4vg", "casa", 257, None, 4, 3, 4, "alto", "bom", None, False, 1249000, "Paullo Victor"),
    ("candeias", "Casa CA0295 250m2 3q/1ste/3vg", "casa", 250, None, 3, 1, 3, "alto", "bom", None, False, 940000, "Paullo Victor"),
    ("candeias", "Casa Bella Citta 147m2 4q/4ste/2vg", "casa", 147, None, 4, 4, 2, "alto", "bom", None, False, 850000, "Paullo Victor"),
    ("candeias", "Casa CA0287 500m2 4q/3ste/4vg", "casa", 500, None, 4, 3, 4, "luxo", "bom", None, False, 1100000, "Paullo Victor"),
    ("candeias", "Casa Parque das Aguas 500m2 5q/5ste/6vg", "casa", 500, None, 5, 5, 6, "luxo", "bom", None, False, 2900000, "Paullo Victor"),
    # ---- Recreio ----
    ("recreio", "San Giorgio Residence 65m2 2ste (novo)", "apartamento", 65, None, 2, 2, 0, "alto", "bom", "novo", True, 500000, "OLX"),
    ("recreio", "Residencial Lara Andrade 95m2 3ste/2vg", "apartamento", 95, None, 3, 3, 2, "alto", "bom", "0_10", False, 680000, "OLX"),
    ("recreio", "Apto Alto Padrao 11 andar 108m2", "apartamento", 108, None, 3, 3, 0, "alto", "bom", None, False, 500000, "MGF"),
    ("recreio", "Apto Maria Julia 88m2 3q", "apartamento", 88, None, 3, 1, 0, "medio", "bom", None, False, 340000, "MGF"),
    ("recreio", "Apto Residencial Recreio 91m2 3q", "apartamento", 91.05, None, 3, 1, 0, "medio", "bom", None, False, 260000, "MGF"),
    ("recreio", "Apto 70m2 3q/2vg", "apartamento", 70, None, 3, 1, 2, "medio", "bom", None, False, 290000, "MGF"),
    ("recreio", "Ed Villa Imperial 310m2 4ste/4vg", "apartamento", 310, None, 4, 4, 4, "luxo", "bom", None, False, 1200000, "MGF"),
    ("recreio", "Cobertura Malu Andrade 300m2 3ste", "cobertura", 300, None, 3, 3, 0, "luxo", "bom", None, False, 3000000, "MGF"),
    ("recreio", "Casa 480m2 terreno 2360 3q/2ste", "casa", 480, 2360, 3, 2, 0, "luxo", "bom", None, False, 3000000, "MGF"),
    ("recreio", "Casa 360m2 terreno 500", "casa", 360, 500, 3, 0, 0, "alto", "bom", None, False, 1500000, "MGF"),
    ("recreio", "Vitoria Tower 42m2 1q (novo)", "apartamento", 42, None, 1, 0, 1, "medio", "bom", "novo", True, 257000, "Sales"),
    # ---- Boa Vista ----
    ("boa_vista", "Casa Duplex Le Ville 71m2 2ste (novo)", "casa", 71, 71, 2, 2, 1, "medio", "bom", "novo", True, 332929, "Sales"),
    ("boa_vista", "Village Porto Seguro 114m2 3q/2ste/2vg", "casa", 114, None, 3, 2, 2, "medio", "bom", "0_10", False, 420000, "Sales"),
    ("boa_vista", "Casa Duplex Parque Reale 118m2 3q/3vg", "casa", 118, None, 3, 1, 3, "alto", "bom", "0_10", False, 440000, "Sales/Arbo"),
    ("boa_vista", "Casa Duque Residence 90m2 3ste (novo)", "casa", 90, None, 3, 3, 2, "alto", "bom", "novo", True, 750000, "Paullo Victor"),
    ("boa_vista", "Casa Lord Residence 180m2 4q/2ste (novo)", "casa", 180, None, 4, 2, 2, "alto", "bom", "novo", True, 1190000, "Paullo Victor"),
    ("boa_vista", "Casa Lord Residence 180m2 4q/3ste (novo)", "casa", 180, None, 4, 3, 2, "luxo", "bom", "novo", True, 1280000, "Paullo Victor"),
    ("boa_vista", "Casa Parque dos Ipes 2 195m2 3ste/4vg (novo)", "casa", 195, None, 3, 3, 4, "luxo", "bom", "novo", True, 1290000, "Paullo Victor"),
    ("boa_vista", "Casa Parque dos Ipes 2 245m2 5q/4ste (novo)", "casa", 245, None, 5, 4, 4, "luxo", "bom", "novo", True, 1749000, "Paullo Victor"),
    ("boa_vista", "Casa Jardim Botanico 320m2 3ste/4vg (novo)", "casa", 320, None, 3, 3, 4, "luxo", "bom", "novo", True, 2200000, "Paullo Victor"),
    ("boa_vista", "Casa CA0276 131m2 3q/2vg", "casa", 131, None, 3, 1, 2, "alto", "bom", "0_10", False, 523900, "Paullo Victor"),
]

# RODADA 2 (Centro, Brasil, Alto Maron) — so itens com AREA e PRECO. Inclui condominios de construtora.
RODADA_2 = [
    # ---- Centro ----
    ("centro", "Casa Rua Jose de Alencar 177m2", "casa", 177, None, 2, 0, 1, "medio", "bom", "20_mais", False, 480000, "ZAP"),
    ("centro", "Casa Av Fernando Spinola 122m2", "casa", 122, None, 3, 0, 1, "medio", "bom", "20_mais", False, 320000, "ZAP"),
    ("centro", "Casa Rua Dom Pedro II 388m2", "casa", 388, None, 3, 0, 3, "alto", "bom", "20_mais", False, 490000, "ZAP"),
    ("centro", "Casa Centro 79m2 reformada", "casa", 79.93, 100, 3, 1, 1, "medio", "reformado", "20_mais", False, 350000, "Imovelweb"),
    ("centro", "MRV Parque Vitoria Imperial 40m2 (tabela)", "apartamento", 40.28, None, 2, 0, 1, "medio", "bom", "novo", True, 147790, "MRV"),
    ("centro", "MRV Parque Vitoria Imperial 42m2 (tabela)", "apartamento", 42, None, 2, 0, 1, "medio", "bom", "novo", True, 185000, "MRV"),
    ("centro", "Casa Popular Centro 54m2", "casa", 54, None, 2, 0, 1, "simples", "regular", "0_10", False, 205000, "Nestoria"),
    ("centro", "Casa Padrao Medio 155m2", "casa", 155, None, 4, 0, 2, "medio", "bom", "10_20", False, 500000, "Nestoria"),
    # ---- Bairro Brasil (so 1 com area+preco confiavel) ----
    ("brasil", "Casa Green Ville 200m2 (condo)", "casa", 200, None, 6, 0, 0, "alto", "bom", "10_20", False, 490000, "MGF"),
    # ---- Alto Maron ----
    ("alto_maron", "Maron Premium 44m2 (tabela construtora)", "apartamento", 44, None, 2, 1, 1, "medio", "bom", "novo", True, 220000, "DTomaz"),
    ("alto_maron", "Casa Rua Primeiro de Maio 436m2", "casa", 436, None, 3, 0, 0, "medio", "bom", "10_20", False, 450000, "Arbo"),
    ("alto_maron", "Casa Joao Pessoa 155m2 4q/2ste", "casa", 155, None, 4, 2, 2, "medio", "bom", "10_20", False, 550000, "Arbo"),
    ("alto_maron", "Casa Sifredo Pedral 145m2 (comercial)", "casa", 145, None, 0, 0, 2, "medio", "bom", "10_20", False, 650000, "Arbo"),
    ("alto_maron", "Club Essential Atalaia 45m2 (tabela)", "apartamento", 45.72, None, 2, 1, 0, "medio", "bom", "novo", True, 240852, "Souza Gomes"),
    ("alto_maron", "Jardim Madrid 68m2 (condo)", "apartamento", 68, None, 2, 0, 0, "medio", "bom", "10_20", False, 450000, "Loft"),
    ("alto_maron", "Casa Av Filipinas 373m2 alto", "casa", 373, None, 3, 1, 2, "alto", "bom", "10_20", False, 500000, "Marcelo Santana"),
]

# RODADA 3 (Felicia, Ibirapuera, Patagonia). SUSPEITOS marcados (bairro errado etc) sao EXCLUIDOS via _LIMPAR.
RODADA_3 = [
    # ---- Felicia ----
    # SUSPEITO excluido: "Apto 161m2 2q Felicia R$259k" = 1.609/m² (impossivel p/ 2q) -> area mal-lida (~61m²); recoletar.
    ("felicia", "Apto 112m2 Morada dos Passaros", "apartamento", 112, None, 3, 1, 1, "medio", "bom", "0_10", False, 330000, "MGF"),
    ("felicia", "Casa 150m2 Av Filipinas alto", "casa", 150, 373, 3, 1, 2, "alto", "reformado", "10_20", False, 500000, "Arbo"),
    ("felicia", "Casa 108m2 Morada dos Passaros", "casa", 108, None, 2, 1, 3, "medio", "bom", "10_20", False, 320000, "Arbo"),
    ("felicia", "Apto 82m2 Morada dos Passaros", "apartamento", 82, None, 3, 1, 1, "medio", "bom", "0_10", False, 265000, "MGF"),
    ("felicia", "Casa 120m2 3q", "casa", 120, None, 3, 1, 2, "medio", "bom", "10_20", False, 400000, "Marcelo Santana"),
    ("felicia", "Apto 56m2 Riverside simples", "apartamento", 56, None, 2, 0, 1, "simples", "bom", "10_20", False, 215000, "MGF"),
    ("felicia", "Apto 50m2 Parque Vitoria Sul simples", "apartamento", 50, None, 2, 0, 1, "simples", "bom", "0_10", False, 225000, "MGF"),
    ("felicia", "Casa 126m2 novo", "casa", 126, None, 3, 1, 2, "medio", "bom", "novo", True, 380000, "MGF"),
    ("felicia", "Apto 45m2 Parque Vitoria Sul simples", "apartamento", 45, None, 2, 0, 1, "simples", "bom", "10_20", False, 220000, "MGF"),
    # ---- Ibirapuera ----
    ("ibirapuera", "Casa Av Para 200m2", "casa", 200, None, 2, 0, 1, "medio", "bom", "10_20", False, 350000, "Chaves na Mao"),
    ("ibirapuera", "Casa Av Jequie 220m2", "casa", 220, None, 3, 0, 0, "medio", "bom", "10_20", False, 600000, "Marcelo Santana"),
    ("ibirapuera", "Casa Av Amazonas 313m2 alto novo", "casa", 313, None, 4, 4, 2, "alto", "reformado", "novo", True, 1100000, "Marcelo Santana"),
    ("ibirapuera", "Casa Rua Monte Sinai 250m2", "casa", 250, None, 4, 0, 4, "medio", "bom", "10_20", False, 455000, "VivaReal"),
    ("ibirapuera", "Apto Rua Maria Rosa 115m2", "apartamento", 115, None, 3, 0, 0, "medio", "bom", "10_20", False, 320000, "ZAP"),
    ("ibirapuera", "Apto Av Jequie 108m2", "apartamento", 108, None, 3, 0, 3, "medio", "bom", "10_20", False, 650000, "ZAP"),
    ("ibirapuera", "Residencial Jatoba 68m2 (tabela)", "apartamento", 68, None, 3, 1, 1, "medio", "bom", "novo", True, 195000, "Sales"),
    ("ibirapuera", "VOG Parque Premier duplex 148m2 (tabela)", "casa", 148, 148, 2, 0, 2, "alto", "bom", "novo", True, 351756, "Sales"),
    ("ibirapuera", "VOG Parque Premier duplex 148m2 3q (tabela)", "casa", 148, 148, 3, 1, 2, "alto", "bom", "novo", True, 396406, "Sales"),
    # ---- Patagonia (so casas legitimas; condos com nome 'Candeias' sao SUSPEITOS -> excluidos) ----
    ("patagonia", "Sobrado 329m2 5q/4ste alto", "casa", 329, None, 5, 4, 0, "alto", "bom", "10_20", False, 1200000, "MGF"),
    ("patagonia", "Casa 100m2 simples", "casa", 100, None, 2, 0, 2, "simples", "bom", "10_20", False, 229000, "MGF"),
]

# Itens com bairro provavelmente ERRADO (agente rotulou Patagonia mas o nome diz Candeias/condo de outro bairro).
# Mantidos fora da calibracao p/ nao sujar. (titulo, bairro_real_provavel)
_SUSPEITOS = [
    ("patagonia", "Vog Candeias Residence -> Candeias"),
    ("patagonia", "Prime Candeias Green -> Candeias"),
]

CAMPOS = ["rodada", "bairro", "titulo", "tipo", "area_util", "area_terreno", "quartos", "suites",
          "vagas", "padrao", "estado", "idade", "recem", "preco_pedido", "fonte",
          "estimativa", "valor_min", "valor_max", "erro_pct", "dentro_faixa"]


import glob
import json

# nomes de bairro (normalizados) -> chave do m2_vdc
_BAIRRO_ALIAS = {
    "alto_da_boa_vista": "boa_vista", "loteamento_alto_da_boa_vista": "boa_vista",
    "terras_alphaville": "alphaville", "haras_camping_club": "haras",
}


def _norm_b(b: str) -> str:
    k = (b or "").strip().lower()
    for a, x in (("í", "i"), ("ó", "o"), ("ã", "a"), ("ô", "o"), ("â", "a"), ("é", "e"), ("ç", "c"), ("ê", "e")):
        k = k.replace(a, x)
    k = k.replace(" ", "_").replace("-", "_")
    return _BAIRRO_ALIAS.get(k, k)


def carregar_lotes() -> list[tuple]:
    """Le calibracao/*.json (chaves curtas) -> tuplas no mesmo formato das RODADAS."""
    out: list[tuple] = []
    for fp in sorted(glob.glob("calibracao/*.json")):
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        for a in data.get("anuncios", []):
            if not a.get("a") or not a.get("pr"):
                continue
            tipo = a.get("t") or "casa"
            if tipo == "sobrado":
                tipo = "casa"
            if tipo not in ("casa", "apartamento", "cobertura", "terreno", "comercial"):
                tipo = "casa"
            out.append((
                _norm_b(a.get("b", "")), (a.get("ti") or "")[:42], tipo, a["a"], a.get("at"),
                a.get("q") or 2, a.get("s") or 0, a.get("v") or 0,
                a.get("p") or "medio", a.get("e") or "bom", a.get("i"),
                bool(a.get("r")), a["pr"], a.get("f", ""),
            ))
    return out


def avalia_item(it):
    (bairro, titulo, tipo, area, area_ter, q, ste, vg, padrao, estado, idade, recem, preco, fonte) = it
    idade_f = idade or ("novo" if recem else "0_10")
    r = avaliar(
        bairro=bairro, area_util=area, quartos=q or 2, suites=ste or 0, vagas=vg or 0,
        padrao=padrao or "medio", estado=estado or "bom", idade=idade_f,
        tipo=tipo, area_terreno=area_ter,
    )
    est = r.valor_central
    erro = (est - preco) / preco * 100
    dentro = r.valor_minimo <= preco <= r.valor_maximo
    return est, r.valor_minimo, r.valor_maximo, erro, dentro


def main():
    combinados = [(n, it) for n, lst in [(1, RODADA_1), (2, RODADA_2), (3, RODADA_3)] for it in lst]
    combinados += [("A", it) for it in carregar_lotes()]
    rows = []
    seen = set()
    for nrod, it in combinados:
        chave = (it[0], it[2], round(float(it[3])), it[12])  # bairro,tipo,area,preco -> dedup
        if chave in seen:
            continue
        seen.add(chave)
        est, vmin, vmax, erro, dentro = avalia_item(it)
        (bairro, titulo, tipo, area, area_ter, q, ste, vg, padrao, estado, idade, recem, preco, fonte) = it
        rows.append({
            "rodada": nrod, "bairro": bairro, "titulo": titulo, "tipo": tipo, "area_util": area,
            "area_terreno": area_ter or "", "quartos": q or "", "suites": ste or "", "vagas": vg or "",
            "padrao": padrao or "medio", "estado": estado or "bom", "idade": idade or ("novo" if recem else "0_10"),
            "recem": recem, "preco_pedido": preco, "fonte": fonte,
            "estimativa": round(est), "valor_min": round(vmin), "valor_max": round(vmax),
            "erro_pct": round(erro, 1), "dentro_faixa": dentro,
        })

    CSV.parent.mkdir(exist_ok=True)
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(rows)

    # Relatorio
    print(f"\n{'BAIRRO':10} {'IMOVEL':42} {'PEDIDO':>11} {'ESTIM':>11} {'ERRO%':>7}  FAIXA")
    print("-" * 95)
    por_bairro: dict[str, list[float]] = {}
    dentro_total = 0
    for r in rows:
        marca = "ok" if r["dentro_faixa"] else "FORA"
        if r["dentro_faixa"]:
            dentro_total += 1
        print(f"{r['bairro']:10} {r['titulo'][:42]:42} {r['preco_pedido']:>11,} {r['estimativa']:>11,} {r['erro_pct']:>7.1f}  {marca}")
        por_bairro.setdefault(r["bairro"], []).append(r["erro_pct"])

    print("\n=== POR BAIRRO (erro = estimativa vs pedido; pedido e ~5-15% acima do fechamento) ===")
    print(f"{'bairro':12} {'n':>3} {'MAPE%':>7} {'mediana_erro%':>14} {'vies':>8}")
    for b, errs in por_bairro.items():
        mape = statistics.mean(abs(e) for e in errs)
        med = statistics.median(errs)
        vies = "ALTO" if med > 8 else ("baixo" if med < -18 else "ok")
        print(f"{b:12} {len(errs):>3} {mape:>7.1f} {med:>14.1f} {vies:>8}")

    # Diagnostico: R$/m2 REAL (pedido/area) por bairro x tipo -> guia pra recalibrar a base
    print("\n=== R$/m2 REAL por bairro x tipo (mediana do pedido/area; base do m2_vdc entre []) ===")
    from app.m2_vdc import M2_VDC as M2_BAIRRO_APTO
    by: dict[tuple, list[float]] = {}
    for r in rows:
        by.setdefault((r["bairro"], "casa" if r["tipo"] == "casa" else "apto/outro"), []).append(r["preco_pedido"] / r["area_util"])
    for (b, t), vals in sorted(by.items()):
        base = M2_BAIRRO_APTO.get(b, "?")
        print(f"  {b:12} {t:11} n={len(vals):>2}  mediana R$/m2={statistics.median(vals):>7,.0f}  (base apto={base})")

    todos = [r["erro_pct"] for r in rows]
    print(f"\nGERAL: n={len(todos)}  MAPE={statistics.mean(abs(e) for e in todos):.1f}%  "
          f"mediana={statistics.median(todos):.1f}%  dentro_da_faixa={dentro_total}/{len(todos)}")
    print(f"CSV salvo em {CSV}")


if __name__ == "__main__":
    main()
