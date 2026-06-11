from __future__ import annotations

import io
from datetime import date, datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.core.constants import STATUS_LABELS, FORMA_PAGAMENTO_LABELS

HOTEL_NOME = "Hotel Aconchego Do Velho Chico"
HOTEL_COR = colors.HexColor("#0D6EFD")


# =============================================================================
# Relatório de Vendas
# =============================================================================

def gerar_relatorio_vendas(
    vendas: list,
    totais: dict,
    filtros: dict,
    logo_path: str = None,
) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    story = []

    # Cabeçalho
    story += _cabecalho(logo_path, "RELATÓRIO DE VENDAS")
    story.append(Spacer(1, 0.3 * cm))

    # Período e filtros
    periodo = f"{_fmt_data(filtros.get('data_inicial'))} a {_fmt_data(filtros.get('data_final'))}"
    story.append(Paragraph(f"Período: {periodo}", _estilo(9, color="#6C757D")))
    story.append(Spacer(1, 0.4 * cm))

    # Cards de totais
    story.append(_cards_totais_vendas(totais))
    story.append(Spacer(1, 0.5 * cm))

    # Tabela de vendas
    story.append(Paragraph("<b>VENDAS DO PERÍODO</b>", _estilo(8, color="#6C757D")))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_tabela_vendas(vendas))
    story.append(Spacer(1, 0.3 * cm))

    # Rodapé
    story.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        _estilo(7, TA_RIGHT, color="#6C757D")
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# =============================================================================
# Relatório de Comissões
# =============================================================================

def gerar_relatorio_comissoes(
    comissoes: list,
    total_vendido: float,
    total_comissao: float,
    total_vendas: int,
    qtd_recepcionistas_ativos: int,
    filtros: dict,
    logo_path: str = None,
) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    story = []

    # Cabeçalho
    story += _cabecalho(logo_path, "RELATÓRIO DE COMISSÕES")
    story.append(Spacer(1, 0.3 * cm))

    # Período
    periodo = f"{_fmt_data(filtros.get('data_inicial'))} a {_fmt_data(filtros.get('data_final'))}"
    story.append(Paragraph(f"Período: {periodo}", _estilo(9, color="#6C757D")))
    story.append(Spacer(1, 0.4 * cm))

    # Cards de totais gerais
    story.append(_cards_totais_comissoes(total_vendas, total_vendido, total_comissao))
    story.append(Spacer(1, 0.5 * cm))

    # Tabela por recepcionista
    story.append(Paragraph("<b>COMISSÃO POR RECEPCIONISTA</b>", _estilo(8, color="#6C757D")))
    story.append(Spacer(1, 0.2 * cm))
    story.append(_tabela_comissoes(comissoes, total_comissao))
    story.append(Spacer(1, 0.5 * cm))

    # Critério do hotel
    if total_comissao > 0:
        story.append(Paragraph("<b>CRITÉRIO DO HOTEL</b>", _estilo(8, color="#6C757D")))
        story.append(Spacer(1, 0.2 * cm))
        story.append(_caixa_criterio_hotel(total_comissao, qtd_recepcionistas_ativos))
        story.append(Spacer(1, 0.3 * cm))

    # Rodapé
    story.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        _estilo(7, TA_RIGHT, color="#6C757D")
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# =============================================================================
# Componentes
# =============================================================================

def _cabecalho(logo_path: str = None, subtitulo: str = "") -> list:
    elementos = []

    if logo_path:
        try:
            from reportlab.platypus import Image
            img = Image(logo_path, width=3.5 * cm, height=1.6 * cm)
            img.hAlign = "CENTER"
            elementos.append(img)
            elementos.append(Spacer(1, 0.2 * cm))
        except Exception:
            pass

    elementos.append(Paragraph(
        HOTEL_NOME,
        _estilo(14, TA_CENTER, bold=True, color="#0D6EFD")
    ))
    if subtitulo:
        elementos.append(Paragraph(subtitulo, _estilo(10, TA_CENTER, color="#6C757D")))

    elementos.append(Spacer(1, 0.2 * cm))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=HOTEL_COR, spaceAfter=0))
    return elementos


