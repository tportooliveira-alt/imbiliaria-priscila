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


# ----- Sugestão de resposta IA (Claude) -----
class SugerirRespostaPayload(BaseModel):
    canal: str = Field("whatsapp", pattern="^(whatsapp|email|ligacao)$")
    instrucao_extra: str | None = Field(None, max_length=500)


def _montar_contexto_lead(lead: dict, copilot: dict) -> str:
    linhas = [
        f"Lead: {lead.get('nome') or 'sem nome'} (id {lead.get('id')})",
        f"Estágio: {lead.get('estagio')} | Temperatura: {lead.get('temperatura')} | Score: {lead.get('score')}/100",
        f"Origem: {lead.get('origem')} | Telefone: {lead.get('telefone') or '-'} | Email: {lead.get('email') or '-'}",
    ]
    tags = lead.get("tags") or []
    if tags:
        linhas.append("Tags: " + ", ".join(tags))
    if lead.get("observacoes"):
        linhas.append("Observações internas: " + lead["observacoes"])
    if copilot.get("objecoes_detectadas"):
        linhas.append("Objeções detectadas: " + ", ".join(copilot["objecoes_detectadas"]))
    interacoes = (lead.get("interacoes") or [])[:8]
    if interacoes:
        linhas.append("\nÚltimas interações (mais recente primeiro):")
        for i in interacoes:
            linhas.append(f"  - [{i.get('tipo')}] {i.get('descricao')}")
    return "\n".join(linhas)


