#!/usr/bin/env python3
"""Calibra o YIELD de aluguel (aluguel mensal / valor de venda) a partir de alugueis reais.

Para cada anuncio de ALUGUEL (calibracao/aluguel_vdc.psv, preco=aluguel mensal), roda a
calculadora de VENDA no mesmo imovel -> valor estimado -> yield = aluguel / valor.
Imprime a mediana do yield por bairro e geral, p/ atualizar yield_bairro em routes_publicas.py.

Uso: PYTHONPATH=. venv/bin/python scripts/calibracao_aluguel.py
"""
from __future__ import annotations

import statistics
from pathlib import Path

from app.avaliacao import avaliar

PSV = Path("calibracao/aluguel_vdc.psv")
_VALID_P = ("simples", "medio", "alto", "luxo")


def _rows():
    linhas = [l for l in PSV.read_text(encoding="utf-8").splitlines() if l.strip()]
    head = [h.strip() for h in linhas[0].split("|")]
    for ln in linhas[1:]:
        yield dict(zip(head, [c.strip() for c in ln.split("|")]))


def main():
    por_bairro: dict[str, list[float]] = {}
    por_bairro_apto: dict[str, list[float]] = {}
    todos: list[float] = []
    n = 0
    for d in _rows():
        try:
            area = float(d.get("area_m2") or 0)
            aluguel = float(d.get("preco") or 0)
        except ValueError:
            continue
        if area <= 0 or aluguel <= 0:
            continue
        tipo = (d.get("tipo") or "casa").lower()
        if tipo not in ("casa", "apartamento", "cobertura", "terreno", "comercial"):
            tipo = "casa"
        p = d.get("padrao") if d.get("padrao") in _VALID_P else "medio"
        r = avaliar(
            bairro=d.get("bairro", ""), area_util=area, tipo=tipo,
            quartos=int(d["quartos"]) if (d.get("quartos") or "").isdigit() else 2,
            suites=int(d["suites"]) if (d.get("suites") or "").isdigit() else 0,
            vagas=int(d["vagas"]) if (d.get("vagas") or "").isdigit() else 0,
            padrao=p, rua=d.get("rua") or None,
        )
        if r.valor_central <= 0:
            continue
        yld = aluguel / r.valor_central  # yield mensal
        por_bairro.setdefault(r.bairro_normalizado, []).append(yld)
        if tipo == "apartamento":
            por_bairro_apto.setdefault(r.bairro_normalizado, []).append(yld)
        todos.append(yld)
        n += 1

    print(f"\n=== YIELD mensal REAL (aluguel / valor estimado) — {n} alugueis ===")
    print(f"{'bairro':14} {'n':>3} {'yield_geral':>11} {'yield_apto':>11}")
    for b in sorted(por_bairro):
        ger = statistics.median(por_bairro[b])
        apto = por_bairro_apto.get(b)
        apto_s = f"{statistics.median(apto)*100:.3f}%" if apto else "—"
        print(f"  {b:12} {len(por_bairro[b]):>3} {ger*100:>10.3f}% {apto_s:>11}")
    print(f"\nGERAL: mediana={statistics.median(todos)*100:.3f}%/mes  "
          f"media={statistics.mean(todos)*100:.3f}%/mes  (anual ~{statistics.median(todos)*12*100:.1f}%)")


if __name__ == "__main__":
    main()
