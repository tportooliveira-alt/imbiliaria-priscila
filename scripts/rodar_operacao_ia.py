"""Roda a operacao autonoma das IAs em ciclos.

Uso rapido:
  python scripts/rodar_operacao_ia.py --setup-instagram --contato 5577999226268
  python scripts/rodar_operacao_ia.py --continuo --intervalo 45 --contato 5577999226268
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from app.db import init_db
from app.operacao_ia import (
    bootstrap_agentes_padrao,
    criar_tarefa,
    executar_ciclo,
    gerar_relatorio_operacao,
    provisionar_instagram_vendas,
)


def _montar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Operacao IA autonoma (procuradora/rastreadora/leads/marketing).")
    p.add_argument("--setup-instagram", action="store_true", help="Provisiona playbook e fila inicial de marketing no Instagram.")
    p.add_argument("--contato", default="", help="Telefone para notificacoes (formato 55DDDNUMERO).")
    p.add_argument("--agente", default="", choices=["", "procuradora", "rastreadora", "leads", "marketing", "orquestrador", "corretor"])
    p.add_argument("--origem", default="", help="Filtro de origem (instagram/web/site/whatsapp).")
    p.add_argument("--limite", type=int, default=25, help="Quantidade maxima de tarefas por ciclo.")
    p.add_argument("--ciclos", type=int, default=1, help="Numero de ciclos para executar.")
    p.add_argument("--continuo", action="store_true", help="Roda em loop ate interrupcao manual (Ctrl+C).")
    p.add_argument("--intervalo", type=int, default=45, help="Segundos de pausa entre ciclos no modo continuo.")
    p.add_argument("--semeador", action="store_true", help="Cria tarefas padrao de prospeccao/rastreamento antes de iniciar.")
    return p


def _semeador_basico(contato: str) -> list[int]:
    payload_extra = {}
    if contato:
        payload_extra = {
            "contato": contato,
            "mensagem_notificacao": "Lead potencial identificado pela operacao IA. Verificar contato rapido.",
        }
    mensagens = [
        ("procuradora", "web", "prospeccao_agencias", "Mapear sinais de compra de casas e terrenos em Vitoria da Conquista."),
        ("rastreadora", "web", "rastreamento_intencao", "Detectar mudancas de intencao e urgencia em leads mornos e frios."),
        ("leads", "site", "qualificacao_rapida", "Qualificar lead em potencial e sugerir proximo passo comercial."),
        ("orquestrador", "interno", "coordenacao", "Distribuir tarefas e priorizar canais com maior chance de conversao."),
    ]
    ids = []
    for agente, origem, tipo, mensagem in mensagens:
        t = criar_tarefa(
            origem=origem,
            tipo=tipo,
            mensagem=mensagem,
            agente_chave=agente,
            prioridade=8,
            payload_extra=payload_extra,
        )
        ids.append(int(t["id"]))
    return ids


def main() -> int:
    load_dotenv(ROOT / ".env")
    args = _montar_parser().parse_args()
    init_db()
    bootstrap_agentes_padrao()

    contato = (args.contato or "").strip()

    if args.setup_instagram:
        out_setup = provisionar_instagram_vendas(contato=contato or None)
        print(f"[setup] instagram ok | tarefas={len(out_setup['tarefas_criadas'])} | conhecimentos={len(out_setup['conhecimentos_criados'])}")

    if args.semeador:
        ids = _semeador_basico(contato)
        print(f"[setup] semeador criou {len(ids)} tarefas: {ids}")

    ciclos = max(1, args.ciclos)
    ciclo_n = 0

    def rodar_um_ciclo(indice: int) -> None:
        resultado = executar_ciclo(
            limite=max(1, args.limite),
            origem=(args.origem or None),
            agente_chave=(args.agente or None),
        )
        rel = gerar_relatorio_operacao(horas=24, limite_itens=12)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{ts}] ciclo={indice} processadas={resultado['processadas']} "
            f"concluidas={resultado['concluidas']} erros={resultado['erros']} "
            f"boas={rel['totais']['boas']} ruins={rel['totais']['ruins']}"
        )

    if args.continuo:
        try:
            while True:
                ciclo_n += 1
                rodar_um_ciclo(ciclo_n)
                time.sleep(max(5, args.intervalo))
        except KeyboardInterrupt:
            print("\n[ok] operacao interrompida manualmente.")
            return 0

    for i in range(ciclos):
        rodar_um_ciclo(i + 1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
