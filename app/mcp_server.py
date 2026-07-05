"""Servidor MCP da imobiliária — expõe o sistema como ferramentas pro Claude (Cowork/Code).

Permite que o Claude Code do PC AJA no sistema: consultar/corrigir leads, imóveis (com
fotos), agenda, financeiro, empreendimentos, depoimentos e gerar a planilha da Priscila.

SEGURANÇA:
- Ferramentas de LEITURA sempre ligadas.
- Ferramentas de ESCRITA/correção só ligam com MCP_WRITE_ENABLED=1 (senão nem aparecem).
- Envio de WhatsApp arbitrário só com MCP_WHATSAPP_ENABLED=1 (padrão off) — evita abuso/prompt-injection.
- IMÓVEL nunca é apagado de verdade: usa desativar_imovel (ativo=0). (regra do dono)
- Publicação no Instagram só com MCP_IG_PUBLISH_ENABLED=1 (padrão off).
- Roda em 127.0.0.1:8765 atrás de túnel/nginx com token (MCP_PUBLIC_TOKEN).
- Rodar atrás de nginx com auth/HTTPS antes de expor publicamente (ver docs/SETUP-DOIS-LADOS.md).

Rodar local (teste):   python -m app.mcp_server
"""
from __future__ import annotations

import dataclasses
import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP  # noqa: E402

from app import agenda as agenda_repo  # noqa: E402
from app import conversas as conversas_repo  # noqa: E402
from app import depoimentos as depoimentos_repo  # noqa: E402
from app import empreendimentos as emp_repo  # noqa: E402
from app import financeiro as financeiro_repo  # noqa: E402
from app import imoveis as imoveis_repo  # noqa: E402
from app import instagram as ig_mod  # noqa: E402
from app import leads as leads_repo  # noqa: E402
from app import whatsapp as whatsapp_mod  # noqa: E402

WRITE = os.getenv("MCP_WRITE_ENABLED", "0") == "1"
WA_OK = os.getenv("MCP_WHATSAPP_ENABLED", "0") == "1"
IG_PUBLISH = os.getenv("MCP_IG_PUBLISH_ENABLED", "0") == "1"

mcp = FastMCP("Priscila Vasconcelos — Imobiliária")


def _j(obj):
    """Torna o retorno serializável (dataclass/Row -> dict)."""
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if isinstance(obj, list):
        return [_j(o) for o in obj]
    try:
        return dict(obj)
    except (TypeError, ValueError):
        return obj


def _resolver_imovel_id(slug_ou_id) -> int | None:
    """Aceita id (int/str numérica) ou slug e devolve o id do imóvel."""
    if isinstance(slug_ou_id, int) or (isinstance(slug_ou_id, str) and slug_ou_id.isdigit()):
        return int(slug_ou_id)
    im = imoveis_repo.buscar_por_slug(str(slug_ou_id))
    return im["id"] if im else None


# ═══════════════ LEITURA (sempre ligada, seguro) ═══════════════
@mcp.tool
def resumo_leads() -> dict:
    """Resumo do funil de leads (totais por estágio/temperatura)."""
    return leads_repo.dashboard()


@mcp.tool
def funil(dias: int = 30) -> dict:
    """Funil de conversao do SITE nos ultimos N dias: visitantes que conversaram com a Ana ->
    quantos deixaram telefone (viraram lead que a Priscila alcanca) -> quantos esquentaram ->
    quantos agendaram. Mostra onde o funil esta vazando e os leads quentes pra agir."""
    from app.db import db_session
    corte = f"-{int(dias)} days"
    with db_session() as conn:
        site = conn.execute(
            "SELECT lead_id, ultimo_stage FROM conversas "
            "WHERE canal='site' AND criado_em >= date('now', ?)", (corte,),
        ).fetchall()
        agendou = conn.execute(
            "SELECT COUNT(DISTINCT lead_id) AS n FROM lead_tags WHERE tag='agendou_visita'"
        ).fetchone()
    total = len(site)
    com_tel = sum(1 for r in site if r["lead_id"] is not None)
    quentes = sum(1 for r in site if (r["ultimo_stage"] or "") == "quente")
    mornos = sum(1 for r in site if (r["ultimo_stage"] or "") == "morno")
    pct = lambda x: round(x * 100 / total) if total else 0
    return {
        "periodo_dias": dias,
        "funil_site": {
            "1_conversaram": total,
            "2_deixaram_contato": com_tel,
            "3_esquentaram": quentes,
            "agendaram_visita_total": (agendou["n"] if agendou else 0),
        },
        "taxa_captura_contato_pct": pct(com_tel),
        "vazamento": (
            "CRITICO: quase ninguem deixa contato — a Ana precisa pedir o WhatsApp como troca de valor"
            if total and com_tel == 0 else
            f"{total - com_tel} conversaram e sairam sem deixar contato (anonimos, Priscila nao alcanca)"
        ),
        "leads_morno_quente": mornos + quentes,
        "obs": "contato = telefone capturado (lead_id != null). Fonte: tabela conversas + lead_tags.",
    }


