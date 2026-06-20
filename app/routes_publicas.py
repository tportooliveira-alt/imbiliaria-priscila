"""Rotas publicas: simulador de financiamento e avaliacao de imovel."""
from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app import avaliacao, busca_natural, financiamento, leads as leads_repo
from app.conversas import registrar_evento_funil
from app.db import db_session
from app.m2_vdc import BAIRROS_DISPONIVEIS

router = APIRouter()
_log = logging.getLogger("imobiliaria.publicas")


def _avisar_priscila_lead_quente(nome: str, remote: str, score: int, ultima_msg: str) -> None:
    """Avisa a Priscila (em background) que um lead esquentou. Loga falha, NUNCA propaga.

    Roda numa thread daemon pra nao segurar a resposta do webhook.
    """
    try:
        import os as _o
        num = _o.getenv("PRISCILA_WHATSAPP", "").strip()
        if not num:
            return
        from app import whatsapp as _wn
        if not _wn.disponivel():
            _log.warning("aviso lead quente nao enviado: whatsapp indisponivel (lead %s)", remote)
            return
        msg = (f"🔥 Lead QUENTE: {nome} ({remote}). Score {score}. "
               f"Última msg: \"{ultima_msg[:120]}\". Atenda rápido — abra o painel.")
        env = _wn.enviar_mensagem(num, msg)
        if not getattr(env, "enviado", False):
            _log.warning("aviso lead quente: envio falhou (lead %s)", remote)
    except Exception:
        _log.exception("erro ao avisar Priscila sobre lead quente (lead %s)", remote)


# ────────────────────────────────────────────────────────────────────────
# Busca em linguagem natural
# ────────────────────────────────────────────────────────────────────────
class BuscaNaturalRequest(BaseModel):
    texto: str = Field(..., min_length=2, max_length=500)
    usar_ia: bool = True
    limite: int = Field(30, ge=1, le=60)


@router.post("/api/busca-natural")
def busca_natural_endpoint(payload: BuscaNaturalRequest) -> dict:
    return busca_natural.buscar(
        payload.texto,
        usar_ia=payload.usar_ia,
        limite=payload.limite,
    )


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
    idade_tomador: int | None = Field(None, ge=18, le=80)
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
            idade_tomador=payload.idade_tomador,
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
                r.parcela_inicial_com_seguros, r.total_pago_com_seguros, r.renda_minima,
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
                idade_tomador=payload.idade_tomador,
            )
            comparativo.append({
                "chave": chave,
                "banco": info["nome"],
                "taxa_anual": info["taxa_anual"],
                "lt_max": info["lt_max"],
                "parcela_inicial": sim_banco.parcela_inicial,
                "parcela_final": sim_banco.parcela_final,
                "parcela_inicial_com_seguros": sim_banco.parcela_inicial_com_seguros,
                "total_pago": sim_banco.total_pago,
                "total_pago_com_seguros": sim_banco.total_pago_com_seguros,
                "total_juros": sim_banco.total_juros,
            })
        except ValueError:
            continue
    comparativo.sort(key=lambda b: b["parcela_inicial_com_seguros"])

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
            f"parcela {r.parcela_inicial_com_seguros:.0f} (com seguros)",
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
                "parcela_inicial_com_seguros": r.parcela_inicial_com_seguros,
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
        "parcela_inicial_com_seguros": r.parcela_inicial_com_seguros,
        "parcela_final_com_seguros": r.parcela_final_com_seguros,
        "total_pago": r.total_pago,
        "total_pago_com_seguros": r.total_pago_com_seguros,
        "total_juros": r.total_juros,
        "total_seguros_estimado": r.total_seguros_estimado,
        "idade_tomador": r.idade_tomador,
        "seguro_mip_inicial": r.seguro_mip_inicial,
        "seguro_dfi_mensal": r.seguro_dfi_mensal,
        "tarifa_adm_mensal": r.tarifa_adm_mensal,
        "renda_minima": r.renda_minima,
        "comprometimento_renda": r.comprometimento_renda,
        "comprometimento_ok": comprometimento_ok,
        "primeiras_parcelas": r.primeiras_parcelas,
        "custos_aquisicao": r.custos_aquisicao,
        "comparativo_bancos": comparativo,
        "fonte_taxas": "Sites oficiais dos bancos (SBPE) - abril/2026",
        "observacoes": [
            "Parcela inclui MIP (seguro morte/invalidez), DFI (seguro do imovel) e tarifa adm.",
            "MIP varia com a idade do tomador — quanto mais velho, mais caro.",
            "Taxa real depende do seu relacionamento com o banco, score de credito e modalidade (FGTS, SBPE, MCMV).",
            "Caixa Pro-Cotista exige 3+ anos de FGTS e nao ter outro imovel; imovel ate R$ 1,5 milhao.",
            "Custos de aquisicao (ITBI 3%, cartorio ~3%) sao pagos UMA vez, fora do financiamento.",
        ],
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
    tipo: Literal["casa", "apartamento", "cobertura", "terreno", "comercial"] = "casa"
    mobilia: Literal["vazio", "semi", "mobiliado"] = "vazio"
    lazer: Literal["sem", "basico", "completo"] = "sem"
    vista: Literal["comum", "livre", "privilegiada"] = "comum"
    andar_alto: bool = False
    elevador: bool = False
    banheiros: int = Field(0, ge=0, le=20)
    area_terreno: float | None = Field(None, gt=0, le=100_000)
    rua: str | None = Field(None, max_length=120)
    ponto_comercial: bool = False
    nome: str | None = Field(None, max_length=120)
    contato: str | None = Field(None, max_length=120)
    prazo_venda: Literal["ja", "3_meses", "6_meses", "12_meses", "pesquisando"] | None = None


