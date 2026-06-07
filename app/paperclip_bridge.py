"""Ponte site -> Paperclip: escala leads quentes como dossie (tarefa no painel).

Quando um lead atinge temperatura "quente", cria uma issue no Paperclip
(atribuida a Ana / Atendimento) com o resumo da conversa. Nunca lanca excecao
para nao quebrar o fluxo de captura/atendimento.
"""
from __future__ import annotations

import json
import os
import urllib.request

from app import leads as leads_repo
from app.db import db_session

PAPERCLIP_API = os.getenv("PAPERCLIP_API", "http://127.0.0.1:3100/api")
PAPERCLIP_CID = os.getenv("PAPERCLIP_CID", "b6e5e386-2a7c-4f26-a129-c06cdfbabcdc")
PAPERCLIP_ASSIGNEE = os.getenv("PAPERCLIP_ASSIGNEE", "a1ff2003-b1c7-46f6-b322-155bfb3c5150")  # Ana
PAPERCLIP_GOAL = os.getenv("PAPERCLIP_GOAL", "065ed32e-c223-49e3-8722-54fbbade8d9c")


def _ja_escalado(interacoes) -> bool:
    return any((i.get("tipo") == "escalado_paperclip") for i in (interacoes or []))


def _montar_dossie(det: dict) -> str:
    nome = det.get("nome") or "Lead"
    tel = det.get("telefone") or ""
    score = det.get("score")
    temp = det.get("temperatura")
    linhas = []
    # interacoes vem em ordem DESC; invertendo para cronologico
    for it in reversed(det.get("interacoes") or []):
        t = it.get("tipo") or ""
        txt = (it.get("descricao") or "")[:180]
        if t == "whatsapp_recebido":
            linhas.append(f"- Cliente: {txt}")
        elif t == "whatsapp_enviado":
            linhas.append(f"- IA: {txt}")
        elif t == "chat":
            linhas.append(f"- (site): {txt}")
    conversa = "\n".join(linhas[-8:]) or "(sem mensagens registradas)"
    return (
        "**Cliente quente captado** — qualificado automaticamente pela Ana (atendimento IA).\n\n"
        f"**Cliente:** {nome} · {tel}\n"
        f"**Score:** {score} · **Temperatura:** {temp} \U0001F525\n\n"
        "**Conversa (resumo):**\n"
        f"{conversa}\n\n"
        "**Próximo passo:** Priscila retornar, propor visita ou enviar opções de imóveis."
    )


def escalar_se_quente(lead_id: int) -> bool:
    """Se o lead estiver quente e ainda nao escalado, cria o dossie no Paperclip."""
    try:
        det = leads_repo.detalhar(lead_id)
        if not det or (det.get("temperatura") or "") != "quente":
            return False
        if _ja_escalado(det.get("interacoes")):
            return False
        nome = det.get("nome") or "Lead"
        body = {
            "title": f"\U0001F525 Cliente quente: {nome}",
            "description": _montar_dossie(det),
            "assigneeAgentId": PAPERCLIP_ASSIGNEE,
            "goalId": PAPERCLIP_GOAL,
            "status": "todo",
        }
        req = urllib.request.Request(
            f"{PAPERCLIP_API}/companies/{PAPERCLIP_CID}/issues",
            data=json.dumps(body).encode(),
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=8)
        # marca como escalado (insert direto, sem recalcular score/temperatura)
        with db_session() as conn:
            conn.execute(
                "INSERT INTO lead_interacoes (lead_id, tipo, descricao, metadata) VALUES (?, ?, ?, ?)",
                (lead_id, "escalado_paperclip", "Dossie enviado ao Paperclip", "{}"),
            )
        return True
    except Exception:
        return False