@mcp.tool
def listar_leads(estagio: str | None = None, temperatura: str | None = None, limite: int = 30) -> list:
    """Lista leads do CRM. Filtra por estagio (ex.: 'quente'/'novo'/'teste') ou temperatura. Limite padrão 30."""
    return _j(leads_repo.listar(estagio=estagio, temperatura=temperatura, limit=min(limite, 100)))


@mcp.tool
def detalhar_lead(lead_id: int) -> dict | None:
    """Detalhe completo de um lead pelo ID (dados, tags, histórico)."""
    return _j(leads_repo.detalhar(lead_id))


@mcp.tool
def listar_imoveis(bairro: str | None = None, incluir_inativos: bool = False) -> list:
    """Lista imóveis da carteira (por padrão só ativos; incluir_inativos=True mostra os desativados)."""
    return _j(imoveis_repo.listar_imoveis(somente_ativos=not incluir_inativos, bairro=bairro))


@mcp.tool
def buscar_imovel(slug: str) -> dict | None:
    """Busca um imóvel pelo slug (todos os campos)."""
    return _j(imoveis_repo.buscar_por_slug(slug))


@mcp.tool
def imovel_fotos(slug_ou_id: str) -> list:
    """Lista as FOTOS de um imóvel (id, arquivo/url, tipo, legenda, ordem). Aceita slug ou id."""
    iid = _resolver_imovel_id(slug_ou_id)
    if not iid:
        return [{"erro": f"imóvel não encontrado: {slug_ou_id}"}]
    return _j(imoveis_repo.listar_imagens(iid))


@mcp.tool
def agenda_listar(status: str | None = None) -> list:
    """Lista compromissos da agenda (filtra por status: agendado/confirmado/realizado/cancelado)."""
    return _j(agenda_repo.listar(status=status))


@mcp.tool
def agenda_lembretes_pendentes(janela_horas: int = 24) -> list:
    """Compromissos com lembrete a enviar nas próximas N horas."""
    return _j(agenda_repo.lembretes_a_enviar(janela_horas=janela_horas))


@mcp.tool
def financeiro_resumo(ano: int | None = None, mes: int | None = None) -> dict:
    """Resumo financeiro (comissões, contas, pipeline da carteira) do mês."""
    return financeiro_repo.dashboard(ano=ano, mes=mes)


@mcp.tool
def listar_comissoes(status: str | None = None, corretor: str | None = None) -> list:
    """Lista comissões (filtros opcionais por status ou corretor)."""
    return _j(financeiro_repo.listar_comissoes(status=status, corretor=corretor))


@mcp.tool
def listar_contas(tipo: str | None = None, pago: bool | None = None) -> list:
    """Lista contas (filtros: tipo='pagar'/'receber', pago=True/False)."""
    return _j(financeiro_repo.listar_contas(tipo=tipo, pago=pago))


@mcp.tool
def listar_empreendimentos(incluir_inativos: bool = False) -> list:
    """Lista os empreendimentos/condomínios cadastrados."""
    return _j(emp_repo.listar_empreendimentos(somente_ativos=not incluir_inativos))


@mcp.tool
def listar_depoimentos(incluir_inativos: bool = False) -> list:
    """Lista os depoimentos de clientes."""
    return _j(depoimentos_repo.listar(somente_ativos=not incluir_inativos))


@mcp.tool
def listar_conversas_ia(limite: int = 30, stage: str | None = None, busca: str | None = None) -> dict:
    """Lista as CONVERSAS da Ana com os clientes (Operação IA). Filtra por stage ou texto (busca)."""
    return _j(conversas_repo.listar_conversas(limit=min(limite, 100), stage=stage, busca=busca))


