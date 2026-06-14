"""Secretária por WhatsApp — a Priscila agenda pelo número PESSOAL dela.

Ela manda do número registrado (env PRISCILA_WHATSAPP): "marca visita com a dona Maria
sexta às 10h" → o sistema interpreta (Claude) e cria o compromisso na agenda, e confirma
de volta no WhatsApp. **Só o número dela** pode (segurança). Fuso de BRASÍLIA (UTC-3).
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timedelta, timezone

from app import agenda as agenda_repo
from app.clients import ClienteClaude

BRT = timezone(timedelta(hours=-3))
_GATILHOS = ("marca", "marcar", "agend", "remarc", "cancel", "compromisso", "visita", "reuni", "horário", "horario")


def _digitos(s: str) -> str:
    return "".join(c for c in (s or "") if c.isdigit())


def eh_priscila(remote: str) -> bool:
    """True se o remetente é o número pessoal registrado da Priscila (PRISCILA_WHATSAPP)."""
    alvo = _digitos(os.getenv("PRISCILA_WHATSAPP", ""))
    r = _digitos(remote)
    if not alvo or not r:
        return False
    return r == alvo or r[-11:] == alvo[-11:]  # tolera DDI/variações nos últimos 11 dígitos


KEYWORD = "sofia"  # palavra-chave (decisão do Thiago): ela diz "Sofia, marca..."


def eh_comando_agenda(texto: str) -> bool:
    t = (texto or "").lower()
    return any(g in t for g in _GATILHOS)


def acionar(remote: str, texto: str) -> bool:
    """Só vira secretária se: número da Priscila + palavra-chave 'Sofia' na mensagem."""
    return eh_priscila(remote) and KEYWORD in (texto or "").lower()


def _limpar(texto: str) -> str:
    """Remove o 'Sofia,' inicial antes de interpretar."""
    return re.sub(r"^\s*sofia[\s,:!-]*", "", texto or "", flags=re.I).strip()


_SYS = (
    "Você é a secretária de agenda da corretora Priscila Vasconcelos. A partir de uma mensagem "
    "dela, extraia UM agendamento e responda APENAS um JSON (nada fora dele):\n"
    '{{"acao":"criar|duvida","titulo":"...","tipo":"visita|reuniao|captacao|followup",'
    '"inicio":"YYYY-MM-DDTHH:MM:00","fim":"YYYY-MM-DDTHH:MM:00","resumo":"confirmação curta"}}\n'
    "Regras:\n"
    "- AGORA, em Brasília (UTC-3), é: {agora}. Interprete datas/horas relativas a isso "
    "(ex.: 'sexta às 10h' = a PRÓXIMA sexta-feira às 10:00).\n"
    "- Duração padrão de 1 hora quando ela não informar o fim.\n"
    "- titulo: inclua o nome da pessoa se houver (ex.: 'Visita - Dona Maria').\n"
    "- Se faltar data ou hora pra entender, use acao='duvida' e em 'resumo' pergunte o que faltou.\n"
    "- Sempre horário de Brasília, ISO sem timezone."
)


def interpretar(texto: str) -> dict:
    agora = datetime.now(BRT).strftime("%A %d/%m/%Y %H:%M")
    r = ClienteClaude().gerar(_SYS.format(agora=agora), texto)
    m = re.search(r"\{.*\}", (r.texto or ""), re.S)
    if not m:
        return {"acao": "duvida", "resumo": "Não entendi. Tenta tipo: 'marca visita com a dona Maria sexta 10h'."}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {"acao": "duvida", "resumo": "Não consegui ler a data/hora. Manda com o dia e a hora, por favor."}


def _mais_1h(iso: str) -> str:
    try:
        return (datetime.fromisoformat(iso) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:00")
    except Exception:
        return iso


def _fmt_br(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        return f"{dias[dt.weekday()]}, {dt.strftime('%d/%m às %H:%M')}"
    except Exception:
        return iso


def processar(texto: str) -> dict:
    """Interpreta e cria o compromisso. Retorna {ok, mensagem} pra confirmar pra Priscila."""
    d = interpretar(_limpar(texto))
    if d.get("acao") != "criar" or not d.get("inicio"):
        return {"ok": False, "mensagem": "🤖 " + (d.get("resumo")
                or "Não entendi o agendamento. Ex.: 'marca visita com a dona Maria sexta às 10h'.")}
    titulo = (d.get("titulo") or "Compromisso").strip()
    inicio = d["inicio"]
    fim = d.get("fim") or _mais_1h(inicio)
    try:
        novo = agenda_repo.criar(titulo=titulo, inicio=inicio, fim=fim,
                                 tipo=d.get("tipo") or "visita",
                                 observacoes="(agendado por WhatsApp pela Priscila)")
    except Exception as exc:
        return {"ok": False, "mensagem": f"🤖 Tentei marcar mas deu erro ({type(exc).__name__})."}
    return {"ok": True, "id": novo,
            "mensagem": f"✅ Marquei: *{titulo}* — {_fmt_br(inicio)}. Tá na sua agenda! 📅"}
