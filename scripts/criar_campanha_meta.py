#!/usr/bin/env python3
"""Cria a campanha Meta (Click-to-WhatsApp) da Priscila — TUDO PAUSADO.

Pré-requisitos (no .env do projeto):
    META_ACCESS_TOKEN   = token de usuário do sistema (ads_management, business_management)
    META_AD_ACCOUNT_ID  = act_XXXXXXXXXX  (com o prefixo act_)
    META_PAGE_ID        = ID da Página do Facebook (de onde sai o anúncio)
    PRISCILA_WHATSAPP   = 5577999395511   (opcional; default abaixo)

Uso:
    venv/bin/python scripts/criar_campanha_meta.py /caminho/da/foto-priscila.jpg

NADA é ativado: campanha, conjunto e anúncio nascem com status PAUSED.
Depois de rodar, revise no Gerenciador de Anúncios e ative manualmente (aí começa
a gastar os R$ 15/dia). O script só PREPARA — quem aperta "ativar" é você.
"""
from __future__ import annotations

import os
import sys
import json
from pathlib import Path
from urllib.parse import quote

import requests
from dotenv import load_dotenv

API = "https://graph.facebook.com/v21.0"

# ── Configuração da campanha (fácil de ajustar) ───────────────────────────────
WHATSAPP = os.getenv("PRISCILA_WHATSAPP") or "5577999395511"
MSG_PREENCHIDA = "Oi, Priscila! Vi seu anúncio e quero saber mais 😊"
ORCAMENTO_DIARIO_CENTAVOS = 1500   # R$ 15,00/dia (BRL em centavos)

NOME_CAMPANHA = "Priscila Vasconcelos — Marca (WhatsApp) — teste"
TEXTO_PRINCIPAL = (
    "Comprar, vender ou alugar em Vitória da Conquista não precisa ser dor de cabeça. 💙\n"
    "Sou Priscila Vasconcelos, corretora (CRECI/BA 29.231), e cuido de cada etapa com "
    "você — do primeiro contato à entrega das chaves.\n"
    "Me chama no WhatsApp e me conta o que você procura."
)
TITULO = "Fale com a Priscila Vasconcelos"
DESCRICAO = "Compra · Venda · Aluguel — VdC e região"

# Público: Vitória da Conquista/BA + raio de 30km, 25–60 anos.
TARGETING = {
    "geo_locations": {
        "custom_locations": [
            {"latitude": -14.8615, "longitude": -40.8442, "radius": 30, "distance_unit": "kilometer"}
        ]
    },
    "age_min": 25,
    "age_max": 60,
    "locales": [6],  # pt_BR
}
# ──────────────────────────────────────────────────────────────────────────────


def _post(path: str, token: str, data: dict, files=None) -> dict:
    data = {**data, "access_token": token}
    r = requests.post(f"{API}/{path}", data=data, files=files, timeout=60)
    try:
        body = r.json()
    except Exception:
        r.raise_for_status()
        raise
    if r.status_code >= 400 or "error" in body:
        print(f"\n❌ Erro na chamada {path}:")
        print(json.dumps(body.get("error", body), indent=2, ensure_ascii=False))
        sys.exit(1)
    return body


def main() -> None:
    # Sem argumento, usa a foto da Priscila que já está no site (página A Marca).
    FOTO_PADRAO = Path(__file__).resolve().parent.parent / "design-recebido/pvscelos-imobiliaria/public/priscila-sobre.jpg"
    foto = Path(sys.argv[1]) if len(sys.argv) >= 2 else FOTO_PADRAO
    if not foto.exists():
        sys.exit(f"Foto não encontrada: {foto}")

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    token = os.getenv("META_ACCESS_TOKEN")
    acct = os.getenv("META_AD_ACCOUNT_ID")
    page = os.getenv("META_PAGE_ID")
    faltando = [k for k, v in {"META_ACCESS_TOKEN": token, "META_AD_ACCOUNT_ID": acct, "META_PAGE_ID": page}.items() if not v]
    if faltando:
        sys.exit("Faltam no .env: " + ", ".join(faltando))
    if not acct.startswith("act_"):
        acct = "act_" + acct

    print(f"→ Conta {acct} · Página {page} · WhatsApp {WHATSAPP}")

    # 1) Sobe a imagem → image_hash
    print("1/5 Enviando a imagem…")
    with open(foto, "rb") as f:
        img = _post(f"{acct}/adimages", token, {}, files={"file": f})
    image_hash = next(iter(img["images"].values()))["hash"]
    print(f"    image_hash: {image_hash}")

    # 2) Campanha (PAUSED)
    print("2/5 Criando a campanha (PAUSADA)…")
    camp = _post(f"{acct}/campaigns", token, {
        "name": NOME_CAMPANHA,
        "objective": "OUTCOME_ENGAGEMENT",
        "status": "PAUSED",
        "special_ad_categories": json.dumps([]),
    })
    print(f"    campaign_id: {camp['id']}")

    # 3) Conjunto de anúncios (PAUSED) — otimiza por CONVERSAS no WhatsApp
    print("3/5 Criando o conjunto (PAUSADO, R$ %.2f/dia)…" % (ORCAMENTO_DIARIO_CENTAVOS / 100))
    adset = _post(f"{acct}/adsets", token, {
        "name": "VdC e região · 25-60",
        "campaign_id": camp["id"],
        "daily_budget": ORCAMENTO_DIARIO_CENTAVOS,
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "CONVERSATIONS",
        "destination_type": "WHATSAPP",
        "promoted_object": json.dumps({"page_id": page}),
        "targeting": json.dumps(TARGETING),
        "status": "PAUSED",
    })
    print(f"    adset_id: {adset['id']}")

    # 4) Criativo — abre o WhatsApp com a mensagem já preenchida
    print("4/5 Criando o criativo…")
    wa_link = f"https://wa.me/{WHATSAPP}?text={quote(MSG_PREENCHIDA)}"
    story = {
        "page_id": page,
        "link_data": {
            "message": TEXTO_PRINCIPAL,
            "link": wa_link,
            "image_hash": image_hash,
            "name": TITULO,
            "description": DESCRICAO,
            "call_to_action": {
                "type": "WHATSAPP_MESSAGE",
                "value": {"app_destination": "WHATSAPP", "link": wa_link},
            },
        },
    }
    creative = _post(f"{acct}/adcreatives", token, {
        "name": "Criativo A — a corretora",
        "object_story_spec": json.dumps(story),
    })
    print(f"    creative_id: {creative['id']}")

    # 5) Anúncio (PAUSED)
    print("5/5 Criando o anúncio (PAUSADO)…")
    ad = _post(f"{acct}/ads", token, {
        "name": "Anúncio A — Priscila (WhatsApp)",
        "adset_id": adset["id"],
        "creative": json.dumps({"creative_id": creative["id"]}),
        "status": "PAUSED",
    })
    print(f"    ad_id: {ad['id']}")

    print("\n✅ Tudo criado e PAUSADO. Nada gastou ainda.")
    print("   Revise no Gerenciador de Anúncios e ative manualmente quando quiser.")
    print(f"   Campanha: {camp['id']} | Conjunto: {adset['id']} | Anúncio: {ad['id']}")


if __name__ == "__main__":
    main()
