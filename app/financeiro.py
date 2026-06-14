"""Modulo financeiro — comissoes, metas e contas (W7).

Foco do MVP:
- Comissoes: registrar venda + percentual, calcular valor automatico, mudar status.
- Metas: meta mensal de vendas/comissao por corretor (ou geral, sem email).
- Contas a pagar/receber: gestao simples + dashboard.

Sem DRE complexa. Sem nota fiscal. Tudo em SQLite, escopo Priscila + ate 3 admins.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

from app.db import db_session


# ─── Comissoes ───────────────────────────────────────────────────────────────
def _row_to_dict(row) -> dict[str, Any] | None:
    if row is None:
        return None
    d = dict(row)
    if "pago" in d:
        d["pago"] = bool(d["pago"])
    return d


def criar_comissao(dados: dict) -> dict:
    valor_venda = float(dados["valor_venda"])
    percentual = float(dados.get("percentual", 0) or 0)
    valor_comissao = float(
        dados.get("valor_comissao")
        or (valor_venda * percentual / 100)
    )
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO comissoes
                (lead_id, imovel_id, corretor_email, descricao,
                 valor_venda, percentual, valor_comissao, status,
                 data_venda, data_recebimento)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados.get("lead_id"),
                dados.get("imovel_id"),
                dados.get("corretor_email"),
                dados["descricao"],
                valor_venda,
                percentual,
                valor_comissao,
                dados.get("status", "previsto"),
                dados.get("data_venda") or date.today().isoformat(),
                dados.get("data_recebimento"),
            ),
        )
        novo = int(cur.lastrowid)
    return buscar_comissao(novo)


def buscar_comissao(cid: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM comissoes WHERE id = ?", (cid,)).fetchone()
    return _row_to_dict(row)


def listar_comissoes(
    *,
    status: str | None = None,
    corretor: str | None = None,
    inicio: str | None = None,
    fim: str | None = None,
) -> list[dict]:
    sql = "SELECT * FROM comissoes WHERE 1=1"
    params: list[Any] = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    if corretor:
        sql += " AND corretor_email = ?"
        params.append(corretor)
    if inicio:
        sql += " AND data_venda >= ?"
        params.append(inicio)
    if fim:
        sql += " AND data_venda <= ?"
        params.append(fim)
    sql += " ORDER BY data_venda DESC, id DESC"
    with db_session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def atualizar_comissao(cid: int, dados: dict) -> dict | None:
    if not buscar_comissao(cid):
        return None
    permitidos = {
        "lead_id", "imovel_id", "corretor_email", "descricao",
        "valor_venda", "percentual", "valor_comissao",
        "status", "data_venda", "data_recebimento",
    }
    sets: list[str] = []
    params: list[Any] = []
    for k, v in dados.items():
        if k in permitidos:
            sets.append(f"{k} = ?")
            params.append(v)
    if not sets:
        return buscar_comissao(cid)
    params.append(cid)
    with db_session() as conn:
        conn.execute(f"UPDATE comissoes SET {', '.join(sets)} WHERE id = ?", params)
    return buscar_comissao(cid)


def excluir_comissao(cid: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM comissoes WHERE id = ?", (cid,))
    return cur.rowcount > 0


# ─── Metas ───────────────────────────────────────────────────────────────────
def upsert_meta(dados: dict) -> dict:
    """Insere ou atualiza meta para o triplo (corretor, ano, mes)."""
    corretor = dados.get("corretor_email")
    ano = int(dados["ano"])
    mes = int(dados["mes"])
    with db_session() as conn:
        existe = conn.execute(
            "SELECT id FROM metas WHERE coalesce(corretor_email,'') = coalesce(?,'') AND ano = ? AND mes = ?",
            (corretor, ano, mes),
        ).fetchone()
        if existe:
            conn.execute(
                "UPDATE metas SET meta_vendas = ?, meta_comissao = ? WHERE id = ?",
                (
                    float(dados.get("meta_vendas", 0)),
                    float(dados.get("meta_comissao", 0)),
                    existe["id"],
                ),
            )
            mid = int(existe["id"])
        else:
            cur = conn.execute(
                """INSERT INTO metas (corretor_email, ano, mes, meta_vendas, meta_comissao)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    corretor,
                    ano,
                    mes,
                    float(dados.get("meta_vendas", 0)),
                    float(dados.get("meta_comissao", 0)),
                ),
            )
            mid = int(cur.lastrowid)
        row = conn.execute("SELECT * FROM metas WHERE id = ?", (mid,)).fetchone()
    return dict(row)


