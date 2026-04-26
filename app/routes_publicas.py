"""Rotas publicas: simulador de financiamento e avaliacao de imovel."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app import avaliacao, financiamento, leads as leads_repo
from app.conversas import registrar_evento_funil
from app.db import db_session
from app.m2_vdc import BAIRROS_DISPONIVEIS

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Simulador de financiamento
# ─────────────────────────────────────────────────────────────────────────────
class SimulacaoRequest(BaseModel):
    valor_imovel: float = Field(..., gt=0, le=20_000_000)
    entrada: float = Field(..., ge=0)
    prazo_meses: int = Field(..., ge=12, le=420)
    taxa_anual: float = Field(11.5, ge=0, le=30)
    sistema: Literal["SAC", "PRICE"] = "SAC"
    renda_mensal: float | None = Field(None, ge=0)
    nome: str | None = Field(None, max_length=120)
    contato: str | None = Field(None, max_length=120)
    bairro: str | None = Field(None, max_length=80)
    tipo_imovel: str | None = Field(None, max_length=40)


@router.get("/api/financiamento/taxas")
def taxas_referenciais() -> dict:
    return {
        "taxas": financiamento.TAXAS_BANCOS,
        "fonte": "Sites oficiais dos bancos (SBPE)",
        "atualizado_em": "abril/2026",
    }


@router.post("/api/simular-financiamento")
def simular(payload: SimulacaoRequest) -> dict:
    try:
        r = financiamento.simular(
            valor_imovel=payload.valor_imovel,
            entrada=payload.entrada,
            prazo_meses=payload.prazo_meses,
            taxa_anual=payload.taxa_anual,
            sistema=payload.sistema,
            renda_mensal=payload.renda_mensal,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Persiste para alimentar funil
    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO simulacoes
                 (valor_imovel, entrada, prazo_meses, taxa_anual, sistema,
                  parcela_inicial, total_pago, renda_minima, nome, contato,
                  bairro, tipo_imovel)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                r.valor_imovel, r.entrada, r.prazo_meses, r.taxa_anual, r.sistema,
                r.parcela_inicial, r.total_pago, r.renda_minima,
                payload.nome, payload.contato,
                payload.bairro, payload.tipo_imovel,
            ),
        )
        sim_id = int(cur.lastrowid)

    registrar_evento_funil(
        "simulacao.criada",
        origem="simulador",
        payload={
            "simulacao_id": sim_id,
            "sistema": r.sistema,
            "bairro": payload.bairro,
            "tipo_imovel": payload.tipo_imovel,
        },
        idempotency_key=f"simulacao:{sim_id}",
    )

    comprometimento_ok = (
        r.comprometimento_renda is not None and r.comprometimento_renda <= 0.30
    )

    # Comparativo entre bancos com taxas reais (mesmo prazo/entrada/sistema)
    comparativo: list[dict] = []
    for chave, info in financiamento.TAXAS_BANCOS.items():
        try:
            sim_banco = financiamento.simular(
                valor_imovel=payload.valor_imovel,
                entrada=payload.entrada,
                prazo_meses=payload.prazo_meses,
                taxa_anual=info["taxa_anual"],
                sistema=payload.sistema,
                renda_mensal=payload.renda_mensal,
            )
            comparativo.append({
                "chave": chave,
                "banco": info["nome"],
                "taxa_anual": info["taxa_anual"],
                "lt_max": info["lt_max"],
                "parcela_inicial": sim_banco.parcela_inicial,
                "parcela_final": sim_banco.parcela_final,
                "total_pago": sim_banco.total_pago,
                "total_juros": sim_banco.total_juros,
            })
        except ValueError:
            continue
    comparativo.sort(key=lambda b: b["parcela_inicial"])

    # Vira lead automaticamente se houver contato
    if payload.nome or payload.contato:
        lead_id = leads_repo.upsert_lead(
            nome=payload.nome,
            telefone=payload.contato,
            email=payload.contato if payload.contato and "@" in payload.contato else None,
            origem="simulador",
        )
        descricao_partes = [
            f"Simulou {r.sistema}: {r.valor_imovel:.0f}",
            f"parcela {r.parcela_inicial:.0f}",
        ]
        if payload.bairro:
            descricao_partes.append(f"bairro {payload.bairro}")
        if payload.tipo_imovel:
            descricao_partes.append(payload.tipo_imovel)
        leads_repo.registrar_interacao(
            lead_id,
            tipo="simulacao",
            descricao=" - ".join(descricao_partes),
            metadata={
                "valor_imovel": r.valor_imovel,
                "parcela_inicial": r.parcela_inicial,
                "comprometimento_renda": r.comprometimento_renda,
                "comprometimento_ok": comprometimento_ok,
                "bairro": payload.bairro,
                "tipo_imovel": payload.tipo_imovel,
            },
            referencia_id=sim_id,
        )
        if payload.bairro:
            leads_repo.adicionar_tag(lead_id, f"bairro:{payload.bairro.lower()}")
        if payload.tipo_imovel:
            leads_repo.adicionar_tag(lead_id, f"tipo:{payload.tipo_imovel.lower()}")
        registrar_evento_funil(
            "lead.qualificado",
            origem="simulador",
            lead_id=lead_id,
            payload={
                "simulacao_id": sim_id,
                "score_estimado": 70 if comprometimento_ok else 45,
                "comprometimento_ok": comprometimento_ok,
            },
            idempotency_key=f"lead.qualificado:simulacao:{sim_id}:{lead_id}",
        )

    return {
        "sistema": r.sistema,
        "valor_imovel": r.valor_imovel,
        "entrada": r.entrada,
        "valor_financiado": r.valor_financiado,
        "prazo_meses": r.prazo_meses,
        "taxa_anual": r.taxa_anual,
        "taxa_mensal": round(r.taxa_mensal, 4),
        "parcela_inicial": r.parcela_inicial,
        "parcela_final": r.parcela_final,
        "total_pago": r.total_pago,
        "total_juros": r.total_juros,
        "renda_minima": r.renda_minima,
        "comprometimento_renda": r.comprometimento_renda,
        "comprometimento_ok": comprometimento_ok,
        "primeiras_parcelas": r.primeiras_parcelas,
        "comparativo_bancos": comparativo,
        "fonte_taxas": "Sites oficiais dos bancos (SBPE) - abril/2026",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Avaliacao de imovel (AVM)
# ─────────────────────────────────────────────────────────────────────────────
class AvaliacaoRequest(BaseModel):
    bairro: str = Field(..., min_length=2, max_length=80)
    area_util: float = Field(..., gt=0, le=10_000)
    quartos: int = Field(2, ge=0, le=20)
    suites: int = Field(0, ge=0, le=20)
    vagas: int = Field(0, ge=0, le=20)
    padrao: Literal["simples", "medio", "alto", "luxo"] = "medio"
    estado: Literal["reformado", "bom", "regular", "precisa_reforma"] = "bom"
    idade: Literal["novo", "0_10", "10_20", "20_mais"] = "0_10"
    tem_area_externa: bool = False
    nome: str | None = Field(None, max_length=120)
    contato: str | None = Field(None, max_length=120)


@router.get("/api/avaliacao/bairros")
def bairros() -> dict:
    return {"bairros": BAIRROS_DISPONIVEIS}


@router.post("/api/avaliar-imovel")
def avaliar(payload: AvaliacaoRequest) -> dict:
    try:
        r = avaliacao.avaliar(
            bairro=payload.bairro,
            area_util=payload.area_util,
            quartos=payload.quartos,
            suites=payload.suites,
            vagas=payload.vagas,
            padrao=payload.padrao,
            estado=payload.estado,
            idade=payload.idade,
            tem_area_externa=payload.tem_area_externa,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    texto = avaliacao.texto_editorial(r, payload.bairro)

    with db_session() as conn:
        cur = conn.execute(
            """INSERT INTO avaliacoes
                 (bairro, area_util, quartos, suites, vagas, padrao, estado, idade,
                  valor_central, valor_minimo, valor_maximo, confianca, nome, contato)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                payload.bairro, payload.area_util, payload.quartos, payload.suites,
                payload.vagas, payload.padrao, payload.estado, payload.idade,
                r.valor_central, r.valor_minimo, r.valor_maximo, r.confianca,
                payload.nome, payload.contato,
            ),
        )
        av_id = int(cur.lastrowid)

    registrar_evento_funil(
        "avaliacao.solicitada",
        origem="avaliacao",
        payload={
            "avaliacao_id": av_id,
            "bairro": payload.bairro,
            "valor_central": r.valor_central,
        },
        idempotency_key=f"avaliacao:{av_id}",
    )

    # Vira lead automaticamente (vendedor) se houver contato
    if payload.nome or payload.contato:
        lead_id = leads_repo.upsert_lead(
            nome=payload.nome,
            telefone=payload.contato,
            email=payload.contato if payload.contato and "@" in payload.contato else None,
            origem="avaliacao",
        )
        leads_repo.adicionar_tag(lead_id, "vendedor")
        leads_repo.registrar_interacao(
            lead_id,
            tipo="avaliacao",
            descricao=f"Avaliou imovel em {payload.bairro}: faixa {r.valor_minimo:.0f} - {r.valor_maximo:.0f}",
            metadata={
                "bairro": payload.bairro,
                "area_util": payload.area_util,
                "valor_central": r.valor_central,
                "valor_minimo": r.valor_minimo,
                "valor_maximo": r.valor_maximo,
            },
            referencia_id=av_id,
        )
        registrar_evento_funil(
            "lead.qualificado",
            origem="avaliacao",
            lead_id=lead_id,
            payload={
                "avaliacao_id": av_id,
                "bairro": payload.bairro,
                "score_estimado": 60,
            },
            idempotency_key=f"lead.qualificado:avaliacao:{av_id}:{lead_id}",
        )

    return {
        "bairro_informado": payload.bairro,
        "bairro_normalizado": r.bairro_normalizado,
        "m2_base": r.m2_base,
        "m2_ajustado": r.m2_ajustado,
        "valor_central": r.valor_central,
        "valor_minimo": r.valor_minimo,
        "valor_maximo": r.valor_maximo,
        "fatores": r.fatores_aplicados,
        "confianca": r.confianca,
        "texto": texto,
    }
