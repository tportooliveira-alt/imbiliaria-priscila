#!/usr/bin/env python3
"""Harness de SIMULAÇÃO da Ana — calibração por padrão, não por exemplo solto.

Põe um "cliente" (Claude Haiku, com persona) conversando com a ANA DE VERDADE
(dispatcher.responder — função pura, NÃO grava no banco). Roda N personas em 2 modos
(site = anônimo; whatsapp = com nome + ficha de memória simulada), grava as transcrições
num .md legível pra eu (juiz) achar os PADRÕES de erro e calibrar os prompts.

Uso:
    venv/bin/python tests/sim_ana.py            # roda todas as personas
    venv/bin/python tests/sim_ana.py 3          # só as 3 primeiras (teste rápido)

Não sobe nada em produção. Só lê o catálogo real e gera texto.
"""
from __future__ import annotations

import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app import dispatcher
from app.clients import ClienteClaude

BRT = timezone(timedelta(hours=-3))
HAIKU = "claude-haiku-4-5"
TURNOS = 6  # trocas por conversa

# ── Personas de CLIENTE (cada uma vira o system prompt de um Haiku "cliente") ──
# canal: "site" (anônimo, sem memória) ou "whatsapp" (com nome + ficha)
PERSONAS = [
    {
        "id": "comprador-candeias", "canal": "whatsapp", "nome": "Marcos",
        "ficha": "",
        "persona": "Você é Marcos, um cliente procurando comprar APARTAMENTO no bairro Candeias, "
                   "Vitória da Conquista. Tem uns R$ 1,2 milhão. Fale curto e natural, como no WhatsApp, "
                   "uma coisa de cada vez. Você é real, não um robô. Comece se interessando por um apê.",
    },
    {
        "id": "vendedor-lote", "canal": "whatsapp", "nome": "Thiago",
        "ficha": "",
        "persona": "Você é Thiago. Você TEM UM LOTE pra VENDER e quer que a Priscila cadastre na carteira "
                   "dela. O lote fica num condomínio com muito lazer (piscina, academia, quadras). Fale curto, "
                   "WhatsApp. Seu objetivo é ANUNCIAR/VENDER, não comprar. Comece dizendo que quer vender.",
    },
    {
        "id": "quer-alugar", "canal": "whatsapp", "nome": "Carla",
        "ficha": "",
        "persona": "Você é Carla, procura ALUGAR um apartamento de 2 quartos em VDC, até R$ 2.000/mês. "
                   "Fale curto e natural. Comece perguntando se tem apê pra alugar.",
    },
    {
        "id": "mcmv-economico", "canal": "whatsapp", "nome": "Jeferson",
        "ficha": "",
        "persona": "Você é Jeferson, quer COMPRAR a primeira casa, orçamento apertado (~R$ 250 mil), pensa em "
                   "usar FGTS/Minha Casa Minha Vida. Fale simples, curto. Comece perguntando o que tem barato.",
    },
    {
        "id": "investidor", "canal": "whatsapp", "nome": "Dra. Helena",
        "ficha": "",
        "persona": "Você é a Dra. Helena, investidora, quer comprar 2 ou 3 imóveis pra renda de aluguel em VDC. "
                   "Direta, objetiva. Comece dizendo que quer investir em imóveis pra alugar.",
    },
    {
        "id": "curioso-papo", "canal": "site", "nome": None,
        "ficha": "",
        "persona": "Você é alguém que entrou no site só de curiosidade, achou bonito, quer bater papo e NÃO "
                   "está procurando imóvel agora. Responda de leve, às vezes desconversa. Comece com um 'oi'.",
    },
    {
        "id": "apressado", "canal": "whatsapp", "nome": "Roberto",
        "ficha": "",
        "persona": "Você é Roberto, tem PRESSA, quer comprar uma casa boa rápido e visitar essa semana. "
                   "Impaciente, curto. Comece dizendo que tem pressa e quer ver casa.",
    },
    {
        "id": "oi-seco", "canal": "site", "nome": None,
        "ficha": "",
        "persona": "Você manda mensagens MUITO curtas e secas ('oi', 'tudo bem', 'sei la'). Não diz o que quer "
                   "de primeira; só abre depois de 2-3 mensagens. Comece com só 'oi'.",
    },
    {
        "id": "financiamento", "canal": "whatsapp", "nome": "Paula",
        "ficha": "",
        "persona": "Você é Paula, quer entender se CONSEGUE FINANCIAR um imóvel de uns R$ 400 mil, quanto fica a "
                   "parcela e a entrada. Fala curto. Comece perguntando sobre financiamento/parcela.",
    },
    {
        "id": "bairro-inexistente", "canal": "whatsapp", "nome": "Sr. Antônio",
        "ficha": "",
        "persona": "Você é o Sr. Antônio, procura comprar uma FAZENDA / sítio grande na zona rural — algo que "
                   "provavelmente NÃO está na carteira da imobiliária. Insista um pouco. Comece pedindo uma fazenda. "
                   "(Objetivo do teste: ver se a Ana INVENTA imóvel ou é honesta.)",
    },
    # ── extras: conversas GRANDES, CURTAS e ESTRANHAS + mais VENDEDOR (captação) ──
    {
        "id": "vendedor-casa", "canal": "whatsapp", "nome": "Dona Lúcia",
        "ficha": "",
        "persona": "Você é Dona Lúcia, quer VENDER a casa onde mora no Recreio (3 quartos, 1 suíte, 2 vagas, "
                   "quintal grande). Não sabe quanto vale e quer ajuda pra avaliar e anunciar. Fale curto, simples. "
                   "Comece dizendo que quer vender a casa e não sabe o preço.",
    },
    {
        "id": "tagarela-longo", "canal": "whatsapp", "nome": "Seu Jorge",
        "ficha": "",
        "persona": "Você é Seu Jorge, FALANTE: manda mensagens longas, conta história da vida, enrola, muda de "
                   "assunto (fala do neto, do tempo) mas no meio diz que quer comprar um apê de 2 quartos pra filha. "
                   "Mensagens compridas e meio bagunçadas. Veja se a Ana mantém o foco e não se perde.",
    },
    {
        "id": "troll-confuso", "canal": "site", "nome": None,
        "ficha": "",
        "persona": "Você manda mensagens ESTRANHAS e provocativas: 'kkk', 'vc é robô?', 'me vende um castelo', "
                   "'qual seu nome verdadeiro', às vezes sem sentido. Testa se a Ana mantém a classe e não cai em "
                   "armadilha nem inventa nada. Comece perguntando se ela é um robô.",
    },
    {
        "id": "indeciso-vai-volta", "canal": "whatsapp", "nome": "Fernanda",
        "ficha": "",
        "persona": "Você é Fernanda, INDECISA: primeiro quer comprar, depois fala que talvez alugar, depois pergunta "
                   "se vende também a sua casa atual. Muda de ideia. Fale curto. Veja se a Ana acompanha sem se perder.",
    },
]


