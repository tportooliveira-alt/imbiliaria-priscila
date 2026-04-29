"""Rotas publicas: simulador de financiamento e avaliacao de imovel."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app import avaliacao, busca_natural, financiamento, leads as leads_repo
from app.conversas import registrar_evento_funil
from app.db import db_session
from app.m2_vdc import BAIRROS_DISPONIVEIS

router = APIRouter()


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
                "perfil_interno": {
                    "visivel_cliente": False,
                    "origem": "avaliacao",
                    "intencao": "vender",
                    "jornada": "captacao",
                    "urgencia": "normal",
                    "proximo_passo": "avaliar captacao e convidar para conversa",
                },
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
        "mensagem": "Recebido! A Priscila te chama em ate 24h.",
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


@router.post("/api/whatsapp/webhook")
def whatsapp_webhook(payload: WebhookWhatsApp) -> dict:
    """Recebe eventos do Evolution API e registra mensagens recebidas como interacao.

    Valida `EVOLUTION_WEBHOOK_TOKEN` se configurado (header opcional do Evolution
    nao e estavel entre versoes; preferimos secret no path em producao).
    Aqui aceitamos qualquer call e filtramos so eventos relevantes.
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

    remote = (key.get("remoteJid") or "").split("@")[0]
    if not remote:
        return {"ignorado": True, "motivo": "sem remoteJid"}

    # extrai texto (varios formatos do whatsapp)
    msg_content = msg.get("message") or {}
    texto = (
        msg_content.get("conversation")
        or (msg_content.get("extendedTextMessage") or {}).get("text")
        or (msg_content.get("imageMessage") or {}).get("caption")
        or "[midia recebida]"
    )

    push_name = msg.get("pushName") or None

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

    # ─── W2.3: auto-resposta IA opcional ──────────────────────────────────
    import os as _os
    if _os.getenv("WHATSAPP_AUTO_REPLY") != "1":
        return {"ok": True, "lead_id": lead_id, "auto_reply": False}

    from app import dispatcher, whatsapp as wa
    if not wa.disponivel():
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "evolution_indisponivel"}

    # historico das ultimas 5 interacoes do tipo whatsapp_*
    detalhe = leads_repo.detalhar(lead_id) or {}
    historico_raw = (detalhe.get("interacoes") or [])[:6]
    historico: list[dict] = []
    # ordem cronologica (mais antiga primeiro), excluindo a mensagem atual
    for it in reversed(historico_raw):
        tipo = it.get("tipo") or ""
        if tipo == "whatsapp_recebido":
            historico.append({"role": "user", "content": it.get("descricao") or ""})
        elif tipo == "whatsapp_enviado":
            historico.append({"role": "assistant", "content": it.get("descricao") or ""})

    try:
        resposta = dispatcher.responder(str(texto), historico=historico[-5:] or None)
        texto_ia = (resposta.get("resposta") or "").strip()
    except Exception as exc:  # IA indisponivel nao pode quebrar webhook
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "erro_ia": str(exc)[:200]}

    if not texto_ia:
        return {"ok": True, "lead_id": lead_id, "auto_reply": False, "motivo": "ia_vazia"}

    envio = wa.enviar_mensagem(remote, texto_ia)
    if envio.enviado:
        leads_repo.registrar_interacao(
            lead_id,
            tipo="whatsapp_enviado",
            descricao=texto_ia[:500],
            metadata={
                "mensagem_id": envio.mensagem_id,
                "auto_reply": True,
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

# ─────────────────────────────────────────────────────────────────────────────
# Lista de Imóveis para o Site Público
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/api/public/imoveis")
def public_imoveis() -> dict:
    from app.imoveis import listar_imoveis, listar_imagens
    imoveis = listar_imoveis(somente_ativos=True)
    
    # Preparar as imagens principais
    for im in imoveis:
        imgs = listar_imagens(im["id"])
        capa = next((i for i in imgs if i["tipo"] == "capa"), None) or (imgs[0] if imgs else None)
        im["imagem_capa"] = capa["arquivo"] if capa else None
        
    return {"imoveis": imoveis}