def listar_metas(*, ano: int | None = None) -> list[dict]:
    sql = "SELECT * FROM metas WHERE 1=1"
    params: list[Any] = []
    if ano:
        sql += " AND ano = ?"
        params.append(ano)
    sql += " ORDER BY ano DESC, mes DESC, corretor_email"
    with db_session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def excluir_meta(mid: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM metas WHERE id = ?", (mid,))
    return cur.rowcount > 0


# ─── Contas ──────────────────────────────────────────────────────────────────
def criar_conta(dados: dict) -> dict:
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO contas
                (tipo, descricao, categoria, valor, vencimento, pago, data_pagamento, observacoes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                dados["tipo"],
                dados["descricao"],
                dados.get("categoria", "geral"),
                float(dados["valor"]),
                dados["vencimento"],
                int(bool(dados.get("pago", False))),
                dados.get("data_pagamento"),
                dados.get("observacoes"),
            ),
        )
        novo = int(cur.lastrowid)
    return buscar_conta(novo)


def buscar_conta(cid: int) -> dict | None:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM contas WHERE id = ?", (cid,)).fetchone()
    return _row_to_dict(row)


def listar_contas(
    *,
    tipo: str | None = None,
    pago: bool | None = None,
    inicio: str | None = None,
    fim: str | None = None,
) -> list[dict]:
    sql = "SELECT * FROM contas WHERE 1=1"
    params: list[Any] = []
    if tipo:
        sql += " AND tipo = ?"
        params.append(tipo)
    if pago is not None:
        sql += " AND pago = ?"
        params.append(1 if pago else 0)
    if inicio:
        sql += " AND vencimento >= ?"
        params.append(inicio)
    if fim:
        sql += " AND vencimento <= ?"
        params.append(fim)
    sql += " ORDER BY vencimento ASC, id DESC"
    with db_session() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [_row_to_dict(r) for r in rows]


def atualizar_conta(cid: int, dados: dict) -> dict | None:
    if not buscar_conta(cid):
        return None
    permitidos = {
        "tipo", "descricao", "categoria", "valor",
        "vencimento", "pago", "data_pagamento", "observacoes",
    }
    sets: list[str] = []
    params: list[Any] = []
    for k, v in dados.items():
        if k in permitidos:
            sets.append(f"{k} = ?")
            params.append(int(bool(v)) if k == "pago" else v)
    if not sets:
        return buscar_conta(cid)
    params.append(cid)
    with db_session() as conn:
        conn.execute(f"UPDATE contas SET {', '.join(sets)} WHERE id = ?", params)
    return buscar_conta(cid)


def marcar_conta_paga(cid: int, *, data_pagamento: str | None = None) -> dict | None:
    if not buscar_conta(cid):
        return None
    return atualizar_conta(
        cid,
        {
            "pago": True,
            "data_pagamento": data_pagamento or date.today().isoformat(),
        },
    )


def excluir_conta(cid: int) -> bool:
    with db_session() as conn:
        cur = conn.execute("DELETE FROM contas WHERE id = ?", (cid,))
    return cur.rowcount > 0