@router.get("/api/avaliacao/bairros")
def bairros() -> dict:
    return {"bairros": BAIRROS_DISPONIVEIS}


@router.get("/api/avaliacao/panorama")
def panorama() -> dict:
    """R$/m² REAL por bairro (calibrado) — alimenta o grafico de panorama de mercado."""
    from app.m2_vdc import M2_TERRENO_VDC, M2_VDC

    construido = sorted(
        [{"bairro": k.replace("_", " ").title(), "m2": v} for k, v in M2_VDC.items() if k != "outro"],
        key=lambda x: -x["m2"],
    )
    terreno = sorted(
        [{"bairro": k.replace("_", " ").title(), "m2": v} for k, v in M2_TERRENO_VDC.items()],
        key=lambda x: -x["m2"],
    )
    return {"construido": construido, "terreno": terreno}


@router.get("/api/config")
def config_publica() -> dict:
    """IDs de rastreamento (pixel/analytics) pro front. Vazio = tracking desligado."""
    import os as _os
    return {
        "meta_pixel_id": _os.getenv("META_PIXEL_ID", "").strip(),
        "ga4_id": _os.getenv("GA4_ID", "").strip(),
        "whatsapp": "5577999395511",
    }


@router.get("/api/depoimentos")
def depoimentos_publicos() -> dict:
    """Depoimentos REAIS ativos (prova social) para o site."""
    from app import depoimentos as depoimentos_repo
    itens = depoimentos_repo.listar(somente_ativos=True)
    media = round(sum(d["estrelas"] for d in itens) / len(itens), 1) if itens else 0
    return {"depoimentos": itens, "total": len(itens), "media": media}


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
            tipo=payload.tipo,
            mobilia=payload.mobilia,
            lazer=payload.lazer,
            vista=payload.vista,
            andar_alto=payload.andar_alto,
            elevador=payload.elevador,
            banheiros=payload.banheiros,
            area_terreno=payload.area_terreno,
            rua=payload.rua,
            ponto_comercial=payload.ponto_comercial,
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
        # Qualificador de PRAZO (BANT): vira urgencia + score do lead
        _PRAZO = {
            "ja": ("já quer vender", "alta", 78),
            "3_meses": ("vender em ~3 meses", "alta", 72),
            "6_meses": ("vender em ~6 meses", "normal", 62),
            "12_meses": ("vender em ~1 ano", "baixa", 55),
            "pesquisando": ("só pesquisando preço", "baixa", 45),
        }
        _plabel, _urg, _score = _PRAZO.get(payload.prazo_venda or "", (None, "normal", 60))
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
            descricao=f"Avaliou imovel em {payload.bairro}: faixa {r.valor_minimo:.0f} - {r.valor_maximo:.0f}" + (f" · {_plabel}" if _plabel else ""),
            metadata={
                "perfil_interno": {
                    "visivel_cliente": False,
                    "origem": "avaliacao",
                    "intencao": "vender",
                    "jornada": "captacao",
                    "urgencia": _urg,
                    "proximo_passo": "avaliar captacao e convidar para conversa",
                },
                "prazo_venda": payload.prazo_venda,
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
                "score_estimado": _score,
            },
            idempotency_key=f"lead.qualificado:avaliacao:{av_id}:{lead_id}",
        )

    # Potencial de aluguel — yield mensal sobre o valor de venda estimado.
    # Yield mensal CALIBRADO com 99 alugueis reais de VDC (17/06). NAO e fixo: cai conforme o
    # imovel encarece ('piso do aluguel' — barato ~0,65%/mes, caro ~0,38%). Ver avaliacao.yield_aluguel_mensal.
    yield_mes = avaliacao.yield_aluguel_mensal(r.valor_central, payload.tipo)
    # PISO do aluguel: abaixo de ~R$950/mes nao se aluga no mercado formal de VDC
    # (minimo real R$900; cluster R$1.000-1.200). Imovel muito barato nao cai abaixo disso.
    # Mobiliado aluga mais caro (web: +15-30%). vazio=base, semi +8%, mobiliado +18%.
    f_mob_aluguel = {"vazio": 1.0, "semi": 1.08, "mobiliado": 1.18}.get(payload.mobilia, 1.0)
    PISO_ALUGUEL = 950
    bruto = round(r.valor_central * yield_mes * f_mob_aluguel)
    aluguel_estimado = max(PISO_ALUGUEL, bruto) if payload.tipo != "terreno" else bruto
    # Liquido aprox: -25% (vacancia ~7% + IPTU + condominio), ANTES do IR. So referencia.
    aluguel_liquido = round(aluguel_estimado * 0.75)
    yield_anual_bruto = round(yield_mes * 12 * 100, 2)

    return {
        "bairro_informado": payload.bairro,
        "bairro_normalizado": r.bairro_normalizado,
        "m2_base": r.m2_base,
        "m2_ajustado": r.m2_ajustado,
        "valor_central": r.valor_central,
        "valor_minimo": r.valor_minimo,
        "valor_maximo": r.valor_maximo,
        "aluguel_estimado": aluguel_estimado,
        "aluguel_yield_pct": round(yield_mes * 100, 2),
        "aluguel_yield_anual_pct": yield_anual_bruto,
        "aluguel_liquido_estimado": aluguel_liquido,
        "aluguel_yield_liquido_anual_pct": round(yield_anual_bruto * 0.75, 2),
        "fatores": r.fatores_aplicados,
        "confianca": r.confianca,
        "texto": texto,
    }

