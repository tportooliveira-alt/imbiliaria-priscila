"""Agente 24/7 para lembretes de agenda via WhatsApp.

Roda fora do processo web para que o site continue leve e para que o VPS
possa reiniciar o agente automaticamente via systemd.
"""
from __future__ import annotations

import logging
import os
import signal
import time

from dotenv import load_dotenv

from app import agenda as agenda_repo
from app import leads as leads_repo
from app import whatsapp
from app.db import init_db

load_dotenv()

LOG_LEVEL = os.getenv("AGENTE_LOG_LEVEL", "INFO").upper()
INTERVALO_SEGUNDOS = int(os.getenv("AGENTE_LEMBRETES_INTERVALO_SEGUNDOS", "900"))
JANELA_HORAS = int(os.getenv("AGENTE_LEMBRETES_JANELA_HORAS", "24"))

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [agente_lembretes] %(message)s",
)
log = logging.getLogger(__name__)
parar = False


def _parar(_signum, _frame) -> None:
    global parar
    parar = True


def executar_ciclo() -> dict:
    """Envia lembretes pendentes e retorna resumo do ciclo."""
    pendentes = agenda_repo.lembretes_a_enviar(janela_horas=JANELA_HORAS)
    if not pendentes:
        return {"total": 0, "enviados": 0, "fallback": False}

    if not whatsapp.disponivel():
        log.warning(
            "Evolution API nao configurada; %s lembrete(s) ficaram pendentes.",
            len(pendentes),
        )
        return {"total": len(pendentes), "enviados": 0, "fallback": True}

    enviados = 0
    falhas = 0
    for item in pendentes:
        lead_id = item.get("lead_id")
        if not lead_id:
            falhas += 1
            continue

        lead = leads_repo.detalhar(int(lead_id)) or {}
        telefone = lead.get("telefone") or ""
        if not telefone:
            falhas += 1
            continue

        nome_curto = (lead.get("nome") or "").split()
        saudacao = f" {nome_curto[0]}" if nome_curto else ""
        msg = (
            f"Oi{saudacao}! Lembrete: {item['titulo']} esta chegando. "
            "Confirma pra mim? - Priscila"
        )
        resp = whatsapp.enviar_mensagem(telefone, msg)
        if resp.enviado:
            agenda_repo.marcar_lembrete_enviado(int(item["id"]))
            leads_repo.registrar_interacao(
                int(lead_id),
                tipo="whatsapp_enviado",
                descricao=f"[Agente lembrete agenda] {item['titulo']}",
                metadata={"agenda_id": item["id"], "mensagem_id": resp.mensagem_id},
            )
            enviados += 1
        else:
            falhas += 1
            log.warning("Falha ao enviar lembrete agenda_id=%s: %s", item["id"], resp.erro)

    return {"total": len(pendentes), "enviados": enviados, "falhas": falhas, "fallback": False}


def enviar_lembretes_priscila_1h() -> dict:
    """~1h antes de cada compromisso, lembra a PRISCILA no WhatsApp dela (pra nao perder horario)."""
    import datetime as _dt

    pri = "".join(c for c in os.getenv("PRISCILA_WHATSAPP", "") if c.isdigit())
    janela = int(os.getenv("AGENTE_LEMBRETE_PRISCILA_MIN", "60"))
    itens = agenda_repo.lembretes_1h_priscila(janela_min=janela)
    if not itens:
        return {"total": 0, "enviados": 0}
    if not pri or not whatsapp.disponivel():
        log.warning("Lembrete 1h Priscila: %s pendente(s) sem numero/Evolution.", len(itens))
        return {"total": len(itens), "enviados": 0, "fallback": True}

    enviados = 0
    for item in itens:
        hora = ""
        try:  # horario em Brasilia (UTC-3)
            ini = _dt.datetime.fromisoformat(str(item["inicio"]).replace("Z", "+00:00"))
            if ini.tzinfo is None:
                ini = ini.replace(tzinfo=_dt.timezone.utc)
            hora = ini.astimezone(_dt.timezone(_dt.timedelta(hours=-3))).strftime("%H:%M")
        except Exception:
            hora = ""
        com = ""
        if item.get("lead_id"):
            lead = leads_repo.detalhar(int(item["lead_id"])) or {}
            nome = (lead.get("nome") or "").split()
            if nome:
                com = f" com {nome[0]}"
        hora_txt = f" as {hora}" if hora else ""
        msg = f"⏰ Priscila, daqui a ~1h: {item['titulo']}{hora_txt}{com}. Nao esquece! \U0001f60a"
        resp = whatsapp.enviar_mensagem(pri, msg)
        if resp.enviado:
            agenda_repo.marcar_lembrete_1h_enviado(int(item["id"]))
            enviados += 1
        else:
            log.warning("Falha lembrete 1h Priscila agenda_id=%s: %s", item["id"], resp.erro)
    return {"total": len(itens), "enviados": enviados, "fallback": False}