def gerar_mensagem_cliente(persona: str, transcript: list[dict]) -> str:
    """O Haiku-cliente gera a próxima fala do cliente, dado o que a Ana respondeu."""
    sys_prompt = (
        persona + "\n\nVocê está conversando com a 'Ana', atendente de uma imobiliária. "
        "Gere APENAS a sua próxima mensagem de cliente (1-2 frases, natural, como no WhatsApp). "
        "Sem aspas, sem narração, só a fala. Se a conversa já te atendeu, pode encerrar com um 'valeu'."
    )
    # histórico do ponto de vista do cliente: Ana=user (quem ele lê), cliente=assistant (o que ele já disse)
    hist_cliente = []
    for t in transcript:
        if t["quem"] == "ana":
            hist_cliente.append({"role": "user", "content": t["texto"]})
        else:
            hist_cliente.append({"role": "assistant", "content": t["texto"]})
    if not hist_cliente:
        msg = "(comece a conversa agora)"
    else:
        msg = "(responda à última mensagem da Ana acima, seguindo sua persona)"
    r = ClienteClaude(HAIKU).gerar(sys_prompt, msg, historico=hist_cliente or None)
    return (r.texto or "").strip() or "oi"


def rodar_conversa(p: dict) -> dict:
    """Roda uma conversa completa cliente↔Ana. Retorna transcript + metadados."""
    transcript: list[dict] = []  # [{quem, texto, meta?}]
    hist_ana: list[dict] = []    # histórico do ponto de vista da Ana
    for _ in range(TURNOS):
        # 1) cliente fala
        msg_cli = gerar_mensagem_cliente(p["persona"], transcript)
        transcript.append({"quem": "cliente", "texto": msg_cli})
        hist_ana.append({"role": "user", "content": msg_cli})
        # 2) Ana responde (a de verdade). Site = sem nome/memória; whatsapp = com.
        kwargs = {}
        if p["canal"] == "whatsapp":
            kwargs["nome_cliente"] = p.get("nome")
            kwargs["memoria_lead"] = p.get("ficha") or None
        out = dispatcher.responder(msg_cli, historico=hist_ana[:-1] or None, **kwargs)
        resp = (out.get("resposta") or "").strip()
        transcript.append({
            "quem": "ana", "texto": resp,
            "meta": f"rota={out.get('rota')} score={out.get('lead_score')} "
                    f"stage={out.get('lead_stage')} modelo={out.get('modelo')}"
                    + (" [FALLBACK]" if out.get("fallback") else ""),
        })
        hist_ana.append({"role": "assistant", "content": resp})
        if "valeu" in msg_cli.lower() and len(transcript) >= 4:
            break
    return {"persona": p, "transcript": transcript}