# ─────────────────────────────────────────────────────────────────────────────
# Captacao: lead vendedor (anuncie seu imovel)
# ─────────────────────────────────────────────────────────────────────────────
class LeadVendedorRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    telefone: str = Field(..., min_length=8, max_length=30)
    bairro: str | None = Field(None, max_length=80)
    tipo: Literal["Casa", "Apartamento", "Cobertura", "Terreno", "Comercial"] = "Casa"
    area: float | None = Field(None, gt=0, le=100_000)
    quartos: int | None = Field(None, ge=0, le=20)
    valor_pretendido: float | None = Field(None, ge=0, le=1_000_000_000)
    observacoes: str | None = Field(None, max_length=1000)


@router.post("/api/lead-vendedor")
def lead_vendedor(payload: LeadVendedorRequest) -> dict:
    """Recebe quem quer anunciar imovel — vira lead com origem='vendedor'."""
    lead_id = leads_repo.upsert_lead(
        nome=payload.nome,
        telefone=payload.telefone,
        origem="vendedor",
    )
    descricao = f"Quer anunciar {payload.tipo}"
    if payload.bairro:
        descricao += f" em {payload.bairro}"
    if payload.area:
        descricao += f" ({payload.area:.0f} m²)"
    if payload.valor_pretendido:
        descricao += f" — pretende R$ {payload.valor_pretendido:,.0f}".replace(",", ".")

    leads_repo.registrar_interacao(
        lead_id,
        tipo="nota",
        descricao=descricao,
        metadata={
            "tipo_imovel": payload.tipo,
            "bairro": payload.bairro,
            "area": payload.area,
            "quartos": payload.quartos,
            "valor_pretendido": payload.valor_pretendido,
            "observacoes": payload.observacoes,
        },
    )
    leads_repo.adicionar_tag(lead_id, "captacao")
    if payload.bairro:
        leads_repo.adicionar_tag(lead_id, f"bairro:{payload.bairro.lower()}")

    registrar_evento_funil(
        "lead.captacao",
        origem="vendedor",
        lead_id=lead_id,
        payload={
            "tipo": payload.tipo,
            "bairro": payload.bairro,
            "valor_pretendido": payload.valor_pretendido,
        },
        idempotency_key=f"lead.captacao:{lead_id}:{payload.telefone}",
    )

    return {
        "ok": True,
        "lead_id": lead_id,
        "mensagem": "Recebido! 💙 A Priscila vai te chamar no WhatsApp com a avaliacao completa, sem compromisso.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Agendamento de visita
# ─────────────────────────────────────────────────────────────────────────────
class AgendarVisitaRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    telefone: str = Field(..., min_length=8, max_length=30)
    data_preferida: str = Field(..., min_length=8, max_length=10)  # YYYY-MM-DD
    turno: Literal["manha", "tarde", "noite"] = "manha"
    codigo_imovel: str | None = Field(None, max_length=20)
    titulo_imovel: str | None = Field(None, max_length=200)
    bairro: str | None = Field(None, max_length=80)
    observacoes: str | None = Field(None, max_length=1000)


@router.post("/api/agendar-visita")
def agendar_visita(payload: AgendarVisitaRequest) -> dict:
    """Recebe pedido de visita ao imovel e cria/atualiza lead com interacao tipo 'visita'."""
    lead_id = leads_repo.upsert_lead(
        nome=payload.nome,
        telefone=payload.telefone,
        origem="site",
    )

    turno_label = {"manha": "manha", "tarde": "tarde", "noite": "noite"}.get(payload.turno, payload.turno)
    descricao_partes = ["Pediu visita"]
    if payload.codigo_imovel:
        descricao_partes.append(f"imovel {payload.codigo_imovel}")
    if payload.bairro:
        descricao_partes.append(f"bairro {payload.bairro}")
    descricao_partes.append(f"data {payload.data_preferida} ({turno_label})")
    descricao = " - ".join(descricao_partes)

    leads_repo.registrar_interacao(
        lead_id,
        tipo="visita",
        descricao=descricao,
        metadata={
            "data_preferida": payload.data_preferida,
            "turno": payload.turno,
            "codigo_imovel": payload.codigo_imovel,
            "titulo_imovel": payload.titulo_imovel,
            "bairro": payload.bairro,
            "observacoes": payload.observacoes,
        },
    )
    leads_repo.adicionar_tag(lead_id, "agendou_visita")
    if payload.codigo_imovel:
        leads_repo.adicionar_tag(lead_id, f"imovel:{payload.codigo_imovel.lower()}")
    if payload.bairro:
        leads_repo.adicionar_tag(lead_id, f"bairro:{payload.bairro.lower()}")

    # Cria o evento na AGENDA interna (aparece no painel da corretora). Nao quebra a marcacao se falhar.
    try:
        from app import agenda as _agenda
        _hora = {"manha": 9, "tarde": 14, "noite": 19}.get(payload.turno, 9)
        _ini = f"{payload.data_preferida}T{_hora:02d}:00:00-03:00"  # fuso Brasilia
        _fim = f"{payload.data_preferida}T{_hora + 1:02d}:00:00-03:00"
        _tit = f"Visita - {payload.nome}" + (f" ({payload.bairro})" if payload.bairro else "")
        _obs = f"Marcou pelo site. {descricao}." + (f" Obs: {payload.observacoes}" if payload.observacoes else "")
        _agenda.criar(titulo=_tit, inicio=_ini, fim=_fim, tipo="visita", lead_id=lead_id, observacoes=_obs)
    except Exception:
        _log.exception("agendar-visita: lead %s criado mas falhou ao criar evento na agenda", lead_id)

    registrar_evento_funil(
        "visita.agendada",
        origem="site",
        lead_id=lead_id,
        payload={
            "codigo_imovel": payload.codigo_imovel,
            "data_preferida": payload.data_preferida,
            "turno": payload.turno,
            "bairro": payload.bairro,
        },
        idempotency_key=f"visita.agendada:{lead_id}:{payload.data_preferida}:{payload.codigo_imovel or 'sem'}",
    )

    return {
        "ok": True,
        "lead_id": lead_id,
        "mensagem": "Visita registrada! A Priscila confirma no seu WhatsApp em ate 2 horas.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Alerta de busca (C.4) — visitante salva filtro e recebe novidades.
# ─────────────────────────────────────────────────────────────────────────────
class AlertaBuscaRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    contato: str = Field(..., min_length=5, max_length=120)
    filtros: dict = Field(default_factory=dict)


@router.post("/api/alerta-busca", status_code=201)
def alerta_busca(payload: AlertaBuscaRequest) -> dict:
    """Cria alerta para o visitante ser avisado quando um imovel novo bater no filtro dele."""
    if not (payload.filtros or {}):
        raise HTTPException(status_code=400, detail="filtros vazios")

    # Cria/atualiza lead leve
    contato_email = payload.contato if "@" in payload.contato else None
    contato_tel = payload.contato if not contato_email else None
    lead_id = leads_repo.upsert_lead(
        nome=payload.nome,
        telefone=contato_tel,
        email=contato_email,
        origem="site",
    )
    alerta_id = leads_repo.criar_alerta(
        nome=payload.nome,
        contato=payload.contato,
        filtros=payload.filtros,
        lead_id=lead_id,
    )
    leads_repo.registrar_interacao(
        lead_id,
        tipo="nota",
        descricao=f"Criou alerta de busca: {payload.filtros}",
        metadata={"alerta_id": alerta_id, "filtros": payload.filtros},
    )
    leads_repo.adicionar_tag(lead_id, "alerta_busca")
    for chave, valor in (payload.filtros or {}).items():
        if isinstance(valor, str) and valor:
            leads_repo.adicionar_tag(lead_id, f"{chave}:{valor.lower()}")

    return {
        "ok": True,
        "alerta_id": alerta_id,
        "lead_id": lead_id,
        "mensagem": "Pronto! Te aviso assim que aparecer um imovel novo nesse perfil.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Webhook WhatsApp / Evolution API (W2.1)
# ─────────────────────────────────────────────────────────────────────────────
class WebhookWhatsApp(BaseModel):
    """Payload simplificado do Evolution API webhook.

    Aceita o formato `messages.upsert` (entrada de mensagens). Campos
    desconhecidos sao ignorados.
    """
    event: str | None = None
    instance: str | None = None
    data: dict | None = None


def _processar_webhook_whatsapp(payload: WebhookWhatsApp) -> dict:
    """Processa um evento do Evolution API (messages.upsert) e registra a mensagem.

    Função INTERNA — o controle de acesso (segredo) é feito pelas rotas finas
    abaixo. Campos desconhecidos sao ignorados; so eventos relevantes seguem.
    """
    if not payload.event or not payload.data:
        return {"ignorado": True, "motivo": "evento vazio"}

    # so processamos mensagens recebidas pelo lead (fromMe=False)
    if "messages.upsert" not in (payload.event or ""):
        return {"ignorado": True, "motivo": f"evento {payload.event} nao tratado"}

    msg = payload.data or {}
    key = msg.get("key") or {}
    from_me = bool(key.get("fromMe"))
    if from_me:
        return {"ignorado": True, "motivo": "fromMe=true"}

    _jid = key.get("remoteJid") or ""
    # Ignora GRUPOS, broadcast/status e newsletters — nao sao leads de cliente
    # (evita capturar ruido e, no auto-reply, evita responder em grupo/concorrente).
    if ("@g.us" in _jid) or ("broadcast" in _jid) or ("@newsletter" in _jid):
        return {"ignorado": True, "motivo": "grupo/broadcast ignorado"}
    remote = _jid.split("@")[0]
    if not remote:
        return {"ignorado": True, "motivo": "sem remoteJid"}
    # Numero que nao parece telefone real (ex.: LID/grupo com 18 digitos) — ignora.
    _so_digitos = "".join(c for c in remote if c.isdigit())
    if len(_so_digitos) < 10 or len(_so_digitos) > 15:
        # DIAGNOSTICO TEMPORARIO (18/06): pega mensagem real que chega via @lid e e
        # descartada calado. Loga jid cru + nome + texto pra confirmar se contato da
        # Priscila esta caindo aqui. Remover depois de diagnosticar.
        try:
            _mc = msg.get("message") or {}
            _txt_dbg = (
                _mc.get("conversation")
                or (_mc.get("extendedTextMessage") or {}).get("text")
                or (_mc.get("imageMessage") or {}).get("caption")
                or "[sem texto/midia]"
            )
            _log.warning(
                "[DIAG-LID] mensagem DESCARTADA (jid nao-telefone): jid=%r push=%r texto=%r",
                _jid, msg.get("pushName"), str(_txt_dbg)[:120],
            )
        except Exception:
            pass
        return {"ignorado": True, "motivo": "remetente nao e telefone (lid/grupo)"}

    # IDEMPOTENCIA: o Evolution pode re-disparar o MESMO evento (mesmo key.id). Se ja
    # processamos esta mensagem, ignora — evita interacao + resposta duplicadas.
    _wa_msg_id = key.get("id")
    if _wa_msg_id:
        try:
            from app.db import db_session as _dbi
            with _dbi() as _ci:
                _ja = _ci.execute(
                    "SELECT 1 FROM lead_interacoes WHERE tipo='whatsapp_recebido' "
                    "AND json_extract(metadata,'$.mensagem_id')=? LIMIT 1",
                    (_wa_msg_id,),
                ).fetchone()
            if _ja:
                return {"ignorado": True, "motivo": "mensagem duplicada (re-disparo)"}
        except Exception:
            pass

    # extrai texto (varios formatos do whatsapp)
    msg_content = msg.get("message") or {}
    _eh_audio = bool(msg_content.get("audioMessage") or msg_content.get("pttMessage"))
    texto = (
        msg_content.get("conversation")
        or (msg_content.get("extendedTextMessage") or {}).get("text")
        or (msg_content.get("imageMessage") or {}).get("caption")
    )
    if not texto:
        if _eh_audio:
            # tenta transcrever (se houver servico configurado); senao marca como [audio]
            # pra responder com jeito, SEM confabular que "recebeu imagem".
            try:
                from app import whatsapp as _wa_t
                texto = (getattr(_wa_t, "transcrever_audio", lambda *_: None)(msg)) or "[audio]"
            except Exception:
                texto = "[audio]"
        else:
            # Ana ENXERGA: baixa a imagem e o Claude descreve no contexto de lead.
            # Fallback total: se nao for imagem, sem chave ou erro -> volta ao placeholder antigo.
            texto = "[midia recebida]"
            if msg_content.get("imageMessage") or msg_content.get("documentMessage") or msg_content.get("stickerMessage"):
                try:
                    from app import visao as _visao
                    from app import whatsapp as _wa_m
                    _mid = _wa_m.baixar_midia_base64(msg)
                    _desc = _visao.analisar_para_atendimento(_mid[0], _mid[1]) if _mid else None
                    if _desc:
                        _cap = (msg_content.get("imageMessage") or {}).get("caption") or ""
                        texto = (f"{_cap}\n\n" if _cap else "") + (
                            "[O cliente enviou uma imagem. Analise automatica do que aparece nela "
                            "(use com naturalidade, confirme com ele e NAO invente nada alem disto): "
                            f"{_desc}]"
                        )
                except Exception:
                    pass

    push_name = msg.get("pushName") or None

    # ─── SECRETÁRIA (Sofia): só a Priscila (número dela + "Sofia") agenda por WhatsApp ──
    # Intercepta ANTES da Ana — cliente (outro número) nunca cai aqui.
    try:
        from app import secretaria
        if secretaria.acionar(remote, str(texto)):
            res = secretaria.processar(str(texto))
            try:
                import os as _os
                from app import whatsapp as _wa
                if _wa.disponivel():
                    # 1) confirmação ESCRITA sempre (registro pra ela ler)
                    _wa.enviar_mensagem(remote, res["mensagem"])
                    # 2) + ÁUDIO (voz do João, Renato calmo) quando der
                    _voz = _os.getenv("ELEVENLABS_VOICE_ID_JOAO", "").strip()
                    _audio = _wa.gerar_voz(res.get("fala") or res["mensagem"], voice_id=_voz, stability=0.85) if _voz else None
                    if _audio:
                        _wa.enviar_audio(remote, _audio)
            except Exception:
                pass
            return {"secretaria": True, "ok": res.get("ok"), "detalhe": res.get("mensagem")}
    except Exception:
        _log.exception("secretaria (Joao) falhou ao processar mensagem de %s", remote)

    lead_id = leads_repo.upsert_lead(
        nome=push_name,
        telefone=remote,
        origem="whatsapp",
    )
    leads_repo.registrar_interacao(
        lead_id,
        tipo="whatsapp_recebido",
        descricao=str(texto)[:1000],
        metadata={"mensagem_id": key.get("id")},
    )
    # Marca da MINHA mensagem recebida (pro debounce: se uma mais nova chegar enquanto eu
    # processo/espero, eu aborto o envio e deixo o handler da mais nova responder).
    _minha_msg_id = None
    try:
        from app.db import db_session as _dbm
        with _dbm() as _cm:
            _rm = _cm.execute(
                "SELECT MAX(id) AS m FROM lead_interacoes WHERE lead_id=? AND tipo='whatsapp_recebido'",
                (lead_id,),
            ).fetchone()
        _minha_msg_id = _rm["m"] if _rm else None
    except Exception:
        _minha_msg_id = None

    # ─── Qualificacao em segundo plano (mesmo sem responder o cliente) ────
    # Roda o qualify_lead (le bairro/orcamento/prazo no conteudo) e grava
    # score + temperatura no lead, sem enviar nenhuma mensagem.
    try:
        from app.lead import qualify_lead
        _det = leads_repo.detalhar(lead_id) or {}
        _hist: list[dict] = []
        for _it in reversed((_det.get("interacoes") or [])[:6]):
            _t = _it.get("tipo") or ""
            if _t == "whatsapp_recebido":
                _hist.append({"role": "user", "content": _it.get("descricao") or ""})
            elif _t == "whatsapp_enviado":
                _hist.append({"role": "assistant", "content": _it.get("descricao") or ""})
        _snap = qualify_lead(str(texto), history=_hist[-5:] or None)
        _temp = {
            "frio": "frio", "morno": "morno", "quente": "quente",
            "pronto_visita": "quente", "pronto_proposta": "quente",
        }.get(_snap.stage, "frio")
        _temp_anterior = _det.get("temperatura")
        leads_repo.atualizar(lead_id, score=int(_snap.score), temperatura=_temp)
        # lead quente -> escala dossie pro Paperclip (painel) automaticamente
        if _temp == "quente":
            try:
                from app import paperclip_bridge
                paperclip_bridge.escalar_se_quente(lead_id)
            except Exception:
                pass
            # avisa a Priscila SO na transicao pra quente (sem spam), em BACKGROUND
            # (thread daemon — nao segura a resposta do webhook) e logando falha.
            if _temp_anterior != "quente":
                import threading as _th
                _nome_lead = _det.get("nome") or push_name or remote
                _th.Thread(
                    target=_avisar_priscila_lead_quente,
                    args=(_nome_lead, remote, int(_snap.score), str(texto)),
                    daemon=True,
                ).start()
    except Exception:
        _log.exception("qualificacao do lead %s falhou (nao quebra a captura)", lead_id)

    # ─── W2.3: auto-resposta IA opcional ──────────────────────────────────
    import os as _os
    if _os.getenv("WHATSAPP_AUTO_REPLY") != "1":
        return {"ok": True, "lead_id": lead_id, "auto_reply": False}

    # MODO TESTE: se WHATSAPP_TEST_NUMBER estiver setado, so responde a esse numero
    # (valida ao vivo sem responder cliente real). Compara pelos ultimos 8 digitos.
    _test = "".join(c for c in _os.getenv("WHATSAPP_TEST_NUMBER", "") if c.isdigit())
    if _test and remote[-8:] != _test[-8:]:
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "modo_teste_outro_numero"}

    from app import dispatcher, whatsapp as wa
    if not wa.disponivel():
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "evolution_indisponivel"}

    # ── FREIOS DE SEGURANCA (Evolution e nao-oficial: evitar cara de robo / ban) ──
    _txt = str(texto).lower()
    # 1) OPT-OUT: se a pessoa pede pra parar, respeita e NAO responde mais.
    if any(p in _txt for p in ("parar", "pare", "para de", "nao quero", "não quero",
                               "descadastr", "sair da lista", "me tira", "para com isso", "chega")):
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "opt_out_respeitado"}
    # 2) TETO DIARIO (warm-up): nao passar de N auto-respostas por dia (env WHATSAPP_DAILY_CAP).
    try:
        from app.db import db_session as _dbs
        _cap = int(_os.getenv("WHATSAPP_DAILY_CAP", "30"))
        with _dbs() as _c:
            _row = _c.execute(
                "SELECT COUNT(*) AS n FROM lead_interacoes "
                "WHERE tipo='whatsapp_enviado' AND date(criado_em)=date('now','localtime')"
            ).fetchone()
        if _row and _row["n"] >= _cap:
            return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": f"teto_diario_{_cap}"}
    except Exception:
        pass

    # historico SO da conversa RECENTE (janela de horas) — evita vazar conversa de
    # dias atras pro contexto. Bug real: cliente novo "tinha orcamento" de uma
    # conversa velha. So consideramos interacoes dentro de WHATSAPP_HISTORY_HOURS.
    detalhe = leads_repo.detalhar(lead_id) or {}
    import datetime as _dt2
    _janela_h = float(_os.getenv("WHATSAPP_HISTORY_HOURS", "48"))
    _corte = _dt2.datetime.now() - _dt2.timedelta(hours=_janela_h)
    def _recente(_it):
        try:
            return _dt2.datetime.fromisoformat(str(_it.get("criado_em") or "")) >= _corte
        except Exception:
            return False  # sem timestamp valido -> nao arrisca vazar conversa antiga
    historico_raw = [
        it for it in (detalhe.get("interacoes") or [])
        if it.get("tipo") in ("whatsapp_recebido", "whatsapp_enviado") and _recente(it)
    ][:20]
    historico: list[dict] = []
    # ordem cronologica (mais antiga primeiro), excluindo a mensagem atual
    for it in reversed(historico_raw):
        tipo = it.get("tipo") or ""
        if tipo == "whatsapp_recebido":
            historico.append({"role": "user", "content": it.get("descricao") or ""})
        elif tipo == "whatsapp_enviado":
            historico.append({"role": "assistant", "content": it.get("descricao") or ""})

    _nome = push_name or (detalhe.get("nome") if detalhe else None)
    if str(texto).strip() == "[audio]":
        # Ana ainda nao "ouve" audio (falta servico de transcricao) — responde com jeito,
        # SEM inventar, e pede texto / oferece a Priscila. Nada de confabular "imagem".
        _pn = (str(_nome).split()[0] if _nome else "")
        _ola = f"Oi, {_pn}! " if _pn else "Oi! "
        texto_ia = (
            _ola + "Recebi seu áudio aqui 🎧 Pra eu já te adiantar por aqui, você consegue me "
            "mandar por escrito? Se preferir falar mesmo, sem problema — já aviso a Priscila pra "
            "te ouvir e retornar 😊"
        )
        resposta = {"modelo": "regra-audio", "rota": "audio"}
    else:
        try:
            try:
                from app import memoria_lead as _mem
                _ficha = _mem.ficha_viva(lead_id)
            except Exception:
                _ficha = ""
            resposta = dispatcher.responder(
                str(texto), historico=historico[-16:] or None, nome_cliente=_nome,
                memoria_lead=_ficha or None,
            )
            texto_ia = (resposta.get("resposta") or "").strip()
        except Exception as exc:  # IA indisponivel nao pode quebrar webhook
            return {"ok": True, "lead_id": lead_id, "auto_reply": False, "erro_ia": str(exc)[:200]}

    if not texto_ia:
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "ia_vazia"}

    # 3) ATRASO HUMANO: espera alguns segundos antes de enviar (parecer digitacao, nao robo
    #    instantaneo). Configuravel por WHATSAPP_DELAY_MIN/MAX (segundos).
    try:
        import random as _rnd, time as _tm
        _dmin = float(_os.getenv("WHATSAPP_DELAY_MIN", "4"))
        _dmax = float(_os.getenv("WHATSAPP_DELAY_MAX", "12"))
        _tm.sleep(_rnd.uniform(_dmin, max(_dmin, _dmax)))
    except Exception:
        pass

    # DEBOUNCE: se o cliente mandou outra mensagem (mais nova) enquanto eu processava/esperava,
    # NAO envio esta resposta — o handler da mensagem mais nova responde com o contexto completo.
    # Corrige a "resposta dobrada" (texto + imagem em rajada gerava 2 saudacoes).
    if _minha_msg_id:
        try:
            from app.db import db_session as _dbd
            with _dbd() as _cd:
                _ult = _cd.execute(
                    "SELECT MAX(id) AS m FROM lead_interacoes WHERE lead_id=? AND tipo='whatsapp_recebido'",
                    (lead_id,),
                ).fetchone()
            if _ult and _ult["m"] and _ult["m"] > _minha_msg_id:
                return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "mensagem_mais_nova_chegou"}
        except Exception:
            pass

    # Responde por VOZ so quando: o cliente mandou AUDIO **e** ja demonstrou interesse
    # (score >= morno). Caso contrario, entende o audio mas responde por TEXTO (mais barato).
    envio = None
    _por_voz = False
    _score = resposta.get("lead_score") or 0
    _min_voz = int(_os.getenv("WHATSAPP_VOZ_SCORE_MIN", "20"))  # 20 = morno
    if _eh_audio and _score >= _min_voz:
        _audio_voz = wa.gerar_voz(texto_ia)
        if _audio_voz:
            envio = wa.enviar_audio(remote, _audio_voz)
            _por_voz = bool(envio and envio.enviado)
    if envio is None or not envio.enviado:
        envio = wa.enviar_mensagem(remote, texto_ia)
    if envio.enviado:
        leads_repo.registrar_interacao(
            lead_id,
            tipo="whatsapp_enviado",
            descricao=texto_ia[:500],
            metadata={
                "mensagem_id": envio.mensagem_id,
                "auto_reply": True,
                "voz": _por_voz,
                "modelo": resposta.get("modelo"),
                "rota": resposta.get("rota"),
            },
        )

    return {
        "ok": True,
        "lead_id": lead_id,
        "auto_reply": envio.enviado,
        "modelo": resposta.get("modelo"),
    }