# ─── Resumo da agenda de MANHÃ pra Priscila (1x/dia, na janela da manhã) ───────
_HORA_RESUMO = int(os.getenv("AGENTE_RESUMO_MANHA_HORA", "7"))  # hora BRT alvo
_STATE_RESUMO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", ".resumo_manha"
)
_ultimo_resumo_dia = None


def _resumo_enviado_hoje(dia: str) -> bool:
    if _ultimo_resumo_dia == dia:
        return True
    try:
        with open(_STATE_RESUMO) as f:
            return f.read().strip() == dia
    except Exception:
        return False


def _marcar_resumo(dia: str) -> None:
    global _ultimo_resumo_dia
    _ultimo_resumo_dia = dia
    try:
        with open(_STATE_RESUMO, "w") as f:
            f.write(dia)
    except Exception:
        pass


def enviar_resumo_manha_priscila() -> dict:
    """Manda o resumo da agenda de HOJE pra Priscila (reusa secretaria.consultar)."""
    pri = "".join(c for c in os.getenv("PRISCILA_WHATSAPP", "") if c.isdigit())
    if not pri or not whatsapp.disponivel():
        return {"enviado": False, "motivo": "sem_numero_ou_evolution"}
    from app import secretaria
    res = secretaria.consultar("o que tem hoje")
    corpo = (res.get("mensagem") or "").replace("🤖 ", "")
    msg = "☀️ Bom dia, dona Priscila!\n\n" + corpo
    resp = whatsapp.enviar_mensagem(pri, msg)
    return {"enviado": bool(resp.enviado), "erro": getattr(resp, "erro", None)}


def resumo_manha_se_hora() -> None:
    """Só na janela da manhã (evita 'bom dia' à tarde) e só 1x por dia."""
    import datetime as _dt
    agora = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=-3)))
    if not (_HORA_RESUMO <= agora.hour < _HORA_RESUMO + 4):
        return
    dia = agora.strftime("%Y-%m-%d")
    if _resumo_enviado_hoje(dia):
        return
    res = enviar_resumo_manha_priscila()
    if res.get("enviado"):
        _marcar_resumo(dia)
        log.info("Resumo da manha enviado pra Priscila (%s)", dia)
    else:
        log.warning("Resumo da manha nao enviado: %s", res)


def main() -> None:
    signal.signal(signal.SIGTERM, _parar)
    signal.signal(signal.SIGINT, _parar)
    init_db()
    log.info(
        "Agente iniciado. intervalo=%ss janela=%sh whatsapp=%s",
        INTERVALO_SEGUNDOS,
        JANELA_HORAS,
        whatsapp.disponivel(),
    )

    while not parar:
        try:
            resumo = executar_ciclo()
            if resumo["total"]:
                log.info("Ciclo concluido: %s", resumo)
            resumo_pri = enviar_lembretes_priscila_1h()
            if resumo_pri["total"]:
                log.info("Lembrete 1h Priscila: %s", resumo_pri)
            resumo_manha_se_hora()
        except Exception:
            log.exception("Erro no ciclo do agente")
        time.sleep(INTERVALO_SEGUNDOS)

    log.info("Agente encerrado.")


if __name__ == "__main__":
    main()
