"""W5 — Geracao de proposta de compra em PDF (reportlab)."""
from __future__ import annotations

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

import os as _os

# Logo da Priscila (marca nos documentos). Caminho estavel no backend.
_LOGO_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "branding", "selo.png")


def _marca_dagua(canvas, doc) -> None:
    """Desenha a logo da Priscila como marca d'agua suave, centralizada em cada pagina."""
    if not _os.path.exists(_LOGO_PATH):
        return
    try:
        canvas.saveState()
        canvas.setFillAlpha(0.05)  # bem suave, nao atrapalha a leitura
        largura, altura = A4
        w = 11 * cm
        h = 11 * cm
        canvas.drawImage(_LOGO_PATH, (largura - w) / 2, (altura - h) / 2,
                         width=w, height=h, mask="auto", preserveAspectRatio=True)
        canvas.restoreState()
    except Exception:
        pass  # marca d'agua e cosmetica: nunca quebra a geracao do PDF


def _moeda(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_proposta_pdf(
    *,
    imovel: dict,
    lead: dict,
    valor_proposta: float,
    forma_pagamento: str = "Financiamento bancario",
    condicoes: str = "",
) -> bytes:
    """Retorna bytes do PDF da proposta de compra.

    Estilo editorial limpo, branding Priscila Vasconcelos.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title="Proposta de compra",
    )

    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle(
        "tit", parent=estilos["Title"], fontName="Helvetica-Bold",
        fontSize=18, textColor=colors.HexColor("#1a1a1a"),
        alignment=1, spaceAfter=18,
    )
    h2 = ParagraphStyle(
        "h2", parent=estilos["Heading2"], fontSize=12,
        textColor=colors.HexColor("#444"), spaceBefore=12, spaceAfter=6,
    )
    corpo = ParagraphStyle(
        "p", parent=estilos["BodyText"], fontSize=10, leading=14,
    )

    flow: list = []

    # Logo da Priscila no topo (marca o documento)
    if _os.path.exists(_LOGO_PATH):
        try:
            logo = Image(_LOGO_PATH, width=3.2 * cm, height=3.2 * cm)
            logo.hAlign = "CENTER"
            flow.append(logo)
            flow.append(Spacer(1, 8))
        except Exception:
            pass

    flow.append(Paragraph("PROPOSTA DE COMPRA", titulo))
    flow.append(Paragraph(
        "Priscila Vasconcelos Imoveis &nbsp;·&nbsp; CRECI/BA 29.231 "
        "&nbsp;·&nbsp; Vitoria da Conquista — BA",
        ParagraphStyle("sub", parent=corpo, alignment=1,
                       textColor=colors.HexColor("#777")),
    ))
    flow.append(Spacer(1, 16))

    agora = datetime.now(timezone.utc).astimezone()
    flow.append(Paragraph(f"Emitida em: {agora.strftime('%d/%m/%Y %H:%M')}", corpo))

    flow.append(Paragraph("Dados do imovel", h2))
    dados_imovel = [
        ["Titulo", str(imovel.get("titulo") or "—")],
        ["Endereco", str(imovel.get("endereco") or imovel.get("bairro") or "—")],
        ["Bairro", str(imovel.get("bairro") or "—")],
        ["Tipo", str(imovel.get("tipo") or "—")],
        ["Quartos", str(imovel.get("quartos") or "—")],
        ["Suites", str(imovel.get("suites") or "—")],
        ["Vagas", str(imovel.get("vagas") or "—")],
        ["Area util", f"{imovel.get('area_util') or '—'} m²"],
        ["Preco anunciado", _moeda(imovel.get("preco"))],
    ]
    flow.append(_tabela_chave_valor(dados_imovel))

    flow.append(Paragraph("Dados do proponente", h2))
    dados_lead = [
        ["Nome", str(lead.get("nome") or "—")],
        ["E-mail", str(lead.get("email") or "—")],
        ["Telefone", str(lead.get("telefone") or "—")],
        ["CPF", str(lead.get("cpf") or "—")],
    ]
    flow.append(_tabela_chave_valor(dados_lead))

    flow.append(Paragraph("Condicoes da proposta", h2))
    cond = [
        ["Valor proposto", _moeda(valor_proposta)],
        ["Forma de pagamento", forma_pagamento],
    ]
    flow.append(_tabela_chave_valor(cond))

    if condicoes:
        flow.append(Paragraph("Observacoes", h2))
        flow.append(Paragraph(condicoes.replace("\n", "<br/>"), corpo))

    flow.append(Spacer(1, 30))
    flow.append(Paragraph(
        "Esta proposta e valida por 7 (sete) dias corridos a contar da data de "
        "emissao e fica condicionada a aprovacao das partes e analise de credito.",
        ParagraphStyle("disc", parent=corpo, fontSize=9,
                       textColor=colors.HexColor("#666")),
    ))
    flow.append(Spacer(1, 40))
    flow.append(_assinaturas())

    doc.build(flow, onFirstPage=_marca_dagua, onLaterPages=_marca_dagua)
    return buffer.getvalue()


def _tabela_chave_valor(linhas: list[list[str]]) -> Table:
    t = Table(linhas, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#444")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#e0dccd")),
    ]))
    return t


def _assinaturas() -> Table:
    linha = "_" * 38
    t = Table(
        [
            [linha, linha],
            ["Proponente", "Priscila Vasconcelos · CRECI/BA 29.231"],
        ],
        colWidths=[8.5 * cm, 8.5 * cm],
    )
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#666")),
        ("TOPPADDING", (0, 1), (-1, 1), 4),
    ]))
    return t


__all__ = ["gerar_proposta_pdf"]
