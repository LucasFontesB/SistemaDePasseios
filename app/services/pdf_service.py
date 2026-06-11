from __future__ import annotations

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.venda import Venda
from app.core.constants import FORMA_PAGAMENTO_LABELS, STATUS_LABELS

HOTEL_NOME = "Hotel Aconchego Do Velho Chico"
HOTEL_COR = colors.HexColor("#0D6EFD")
FORMA_LABELS = FORMA_PAGAMENTO_LABELS


def gerar_voucher_recibo(venda: Venda, logo_path: str = None) -> bytes:
    """
    Gera PDF com voucher (parte superior, sem logo) e recibo (parte inferior, com logo)
    separados por linha pontilhada de corte. Tudo em uma página A4.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.0 * cm,
        rightMargin=1.0 * cm,
        topMargin=0.8 * cm,
        bottomMargin=0.8 * cm,
    )

    story = []

    # VOUCHER — com logo
    story += _secao_voucher(venda, logo_path)

    # Linha de corte
    story.append(Spacer(1, 0.25 * cm))
    story.append(_linha_corte())
    story.append(Spacer(1, 0.25 * cm))

    # RECIBO — sem logo
    story += _secao_recibo(venda, None)

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# =============================================================================
# Voucher
# =============================================================================

def _secao_voucher(venda: Venda, logo_path: str = None) -> list:
    elementos = []

    # Cabeçalho com logo
    elementos += _cabecalho(logo_path=logo_path, subtitulo="VOUCHER DE RESERVA")
    elementos.append(Spacer(1, 0.2 * cm))

    # Número e status
    elementos.append(Paragraph(
        f'<font color="#0D6EFD"><b>Nº {venda.numero_venda}</b></font>'
        f'&nbsp;&nbsp;•&nbsp;&nbsp;{STATUS_LABELS.get(venda.status, venda.status)}',
        _estilo(10, TA_CENTER)
    ))
    elementos.append(Spacer(1, 0.3 * cm))

    # Dados em duas colunas lado a lado
    dados_passeio = [
        ("Passeio",       venda.passeio.nome),
        ("Tipo",          venda.tipo_passeio.nome),
        ("Embarcação",    venda.embarcacao.nome if venda.embarcacao else "—"),
        ("Data de Saída", venda.data_saida.strftime("%d/%m/%Y")),
        ("Horário",       venda.horario_saida.strftime("%H:%M") if venda.horario_saida else "—"),
    ]
    dados_contratante = [
        ("Contratante", venda.contratante),
        ("Telefone",    venda.telefone or "—"),
        ("Adultos",     str(venda.adultos)),
        ("Crianças",    str(venda.criancas)),
        ("Total Pax",   str(venda.adultos + venda.criancas)),
    ]

    elementos.append(_duas_colunas(
        ("DADOS DO PASSEIO", dados_passeio),
        ("DADOS DO CONTRATANTE", dados_contratante),
    ))

    if venda.observacao:
        elementos.append(Spacer(1, 0.2 * cm))
        elementos.append(_titulo_secao("OBSERVAÇÕES"))
        elementos.append(Paragraph(venda.observacao, _estilo(8)))

    elementos.append(Spacer(1, 0.15 * cm))
    elementos.append(Paragraph(
        f'Emitido em {datetime.now().strftime("%d/%m/%Y às %H:%M")}',
        _estilo(7, TA_RIGHT, color="#6C757D")
    ))

    return elementos


# =============================================================================
# Recibo
# =============================================================================

def _secao_recibo(venda: Venda, logo_path: str = None) -> list:
    elementos = []

    # Cabeçalho com logo
    elementos += _cabecalho(logo_path=logo_path, subtitulo="RECIBO DE PAGAMENTO")
    elementos.append(Spacer(1, 0.2 * cm))

    elementos.append(Paragraph(
        f'<font color="#0D6EFD"><b>Ref. Venda Nº {venda.numero_venda}</b></font>',
        _estilo(10, TA_CENTER)
    ))
    elementos.append(Spacer(1, 0.3 * cm))

    forma = FORMA_LABELS.get(venda.forma_pagamento, "Não informada") if venda.forma_pagamento else "Não informada"

    dados_recibo = [
        ("Contratante",         venda.contratante),
        ("Passeio",             venda.passeio.nome),
        ("Data do Passeio",     venda.data_saida.strftime("%d/%m/%Y")),
        ("Passageiros",         f"{venda.adultos + venda.criancas} ({venda.adultos} adulto(s), {venda.criancas} criança(s))"),
        ("Forma de Pagamento",  forma),
    ]

    elementos.append(_titulo_secao("DADOS DO PAGAMENTO"))
    elementos.append(_tabela_dados(dados_recibo))
    elementos.append(Spacer(1, 0.3 * cm))

    # Valor em destaque
    elementos.append(_caixa_valor(venda))
    elementos.append(Spacer(1, 0.35 * cm))

    # Assinaturas
    elementos.append(_linha_assinatura())
    elementos.append(Spacer(1, 0.15 * cm))

    elementos.append(Paragraph(
        f'Emitido em {datetime.now().strftime("%d/%m/%Y às %H:%M")}  •  '
        f'Registrado por {venda.usuario.nome}',
        _estilo(7, TA_CENTER, color="#6C757D")
    ))

    return elementos


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
        _estilo(13, TA_CENTER, bold=True, color="#0D6EFD")
    ))

    if subtitulo:
        elementos.append(Paragraph(
            subtitulo,
            _estilo(9, TA_CENTER, color="#6C757D")
        ))

    elementos.append(Spacer(1, 0.2 * cm))
    elementos.append(HRFlowable(
        width="100%", thickness=1.5,
        color=HOTEL_COR, spaceAfter=0
    ))

    return elementos


def _titulo_secao(texto: str) -> Paragraph:
    return Paragraph(
        f'<b>{texto}</b>',
        ParagraphStyle(
            "secao",
            fontSize=7,
            textColor=colors.HexColor("#6C757D"),
            spaceBefore=3,
            spaceAfter=2,
        )
    )


def _tabela_dados(linhas: list[tuple]) -> Table:
    data = [[
        Paragraph(f'<b>{label}</b>', _estilo(8)),
        Paragraph(str(valor), _estilo(8)),
    ] for label, valor in linhas]

    tabela = Table(data, colWidths=[4 * cm, None])
    tabela.setStyle(TableStyle([
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("TOPPADDING",     (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 3),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
        ("LINEBELOW",      (0, -1), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
    ]))
    return tabela


def _duas_colunas(esq: tuple, dir: tuple) -> Table:
    """Renderiza duas tabelas de dados lado a lado."""
    titulo_esq, dados_esq = esq
    titulo_dir, dados_dir = dir

    col_esq = [
        [Paragraph(f'<b>{titulo_esq}</b>', _estilo(7, color="#6C757D"))],
    ] + [[
        Paragraph(f'<b>{l}</b>', _estilo(8)),
        Paragraph(str(v), _estilo(8)),
    ] for l, v in dados_esq]

    col_dir = [
        [Paragraph(f'<b>{titulo_dir}</b>', _estilo(7, color="#6C757D"))],
    ] + [[
        Paragraph(f'<b>{l}</b>', _estilo(8)),
        Paragraph(str(v), _estilo(8)),
    ] for l, v in dados_dir]

    tab_esq = Table(col_esq, colWidths=[3 * cm, None])
    tab_esq.setStyle(TableStyle([
        ("SPAN",           (0, 0), (-1, 0)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("TOPPADDING",     (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 2),
        ("LEFTPADDING",    (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 4),
    ]))

    tab_dir = Table(col_dir, colWidths=[3 * cm, None])
    tab_dir.setStyle(TableStyle([
        ("SPAN",           (0, 0), (-1, 0)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("TOPPADDING",     (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 2),
        ("LEFTPADDING",    (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 4),
    ]))

    container = Table([[tab_esq, tab_dir]], colWidths=["50%", "50%"])
    container.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("LINEBEFORE",   (1, 0), (1, -1), 0.5, colors.HexColor("#DEE2E6")),
    ]))
    return container


def _caixa_valor(venda: Venda) -> Table:
    valor_fmt = f"R$ {float(venda.valor_total):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    data = [[
        Paragraph("VALOR TOTAL PAGO", _estilo(8, TA_CENTER, color="#6C757D")),
        Paragraph(f'<b>{valor_fmt}</b>', _estilo(16, TA_CENTER, color="#198754", bold=True)),
    ]]
    tabela = Table(data, colWidths=["40%", "60%"])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return tabela


def _linha_assinatura() -> Table:
    data = [[
        Paragraph("_________________________", _estilo(9, TA_CENTER)),
        Paragraph("_________________________", _estilo(9, TA_CENTER)),
    ], [
        Paragraph("Assinatura do Cliente", _estilo(7, TA_CENTER, color="#6C757D")),
        Paragraph("Assinatura do Responsável", _estilo(7, TA_CENTER, color="#6C757D")),
    ]]
    tabela = Table(data, colWidths=["50%", "50%"])
    tabela.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tabela


def _linha_corte() -> Table:
    data = [[Paragraph("✂  RECORTE AQUI  ✂", _estilo(8, TA_CENTER, color="#6C757D"))]]
    tabela = Table(data, colWidths=["100%"])
    tabela.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LINEABOVE",     (0, 0), (-1, 0), 1, colors.HexColor("#ADB5BD"), 1, 3),
        ("LINEBELOW",     (0, 0), (-1, 0), 1, colors.HexColor("#ADB5BD"), 1, 3),
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