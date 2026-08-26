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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models.grupo_orcamento import GrupoOrcamento
from app.core.constants import ORCAMENTO_STATUS_LABELS, GRUPO_STATUS_LABELS, FORMA_PAGAMENTO_LABELS

HOTEL_NOME = "Hotel Aconchego Do Velho Chico"
HOTEL_COR = colors.HexColor("#0D6EFD")
LOGO_PATH_PADRAO = "app/static/img/logo.png"


def _money(valor) -> str:
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_pdf_orcamento(orcamento: GrupoOrcamento, logo_path: str = None) -> bytes:
    """
    Gera o PDF do orçamento na versão informada.

    RN-G022 (substitui a RN-G016, revogada): mostra as duas tarifas — net e
    sistema — lado a lado por tipo de apartamento, mais quantidade total,
    valor total geral, pagamentos recebidos, saldo, status e prazos. Tudo
    lido exclusivamente do snapshot da versão (RN-G013), nunca recalculado
    a partir do grupo atual — reimprimir uma versão antiga sempre reproduz
    o documento exatamente como foi enviado.
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

    grupo = orcamento.grupo
    logo = logo_path if logo_path else (LOGO_PATH_PADRAO if os.path.exists(LOGO_PATH_PADRAO) else None)
    story = []

    story += _cabecalho(logo)
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        f'<font color="#0D6EFD"><b>Orçamento — Versão {orcamento.versao}</b></font>'
        f'&nbsp;&nbsp;•&nbsp;&nbsp;{ORCAMENTO_STATUS_LABELS.get(orcamento.status, orcamento.status)}',
        _estilo(11, TA_CENTER)
    ))
    story.append(Spacer(1, 0.4 * cm))

    dados_grupo = [
        ("Grupo", grupo.nome),
        ("Código", grupo.codigo),
        ("Responsável", grupo.responsavel or "—"),
        ("Telefone", grupo.telefone or "—"),
        ("E-mail", grupo.email or "—"),
    ]
    intermediario = grupo.agencia.nome if grupo.agencia else (grupo.guia.nome if grupo.guia else "Direto")
    entrada = orcamento.data_entrada_snapshot or grupo.data_entrada
    saida = orcamento.data_saida_snapshot or grupo.data_saida
    dados_periodo = [
        ("Intermediário", intermediario),
        ("Entrada", entrada.strftime("%d/%m/%Y")),
        ("Saída", saida.strftime("%d/%m/%Y")),
        ("Noites", str(orcamento.noites)),
        ("Hóspedes", str(orcamento.qtd_hospedes)),
        ("Apartamentos", str(orcamento.apartamentos_ocupados)),
    ]

    story.append(_duas_colunas(
        ("DADOS DO GRUPO", dados_grupo),
        ("PERÍODO E OCUPAÇÃO", dados_periodo),
    ))
    story.append(Spacer(1, 0.3 * cm))

    story.append(_titulo_secao("TARIFA POR TIPO DE APARTAMENTO"))
    story.append(_tabela_apartamentos(orcamento))
    story.append(Spacer(1, 0.3 * cm))

    story.append(_caixa_valores(orcamento))
    story.append(Spacer(1, 0.3 * cm))

    dados_status_prazos = [
        ("Status do Grupo", GRUPO_STATUS_LABELS.get(orcamento.status_snapshot, orcamento.status_snapshot or "—")),
        ("Saldo", _money(orcamento.saldo_snapshot)),
    ]
    if orcamento.prazo_deadline_snapshot:
        dados_status_prazos.append(("Prazo Deadline", orcamento.prazo_deadline_snapshot.strftime("%d/%m/%Y")))
    if orcamento.prazo_roomlist_snapshot:
        dados_status_prazos.append(("Prazo Roomlist", orcamento.prazo_roomlist_snapshot.strftime("%d/%m/%Y")))
    if orcamento.validade:
        dados_status_prazos.append(("Validade da Proposta", orcamento.validade.strftime("%d/%m/%Y")))
    story.append(_titulo_secao("STATUS, SALDO E PRAZOS"))
    story.append(_tabela_dados(dados_status_prazos))
    story.append(Spacer(1, 0.3 * cm))

    pagamentos = orcamento.pagamentos
    if pagamentos:
        story.append(_titulo_secao("PAGAMENTOS RECEBIDOS ATÉ ESTA VERSÃO"))
        story.append(_tabela_pagamentos(pagamentos))
        story.append(Spacer(1, 0.3 * cm))

    if orcamento.condicoes:
        story.append(_titulo_secao("CONDIÇÕES ADICIONAIS"))
        story.append(Paragraph(orcamento.condicoes, _estilo(9)))
        story.append(Spacer(1, 0.3 * cm))

    if orcamento.motivo:
        story.append(_titulo_secao("OBSERVAÇÃO DESTA VERSÃO"))
        story.append(Paragraph(orcamento.motivo, _estilo(9)))
        story.append(Spacer(1, 0.3 * cm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DEE2E6")))
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph(
        f'Emitido em {datetime.now().strftime("%d/%m/%Y às %H:%M")}  •  '
        f'Gerado por {orcamento.usuario.nome}',
        _estilo(7, TA_CENTER, color="#6C757D")
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# =============================================================================
# Componentes (mesmo padrão visual de app/services/pdf_service.py)
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
        "ORÇAMENTO DE HOSPEDAGEM — GRUPO",
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
            fontSize=8,
            textColor=colors.HexColor("#6C757D"),
            spaceBefore=3,
            spaceAfter=3,
        )
    )


def _tabela_dados(linhas: list[tuple]) -> Table:
    data = [[
        Paragraph(f'<b>{label}</b>', _estilo(9)),
        Paragraph(str(valor), _estilo(9)),
    ] for label, valor in linhas]

    tabela = Table(data, colWidths=[5 * cm, None])
    tabela.setStyle(TableStyle([
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 6),
        ("LINEBELOW",      (0, -1), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
    ]))
    return tabela


def _tabela_apartamentos(orcamento: GrupoOrcamento) -> Table:
    cabecalho = [
        Paragraph('<b>Tipo</b>', _estilo(8)),
        Paragraph('<b>Qtd</b>', _estilo(8, TA_CENTER)),
        Paragraph('<b>Diária Net</b>', _estilo(8, TA_RIGHT)),
        Paragraph('<b>Diária Sistema</b>', _estilo(8, TA_RIGHT)),
        Paragraph('<b>Subtotal Net</b>', _estilo(8, TA_RIGHT)),
        Paragraph('<b>Subtotal Sistema</b>', _estilo(8, TA_RIGHT)),
    ]
    linhas = orcamento.apartamentos
    data = [cabecalho]
    for l in linhas:
        data.append([
            Paragraph(l.tipo_apartamento_nome, _estilo(8)),
            Paragraph(str(l.quantidade), _estilo(8, TA_CENTER)),
            Paragraph(_money(l.valor_diaria_net), _estilo(8, TA_RIGHT)),
            Paragraph(_money(l.valor_diaria_sistema), _estilo(8, TA_RIGHT)),
            Paragraph(_money(l.valor_total_net), _estilo(8, TA_RIGHT)),
            Paragraph(_money(l.valor_total_sistema), _estilo(8, TA_RIGHT)),
        ])
    if not linhas:
        data.append([Paragraph("Nenhum tipo de apartamento nesta versão.", _estilo(8)), "", "", "", "", ""])

    tabela = Table(data, colWidths=[None, 1.5 * cm, 2.6 * cm, 2.8 * cm, 2.6 * cm, 2.8 * cm])
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


def _tabela_pagamentos(pagamentos: list) -> Table:
    cabecalho = [
        Paragraph('<b>Data</b>', _estilo(8)),
        Paragraph('<b>Valor</b>', _estilo(8, TA_RIGHT)),
        Paragraph('<b>Forma</b>', _estilo(8)),
    ]
    data = [cabecalho]
    for p in pagamentos:
        data.append([
            Paragraph(p.data_pagamento.strftime("%d/%m/%Y"), _estilo(8)),
            Paragraph(_money(p.valor), _estilo(8, TA_RIGHT)),
            Paragraph(FORMA_PAGAMENTO_LABELS.get(p.forma_pagamento, p.forma_pagamento or "—"), _estilo(8)),
        ])

    tabela = Table(data, colWidths=[3.5 * cm, 3.5 * cm, None])
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


def _duas_colunas(esq: tuple, dir: tuple) -> Table:
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
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBEFORE",    (1, 0), (1, -1), 0.5, colors.HexColor("#DEE2E6")),
    ]))
    return container


def _caixa_valores(orcamento: GrupoOrcamento) -> Table:
    # RN-G027/RN-G034: sistema é a base financeira (pagamento/saldo do
    # hotel) — recebe o destaque principal. Net é referência de agência/
    # comissão, mostrado em estilo secundário, mas não removido.
    bloco_qtd = Table([
        [Paragraph("QTD. TOTAL", _estilo(8, TA_CENTER, color="#6C757D"))],
        [Paragraph(f'<b>{orcamento.qtd_apartamentos}</b>', _estilo(13, TA_CENTER, bold=True))],
    ], colWidths=["100%"])
    bloco_sistema = Table([
        [Paragraph("VALOR TOTAL (SISTEMA)", _estilo(8, TA_CENTER, color="#6C757D"))],
        [Paragraph(f'<b>{_money(orcamento.valor_total_sistema)}</b>', _estilo(14, TA_CENTER, color="#198754", bold=True))],
    ], colWidths=["100%"])
    bloco_net = Table([
        [Paragraph("VALOR TOTAL NET (REF. AGÊNCIA)", _estilo(8, TA_CENTER, color="#6C757D"))],
        [Paragraph(_money(orcamento.valor_total_net), _estilo(11, TA_CENTER, color="#6C757D"))],
    ], colWidths=["100%"])
    for bloco in (bloco_qtd, bloco_sistema, bloco_net):
        bloco.setStyle(TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))

    tabela = Table([[bloco_qtd, bloco_sistema, bloco_net]], colWidths=["20%", "40%", "40%"])
    tabela.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
        ("LINEBEFORE",    (1, 0), (1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("LINEBEFORE",    (2, 0), (2, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
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
