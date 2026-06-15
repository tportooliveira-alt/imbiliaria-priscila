"""Follow-up / nutrição de lead morno — REAQUECE leads que esfriaram, via WhatsApp.

A pesquisa do funil apontou o lead morno que esfria e some como vazamento clássico.
Sequência de até 3 toques (templates — NÃO inventa imóvel/preço), na voz da Ana.

SEGURANÇA:
- Respeita OPT-OUT (quem pediu pra parar nunca recebe).
- Respeita WHATSAPP_DAILY_CAP (teto diário de mensagens).
- Só reaquece quem FICOU QUIETO (não mexe em quem respondeu — esse a Ana atende).
- Máx 3 toques por lead; depois para (não vira spam).
- Só DISPARA de verdade com FOLLOWUP_ENABLED=1; sem isso, fica em modo PREVIEW (lista quem receberia).
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from app import leads as leads_repo
from app.db import db_session

ENABLED = os.getenv("FOLLOWUP_ENABLED", "0") == "1"
ESPACAMENTO = [2, 3, 5]   # dias: toque 1 após 2d quieto · 2 após +3d · 3 após +5d
MAX_TOQUES = 3
_OPTOUT = ("parar", "pare", "para de", "nao quero", "não quero", "descadastr",
           "sair da lista", "me tira", "para com isso", "chega")


def _primeiro_nome(nome: str | None) -> str:
    return (nome or "").strip().split(" ")[0] if nome else ""


# não reaquecer corretores/empresas/concorrentes (não são compradores reais)
_NAO_COMPRADOR = ("imóveis", "imoveis", "imobiliá", "imobilia", "corretor", "creci",
                  "ltda", "me ", "imob", "construtora", "incorporad", "test", "deny")


def _eh_empresa(nome: str | None) -> bool:
    n = (nome or "").lower()
    return any(p in n for p in _NAO_COMPRADOR)


def mensagem(toque: int, nome: str | None) -> str:
    n = _primeiro_nome(nome)
    ola = f"Oi {n}! " if n else "Oi! "
    if toque <= 1:
        return (ola + "Aqui é a Ana, da Priscila Vasconcelos 😊 Passando só pra saber se você ainda "
                "está procurando imóvel. Surgiram umas opções boas e lembrei de você! Quer que eu te mostre?")
    if toque == 2:
        return (ola + "Tudo bem? Se ainda estiver na busca, posso te separar 2-3 opções que combinam com "
                "o que você procura — sem compromisso. É só me falar! 🙂")
    return (ola + "Passando pela última vez por aqui 😅 Se quiser retomar a procura quando der, é só me "
            "responder que a Priscila e eu te ajudamos. Um abraço! 👋")


def _parse(ts: str):
    try:
        return datetime.fromisoformat(str(ts).replace("T", " ").split(".")[0])
    except Exception:
        return None


def elegiveis(limite: int = 50) -> list[dict]:
    """Leads morno/quente que ficaram quietos e ainda têm toque a dar."""
    agora = datetime.utcnow()
    res: list[dict] = []
    with db_session() as conn:
        leads = conn.execute(
            "SELECT id, nome, telefone, temperatura FROM leads "
            "WHERE temperatura IN ('morno','quente') AND telefone IS NOT NULL AND telefone != ''"
        ).fetchall()
        for ld in leads:
            lid = ld["id"]
            if _eh_empresa(ld["nome"]):   # pula corretor/empresa/teste
                continue
            inter = conn.execute(
                "SELECT tipo, descricao, criado_em FROM lead_interacoes WHERE lead_id=? ORDER BY id DESC",
                (lid,),
            ).fetchall()
            if not inter:
                continue
            # opt-out: alguma mensagem recebida pedindo pra parar
            if any(it["tipo"] == "whatsapp_recebido" and any(p in (it["descricao"] or "").lower() for p in _OPTOUT)
                   for it in inter):
                continue
            followups = [it for it in inter if it["tipo"] == "followup_enviado"]
            n_toques = len(followups)
            if n_toques >= MAX_TOQUES:
                continue
            ult_followup = _parse(followups[0]["criado_em"]) if followups else None
            # respondeu DEPOIS do último follow-up? então deixa pra Ana (não reaquece)
            if ult_followup and any(it["tipo"] == "whatsapp_recebido" and (_parse(it["criado_em"]) or agora) > ult_followup
                                    for it in inter):
                continue
            ref = ult_followup or _parse(inter[0]["criado_em"])  # última atividade
            if ref is None:
                continue
            dias = (agora - ref).days
            if dias < ESPACAMENTO[min(n_toques, len(ESPACAMENTO) - 1)]:
                continue
            res.append({"lead_id": lid, "nome": ld["nome"], "telefone": ld["telefone"],
                        "temperatura": ld["temperatura"], "toque": n_toques + 1, "dias_quieto": dias,
                        "mensagem": mensagem(n_toques + 1, ld["nome"])})
            if len(res) >= limite:
                break
    return res


def _enviados_hoje() -> int:
    with db_session() as conn:
        r = conn.execute(
            "SELECT COUNT(*) n FROM lead_interacoes WHERE tipo IN ('whatsapp_enviado','followup_enviado') "
            "AND date(criado_em)=date('now','localtime')"
        ).fetchone()
    return int(r["n"] or 0)


def processar(limite: int = 30) -> dict:
    """Envia os follow-ups elegíveis (se FOLLOWUP_ENABLED=1). Sem a flag, retorna o PREVIEW."""
    alvos = elegiveis(limite)
    if not ENABLED:
        return {"modo": "preview", "habilitado": False, "total": len(alvos), "itens": alvos}
    from app import whatsapp as wa
    if not wa.disponivel():
        return {"modo": "envio", "erro": "whatsapp indisponivel", "total": len(alvos)}
    cap = int(os.getenv("WHATSAPP_DAILY_CAP", "20"))
    enviados = 0
    detalhes = []
    for a in alvos:
        if _enviados_hoje() >= cap:
            detalhes.append({"lead_id": a["lead_id"], "status": "teto_diario"})
            break
        r = wa.enviar_mensagem(a["telefone"], a["mensagem"])
        ok = getattr(r, "enviado", False)
        if ok:
            leads_repo.registrar_interacao(
                a["lead_id"], tipo="followup_enviado",
                descricao=f"[follow-up toque {a['toque']}] " + a["mensagem"][:200],
                metadata={"toque": a["toque"], "dias_quieto": a["dias_quieto"]})
            enviados += 1
        detalhes.append({"lead_id": a["lead_id"], "toque": a["toque"], "status": "ok" if ok else "falhou"})
    return {"modo": "envio", "habilitado": True, "elegiveis": len(alvos), "enviados": enviados, "detalhes": detalhes}


if __name__ == "__main__":
    import json
    print(json.dumps(processar(), ensure_ascii=False, indent=2, default=str))