def _cards_totais_vendas(totais: dict) -> Table:
    dados = [
        [
            Paragraph("VENDAS", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("ATIVAS", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("TOTAL VENDIDO", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("COMISSÕES", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("PASSAGEIROS", _estilo(8, TA_CENTER, color="#6C757D")),
        ],
        [
            Paragraph(str(totais["quantidade"]), _estilo(18, TA_CENTER, bold=True, color="#0D6EFD")),
            Paragraph(str(totais["quantidade_ativas"]), _estilo(18, TA_CENTER, bold=True)),
            Paragraph(_fmt_valor(totais["total_vendido"]), _estilo(16, TA_CENTER, bold=True, color="#198754")),
            Paragraph(_fmt_valor(totais["total_comissao"]), _estilo(16, TA_CENTER, bold=True, color="#0D6EFD")),
            Paragraph(str(totais["total_passageiros"]), _estilo(18, TA_CENTER, bold=True, color="#20C997")),
        ],
    ]

    tabela = Table(dados, colWidths=["20%", "20%", "20%", "20%", "20%"])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tabela


def _cards_totais_comissoes(total_vendas: int, total_vendido: float, total_comissao: float) -> Table:
    dados = [
        [
            Paragraph("TOTAL DE VENDAS", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("TOTAL VENDIDO", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("TOTAL COMISSÕES", _estilo(8, TA_CENTER, color="#6C757D")),
        ],
        [
            Paragraph(str(total_vendas), _estilo(20, TA_CENTER, bold=True, color="#0D6EFD")),
            Paragraph(_fmt_valor(total_vendido), _estilo(16, TA_CENTER, bold=True, color="#198754")),
            Paragraph(_fmt_valor(total_comissao), _estilo(16, TA_CENTER, bold=True, color="#0D6EFD")),
        ],
    ]

    tabela = Table(dados, colWidths=["33%", "33%", "34%"])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tabela


def _tabela_vendas(vendas: list) -> Table:
    cabecalho = [
        Paragraph("<b>Número</b>",      _estilo(8)),
        Paragraph("<b>Contratante</b>", _estilo(8)),
        Paragraph("<b>Passeio</b>",     _estilo(8)),
        Paragraph("<b>Data Saída</b>",  _estilo(8)),
        Paragraph("<b>Pax</b>",         _estilo(8, TA_CENTER)),
        Paragraph("<b>Valor</b>",       _estilo(8, TA_RIGHT)),
        Paragraph("<b>Comissão</b>",    _estilo(8, TA_RIGHT)),
        Paragraph("<b>Recepcionista</b>", _estilo(8)),
        Paragraph("<b>Status</b>",      _estilo(8, TA_CENTER)),
    ]

    linhas = [cabecalho]
    for v in vendas:
        linhas.append([
            Paragraph(v.numero_venda, _estilo(7)),
            Paragraph(v.contratante, _estilo(7)),
            Paragraph(v.passeio.nome, _estilo(7)),
            Paragraph(v.data_saida.strftime("%d/%m/%Y"), _estilo(7)),
            Paragraph(str(v.adultos + v.criancas), _estilo(7, TA_CENTER)),
            Paragraph(_fmt_valor(float(v.valor_total)), _estilo(7, TA_RIGHT)),
            Paragraph(_fmt_valor(float(v.valor_comissao)), _estilo(7, TA_RIGHT)),
            Paragraph(v.usuario.nome.split()[0], _estilo(7)),
            Paragraph(STATUS_LABELS.get(v.status, v.status), _estilo(7, TA_CENTER)),
        ])

    if not vendas:
        linhas.append([
            Paragraph("Nenhuma venda encontrada no período.", _estilo(8, TA_CENTER)),
            "", "", "", "", "", "", "", "",
        ])

    tabela = Table(linhas, colWidths=[3*cm, 4*cm, 3.5*cm, 2.5*cm, 1.2*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("SPAN",          (0, 1), (-1, 1)) if not vendas else ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
    ]))
    return tabela


def _tabela_comissoes(comissoes: list, total_comissao: float) -> Table:
    cabecalho = [
        Paragraph("<b>Recepcionista</b>",  _estilo(9)),
        Paragraph("<b>Qtd. Vendas</b>",    _estilo(9, TA_CENTER)),
        Paragraph("<b>Total Vendido</b>",  _estilo(9, TA_RIGHT)),
        Paragraph("<b>Total Comissão</b>", _estilo(9, TA_RIGHT)),
        Paragraph("<b>% do Total</b>",     _estilo(9, TA_CENTER)),
    ]

    linhas = [cabecalho]
    for c in comissoes:
        pct = f"{float(c.total_comissao) / total_comissao * 100:.1f}%" if total_comissao > 0 else "—"
        linhas.append([
            Paragraph(c.nome, _estilo(9)),
            Paragraph(str(c.quantidade_vendas), _estilo(9, TA_CENTER)),
            Paragraph(_fmt_valor(float(c.total_vendido)), _estilo(9, TA_RIGHT)),
            Paragraph(_fmt_valor(float(c.total_comissao)), _estilo(9, TA_RIGHT, color="#0D6EFD", bold=True)),
            Paragraph(pct, _estilo(9, TA_CENTER)),
        ])

    # Linha de total
    if comissoes:
        total_qtd = sum(c.quantidade_vendas for c in comissoes)
        total_vnd = sum(float(c.total_vendido) for c in comissoes)
        linhas.append([
            Paragraph("<b>Total</b>", _estilo(9)),
            Paragraph(f"<b>{total_qtd}</b>", _estilo(9, TA_CENTER)),
            Paragraph(f"<b>{_fmt_valor(total_vnd)}</b>", _estilo(9, TA_RIGHT)),
            Paragraph(f"<b>{_fmt_valor(total_comissao)}</b>", _estilo(9, TA_RIGHT, color="#0D6EFD")),
            Paragraph("<b>100%</b>", _estilo(9, TA_CENTER)),
        ])

    if not comissoes:
        linhas.append([Paragraph("Nenhuma comissão encontrada no período.", _estilo(9, TA_CENTER)), "", "", "", ""])

    n = len(linhas)
    tabela = Table(linhas, colWidths=["35%", "15%", "20%", "20%", "10%"])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
        ("BACKGROUND",    (0, n-1), (-1, n-1), colors.HexColor("#F8F9FA")) if comissoes else ("VALIGN", (0,0),(0,0),"MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, n-2), [colors.white, colors.HexColor("#F8F9FA")]) if comissoes else ("VALIGN",(0,0),(0,0),"MIDDLE"),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tabela


def _caixa_criterio_hotel(total_comissao: float, qtd_recepcionistas: int) -> Table:
    parte = total_comissao / 2
    por_recepcionista = parte / qtd_recepcionistas

    dados = [
        [
            Paragraph("Total Geral", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("÷ 2 = Parte dos Recepcionistas", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph(f"÷ {qtd_recepcionistas} recepcionista(s)", _estilo(8, TA_CENTER, color="#6C757D")),
            Paragraph("= Por Recepcionista", _estilo(8, TA_CENTER, color="#6C757D")),
        ],
        [
            Paragraph(_fmt_valor(total_comissao), _estilo(14, TA_CENTER, bold=True)),
            Paragraph(_fmt_valor(parte), _estilo(14, TA_CENTER, bold=True)),
            Paragraph(str(qtd_recepcionistas), _estilo(14, TA_CENTER, bold=True)),
            Paragraph(_fmt_valor(por_recepcionista), _estilo(16, TA_CENTER, bold=True, color="#0D6EFD")),
        ],
    ]

    tabela = Table(dados, colWidths=["25%", "25%", "25%", "25%"])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BACKGROUND",    (3, 0), (3, -1), colors.HexColor("#EBF3FF")),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tabela


# =============================================================================
# Helpers
# =============================================================================

def _fmt_valor(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_data(valor: str) -> str:
    if not valor:
        return "—"
    try:
        return date.fromisoformat(valor).strftime("%d/%m/%Y")
    except Exception:
        return valor


def _estilo(
    size: int = 10,
    align: int = TA_LEFT,
    bold: bool = False,
    color: str = "#212529",
) -> ParagraphStyle:
    return ParagraphStyle(
        "custom",
        fontSize=size,
        leading=size * 1.3,
        alignment=align,
        textColor=colors.HexColor(color),
        fontName="Helvetica-Bold" if bold else "Helvetica",
    )
