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
        except Exception:
            log.exception("Erro no ciclo do agente")
        time.sleep(INTERVALO_SEGUNDOS)

    log.info("Agente encerrado.")


if __name__ == "__main__":
    main()
