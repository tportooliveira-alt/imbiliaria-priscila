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


# Marcadores de CONSULTA (ela PERGUNTA a agenda, em vez de marcar algo novo).
_CONSULTA_MARKERS = (
    "o que tem", "o que tenho", "que tem", "que tenho", "q tem", "tem marcado",
    "tem algo", "tem hoje", "tem amanha", "quais", "minha agenda", "ver agenda",
    "ver a agenda", "como ta", "como esta", "tem compromisso", "tem alguma coisa",
    "me fala", "me diz", "lista",
)


_CREATE_VERBS = ("marca", "marcar", "agend", "remarc", "cancel", "desmarc")


def eh_consulta_agenda(texto: str) -> bool:
    """True se a Priscila esta PERGUNTANDO a agenda (em vez de marcar algo novo).

    Ordem importa: marcador de consulta vence (inclui 'tem marcado'); depois verbo de
    marcar = criacao; por fim pergunta curta de periodo ('e amanha?', 'hoje?').
    """
    t = _sem_acento(_limpar(texto))
    if any(m in t for m in _CONSULTA_MARKERS):
        return True
    if any(v in t for v in _CREATE_VERBS):
        return False
    if ("?" in t or t.startswith("e ")) and any(p in t for p in ("hoje", "amanha", "semana")):
        return True
    return False


def acionar(remote: str, texto: str) -> bool:
    """Só vira o João se: número da Priscila + a palavra 'João' na mensagem."""
    return eh_priscila(remote) and KEYWORD in _sem_acento(texto)


def _limpar(texto: str) -> str:
    """Remove o 'João,' inicial antes de interpretar."""
    return re.sub(r"^\s*jo[aã]o[\s,:!-]*", "", texto or "", flags=re.I).strip()


_SYS = (
    "Você é o João, assistente de agenda da Priscila Vasconcelos. A partir de uma mensagem dela, "
    "extraia UM compromisso e responda APENAS um JSON (nada fora dele):\n"
    '{{"acao":"criar|duvida","titulo":"...","tipo":"visita|reuniao|pessoal|outro",'
    '"inicio":"YYYY-MM-DDTHH:MM:00","fim":"YYYY-MM-DDTHH:MM:00","resumo":"confirmação curta"}}\n'
    "Regras:\n"
    "- O compromisso pode ser QUALQUER COISA da agenda dela: visita de imóvel, reunião, médico, "
    "unha/cabelo, almoço, pessoal — qualquer um. Não limite a imóveis.\n"
    "- tipo: 'visita' (imóvel) / 'reuniao' / 'pessoal' (unha, médico, etc.) / 'outro'.\n"
    "- titulo: descreva o compromisso de forma curta e clara, com o nome/lugar se houver "
    "(ex.: 'Visita - Dona Maria', 'Fazer a unha', 'Médico', 'Reunião com o cliente do apê').\n"
    "- AGORA, em Brasília (UTC-3), é: {agora}. Interprete datas/horas relativas a isso "
    "(ex.: 'sexta às 10h' = a PRÓXIMA sexta-feira às 10:00; 'amanhã' = o dia seguinte).\n"
    "- Duração padrão de 1 hora quando ela não informar o fim.\n"
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


def _dia_brt(iso: str) -> datetime:
    """Converte o 'inicio' do compromisso pra datetime em Brasília (aceita com/sem tz)."""
    dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=BRT)
    return dt.astimezone(BRT)


def consultar(texto: str) -> dict:
    """Responde a agenda de hoje / amanhã / esta semana. Retorna {ok, mensagem, fala}.

    Filtra o periodo em Python (robusto a formato de data), ignora cancelados.
    """
    t = _sem_acento(_limpar(texto))
    agora = datetime.now(BRT)
    if "amanha" in t:
        rotulo = "amanhã"; _alvo = (agora + timedelta(days=1)).date()
        cabe = lambda d: d == _alvo
    elif "semana" in t:
        rotulo = "esta semana"; _ini = agora.date(); _fim = (agora + timedelta(days=7)).date()
        cabe = lambda d: _ini <= d <= _fim
    else:
        rotulo = "hoje"; _alvo = agora.date()
        cabe = lambda d: d == _alvo
    try:
        todos = agenda_repo.listar()
    except Exception as exc:
        m = f"Opa, tentei ver a agenda mas deu um problema aqui ({type(exc).__name__}), dona Priscila."
        return {"ok": False, "mensagem": "🤖 " + m, "fala": m}
    itens = []
    for it in todos:
        if (it.get("status") or "") == "cancelado":
            continue
        try:
            if cabe(_dia_brt(it["inicio"]).date()):
                itens.append(it)
        except Exception:
            continue
    itens.sort(key=lambda it: str(it.get("inicio")))
    if not itens:
        m = f"Sua agenda de {rotulo} tá livre, dona Priscila — nada marcado! 👍"
        return {"ok": True, "mensagem": "🤖 " + m, "fala": m}
    _sem = rotulo == "esta semana"
    _wd = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
    linhas, fala_itens = [], []
    for it in itens:
        dt = _dia_brt(it["inicio"])
        tit = (it.get("titulo") or "Compromisso").strip()
        if _sem:
            linhas.append(f"• {_wd[dt.weekday()]} {dt.strftime('%d/%m %H:%M')} — {tit}")
        else:
            linhas.append(f"• {dt.strftime('%H:%M')} — {tit}")
        _h = f"{dt.hour} horas" if dt.minute == 0 else f"{dt.hour} e {dt.minute:02d}"
        fala_itens.append(f"às {_h}, {tit}")
    m = f"📅 {rotulo.capitalize()}, dona Priscila — {len(itens)} compromisso(s):\n" + "\n".join(linhas)
    fala = f"{rotulo.capitalize()}, dona Priscila, você tem: " + "; ".join(fala_itens) + "."
    return {"ok": True, "mensagem": m, "fala": fala}
