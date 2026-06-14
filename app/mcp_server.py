"""Servidor MCP da imobiliária — expõe o sistema como ferramentas pro Claude (Cowork/Code).

Permite que o agente do Cowork AJA no sistema conversando: consultar leads, ver agenda,
marcar compromisso, resumo financeiro, e (se liberado) enviar WhatsApp.

SEGURANÇA (pesquisa de integrações):
- Ferramentas de ESCRITA/ação só ligam com MCP_WRITE_ENABLED=1 no .env (padrão = só leitura).
- Envio de WhatsApp arbitrário só com MCP_WHATSAPP_ENABLED=1 (padrão off) — evita abuso/prompt-injection.
- Rodar atrás de nginx com auth/HTTPS antes de expor publicamente (ver docs/SETUP-DOIS-LADOS.md).

Rodar local (teste):   python -m app.mcp_server
Transporte HTTP em 127.0.0.1:8765 (nginx faz o TLS + auth na exposição).
"""
from __future__ import annotations

import dataclasses
import os

from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP  # noqa: E402

from app import agenda as agenda_repo  # noqa: E402
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


# ─── LEITURA (seguro) ────────────────────────────────────────────────────────
@mcp.tool
def resumo_leads() -> dict:
    """Resumo do funil de leads (totais por estágio/temperatura)."""
    return leads_repo.dashboard()


@mcp.tool
def listar_leads(estagio: str | None = None, temperatura: str | None = None, limite: int = 30) -> list:
    """Lista leads do CRM. Filtra por estagio (ex.: 'quente') ou temperatura. Limite padrão 30."""
    return _j(leads_repo.listar(estagio=estagio, temperatura=temperatura, limit=min(limite, 100)))


@mcp.tool
def detalhar_lead(lead_id: int) -> dict | None:
    """Detalhe completo de um lead pelo ID."""
    return _j(leads_repo.detalhar(lead_id))


@mcp.tool
def listar_imoveis(bairro: str | None = None) -> list:
    """Lista os imóveis ATIVOS da carteira (opcional filtrar por bairro)."""
    return _j(imoveis_repo.listar_imoveis(somente_ativos=True, bairro=bairro))


@mcp.tool
def buscar_imovel(slug: str) -> dict | None:
    """Busca um imóvel pelo slug."""
    return _j(imoveis_repo.buscar_por_slug(slug))


@mcp.tool
def agenda_listar(status: str | None = None) -> list:
    """Lista compromissos da agenda (opcional filtrar por status: agendado/confirmado/realizado/cancelado)."""
    return _j(agenda_repo.listar(status=status))


@mcp.tool
def agenda_lembretes_pendentes(janela_horas: int = 24) -> list:
    """Compromissos com lembrete a enviar nas próximas N horas."""
    return _j(agenda_repo.lembretes_a_enviar(janela_horas=janela_horas))


@mcp.tool
def financeiro_resumo(ano: int | None = None, mes: int | None = None) -> dict:
    """Resumo financeiro (comissões, contas, pipeline da carteira) do mês."""
    return financeiro_repo.dashboard(ano=ano, mes=mes)


# ─── AÇÃO (só REGISTRADAS quando habilitadas — senão nem aparecem pro Cowork) ──
if WRITE:
    @mcp.tool
    def agenda_criar(titulo: str, inicio: str, fim: str, tipo: str = "visita",
                     lead_id: int | None = None, observacoes: str = "") -> dict:
        """Cria um compromisso na agenda. inicio/fim em ISO (YYYY-MM-DDTHH:MM). Horário de BRASÍLIA (UTC-3)."""
        novo = agenda_repo.criar(titulo=titulo, inicio=inicio, fim=fim, tipo=tipo,
                                 lead_id=lead_id, observacoes=observacoes)
        return {"ok": True, "id": novo}

if WRITE and WA_OK:
    @mcp.tool
    def enviar_whatsapp_lembrete(telefone: str, texto: str) -> dict:
        """Envia 1 mensagem de WhatsApp (lembrete). Só com MCP_WRITE_ENABLED=1 e MCP_WHATSAPP_ENABLED=1."""
        if not whatsapp_mod.disponivel():
            return {"erro": "WhatsApp não configurado"}
        return _j(whatsapp_mod.enviar_mensagem(telefone, texto))


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8765)
