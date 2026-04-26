"""Rotas admin de CRM: leads + dashboard."""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app import conversas as conversas_repo
from app import leads as leads_repo
from app.routes_admin import requer_admin

router = APIRouter(prefix="/api/admin")


class LeadUpdate(BaseModel):
    nome: str | None = Field(None, max_length=120)
    telefone: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=200)
    estagio: str | None = None
    observacoes: str | None = Field(None, max_length=4000)
    responsavel_id: int | None = None


class LeadCreate(BaseModel):
    nome: str | None = Field(None, max_length=120)
    telefone: str | None = Field(None, max_length=40)
    email: str | None = Field(None, max_length=200)
    origem: str = "manual"
    observacoes: str = ""


class TagPayload(BaseModel):
    tag: str = Field(..., min_length=1, max_length=40)


class NotaPayload(BaseModel):
    descricao: str = Field(..., min_length=1, max_length=2000)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/dashboard")
def dashboard(_user=Depends(requer_admin)) -> dict:
    return leads_repo.dashboard()


# ─────────────────────────────────────────────────────────────────────────────
# Leads
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/leads")
def listar(
    estagio: str | None = None,
    temperatura: str | None = None,
    origem: str | None = None,
    busca: str | None = None,
    limit: int = 100,
    offset: int = 0,
    _user=Depends(requer_admin),
) -> dict:
    rows = leads_repo.listar(
        estagio=estagio,
        temperatura=temperatura,
        origem=origem,
        busca=busca,
        limit=min(max(limit, 1), 500),
        offset=max(offset, 0),
    )
    return {"leads": rows, "total": len(rows)}


@router.post("/leads", status_code=201)
def criar(payload: LeadCreate, _user=Depends(requer_admin)) -> dict:
    if not (payload.nome or payload.telefone or payload.email):
        raise HTTPException(status_code=400, detail="informe ao menos nome, telefone ou email")
    lead_id = leads_repo.upsert_lead(
        nome=payload.nome,
        telefone=payload.telefone,
        email=payload.email,
        origem=payload.origem,
    )
    if payload.observacoes:
        leads_repo.atualizar(lead_id, observacoes=payload.observacoes)
    return {"id": lead_id}