@mcp.tool
def detalhar_conversa_ia(conversa_id: int) -> dict | None:
    """Detalhe de UMA conversa da Ana — todas as mensagens trocadas (o que o cliente disse e a Ana respondeu)."""
    return _j(conversas_repo.detalhar_conversa(conversa_id))


@mcp.tool
def metricas_ia(horas: int = 24) -> dict:
    """Métricas da Operação IA (Ana) nas últimas N horas: volume, rotas, modelos, fallback, etc."""
    return conversas_repo.metricas_operacao_ia(horas=horas)


@mcp.tool
def panorama_geral() -> dict:
    """RAIO-X CENTRALIZADO da imobiliaria numa chamada so: leads (com os QUENTES), agenda de HOJE +
    proximos, financeiro do mes e pendencias. Use pra ter todo o contexto de uma vez."""
    import datetime as _dt
    hoje = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=-3))).strftime("%Y-%m-%d")
    pan: dict = {"data": hoje}
    try:
        d = leads_repo.dashboard()
        quentes = _j(leads_repo.listar(temperatura="quente", limit=20))
        pan["leads"] = {
            "total": d.get("total_leads"),
            "por_temperatura": d.get("por_temperatura"),
            "novos_7d": d.get("novos_7d"),
            "imoveis_ativos": d.get("imoveis_ativos"),
            "quentes": [
                {"id": q.get("id"), "nome": q.get("nome"), "telefone": q.get("telefone"),
                 "estagio": q.get("estagio")}
                for q in quentes if q.get("estagio") != "teste"
            ],
        }
    except Exception as e:
        pan["leads"] = {"erro": str(e)}
    try:
        ag = _j(agenda_repo.listar(status="agendado"))
        pan["agenda"] = {
            "hoje": [
                {"hora": str(a.get("inicio", ""))[11:16], "titulo": a.get("titulo"), "tipo": a.get("tipo")}
                for a in ag if str(a.get("inicio", "")).startswith(hoje)
            ],
            "proximos": [
                {"quando": str(a.get("inicio", ""))[:16], "titulo": a.get("titulo")}
                for a in ag if str(a.get("inicio", "")) > hoje
            ][:10],
        }
    except Exception as e:
        pan["agenda"] = {"erro": str(e)}
    try:
        f = financeiro_repo.dashboard()
        pan["financeiro"] = {
            "periodo": f.get("periodo"), "comissoes": f.get("comissoes"),
            "contas": f.get("contas"), "pipeline": f.get("pipeline"),
        }
    except Exception as e:
        pan["financeiro"] = {"erro": str(e)}
    try:
        pan["pendencias"] = {"lembretes_proximas_24h": len(_j(agenda_repo.lembretes_a_enviar(janela_horas=24)))}
    except Exception as e:
        pan["pendencias"] = {"erro": str(e)}
    return pan


@mcp.tool
def monitor_site_ao_vivo(limite: int = 8, com_mensagens: bool = True) -> dict:
    """AO VIVO: o que está acontecendo AGORA nas conversas da Ana NO SITE (canal=site).
    Traz as conversas mais recentes com score/temperatura, tempo e (se com_mensagens=True)
    todas as mensagens trocadas. Pensado pra um dashboard que chama em loop e atualiza no segundo.
    Use junto com metricas_ia() pra ter números + conteúdo."""
    from app.db import db_session
    import datetime as _dt
    agora = _dt.datetime.now(_dt.timezone(_dt.timedelta(hours=-3)))
    out: dict = {"gerado_em": agora.strftime("%Y-%m-%d %H:%M:%S"), "conversas": []}
    with db_session() as conn:
        linhas = conn.execute(
            """SELECT c.id, c.sessao_id, c.ultimo_score, c.ultimo_stage, c.rota_atual,
                      c.status, c.atualizado_em,
                      (SELECT COUNT(*) FROM mensagens_conversa m WHERE m.conversa_id=c.id) AS msgs
                 FROM conversas c
                WHERE c.canal='site'
                ORDER BY c.atualizado_em DESC
                LIMIT ?""",
            (min(limite, 30),),
        ).fetchall()
        for r in linhas:
            d = dict(r)
            item = {
                "id": d["id"],
                "sessao": d["sessao_id"],
                "score": d["ultimo_score"],
                "temperatura": d["ultimo_stage"],
                "rota": d["rota_atual"],
                "status": d["status"],
                "atualizado_em": d["atualizado_em"],
                "total_mensagens": d["msgs"],
            }
            if com_mensagens:
                msgs = conn.execute(
                    "SELECT papel, conteudo, criado_em FROM mensagens_conversa "
                    "WHERE conversa_id=? ORDER BY id",
                    (d["id"],),
                ).fetchall()
                item["mensagens"] = [
                    {"quem": "cliente" if m["papel"] == "user" else "Ana",
                     "texto": m["conteudo"], "em": m["criado_em"]}
                    for m in msgs
                ]
            out["conversas"].append(item)
    out["total_conversas_site"] = len(out["conversas"])
    return out