# ─── Dashboard agregado ──────────────────────────────────────────────────────
def dashboard(*, ano: int | None = None, mes: int | None = None) -> dict:
    """Resumo financeiro: comissoes, metas vs realizado, contas em aberto.

    Se ano/mes nao informado, usa mes corrente.
    """
    hoje = datetime.utcnow().date()
    ano = ano or hoje.year
    mes = mes or hoje.month
    inicio_mes = f"{ano:04d}-{mes:02d}-01"
    if mes == 12:
        fim_mes = f"{ano + 1:04d}-01-01"
    else:
        fim_mes = f"{ano:04d}-{mes + 1:02d}-01"

    with db_session() as conn:
        # Comissoes do mes
        com_total = conn.execute(
            """SELECT
                 COALESCE(SUM(valor_venda), 0) AS vendas,
                 COALESCE(SUM(valor_comissao), 0) AS comissoes,
                 COUNT(*) AS qtd
               FROM comissoes
               WHERE data_venda >= ? AND data_venda < ?
                 AND status != 'cancelado'""",
            (inicio_mes, fim_mes),
        ).fetchone()

        com_recebida = conn.execute(
            """SELECT COALESCE(SUM(valor_comissao), 0) AS recebida
               FROM comissoes
               WHERE data_venda >= ? AND data_venda < ? AND status = 'recebido'""",
            (inicio_mes, fim_mes),
        ).fetchone()

        # Metas do mes (soma de todos corretores ou geral)
        meta_row = conn.execute(
            """SELECT
                 COALESCE(SUM(meta_vendas), 0) AS meta_vendas,
                 COALESCE(SUM(meta_comissao), 0) AS meta_comissao
               FROM metas WHERE ano = ? AND mes = ?""",
            (ano, mes),
        ).fetchone()

        # Contas em aberto
        contas_pagar = conn.execute(
            """SELECT COALESCE(SUM(valor), 0) AS total, COUNT(*) AS qtd
               FROM contas WHERE tipo = 'pagar' AND pago = 0"""
        ).fetchone()
        contas_receber = conn.execute(
            """SELECT COALESCE(SUM(valor), 0) AS total, COUNT(*) AS qtd
               FROM contas WHERE tipo = 'receber' AND pago = 0"""
        ).fetchone()

        # Vencidas (vencimento < hoje, nao pago)
        vencidas = conn.execute(
            """SELECT COUNT(*) AS qtd FROM contas
               WHERE pago = 0 AND vencimento < ?""",
            (hoje.isoformat(),),
        ).fetchone()

        # ── Serie de 12 meses: fluxo de caixa REAL (entradas x saidas x saldo) ──
        MESES_PT = ["", "jan", "fev", "mar", "abr", "mai", "jun",
                    "jul", "ago", "set", "out", "nov", "dez"]
        meses12 = []
        yy, mm = ano, mes
        for _ in range(12):
            meses12.append((yy, mm))
            mm -= 1
            if mm == 0:
                mm, yy = 12, yy - 1
        meses12.reverse()
        serie = []
        acumulado = 0.0
        for (y, m) in meses12:
            ini = f"{y:04d}-{m:02d}-01"
            fim = f"{y + 1:04d}-01-01" if m == 12 else f"{y:04d}-{m + 1:02d}-01"
            ent_com = conn.execute(
                "SELECT COALESCE(SUM(valor_comissao),0) FROM comissoes "
                "WHERE status='recebido' AND data_recebimento >= ? AND data_recebimento < ?",
                (ini, fim)).fetchone()[0]
            ent_con = conn.execute(
                "SELECT COALESCE(SUM(valor),0) FROM contas "
                "WHERE tipo='receber' AND pago=1 AND data_pagamento >= ? AND data_pagamento < ?",
                (ini, fim)).fetchone()[0]
            sai_con = conn.execute(
                "SELECT COALESCE(SUM(valor),0) FROM contas "
                "WHERE tipo='pagar' AND pago=1 AND data_pagamento >= ? AND data_pagamento < ?",
                (ini, fim)).fetchone()[0]
            entradas = float(ent_com or 0) + float(ent_con or 0)
            saidas = float(sai_con or 0)
            acumulado += entradas - saidas
            serie.append({
                "ano": y, "mes": m, "label": f"{MESES_PT[m]}/{str(y)[2:]}",
                "entradas": entradas, "saidas": saidas,
                "saldo": entradas - saidas, "acumulado": acumulado,
            })

        ini_ano, fim_ano = f"{ano:04d}-01-01", f"{ano + 1:04d}-01-01"
        # Comissoes por status (ano)
        com_status_rows = conn.execute(
            "SELECT status, COUNT(*) qtd, COALESCE(SUM(valor_comissao),0) total "
            "FROM comissoes WHERE data_venda >= ? AND data_venda < ? GROUP BY status",
            (ini_ano, fim_ano)).fetchall()
        comissoes_status = [
            {"status": r["status"], "qtd": int(r["qtd"]), "total": float(r["total"] or 0)}
            for r in com_status_rows]
        # Despesas por categoria (contas a pagar quitadas no ano)
        desp_rows = conn.execute(
            "SELECT COALESCE(categoria,'geral') categoria, COALESCE(SUM(valor),0) total "
            "FROM contas WHERE tipo='pagar' AND pago=1 AND data_pagamento >= ? AND data_pagamento < ? "
            "GROUP BY categoria ORDER BY total DESC",
            (ini_ano, fim_ano)).fetchall()
        despesas_categoria = [
            {"categoria": r["categoria"], "total": float(r["total"] or 0)} for r in desp_rows]
        # Pipeline REAL: carteira de imoveis ativos (VGV) e comissao potencial a 6%
        pipe = conn.execute(
            "SELECT COUNT(*) qtd, COALESCE(SUM(preco),0) vgv FROM imoveis WHERE ativo = 1").fetchone()

    vendas = float(com_total["vendas"] or 0)
    comissoes = float(com_total["comissoes"] or 0)
    meta_v = float(meta_row["meta_vendas"] or 0)
    meta_c = float(meta_row["meta_comissao"] or 0)

    return {
        "periodo": {"ano": ano, "mes": mes},
        "comissoes": {
            "qtd": int(com_total["qtd"] or 0),
            "valor_vendas": vendas,
            "valor_comissoes": comissoes,
            "valor_recebido": float(com_recebida["recebida"] or 0),
        },
        "metas": {
            "meta_vendas": meta_v,
            "meta_comissao": meta_c,
            "atingido_vendas_pct": (vendas / meta_v * 100) if meta_v > 0 else 0,
            "atingido_comissao_pct": (comissoes / meta_c * 100) if meta_c > 0 else 0,
        },
        "contas": {
            "a_pagar_total": float(contas_pagar["total"] or 0),
            "a_pagar_qtd": int(contas_pagar["qtd"] or 0),
            "a_receber_total": float(contas_receber["total"] or 0),
            "a_receber_qtd": int(contas_receber["qtd"] or 0),
            "vencidas_qtd": int(vencidas["qtd"] or 0),
        },
        "serie": serie,
        "comissoes_status": comissoes_status,
        "despesas_categoria": despesas_categoria,
        "pipeline": {
            "imoveis_ativos": int(pipe["qtd"] or 0),
            "vgv": float(pipe["vgv"] or 0),
            "comissao_potencial": float(pipe["vgv"] or 0) * 0.06,
        },
    }
