"""Secretária por WhatsApp — a Priscila agenda pelo número PESSOAL dela.

Ela manda do número registrado (env PRISCILA_WHATSAPP): "marca visita com a dona Maria
sexta às 10h" → o sistema interpreta (Claude) e cria o compromisso na agenda, e confirma
de volta no WhatsApp. **Só o número dela** pode (segurança). Fuso de BRASÍLIA (UTC-3).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
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
    # WhatsApp BR varia o "9" extra do celular -> compara os ÚLTIMOS 8 dígitos (parte única do número),
    # igual o gate de auto-reply. Evita falha por 5577999823787 (cadastrado) vs 557799823787 (recebido).
    return r == alvo or r[-8:] == alvo[-8:]


NOME = "João"        # assistente de AGENDA — IA masculina (distinta da Ana, que atende cliente)
KEYWORD = "joao"     # ela diz "João, marca..." (comparado sem acento)


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower()


def eh_comando_agenda(texto: str) -> bool:
    return any(g in _sem_acento(texto) for g in _GATILHOS)


def acionar(remote: str, texto: str) -> bool:
    """Só vira o João se: número da Priscila + a palavra 'João' na mensagem."""
    return eh_priscila(remote) and KEYWORD in _sem_acento(texto)


def _limpar(texto: str) -> str:
    """Remove o 'João,' inicial antes de interpretar."""
    return re.sub(r"^\s*jo[aã]o[\s,:!-]*", "", texto or "", flags=re.I).strip()


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
    """Interpreta e cria o compromisso. Retorna {ok, mensagem (texto), fala (pra áudio do João)}."""
    d = interpretar(_limpar(texto))
    if d.get("acao") != "criar" or not d.get("inicio"):
        base = d.get("resumo") or "Opa, não entendi direito, dona Priscila. Tenta tipo: 'João, marca visita com a dona Maria sexta às 10h'."
        return {"ok": False, "mensagem": "🤖 " + base, "fala": base}
    titulo = (d.get("titulo") or "Compromisso").strip()
    inicio = d["inicio"]
    fim = d.get("fim") or _mais_1h(inicio)
    obs = f'Agendado pela Priscila via WhatsApp (João). Pedido: "{_limpar(texto)[:300]}"'
    try:
        novo = agenda_repo.criar(titulo=titulo, inicio=inicio, fim=fim,
                                 tipo=d.get("tipo") or "visita", observacoes=obs)
    except Exception as exc:
        m = f"Opa, tentei marcar mas deu um problema aqui ({type(exc).__name__}), dona Priscila."
        return {"ok": False, "mensagem": "🤖 " + m, "fala": m}
    msg = f"✅ Fechou, dona Priscila! Marquei: {titulo} — {_fmt_br(inicio)}. Tá na sua agenda 👊"
    fala = (f"Fechou, dona Priscila! Marquei {titulo}, {_fala_data(inicio)}. "
            "Tá na sua agenda, viu? Qualquer coisa é só me chamar.")
    return {"ok": True, "id": novo, "mensagem": msg, "fala": fala}


_MESES = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
          "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
_DIAS_FALA = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]


def _fala_data(iso: str) -> str:
    """Data falada e natural pro áudio (ex.: 'sexta-feira, dia 19 de junho, às 10 horas')."""
    try:
        dt = datetime.fromisoformat(iso)
        hora = f"{dt.hour} horas" if dt.minute == 0 else f"{dt.hour} e {dt.minute:02d}"
        return f"{_DIAS_FALA[dt.weekday()]}, dia {dt.day} de {_MESES[dt.month]}, às {hora}"
    except Exception:
        return iso