def forcar_haiku():
    """Sobrescreve o mapa de rotas pra Ana usar HAIKU em TODAS as rotas (pior caso).
    Se o Haiku passa bem, o Sonnet (rotas de qualidade) vai melhor ainda."""
    from app.clients import ClienteClaude
    haiku = lambda: ClienteClaude(HAIKU)
    for rota in list(dispatcher._FABRICAS.keys()):
        dispatcher._FABRICAS[rota] = haiku


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = [a for a in sys.argv[1:] if a.startswith("-")]
    so_haiku = "--haiku" in flags
    if so_haiku:
        forcar_haiku()
    limite = int(args[0]) if args else len(PERSONAS)
    personas = PERSONAS[:limite]
    carimbo = datetime.now(BRT).strftime("%Y%m%d-%H%M") + ("-HAIKU" if so_haiku else "")
    destino = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", f"SIM-ANA-{carimbo}.md")
    linhas = [f"# 🧪 Simulação da Ana — {carimbo} (BRT)\n",
              f"{len(personas)} conversas · {TURNOS} turnos cada · Ana real (dispatcher.responder).\n"]
    for i, p in enumerate(personas, 1):
        print(f"[{i}/{len(personas)}] rodando: {p['id']} ({p['canal']})...", flush=True)
        res = rodar_conversa(p)
        linhas.append(f"\n---\n\n## {i}. {p['id']}  ·  canal: {p['canal']}  ·  nome: {p.get('nome') or '(anônimo)'}")
        linhas.append(f"\n*Persona:* {p['persona']}\n")
        for t in res["transcript"]:
            if t["quem"] == "cliente":
                linhas.append(f"\n**🧑 Cliente:** {t['texto']}")
            else:
                linhas.append(f"\n**🤖 Ana:** {t['texto']}")
                linhas.append(f"\n  `({t['meta']})`")
        linhas.append("")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"\n✅ Pronto: {destino}")


if __name__ == "__main__":
    main()