@mcp.tool
def saude_ads() -> dict:
    """Verifica ao vivo se GA4, Google Ads e Meta Pixel estão carregando no site.
    Retorna status de cada tag + se o evento generate_lead está no bundle JS."""
    import urllib.request as _ur
    url = "https://pvscelosimobiliaria.com/"
    resultado = {"url": url, "tags": {}, "erro": None}
    try:
        with _ur.urlopen(url, timeout=10) as r:
            html = r.read().decode("utf-8", errors="ignore")
        resultado["tags"]["GA4"] = "G-RDZY8DPY32" in html
        resultado["tags"]["Google_Ads"] = "AW-18124594477" in html
        resultado["tags"]["Meta_Pixel"] = "27844979038460971" in html
        # verifica bundle JS
        import re as _re
        bundle = _re.search(r'/app/index-[^"]+\.js', html)
        if bundle:
            js_url = "https://pvscelosimobiliaria.com" + bundle.group()
            with _ur.urlopen(js_url, timeout=10) as r2:
                js = r2.read().decode("utf-8", errors="ignore")
            resultado["tags"]["generate_lead_no_bundle"] = "generate_lead" in js
            resultado["tags"]["fbq_Lead_no_bundle"] = "fbq" in js
    except Exception as e:
        resultado["erro"] = str(e)
    return resultado


# ─── INSTAGRAM · LEITURA (seguro — sempre disponível se houver token) ─────────
@mcp.tool
def ig_status() -> dict:
    """Status seguro da configuração Instagram/Meta sem expor tokens."""
    return ig_mod.status_config()


@mcp.tool
def ig_perfil() -> dict:
    """Dados da conta IG da Priscila (seguidores, nº de posts, bio). Graph API oficial."""
    r = ig_mod.perfil()
    return {"ok": r.ok, "dados": r.dados, "erro": r.erro}


@mcp.tool
def ig_listar_midias(limite: int = 12) -> dict:
    """Últimas publicações do Instagram com curtidas/comentários."""
    r = ig_mod.listar_midias(limite=limite)
    return {"ok": r.ok, "dados": r.dados, "erro": r.erro}


@mcp.tool
def ig_insights(periodo: str = "day") -> dict:
    """Insights da conta IG (alcance/impressões/visitas). periodo: day/week/days_28."""
    r = ig_mod.insights_conta(periodo=periodo)
    return {"ok": r.ok, "dados": r.dados, "erro": r.erro}