# ── Rotas do webhook do WhatsApp (SEGREDO NO PATH) ───────────────────────
# A rota com /{token} é a de PRODUÇÃO (o Evolution aponta pra ela). A rota
# antiga, sem token, só funciona enquanto EVOLUTION_WEBHOOK_TOKEN não existir;
# com o token configurado ela passa a REJEITAR — fecha o furo de mensagem forjada.
@router.post("/api/whatsapp/webhook")
def whatsapp_webhook(payload: WebhookWhatsApp) -> dict:
    import os as _o
    if _o.getenv("EVOLUTION_WEBHOOK_TOKEN", "").strip():
        return {"ignorado": True, "motivo": "rota sem token desativada — use secret path"}
    return _processar_webhook_whatsapp(payload)


@router.post("/api/whatsapp/webhook/{token}")
def whatsapp_webhook_seguro(token: str, payload: WebhookWhatsApp) -> dict:
    import os as _o
    _t = _o.getenv("EVOLUTION_WEBHOOK_TOKEN", "").strip()
    if _t and token != _t:
        raise HTTPException(status_code=401, detail="token invalido")
    return _processar_webhook_whatsapp(payload)


# ────────────────────────────────────────────────────────────────────────
# W5 — Consentimento LGPD (banner publico)
# ────────────────────────────────────────────────────────────────────────
class ConsentimentoPayload(BaseModel):
    tipo: str = Field("contato", max_length=40)
    aceito: bool = True
    email: str | None = Field(None, max_length=200)
    telefone: str | None = Field(None, max_length=40)
    texto_versao: str = Field("v1", max_length=20)


@router.post("/api/consentimento", status_code=201)
def registrar_consentimento_publico(
    payload: ConsentimentoPayload,
    request: Request,
) -> dict:
    from app import documentos as documentos_repo

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")[:300]
    try:
        consent_id = documentos_repo.registrar_consentimento(
            tipo=payload.tipo,
            aceito=payload.aceito,
            email=payload.email,
            telefone=payload.telefone,
            ip=ip,
            user_agent=ua,
            texto_versao=payload.texto_versao,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "id": consent_id}
