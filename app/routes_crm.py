"""Rotas admin de CRM: leads + dashboard."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

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