@mcp.tool
def status_ecossistema() -> dict:
    """Status seguro do ecossistema Codex, site, Instagram, WhatsApp e IAs da VPS.

    Nao retorna tokens, telefones, nomes de leads ou qualquer segredo.
    """
    try:
        funil = leads_repo.dashboard()
    except Exception as exc:  # noqa: BLE001
        funil = {"erro": type(exc).__name__}

    try:
        imoveis_ativos = len(imoveis_repo.listar_imoveis(somente_ativos=True))
    except Exception as exc:  # noqa: BLE001
        imoveis_ativos = None
        funil.setdefault("avisos", []).append(f"imoveis_indisponiveis:{type(exc).__name__}")

    instagram = ig_mod.status_config()
    whatsapp_disponivel = whatsapp_mod.disponivel()

    return {
        "mcp_codex": {
            "nome": "imobiliaria_priscila",
            "modo_recomendado": "stdio local no Codex",
            "leitura_ok": True,
            "escrita_habilitada": WRITE,
            "whatsapp_habilitado_no_mcp": WRITE and WA_OK,
            "instagram_publicacao_habilitada_no_mcp": IG_PUBLISH,
        },
        "site": {
            "rotas_chave": [
                "/api/health",
                "/api/chat",
                "/api/imoveis",
                "/api/simular-financiamento",
                "/api/avaliar-imovel",
                "/api/whatsapp/webhook",
            ],
            "carteira_injetada_na_ana": True,
            "imoveis_ativos": imoveis_ativos,
        },
        "funil_agregado": {
            "total_leads": funil.get("total_leads"),
            "novos_7d": funil.get("novos_7d"),
            "por_temperatura": funil.get("por_temperatura"),
            "por_origem": funil.get("por_origem"),
            "simulacoes": funil.get("simulacoes"),
            "avaliacoes": funil.get("avaliacoes"),
        },
        "instagram": instagram,
        "whatsapp": {
            "evolution_configurada": whatsapp_disponivel,
            "instancia": os.getenv("EVOLUTION_INSTANCIA", "priscila"),
            "numero_alerta_interno_configurado": bool(os.getenv("ALERTA_WHATSAPP_NUMERO", "").strip()),
            "auto_reply_habilitado": os.getenv("WHATSAPP_AUTO_REPLY", "0") == "1",
            "modo_teste_configurado": bool(os.getenv("WHATSAPP_TEST_NUMBER", "").strip()),
            "limite_diario_auto_reply": os.getenv("WHATSAPP_DAILY_CAP", "30"),
            "historico_horas": os.getenv("WHATSAPP_HISTORY_HOURS", "48"),
            "transcricao_audio_configurada": bool(os.getenv("GROQ_API_KEY", "").strip()),
            "voz_configurada": bool(
                os.getenv("ELEVENLABS_API_KEY", "").strip()
                and os.getenv("ELEVENLABS_VOICE_ID", "").strip()
            ),
        },
        "ias_vps": {
            "gemini_configurado": bool(os.getenv("GOOGLE_API_KEY", "").strip()),
            "claude_configurado": bool(os.getenv("ANTHROPIC_API_KEY", "").strip()),
            "fallback_offline_disponivel": True,
            "modelos": {
                "gemini_flash": "gemini-2.5-flash",
                "gemini_pro": "gemini-2.5-pro",
                "claude_sonnet": "claude-sonnet-4-6",
                "claude_haiku": "claude-haiku-4-5-20251001",
            },
        },
        "campanhas_resultados": {
            "meta_facebook_instagram": {
                "access_token_configurado": bool(os.getenv("META_ACCESS_TOKEN", "").strip()),
                "ad_account_configurada": bool(os.getenv("META_AD_ACCOUNT_ID", "").strip()),
                "page_id_configurada": bool(os.getenv("META_PAGE_ID", "").strip()),
                "instagram_actor_configurado": bool(os.getenv("META_INSTAGRAM_ACTOR_ID", "").strip()),
                "pixel_id_configurado": bool(os.getenv("META_PIXEL_ID", "").strip()),
                "modo_recomendado": "somente leitura primeiro; criacao apenas PAUSED e HOUSING",
            },
            "google_ads": {
                "developer_token_configurado": bool(os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip()),
                "oauth_client_configurado": bool(
                    os.getenv("GOOGLE_ADS_CLIENT_ID", "").strip()
                    and os.getenv("GOOGLE_ADS_CLIENT_SECRET", "").strip()
                ),
                "refresh_token_configurado": bool(os.getenv("GOOGLE_ADS_REFRESH_TOKEN", "").strip()),
                "customer_id_configurado": bool(os.getenv("GOOGLE_ADS_CUSTOMER_ID", "").strip()),
                "login_customer_id_configurado": bool(os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").strip()),
                "modo_recomendado": "somente leitura de gasto, conversoes, termos e campanhas",
            },
            "metricas_que_precisamos_cruzar": [
                "gasto",
                "impressoes",
                "cliques",
                "ctr",
                "cpc",
                "leads",
                "cpl",
                "conversas_whatsapp",
                "avaliacoes_online",
                "visitas_agendadas",
                "lead_quente",
                "custo_por_lead_quente",
            ],
        },
        "travas": [
            "Ana nao revela bastidores de marketing ou sistema",
            "Instagram so publica se MCP_IG_PUBLISH_ENABLED=1",
            "WhatsApp so envia pelo MCP se MCP_WRITE_ENABLED=1 e MCP_WHATSAPP_ENABLED=1",
            "Auto-resposta WhatsApp so liga com WHATSAPP_AUTO_REPLY=1",
            "Meta/Facebook/Instagram e Google Ads comecam em leitura para relatorio",
            "Fotos publicas de marketing precisam de marca d'agua real da Priscila",
            "Ads imobiliarios sempre HOUSING e PAUSED ate aprovacao humana",
        ],
        "proximas_acoes": [
            "Configurar credenciais Meta/Instagram no cofre ou .env da VPS, sem colar no chat",
            "Validar Evolution API e auto-resposta primeiro em numero interno",
            "Instalar/validar Meta Pixel, GA4 e eventos do site",
            "Configurar Google Ads somente para leitura de resultados antes de qualquer otimizacao",
            "Usar status_ecossistema antes de acionar automacoes sensiveis",
        ],
    }


# ─── INSTAGRAM · PUBLICAÇÃO (só com MCP_IG_PUBLISH_ENABLED=1) ──────────────────
if IG_PUBLISH:
    @mcp.tool
    def ig_publicar_foto(image_url: str, legenda: str = "") -> dict:
        """Publica 1 foto no Insta. image_url DEVE ser URL pública (servir pela VPS)."""
        r = ig_mod.publicar_foto(image_url, legenda)
        return {"ok": r.ok, "dados": r.dados, "erro": r.erro}

    @mcp.tool
    def ig_publicar_carrossel(image_urls: list[str], legenda: str = "") -> dict:
        """Publica carrossel (2-10 imagens públicas) no Insta."""
        r = ig_mod.publicar_carrossel(image_urls, legenda)
        return {"ok": r.ok, "dados": r.dados, "erro": r.erro}

    @mcp.tool
    def ig_publicar_reel(video_url: str, legenda: str = "", capa_url: str | None = None) -> dict:
        """Publica um Reel (vídeo de URL pública) no Insta."""
        r = ig_mod.publicar_reel(video_url, legenda, capa_url)
        return {"ok": r.ok, "dados": r.dados, "erro": r.erro}


# ═══════════════ ESCRITA / CORREÇÃO (só com MCP_WRITE_ENABLED=1) ═══════════════
if WRITE:
    # ── Agenda ──
    @mcp.tool
    def agenda_criar(titulo: str, inicio: str, fim: str, tipo: str = "visita",
                     lead_id: int | None = None, observacoes: str = "") -> dict:
        """Cria compromisso na agenda. inicio/fim ISO (YYYY-MM-DDTHH:MM). Horário de BRASÍLIA (UTC-3).
        Já espelha no Google Agenda automaticamente."""
        novo = agenda_repo.criar(titulo=titulo, inicio=inicio, fim=fim, tipo=tipo,
                                 lead_id=lead_id, observacoes=observacoes)
        return {"ok": True, "id": novo}

    # ── Leads (correção) ──
    @mcp.tool
    def corrigir_lead(lead_id: int, campos: dict) -> dict:
        """Corrige campos de um lead (ex.: {"nome": "...", "temperatura": "quente", "estagio": "novo", "observacoes": "..."})."""
        ok = leads_repo.atualizar(lead_id, **campos)
        return {"ok": bool(ok), "lead_id": lead_id}

    @mcp.tool
    def lead_tag(lead_id: int, tag: str, remover: bool = False) -> dict:
        """Adiciona (ou remove, se remover=True) uma tag de um lead."""
        if remover:
            leads_repo.remover_tag(lead_id, tag)
        else:
            leads_repo.adicionar_tag(lead_id, tag)
        return {"ok": True, "lead_id": lead_id, "tag": tag, "removida": remover}

    # ── Imóveis (criar / corrigir / desativar — NUNCA apaga de verdade) ──
    @mcp.tool
    def criar_imovel(dados: dict) -> dict:
        """Cria um imóvel. dados = dict com titulo, bairro, tipo, valor, area, quartos, etc."""
        return _j(imoveis_repo.criar_imovel(dados))

    @mcp.tool
    def corrigir_imovel(slug_ou_id: str, dados: dict) -> dict | None:
        """Corrige campos de um imóvel (preço, descrição, quartos, etc.). Aceita slug ou id."""
        iid = _resolver_imovel_id(slug_ou_id)
        if not iid:
            return {"erro": f"imóvel não encontrado: {slug_ou_id}"}
        return _j(imoveis_repo.atualizar_imovel(iid, dados))

    @mcp.tool
    def desativar_imovel(slug_ou_id: str) -> dict:
        """Tira um imóvel do ar (ativo=0). NÃO apaga — é reversível reativando depois."""
        iid = _resolver_imovel_id(slug_ou_id)
        if not iid:
            return {"erro": f"imóvel não encontrado: {slug_ou_id}"}
        return {"ok": imoveis_repo.desativar_imovel(iid), "imovel_id": iid}

    # ── Fotos do imóvel (corrigir legenda/tipo, reordenar, remover) ──
    @mcp.tool
    def corrigir_foto(imagem_id: int, tipo: str | None = None, legenda: str | None = None) -> dict | None:
        """Corrige o tipo (fachada/sala/quarto...) ou a legenda de uma foto."""
        return _j(imoveis_repo.atualizar_imagem(imagem_id, tipo=tipo, legenda=legenda))

    @mcp.tool
    def reordenar_fotos(slug_ou_id: str, ordem_ids: list[int]) -> dict:
        """Reordena as fotos do imóvel (lista de imagem_id na ordem desejada; a 1ª vira a capa)."""
        iid = _resolver_imovel_id(slug_ou_id)
        if not iid:
            return {"erro": f"imóvel não encontrado: {slug_ou_id}"}
        imoveis_repo.reordenar_imagens(iid, ordem_ids)
        return {"ok": True, "imovel_id": iid}

    @mcp.tool
    def remover_foto(imagem_id: int) -> dict:
        """Remove UMA foto específica de um imóvel (pelo id da imagem)."""
        return {"ok": imoveis_repo.remover_imagem(imagem_id), "imagem_id": imagem_id}

    # ── Financeiro (correções de comissão/conta) ──
    @mcp.tool
    def criar_comissao(dados: dict) -> dict:
        """Lança uma comissão. dados = dict (imovel/valor/percentual/status/etc.)."""
        return _j(financeiro_repo.criar_comissao(dados))

    @mcp.tool
    def corrigir_comissao(comissao_id: int, dados: dict) -> dict | None:
        """Corrige campos de uma comissão."""
        return _j(financeiro_repo.atualizar_comissao(comissao_id, dados))

    @mcp.tool
    def criar_conta(dados: dict) -> dict:
        """Lança uma conta a pagar/receber."""
        return _j(financeiro_repo.criar_conta(dados))

    @mcp.tool
    def marcar_conta_paga(conta_id: int, data_pagamento: str | None = None) -> dict | None:
        """Marca uma conta como paga (data ISO opcional; padrão = hoje)."""
        return _j(financeiro_repo.marcar_conta_paga(conta_id, data_pagamento=data_pagamento))

    # ── Depoimentos ──
    @mcp.tool
    def criar_depoimento(nome: str, texto: str, estrelas: int = 5, contexto: str = "") -> dict:
        """Cadastra um depoimento de cliente."""
        return _j(depoimentos_repo.criar(nome=nome, texto=texto, estrelas=estrelas, contexto=contexto))

    @mcp.tool
    def corrigir_depoimento(depoimento_id: int, dados: dict) -> dict | None:
        """Corrige um depoimento (texto, estrelas, ativo, etc.)."""
        return _j(depoimentos_repo.atualizar(depoimento_id, dados))

    # ── Planilha da Priscila (Excel) ──
    @mcp.tool
    def gerar_planilha_priscila() -> dict:
        """Gera/atualiza a planilha Excel da Priscila (imóveis, aluguéis, resumo por bairro, ruas).
        Retorna o caminho do arquivo no servidor."""
        raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        proc = subprocess.run(
            [sys.executable, "scripts/gerar_planilha_priscila.py"],
            cwd=raiz, capture_output=True, text=True, timeout=120,
        )
        caminho = os.path.join(raiz, "relatorio-priscila", "IMOVEIS-VDC.xlsx")
        ok = proc.returncode == 0 and os.path.isfile(caminho)
        return {
            "ok": ok,
            "arquivo": caminho if ok else None,
            "saida": (proc.stdout or proc.stderr or "").strip()[-500:],
        }


# ═══════════════ WHATSAPP (só com MCP_WRITE_ENABLED=1 E MCP_WHATSAPP_ENABLED=1) ═══════════════
if WRITE and WA_OK:
    @mcp.tool
    def enviar_whatsapp_lembrete(telefone: str, texto: str) -> dict:
        """Envia 1 mensagem de WhatsApp (lembrete). Só com MCP_WRITE_ENABLED=1 e MCP_WHATSAPP_ENABLED=1."""
        if not whatsapp_mod.disponivel():
            return {"erro": "WhatsApp não configurado"}
        return _j(whatsapp_mod.enviar_mensagem(telefone, texto))


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8765)
