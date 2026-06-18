"""Servidor MCP da imobiliária — expõe o sistema como ferramentas pro Claude (Cowork/Code).

Permite que o Claude Code do PC AJA no sistema: consultar/corrigir leads, imóveis (com
fotos), agenda, financeiro, empreendimentos, depoimentos e gerar a planilha da Priscila.

SEGURANÇA:
- Ferramentas de LEITURA sempre ligadas.
- Ferramentas de ESCRITA/correção só ligam com MCP_WRITE_ENABLED=1 (senão nem aparecem).
- Envio de WhatsApp arbitrário só com MCP_WHATSAPP_ENABLED=1 (padrão off) — evita abuso/prompt-injection.
- IMÓVEL nunca é apagado de verdade: usa desativar_imovel (ativo=0). (regra do dono)
- Roda em 127.0.0.1:8765 atrás de túnel/nginx com token (MCP_PUBLIC_TOKEN).

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
from app import leads as leads_repo  # noqa: E402
from app import whatsapp as whatsapp_mod  # noqa: E402

WRITE = os.getenv("MCP_WRITE_ENABLED", "0") == "1"
WA_OK = os.getenv("MCP_WHATSAPP_ENABLED", "0") == "1"

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
