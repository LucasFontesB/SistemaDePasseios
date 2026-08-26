from __future__ import annotations

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

HOTEL_NOME = "Hotel Aconchego Do Velho Chico"
HOTEL_COR = colors.HexColor("#0D6EFD")
LOGO_PATH_PADRAO = "app/static/img/logo.png"


def gerar_pdf_roomlist(grupo, roomlist_agrupada: list[tuple[str, list]], logo_path: str = None) -> bytes:
    """
    RN-G033: exportação da roomlist completa, agrupada por tipo de
    apartamento na ordem do cadastro (`ordem`) — o agrupamento vem pronto
    de GrupoRoomlistService.agrupar_por_tipo. Linha ainda vazia
    (hospede_nome nulo) aparece como "A definir". Mesmo padrão visual de
    app/utils/pdf_orcamento.py.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    logo = logo_path if logo_path else (LOGO_PATH_PADRAO if os.path.exists(LOGO_PATH_PADRAO) else None)
    story = []

    story += _cabecalho(logo)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        f'<font color="#0D6EFD"><b>{grupo.nome}</b></font>'
        f'&nbsp;&nbsp;•&nbsp;&nbsp;{grupo.codigo}',
        _estilo(11, TA_CENTER)
    ))
    story.append(Paragraph(
        f'{grupo.data_entrada.strftime("%d/%m/%Y")} a {grupo.data_saida.strftime("%d/%m/%Y")}',
        _estilo(9, TA_CENTER, color="#6C757D")
    ))
    story.append(Spacer(1, 0.4 * cm))

    for nome_tipo, itens in roomlist_agrupada:
        story.append(_titulo_secao(f"{nome_tipo} ({len(itens)})"))
        story.append(_tabela_roomlist(itens))
        story.append(Spacer(1, 0.3 * cm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DEE2E6")))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        f'Emitido em {datetime.now().strftime("%d/%m/%Y às %H:%M")}',
        _estilo(7, TA_CENTER, color="#6C757D")
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# =============================================================================
# Componentes (mesmo padrão visual de app/utils/pdf_orcamento.py)
# =============================================================================

def _cabecalho(logo_path: str = None) -> list:
    elementos = []

    if logo_path:
        try:
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
    elementos.append(Paragraph(
        "ROOMLIST DO GRUPO",
        _estilo(9, TA_CENTER, color="#6C757D")
    ))
    elementos.append(Spacer(1, 0.2 * cm))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=HOTEL_COR, spaceAfter=0))

    return elementos


def _titulo_secao(texto: str) -> Paragraph:
    return Paragraph(
        f'<b>{texto}</b>',
        ParagraphStyle(
            "secao",
            fontSize=9,
            textColor=HOTEL_COR,
            spaceBefore=4,
            spaceAfter=3,
        )
    )


def _tabela_roomlist(itens: list) -> Table:
    cabecalho = [
        Paragraph('<b>Apartamento</b>', _estilo(8)),
        Paragraph('<b>Hóspede</b>', _estilo(8)),
        Paragraph('<b>Documento</b>', _estilo(8)),
        Paragraph('<b>Check-in</b>', _estilo(8)),
        Paragraph('<b>Check-out</b>', _estilo(8)),
        Paragraph('<b>Observação</b>', _estilo(8)),
    ]
    data = [cabecalho]
    for item in itens:
        hospede = item.hospede_nome if item.hospede_nome else "A definir"
        if item.cortesia:
            hospede += " (cortesia)"
        data.append([
            Paragraph(item.apartamento or "—", _estilo(8)),
            Paragraph(hospede, _estilo(8)),
            Paragraph(item.documento or "—", _estilo(8)),
            Paragraph(item.check_in.strftime("%d/%m/%Y") if item.check_in else "—", _estilo(8)),
            Paragraph(item.check_out.strftime("%d/%m/%Y") if item.check_out else "—", _estilo(8)),
            Paragraph(item.observacao or "—", _estilo(8)),
        ])

    tabela = Table(data, colWidths=[2.3 * cm, 3.8 * cm, 2.8 * cm, 2.2 * cm, 2.2 * cm, None])
    tabela.setStyle(TableStyle([
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#F8F9FA")),
        ("LINEBELOW",      (0, 0), (-1, 0), 0.75, colors.HexColor("#DEE2E6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
        ("LINEBELOW",      (0, -1), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
    ]))
    return tabela


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