@router.get("/leads/{lead_id}")
def detalhar(lead_id: int, _user=Depends(requer_admin)) -> dict:
    lead = leads_repo.detalhar(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead nao encontrado")
    return lead


@router.patch("/leads/{lead_id}")
def atualizar(lead_id: int, payload: LeadUpdate, _user=Depends(requer_admin)) -> dict:
    try:
        ok = leads_repo.atualizar(lead_id, **payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=400, detail="nada para atualizar")
    return {"ok": True}


@router.post("/leads/{lead_id}/notas", status_code=201)
def adicionar_nota(lead_id: int, payload: NotaPayload, user=Depends(requer_admin)) -> dict:
    if not leads_repo.detalhar(lead_id):
        raise HTTPException(status_code=404, detail="lead nao encontrado")
    leads_repo.registrar_interacao(
        lead_id,
        tipo="nota",
        descricao=payload.descricao,
        metadata={"autor": user.get("email")},
    )
    return {"ok": True}


@router.post("/leads/{lead_id}/tags", status_code=201)
def add_tag(lead_id: int, payload: TagPayload, _user=Depends(requer_admin)) -> dict:
    if not leads_repo.detalhar(lead_id):
        raise HTTPException(status_code=404, detail="lead nao encontrado")
    leads_repo.adicionar_tag(lead_id, payload.tag)
    return {"ok": True}


@router.delete("/leads/{lead_id}/tags/{tag}")
def del_tag(lead_id: int, tag: str, _user=Depends(requer_admin)) -> dict:
    leads_repo.remover_tag(lead_id, tag)
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────────
# Operacao IA (telemetria + conversas)
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/operacao-ia/metricas")
def metricas_operacao_ia(horas: int = 24, _user=Depends(requer_admin)) -> dict:
    return conversas_repo.metricas_operacao_ia(horas=horas)


@router.get("/operacao-ia/conversas")
def listar_conversas(
    stage: str | None = None,
    busca: str | None = None,
    limit: int = 50,
    offset: int = 0,
    _user=Depends(requer_admin),
) -> dict:
    return conversas_repo.listar_conversas(
        limit=min(max(limit, 1), 200),
        offset=max(offset, 0),
        stage=stage,
        busca=busca,
    )


@router.get("/operacao-ia/conversas/{conversa_id}")
def detalhe_conversa(conversa_id: int, _user=Depends(requer_admin)) -> dict:
    out = conversas_repo.detalhar_conversa(conversa_id)
    if not out:
        raise HTTPException(status_code=404, detail="conversa nao encontrada")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Co-pilot do lead (C.3) — heurística 100% local, zero LLM.
# Resume o estado, sugere próxima ação, detecta objeções e melhor horário.
# ─────────────────────────────────────────────────────────────────────────────
_PROXIMA_ACAO_POR_ESTAGIO = {
    "novo": "Primeiro contato: ligar ou mandar mensagem no WhatsApp em até 1h. Confirmar nome, bairro de interesse e prazo.",
    "contatado": "Qualificar: quanto pretende investir, prazo de decisão, se já tem entrada/financiamento aprovado.",
    "qualificado": "Mandar 3 imóveis com match >=85% e propor visita conjunta na próxima semana.",
    "visita": "Pós-visita: ligar em 24h para colher impressões e propor próxima ação (segunda visita, contraproposta, alternativa).",
    "proposta": "Negociação ativa: confirmar prazo de resposta com vendedor, reforçar diferenciais, manter cliente aquecido.",
    "fechado": "Pós-venda: agradecer, pedir indicação e reforçar acompanhamento da escritura.",
    "perdido": "Follow-up educacional em 30 dias com 1 novidade do bairro/perfil dele.",
}

_OBJ_PADROES = [
    ("preço alto", ["caro", "alto demais", "ta caro", "fora do orcamento", "fora do orçamento", "passou do que"]),
    ("financiamento", ["banco negou", "nao aprovou", "não aprovou", "score baixo", "sem entrada", "sem fgts"]),
    ("indecisão", ["vou pensar", "depois te falo", "qualquer coisa eu volto", "vou conversar com"]),
    ("concorrência", ["outra imobiliaria", "outro corretor", "vi em outro site"]),
    ("imóvel não bateu", ["nao bateu", "não bateu", "nao gostei", "não gostei", "fora do que queria"]),
    ("prazo longo", ["nao tenho pressa", "ano que vem", "daqui uns meses"]),
]


def _detectar_objecoes(interacoes: list[dict]) -> list[str]:
    texto = " ".join((i.get("descricao") or "").lower() for i in interacoes)
    achadas = []
    for nome, padroes in _OBJ_PADROES:
        if any(p in texto for p in padroes):
            achadas.append(nome)
    return achadas


def _melhor_horario(interacoes: list[dict]) -> str | None:
    horas: list[int] = []
    for i in interacoes:
        ts = i.get("criado_em")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            horas.append(dt.hour)
        except Exception:
            continue
    if not horas:
        return None
    mais_comum, _ = Counter(horas).most_common(1)[0]
    if 6 <= mais_comum < 12:
        faixa = "manhã"
    elif 12 <= mais_comum < 18:
        faixa = "tarde"
    else:
        faixa = "noite"
    return f"{faixa} (~{mais_comum:02d}h)"


def _proximas_perguntas(lead: dict) -> list[str]:
    perguntas = []
    fields = lead.get("fields") or {}  # campo opcional no detalhar
    if not lead.get("telefone") and not lead.get("email"):
        perguntas.append("Qual o melhor canal pra contato? WhatsApp ou email?")
    estagio = lead.get("estagio")
    if estagio in ("novo", "contatado"):
        if not any("orcamento" in (str(f).lower()) for f in fields.values()) and "orcamento" not in (lead.get("observacoes") or "").lower():
            perguntas.append("Qual a faixa de orçamento que você está considerando?")
        perguntas.append("Já tem entrada guardada ou pretende financiar 100%?")
    if estagio in ("qualificado", "visita"):
        perguntas.append("Pode me contar o que mais pesa: bairro, metragem ou diferenciais (elevador, garagem, área externa)?")
    if "vendedor" in (lead.get("tags") or []):
        perguntas.append("Você tem documentação atualizada (matrícula, IPTU em dia)?")
        perguntas.append("Tem urgência na venda ou pode esperar pelo melhor preço?")
    return perguntas[:4]


@router.get("/leads/{lead_id}/copilot")
def copilot_lead(lead_id: int, _user=Depends(requer_admin)) -> dict:
    lead = leads_repo.detalhar(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead nao encontrado")
    interacoes = lead.get("interacoes") or []
    objecoes = _detectar_objecoes(interacoes)
    horario = _melhor_horario(interacoes)
    proxima = _PROXIMA_ACAO_POR_ESTAGIO.get(lead.get("estagio") or "", "Avançar conforme contexto.")
    perguntas = _proximas_perguntas(lead)

    # Resumo curto (1 parágrafo)
    nome = lead.get("nome") or f"Lead #{lead.get('id')}"
    tags = lead.get("tags") or []
    bairro_tag = next((t.split(":", 1)[1] for t in tags if t.startswith("bairro:")), None)
    perfil = "vendedor" if "vendedor" in tags else "comprador"
    resumo_partes = [f"{nome} ({perfil}, {len(interacoes)} interações, score {lead.get('score', 0)}/100)"]
    if bairro_tag:
        resumo_partes.append(f"interesse em {bairro_tag}")
    if objecoes:
        resumo_partes.append("objeções: " + ", ".join(objecoes))
    if horario:
        resumo_partes.append(f"costuma interagir à {horario}")
    resumo = ". ".join(resumo_partes) + "."

    return {
        "lead_id": lead_id,
        "resumo": resumo,
        "proxima_acao": proxima,
        "perguntas_sugeridas": perguntas,
        "objecoes_detectadas": objecoes,
        "melhor_horario": horario,
        "perfil": perfil,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Alertas de busca (C.4) — visitante salva filtro e recebe novidades.
# ─────────────────────────────────────────────────────────────────────────────
class AlertaCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    contato: str = Field(..., min_length=5, max_length=120)  # telefone OU email
    filtros: dict = Field(default_factory=dict)


@router.get("/alertas")
def listar_alertas(_user=Depends(requer_admin)) -> dict:
    return {"alertas": leads_repo.listar_alertas()}


@router.delete("/alertas/{alerta_id}")
def remover_alerta(alerta_id: int, _user=Depends(requer_admin)) -> dict:
    leads_repo.desativar_alerta(alerta_id)
    return {"ok": True}
