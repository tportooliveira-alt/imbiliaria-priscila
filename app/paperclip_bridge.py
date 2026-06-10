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


def _simulacao_financeira(conversa: str) -> str:
    """Extrai (sem inventar) os numeros de financiamento da conversa e simula a parcela.
    Retorna '' se nao for caso de financiamento ou faltar dado. Nunca lanca."""
    if not (conversa or "").strip():
        return ""
    try:
        from app.clients import ClienteClaude
        cli = ClienteClaude("claude-haiku-4-5")
        if not cli.available():
            return ""
        system = (
            "Voce le uma conversa de atendimento imobiliario e extrai SO os numeros que o "
            "CLIENTE realmente disse, para simular financiamento. Responda APENAS um JSON: "
            '{"financiamento": true|false, "valor_imovel": numero|null, "entrada": numero|null, '
            '"renda_mensal": numero|null, "prazo_anos": numero|null, "usa_fgts": true|false|null, '
            '"servidor_publico": true|false|null}. '
            "financiamento=true so se o cliente fala em financiar/parcelar (nao a vista). "
            "Use null quando o cliente NAO disse o numero. NUNCA invente."
        )
        resp = cli.gerar(system, conversa[:4000])
        if resp.fallback or not resp.texto:
            return ""
        import json
        import re
        m = re.search(r"\{.*\}", resp.texto, re.DOTALL)
        if not m:
            return ""
        d = json.loads(m.group(0))
        if not d.get("financiamento"):
            return ""
        valor = d.get("valor_imovel")
        if not valor:
            return ""
        valor = float(valor)
        tem_entrada = d.get("entrada") is not None
        entrada = float(d.get("entrada") or round(valor * 0.2))
        prazo = int(float(d.get("prazo_anos") or 30) * 12)
        renda = d.get("renda_mensal")
        renda = float(renda) if renda else None
        usa_fgts = bool(d.get("usa_fgts"))
        servidor = bool(d.get("servidor_publico"))
        from app import financiamento as fin
        recom = fin.recomendar_financiamento(valor, renda, usa_fgts, servidor)
        rc = recom.get("recomendada")
        if not rc:
            return ""
        taxa = float(rc["taxa_anual"])
        r = fin.simular(
            valor_imovel=valor, entrada=entrada, prazo_meses=prazo,
            taxa_anual=taxa, renda_mensal=renda,
        )

        def _m(v):
            return f"R$ {v:,.0f}".replace(",", ".")

        alts = ", ".join(
            f"{a['nome']} ({a['taxa_anual']}%)" for a in recom.get("alternativas", [])
        )
        linhas = [
            "",
            f"**\U0001F4B0 Simulacao ESTIMATIVA (taxas de {recom.get('atualizado_em', '?')}):**",
            f"- Melhor opcao p/ o perfil: **{rc['nome']} — {taxa:.2f}% a.a.** (SAC)"
            + (f" · outras: {alts}" if alts else ""),
            f"- Imovel {_m(valor)} · entrada {_m(entrada)}"
            + ("" if tem_entrada else " (estimada 20%)")
            + f" · financia {_m(r.valor_financiado)} em {prazo // 12} anos",
            f"- **1ª parcela ~{_m(r.parcela_inicial_com_seguros)}** (com seguros), caindo ate ~{_m(r.parcela_final_com_seguros)}",
            f"- Renda minima sugerida (30%): ~{_m(r.renda_minima)}",
        ]
        if renda:
            ok = renda >= r.renda_minima
            linhas.append(
                f"- Cliente informou renda {_m(renda)} → "
                + ("✅ renda compativel na simulacao" if ok
                   else "⚠️ pode NAO fechar a 30% (ver prazo maior, mais entrada ou co-titular)")
            )
        linhas.append(
            "- _Estimativa — taxa e aprovacao finais dependem da analise do banco._"
        )
        if recom.get("desatualizada"):
            linhas.append(
                f"- ⚠️ Taxas de {recom.get('atualizado_em')} — podem ter mudado, confirmar com o banco."
            )
        return "\n".join(linhas)
    except Exception:
        return ""


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
    simulacao = _simulacao_financeira(conversa)
    return (
        "**Cliente quente captado** — qualificado automaticamente pela Ana (atendimento IA).\n\n"
        f"**Cliente:** {nome} · {tel}\n"
        f"**Score:** {score} · **Temperatura:** {temp} \U0001F525\n\n"
        "**Conversa (resumo):**\n"
        f"{conversa}\n"
        f"{simulacao}\n\n"
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