@router.post("/leads/{lead_id}/copilot/sugerir-resposta")
def sugerir_resposta(
    lead_id: int,
    payload: SugerirRespostaPayload,
    _user=Depends(requer_admin),
) -> dict:
    lead = leads_repo.detalhar(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead nao encontrado")

    copilot = copilot_lead(lead_id, _user=_user)
    contexto = _montar_contexto_lead(lead, copilot)

    canal = payload.canal
    canal_instrucao = {
        "whatsapp": "Mensagem curta de WhatsApp (máx 4 linhas, tom direto, sem saudação longa).",
        "email": "E-mail profissional, com saudação e assinatura 'Priscila Vasconcelos | CRECI/BA 29.231'.",
        "ligacao": "Roteiro de ligação: 3 bullets curtos do que falar, em ordem.",
    }[canal]

    from app.clients import ClienteClaude
    from app.prompts import PRISCILA_PERSONA

    sistema = (
        PRISCILA_PERSONA
        + "\n\nMODO CO-PILOT: você está escrevendo uma sugestão de resposta para a Priscila enviar pessoalmente. "
        + "Escreva como SE FOSSE a Priscila respondendo. Não explique nada para a Priscila, não faça meta-comentário. "
        + "Só entregue o texto pronto para copiar e colar. Sem aspas, sem prefixo 'Resposta:'.\n\n"
        + f"FORMATO: {canal_instrucao}"
    )

    instrucao = payload.instrucao_extra or ""
    mensagem = (
        f"Contexto do lead:\n{contexto}\n\n"
        f"Próxima ação sugerida pelo sistema: {copilot.get('proxima_acao')}\n"
        + (f"Instrução adicional: {instrucao}\n" if instrucao else "")
        + "\nEscreva a mensagem agora."
    )

    cli = ClienteClaude("claude-sonnet-4-5")
    if not cli.available():
        return {
            "texto": "",
            "canal": canal,
            "fallback": True,
            "mensagem_fallback": "Sugestão IA indisponível (sem ANTHROPIC_API_KEY). Use o resumo do co-pilot para escrever manualmente.",
        }
    resp = cli.gerar(sistema, mensagem)
    return {
        "texto": (resp.texto or "").strip(),
        "canal": canal,
        "modelo": resp.modelo,
        "fallback": resp.fallback,
    }


# ----- Sugestão de resposta IA (Claude) -----
class SugerirRespostaPayload(BaseModel):
    canal: str = Field("whatsapp", pattern="^(whatsapp|email|ligacao)$")
    instrucao_extra: str | None = Field(None, max_length=500)


def _montar_contexto_lead(lead: dict, copilot: dict) -> str:
    linhas = [
        f"Lead: {lead.get('nome') or 'sem nome'} (id {lead.get('id')})",
        f"Estágio: {lead.get('estagio')} | Temperatura: {lead.get('temperatura')} | Score: {lead.get('score')}/100",
        f"Origem: {lead.get('origem')} | Telefone: {lead.get('telefone') or '-'} | Email: {lead.get('email') or '-'}",
    ]
    tags = lead.get("tags") or []
    if tags:
        linhas.append("Tags: " + ", ".join(tags))
    if lead.get("observacoes"):
        linhas.append("Observações internas: " + lead["observacoes"])
    if copilot.get("objecoes_detectadas"):
        linhas.append("Objeções detectadas: " + ", ".join(copilot["objecoes_detectadas"]))
    interacoes = (lead.get("interacoes") or [])[:8]
    if interacoes:
        linhas.append("\nÚltimas interações (mais recente primeiro):")
        for i in interacoes:
            linhas.append(f"  - [{i.get('tipo')}] {i.get('descricao')}")
    return "\n".join(linhas)


@router.post("/leads/{lead_id}/copilot/sugerir-resposta")
def sugerir_resposta(
    lead_id: int,
    payload: SugerirRespostaPayload,
    _user=Depends(requer_admin),
) -> dict:
    lead = leads_repo.detalhar(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead nao encontrado")

    copilot = copilot_lead(lead_id, _user=_user)
    contexto = _montar_contexto_lead(lead, copilot)

    canal = payload.canal
    canal_instrucao = {
        "whatsapp": "Mensagem curta de WhatsApp (máx 4 linhas, tom direto, sem saudação longa).",
        "email": "E-mail profissional, com saudação e assinatura 'Priscila Vasconcelos | CRECI/BA 29.231'.",
        "ligacao": "Roteiro de ligação: 3 bullets curtos do que falar, em ordem.",
    }[canal]

    from app.clients import ClienteClaude
    from app.prompts import PRISCILA_PERSONA

    sistema = (
        PRISCILA_PERSONA
        + "\n\nMODO CO-PILOT: você está escrevendo uma sugestão de resposta para a Priscila enviar pessoalmente. "
        + "Escreva como SE FOSSE a Priscila respondendo. Não explique nada para a Priscila, não faça meta-comentário. "
        + "Só entregue o texto pronto para copiar e colar. Sem aspas, sem prefixo 'Resposta:'.\n\n"
        + f"FORMATO: {canal_instrucao}"
    )

    instrucao = payload.instrucao_extra or ""
    mensagem = (
        f"Contexto do lead:\n{contexto}\n\n"
        f"Próxima ação sugerida pelo sistema: {copilot.get('proxima_acao')}\n"
        + (f"Instrução adicional: {instrucao}\n" if instrucao else "")
        + "\nEscreva a mensagem agora."
    )

    cli = ClienteClaude("claude-sonnet-4-5")
    if not cli.available():
        return {
            "texto": "",
            "canal": canal,
            "fallback": True,
            "mensagem_fallback": "Sugestão IA indisponível (sem ANTHROPIC_API_KEY). Use o resumo do co-pilot para escrever manualmente.",
        }
    resp = cli.gerar(sistema, mensagem)
    return {
        "texto": (resp.texto or "").strip(),
        "canal": canal,
        "modelo": resp.modelo,
        "fallback": resp.fallback,
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


def _imovel_combina_com_filtros(imovel: dict, filtros: dict) -> bool:
    """Heurística simples — todos os filtros presentes precisam casar."""
    if not filtros:
        return False
    bairro = (filtros.get("bairro") or "").strip().lower()
    if bairro and (imovel.get("bairro") or "").strip().lower() != bairro:
        return False
    tipo = (filtros.get("tipo") or "").strip().lower()
    if tipo and (imovel.get("tipo") or "").strip().lower() != tipo:
        return False
    preco = float(imovel.get("preco") or 0)
    if filtros.get("preco_min") and preco < float(filtros["preco_min"]):
        return False
    if filtros.get("preco_max") and preco > float(filtros["preco_max"]):
        return False
    if filtros.get("quartos_min") and int(imovel.get("quartos") or 0) < int(filtros["quartos_min"]):
        return False
    if filtros.get("area_min") and float(imovel.get("area_util") or 0) < float(filtros["area_min"]):
        return False
    return True


@router.get("/alertas/matches")
def alertas_matches(_user=Depends(requer_admin)) -> dict:
    """B.4: cruza alertas ativos com imoveis ativos criados após o alerta.

    Retorna lista de matches sem mutar nada — a Priscila decide se notifica.
    """
    from app import imoveis as imoveis_repo

    alertas = leads_repo.listar_alertas(ativa=True)
    imoveis_ativos = imoveis_repo.listar_imoveis(somente_ativos=True)

    resultado: list[dict] = []
    for a in alertas:
        criado_alerta = a.get("criado_em") or ""
        novos: list[dict] = []
        for im in imoveis_ativos:
            criado_imovel = im.get("criado_em") or im.get("atualizado_em") or ""
            # so propor imoveis cadastrados apos o alerta
            if criado_alerta and criado_imovel and criado_imovel < criado_alerta:
                continue
            if _imovel_combina_com_filtros(im, a.get("filtros") or {}):
                novos.append({
                    "id": im.get("id"),
                    "slug": im.get("slug"),
                    "titulo": im.get("titulo"),
                    "bairro": im.get("bairro"),
                    "preco": im.get("preco"),
                    "quartos": im.get("quartos"),
                })
        if novos:
            resultado.append({
                "alerta_id": a["id"],
                "nome": a["nome"],
                "contato": a["contato"],
                "filtros": a["filtros"],
                "imoveis": novos,
            })
    return {"total": len(resultado), "matches": resultado}


@router.post("/alertas/{alerta_id}/marcar-notificado")
def marcar_alerta_notificado(alerta_id: int, _user=Depends(requer_admin)) -> dict:
    """Incrementa contador apos a Priscila confirmar que enviou ao lead."""
    from datetime import datetime as _dt
    from app.db import db_session

    with db_session() as conn:
        cur = conn.execute(
            "UPDATE alertas_busca SET notificacoes_enviadas = notificacoes_enviadas + 1, "
            "ultima_notificacao = ? WHERE id = ? AND ativa = 1",
            (_dt.utcnow().isoformat(), alerta_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="alerta nao encontrado ou inativo")
    return {"ok": True}


# ─────────────────────────────────────────────────────────────────────────────
# WhatsApp via Evolution API (W2.1) — envio direto pelo admin.
# ─────────────────────────────────────────────────────────────────────────────
class EnvioWhatsAppPayload(BaseModel):
    texto: str = Field(..., min_length=1, max_length=4000)


@router.post("/leads/{lead_id}/whatsapp")
def enviar_whatsapp_lead(
    lead_id: int,
    payload: EnvioWhatsAppPayload,
    _user=Depends(requer_admin),
) -> dict:
    """Envia mensagem WhatsApp ao lead e registra como interacao.

    Quando Evolution API nao esta configurada (sem `EVOLUTION_API_URL`),
    devolve `fallback=True` para a UI cair no `wa.me` do navegador.
    """
    from app import whatsapp

    lead = leads_repo.detalhar(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead nao encontrado")
    telefone = (lead.get("telefone") or "").strip()
    if not telefone:
        raise HTTPException(status_code=400, detail="lead sem telefone cadastrado")

    resultado = whatsapp.enviar_mensagem(telefone, payload.texto)
    if resultado.fallback:
        return {
            "enviado": False,
            "fallback": True,
            "mensagem": "Evolution API nao configurada; use o botao 'Abrir WhatsApp' do navegador.",
        }
    if not resultado.enviado:
        raise HTTPException(status_code=502, detail=resultado.erro or "falha ao enviar")

    leads_repo.registrar_interacao(
        lead_id,
        tipo="whatsapp_enviado",
        descricao=payload.texto[:500],
        metadata={"mensagem_id": resultado.mensagem_id},
    )
    return {
        "enviado": True,
        "fallback": False,
        "mensagem_id": resultado.mensagem_id,
    }


# ─────────────────────────────────────────────────────────────────────────────
# W2.2 — Notificar alerta via WhatsApp (cruza match + dispara mensagem)
# ─────────────────────────────────────────────────────────────────────────────
def _formatar_mensagem_alerta(nome: str, imoveis: list[dict]) -> str:
    """Mensagem amigavel listando ate 3 imoveis novos para o lead."""
    saudacao = f"Oi {nome.split()[0]}! Aqui e a Priscila."
    intro = "Apareceram opcoes novas que combinam com o que voce procura:"
    linhas = []
    for im in imoveis[:3]:
        preco_fmt = f"R$ {float(im.get('preco') or 0):,.0f}".replace(",", ".")
        bairro = im.get("bairro") or ""
        quartos = im.get("quartos") or 0
        titulo = im.get("titulo") or ""
        slug = im.get("slug") or ""
        linha = f"• {titulo} — {bairro}, {quartos}q — {preco_fmt}"
        if slug:
            linha += f"\n  https://priscilavasconcelos.com.br/v3-editorial/#imovel-{slug}"
        linhas.append(linha)
    fechamento = "Quer que eu te mande mais detalhes ou agende uma visita?"
    return f"{saudacao}\n\n{intro}\n\n" + "\n".join(linhas) + f"\n\n{fechamento}"


@router.post("/alertas/{alerta_id}/notificar-whatsapp")
def notificar_alerta_whatsapp(alerta_id: int, _user=Depends(requer_admin)) -> dict:
    """Cruza o alerta com imoveis ativos e dispara WhatsApp pela Evolution.

    Sem Evolution configurada, devolve `fallback=True` com a mensagem pronta
    para a Priscila copiar manualmente.
    """
    from app import imoveis as imoveis_repo
    from app import whatsapp

    alertas = leads_repo.listar_alertas(ativa=True)
    alerta = next((a for a in alertas if a["id"] == alerta_id), None)
    if not alerta:
        raise HTTPException(status_code=404, detail="alerta nao encontrado ou inativo")

    criado_alerta = alerta.get("criado_em") or ""
    imoveis_ativos = imoveis_repo.listar_imoveis(somente_ativos=True)
    matches = []
    for im in imoveis_ativos:
        criado_imovel = im.get("criado_em") or im.get("atualizado_em") or ""
        if criado_alerta and criado_imovel and criado_imovel < criado_alerta:
            continue
        if _imovel_combina_com_filtros(im, alerta.get("filtros") or {}):
            matches.append(im)
    if not matches:
        raise HTTPException(status_code=400, detail="nenhum imovel novo combina com este alerta")

    mensagem = _formatar_mensagem_alerta(alerta["nome"], matches)
    resultado = whatsapp.enviar_mensagem(alerta["contato"], mensagem)

    if resultado.fallback:
        return {
            "enviado": False,
            "fallback": True,
            "mensagem": mensagem,
            "imoveis_id": [im["id"] for im in matches[:3]],
        }
    if not resultado.enviado:
        raise HTTPException(status_code=502, detail=resultado.erro or "falha ao enviar")

    # incrementa contador igual ao marcar-notificado
    from datetime import datetime as _dt
    from app.db import db_session
    with db_session() as conn:
        conn.execute(
            "UPDATE alertas_busca SET notificacoes_enviadas = notificacoes_enviadas + 1, "
            "ultima_notificacao = ? WHERE id = ?",
            (_dt.utcnow().isoformat(), alerta_id),
        )
        conn.commit()

    # registra interacao no lead vinculado, se houver
    if alerta.get("lead_id"):
        leads_repo.registrar_interacao(
            int(alerta["lead_id"]),
            tipo="whatsapp_enviado",
            descricao=f"[Alerta de busca] {len(matches)} imoveis enviados",
            metadata={"alerta_id": alerta_id, "mensagem_id": resultado.mensagem_id},
        )

    return {
        "enviado": True,
        "fallback": False,
        "mensagem_id": resultado.mensagem_id,
        "imoveis_enviados": len(matches[:3]),
    }


# ─────────────────────────────────────────────────────────────────────────────
# W4 — Agenda (visitas, reunioes, follow-ups)
# ─────────────────────────────────────────────────────────────────────────────
class AgendaCriar(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    inicio: str = Field(..., description="ISO8601 UTC")
    fim: str = Field(..., description="ISO8601 UTC")
    tipo: str = "visita"
    lead_id: int | None = None
    imovel_id: int | None = None
    observacoes: str | None = Field(None, max_length=2000)


class AgendaAtualizar(BaseModel):
    titulo: str | None = Field(None, min_length=2, max_length=200)
    inicio: str | None = None
    fim: str | None = None
    tipo: str | None = None
    status: str | None = None
    lead_id: int | None = None
    imovel_id: int | None = None
    observacoes: str | None = Field(None, max_length=2000)


@router.post("/agenda", status_code=201)
def agenda_criar(payload: AgendaCriar, _user=Depends(requer_admin)) -> dict:
    from app import agenda as agenda_repo
    try:
        novo_id = agenda_repo.criar(
            titulo=payload.titulo,
            inicio=payload.inicio,
            fim=payload.fim,
            tipo=payload.tipo,
            lead_id=payload.lead_id,
            imovel_id=payload.imovel_id,
            observacoes=payload.observacoes or "",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    item = agenda_repo.detalhar(novo_id)
    return {"ok": True, "item": item}


@router.get("/agenda")
def agenda_listar(
    inicio_de: str | None = None,
    inicio_ate: str | None = None,
    status: str | None = None,
    lead_id: int | None = None,
    _user=Depends(requer_admin),
) -> dict:
    from app import agenda as agenda_repo
    try:
        items = agenda_repo.listar(
            inicio_de=inicio_de, inicio_ate=inicio_ate,
            status=status, lead_id=lead_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"total": len(items), "items": items}


@router.get("/agenda/{item_id}")
def agenda_detalhe(item_id: int, _user=Depends(requer_admin)) -> dict:
    from app import agenda as agenda_repo
    item = agenda_repo.detalhar(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="compromisso nao encontrado")
    return item


@router.patch("/agenda/{item_id}")
def agenda_atualizar(item_id: int, payload: AgendaAtualizar, _user=Depends(requer_admin)) -> dict:
    from app import agenda as agenda_repo
    try:
        item = agenda_repo.atualizar(item_id, **payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not item:
        raise HTTPException(status_code=404, detail="compromisso nao encontrado")
    return item


@router.delete("/agenda/{item_id}", status_code=204)
def agenda_remover(item_id: int, _user=Depends(requer_admin)) -> None:
    from app import agenda as agenda_repo
    if not agenda_repo.remover(item_id):
        raise HTTPException(status_code=404, detail="compromisso nao encontrado")


@router.post("/agenda/lembretes/enviar")
def agenda_enviar_lembretes(janela_horas: int = 24, _user=Depends(requer_admin)) -> dict:
    """Envia WhatsApp para leads com compromisso nas proximas N horas.

    Sem Evolution configurada, retorna lista de pendentes para acionar manualmente.
    """
    from app import agenda as agenda_repo
    from app import whatsapp

    pendentes = agenda_repo.lembretes_a_enviar(janela_horas=janela_horas)
    if not pendentes:
        return {"total": 0, "enviados": 0, "fallback": False, "items": []}

    if not whatsapp.disponivel():
        return {
            "total": len(pendentes),
            "enviados": 0,
            "fallback": True,
            "items": pendentes,
        }

    enviados = 0
    detalhes = []
    for item in pendentes:
        if not item.get("lead_id"):
            continue
        lead = leads_repo.detalhar(int(item["lead_id"]))
        telefone = (lead or {}).get("telefone") or ""
        if not telefone:
            continue
        inicio_dt = datetime.fromisoformat(str(item["inicio"]).replace("Z", "+00:00"))
        msg = (
            f"Oi {(lead.get('nome') or '').split()[0] if lead.get('nome') else ''}! "
            f"Lembrete: {item['titulo']} amanha as "
            f"{inicio_dt.strftime('%H:%M')}. Confirma pra mim? — Priscila"
        ).strip()
        resp = whatsapp.enviar_mensagem(telefone, msg)
        if resp.enviado:
            agenda_repo.marcar_lembrete_enviado(int(item["id"]))
            leads_repo.registrar_interacao(
                int(lead["id"]),
                tipo="whatsapp_enviado",
                descricao=f"[Lembrete agenda] {item['titulo']}",
                metadata={"agenda_id": item["id"], "mensagem_id": resp.mensagem_id},
            )
            enviados += 1
            detalhes.append({"id": item["id"], "ok": True})
        else:
            detalhes.append({"id": item["id"], "ok": False, "erro": resp.erro})
    return {
        "total": len(pendentes),
        "enviados": enviados,
        "fallback": False,
        "items": detalhes,
    }


# ─────────────────────────────────────────────────────────────────────────────
# W5 — Documentos do lead/imovel + Consentimentos LGPD + Proposta PDF
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import File, Form, UploadFile  # noqa: E402
from fastapi.responses import FileResponse, Response  # noqa: E402

from app import documentos as documentos_repo  # noqa: E402
from app import imoveis as imoveis_repo  # noqa: E402
from app import proposta_pdf  # noqa: E402


@router.post("/documentos", status_code=201)
async def doc_upload(
    arquivo: UploadFile = File(...),
    lead_id: int | None = Form(None),
    imovel_id: int | None = Form(None),
    tipo: str = Form("outro"),
    observacoes: str = Form(""),
    _user=Depends(requer_admin),
) -> dict:
    conteudo = await arquivo.read()
    try:
        doc = documentos_repo.salvar(
            nome_original=arquivo.filename or "arquivo",
            conteudo=conteudo,
            mime=arquivo.content_type,
            lead_id=lead_id,
            imovel_id=imovel_id,
            tipo=tipo,
            observacoes=observacoes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    doc.pop("caminho", None)
    return {"ok": True, "documento": doc}


@router.get("/documentos")
def doc_listar(
    lead_id: int | None = None,
    imovel_id: int | None = None,
    _user=Depends(requer_admin),
) -> dict:
    items = documentos_repo.listar(lead_id=lead_id, imovel_id=imovel_id)
    return {"total": len(items), "items": items}


@router.get("/documentos/{doc_id}/download")
def doc_download(doc_id: int, _user=Depends(requer_admin)) -> FileResponse:
    info = documentos_repo.detalhar(doc_id)
    if not info:
        raise HTTPException(status_code=404, detail="documento nao encontrado")
    return FileResponse(
        info["caminho"],
        media_type=info.get("mime") or "application/octet-stream",
        filename=info["nome_original"],
    )


@router.delete("/documentos/{doc_id}", status_code=204)
def doc_remover(doc_id: int, _user=Depends(requer_admin)) -> None:
    if not documentos_repo.remover(doc_id):
        raise HTTPException(status_code=404, detail="documento nao encontrado")


@router.get("/consentimentos")
def consentimentos_listar(
    lead_id: int | None = None,
    email: str | None = None,
    _user=Depends(requer_admin),
) -> dict:
    items = documentos_repo.listar_consentimentos(lead_id=lead_id, email=email)
    return {"total": len(items), "items": items}


class PropostaPayload(BaseModel):
    imovel_id: int
    lead_id: int
    valor_proposta: float = Field(..., gt=0)
    forma_pagamento: str = Field("Financiamento bancario", max_length=120)
    condicoes: str = Field("", max_length=4000)
    salvar_documento: bool = True


@router.post("/proposta-pdf")
def gerar_proposta(payload: PropostaPayload, _user=Depends(requer_admin)) -> Response:
    imovel = imoveis_repo.buscar_por_id(payload.imovel_id)
    if not imovel:
        raise HTTPException(status_code=404, detail="imovel nao encontrado")
    lead = leads_repo.detalhar(payload.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="lead nao encontrado")

    pdf_bytes = proposta_pdf.gerar_proposta_pdf(
        imovel=imovel,
        lead=lead,
        valor_proposta=payload.valor_proposta,
        forma_pagamento=payload.forma_pagamento,
        condicoes=payload.condicoes,
    )

    if payload.salvar_documento:
        try:
            documentos_repo.salvar(
                nome_original=f"proposta_{payload.imovel_id}_{payload.lead_id}.pdf",
                conteudo=pdf_bytes,
                mime="application/pdf",
                lead_id=payload.lead_id,
                imovel_id=payload.imovel_id,
                tipo="proposta",
                observacoes=f"Valor: R$ {payload.valor_proposta:.2f}",
            )
        except ValueError:
            pass

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="proposta_{payload.imovel_id}_'
                f'{payload.lead_id}.pdf"'
            ),
        },
    )


# ============================================================
# W7 — Financeiro (comissoes, metas, contas)
# ============================================================
from app import financeiro as financeiro_repo  # noqa: E402


class ComissaoPayload(BaseModel):
    descricao: str = Field(..., min_length=2, max_length=200)
    valor_venda: float = Field(..., gt=0)
    percentual: float = Field(0, ge=0, le=100)
    valor_comissao: float | None = None
    lead_id: int | None = None
    imovel_id: int | None = None
    corretor_email: str | None = None
    status: str = Field("previsto", pattern="^(previsto|recebido|cancelado)$")
    data_venda: str | None = None
    data_recebimento: str | None = None


class ComissaoUpdate(BaseModel):
    descricao: str | None = None
    valor_venda: float | None = None
    percentual: float | None = None
    valor_comissao: float | None = None
    lead_id: int | None = None
    imovel_id: int | None = None
    corretor_email: str | None = None
    status: str | None = Field(None, pattern="^(previsto|recebido|cancelado)$")
    data_venda: str | None = None
    data_recebimento: str | None = None


class MetaPayload(BaseModel):
    ano: int = Field(..., ge=2020, le=2100)
    mes: int = Field(..., ge=1, le=12)
    meta_vendas: float = Field(0, ge=0)
    meta_comissao: float = Field(0, ge=0)
    corretor_email: str | None = None


class ContaPayload(BaseModel):
    tipo: str = Field(..., pattern="^(pagar|receber)$")
    descricao: str = Field(..., min_length=2, max_length=200)
    categoria: str = "geral"
    valor: float = Field(..., gt=0)
    vencimento: str
    pago: bool = False
    data_pagamento: str | None = None
    observacoes: str | None = None


class ContaUpdate(BaseModel):
    tipo: str | None = Field(None, pattern="^(pagar|receber)$")
    descricao: str | None = None
    categoria: str | None = None
    valor: float | None = None
    vencimento: str | None = None
    pago: bool | None = None
    data_pagamento: str | None = None
    observacoes: str | None = None


# --- Comissoes ---
@router.post("/financeiro/comissoes")
def criar_comissao(payload: ComissaoPayload, _admin=Depends(requer_admin)):
    return financeiro_repo.criar_comissao(payload.model_dump())


@router.get("/financeiro/comissoes")
def listar_comissoes(
    status: str | None = None,
    corretor: str | None = None,
    inicio: str | None = None,
    fim: str | None = None,
    _admin=Depends(requer_admin),
):
    return financeiro_repo.listar_comissoes(
        status=status, corretor=corretor, inicio=inicio, fim=fim
    )


@router.put("/financeiro/comissoes/{cid}")
def atualizar_comissao(cid: int, payload: ComissaoUpdate, _admin=Depends(requer_admin)):
    dados = {k: v for k, v in payload.model_dump().items() if v is not None}
    res = financeiro_repo.atualizar_comissao(cid, dados)
    if res is None:
        raise HTTPException(404, "Comissao nao encontrada")
    return res


@router.delete("/financeiro/comissoes/{cid}")
def excluir_comissao(cid: int, _admin=Depends(requer_admin)):
    if not financeiro_repo.excluir_comissao(cid):
        raise HTTPException(404, "Comissao nao encontrada")
    return {"ok": True}


# --- Metas ---
@router.post("/financeiro/metas")
def upsert_meta(payload: MetaPayload, _admin=Depends(requer_admin)):
    return financeiro_repo.upsert_meta(payload.model_dump())


@router.get("/financeiro/metas")
def listar_metas(ano: int | None = None, _admin=Depends(requer_admin)):
    return financeiro_repo.listar_metas(ano=ano)


@router.delete("/financeiro/metas/{mid}")
def excluir_meta(mid: int, _admin=Depends(requer_admin)):
    if not financeiro_repo.excluir_meta(mid):
        raise HTTPException(404, "Meta nao encontrada")
    return {"ok": True}


# --- Contas ---
@router.post("/financeiro/contas")
def criar_conta(payload: ContaPayload, _admin=Depends(requer_admin)):
    return financeiro_repo.criar_conta(payload.model_dump())


@router.get("/financeiro/contas")
def listar_contas(
    tipo: str | None = None,
    pago: bool | None = None,
    inicio: str | None = None,
    fim: str | None = None,
    _admin=Depends(requer_admin),
):
    return financeiro_repo.listar_contas(tipo=tipo, pago=pago, inicio=inicio, fim=fim)


@router.put("/financeiro/contas/{cid}")
def atualizar_conta(cid: int, payload: ContaUpdate, _admin=Depends(requer_admin)):
    dados = {k: v for k, v in payload.model_dump().items() if v is not None}
    res = financeiro_repo.atualizar_conta(cid, dados)
    if res is None:
        raise HTTPException(404, "Conta nao encontrada")
    return res


@router.post("/financeiro/contas/{cid}/pagar")
def marcar_paga(cid: int, _admin=Depends(requer_admin)):
    res = financeiro_repo.marcar_conta_paga(cid)
    if res is None:
        raise HTTPException(404, "Conta nao encontrada")
    return res


@router.delete("/financeiro/contas/{cid}")
def excluir_conta(cid: int, _admin=Depends(requer_admin)):
    if not financeiro_repo.excluir_conta(cid):
        raise HTTPException(404, "Conta nao encontrada")
    return {"ok": True}


# --- Dashboard ---
@router.get("/financeiro/dashboard")
def dashboard_financeiro(
    ano: int | None = None,
    mes: int | None = None,
    _admin=Depends(requer_admin),
):
    return financeiro_repo.dashboard(ano=ano, mes=mes)

