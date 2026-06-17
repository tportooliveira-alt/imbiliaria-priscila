#!/usr/bin/env python3
"""Gera a planilha Excel da pesquisa de imoveis de VDC para a Priscila.

Junta os ~792 anuncios de VENDA + ~99 de ALUGUEL coletados, roda a calculadora em cada um
(valor estimado, faixa, aluguel) e exporta um .xlsx com abas:
  - Imoveis a venda (cada casa, preco anunciado vs valor estimado nosso)
  - Alugueis
  - Resumo por bairro (R$/m2 medio)
  - Ruas (premium / popular / comercial por bairro)

Uso: PYTHONPATH=. venv/bin/python scripts/gerar_planilha_priscila.py
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

import pandas as pd

from app.avaliacao import avaliar, yield_aluguel_mensal
from scripts.calibracao_eval import RODADA_1, RODADA_2, RODADA_3, carregar_lotes, carregar_psv

SAIDA = Path("relatorio-priscila/IMOVEIS-VDC.xlsx")
PT_TIPO = {"casa": "Casa", "apartamento": "Apartamento", "cobertura": "Cobertura",
           "terreno": "Terreno", "comercial": "Comercial"}
PT_PAD = {"simples": "Simples", "medio": "Médio", "alto": "Alto", "luxo": "Luxo"}


def _linha_venda(it):
    bairro, titulo, tipo, area, area_ter, q, ste, vg, padrao, estado, idade, recem, preco, fonte = it[:14]
    rua = it[14] if len(it) > 14 else None
    try:
        r = avaliar(bairro=bairro, area_util=area, tipo=tipo, quartos=q or 2, suites=ste or 0,
                    vagas=vg or 0, padrao=padrao or "medio", estado=estado or "bom",
                    idade=idade or ("novo" if recem else "0_10"), area_terreno=area_ter, rua=rua)
    except Exception:
        return None
    erro = round((r.valor_central - preco) / preco * 100, 1) if preco else None
    return {
        "Bairro": bairro.replace("_", " ").title(), "Rua": rua or "",
        "Tipo": PT_TIPO.get(tipo, tipo), "Área (m²)": area, "Quartos": q or "",
        "Suítes": ste or "", "Vagas": vg or "", "Padrão": PT_PAD.get(padrao, padrao or ""),
        "Preço anunciado (R$)": int(preco),
        "R$/m² anunciado": round(preco / area) if area else "",
        "Valor estimado (R$)": int(r.valor_central),
        "Faixa mín (R$)": int(r.valor_minimo), "Faixa máx (R$)": int(r.valor_maximo),
        "Dif. estim. vs anúncio (%)": erro,
        "Aluguel estimado (R$/mês)": int(round(r.valor_central * yield_aluguel_mensal(r.valor_central, tipo))),
        "Confiança": r.confianca, "Fonte": fonte, "Título": titulo,
    }


def _linhas_aluguel():
    p = Path("calibracao/aluguel_vdc.psv")
    if not p.exists():
        return []
    linhas = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    head = [h.strip() for h in linhas[0].split("|")]
    out = []
    for ln in linhas[1:]:
        d = dict(zip(head, [c.strip() for c in ln.split("|")]))
        try:
            area = float(d["area_m2"]); aluguel = float(d["preco"])
        except (ValueError, KeyError):
            continue
        if area <= 0 or aluguel <= 0:
            continue
        out.append({
            "Bairro": d["bairro"], "Rua": d.get("rua", ""), "Tipo": PT_TIPO.get(d["tipo"], d["tipo"]),
            "Área (m²)": area, "Quartos": d.get("quartos", ""), "Padrão": PT_PAD.get(d.get("padrao", ""), ""),
            "Aluguel (R$/mês)": int(aluguel), "R$/m² aluguel": round(aluguel / area, 1),
            "Data": d.get("data", ""), "Fonte": d.get("fonte", ""), "Título": d.get("titulo", ""),
        })
    return out


def main():
    SAIDA.parent.mkdir(exist_ok=True)
    vendas = [_linha_venda(it) for n in (RODADA_1, RODADA_2, RODADA_3) for it in n]
    vendas += [_linha_venda(it) for it in carregar_lotes()]
    vendas += [_linha_venda(it) for it in carregar_psv()]
    vendas = [v for v in vendas if v]
    # dedup por bairro+tipo+area+preco
    seen, uniq = set(), []
    for v in vendas:
        k = (v["Bairro"], v["Tipo"], round(v["Área (m²)"]), v["Preço anunciado (R$)"])
        if k in seen:
            continue
        seen.add(k); uniq.append(v)
    df_v = pd.DataFrame(uniq).sort_values(["Bairro", "Preço anunciado (R$)"])
    df_a = pd.DataFrame(_linhas_aluguel()).sort_values(["Bairro", "Aluguel (R$/mês)"]) if _linhas_aluguel() else pd.DataFrame()

    # Resumo por bairro
    res = []
    for b, g in df_v.groupby("Bairro"):
        rm2 = [r for r in g["R$/m² anunciado"] if isinstance(r, (int, float))]
        res.append({"Bairro": b, "Imóveis": len(g),
                    "R$/m² mediano": round(statistics.median(rm2)) if rm2 else "",
                    "Preço mín (R$)": int(g["Preço anunciado (R$)"].min()),
                    "Preço máx (R$)": int(g["Preço anunciado (R$)"].max())})
    df_r = pd.DataFrame(res).sort_values("Imóveis", ascending=False)

    # Ruas
    ruas_rows = []
    rmap = json.load(open("calibracao/ruas_vdc.json"))["bairros"]
    for b, v in rmap.items():
        ruas_rows.append({"Bairro": b.replace("_", " ").title(),
                          "Ruas premium (caras)": "; ".join(v.get("premium", [])),
                          "Ruas populares (baratas)": "; ".join(v.get("popular", [])),
                          "Corredores comerciais": "; ".join(v.get("comercial", [])),
                          "Observação": v.get("obs", "")})
    df_ruas = pd.DataFrame(ruas_rows)

    with pd.ExcelWriter(SAIDA, engine="openpyxl") as xl:
        df_v.to_excel(xl, sheet_name="Imóveis à venda", index=False)
        if not df_a.empty:
            df_a.to_excel(xl, sheet_name="Aluguéis", index=False)
        df_r.to_excel(xl, sheet_name="Resumo por bairro", index=False)
        df_ruas.to_excel(xl, sheet_name="Ruas por bairro", index=False)
        # largura de coluna basica
        for ws in xl.book.worksheets:
            for col in ws.columns:
                w = max((len(str(c.value)) for c in col if c.value is not None), default=10)
                ws.column_dimensions[col[0].column_letter].width = min(max(w + 2, 10), 48)

    print(f"OK: {len(df_v)} imoveis a venda + {len(df_a)} alugueis -> {SAIDA}")


if __name__ == "__main__":
    main()
