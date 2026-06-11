from __future__ import annotations

import io
from datetime import date, datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.core.constants import FORMA_PAGAMENTO_LABELS

HOTEL_NOME = "Hotel Aconchego Do Velho Chico"
HOTEL_COR = colors.HexColor("#0D6EFD")


def gerar_relatorio_gerencial(dados: dict, filtros: dict, logo_path: str = None) -> bytes:
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
    story += _cabecalho(logo_path, "RELATÓRIO GERENCIAL")
    story.append(Spacer(1, 0.2 * cm))
    periodo = f"{_fmt_data(filtros.get('data_inicial'))} a {_fmt_data(filtros.get('data_final'))}"
    story.append(Paragraph(f"Período: {periodo}", _estilo(9, color="#6C757D")))
    story.append(Spacer(1, 0.4 * cm))

    # 1. Resumo geral
    story.append(KeepTogether(_secao_resumo(dados["resumo"])))
    story.append(Spacer(1, 0.4 * cm))

    # 2. Ranking de vendedores
    story.append(KeepTogether(_secao_ranking(
        "👤 RANKING DE VENDEDORES",
        ["Vendedor", "Vendas", "Passageiros", "Receita", "Comissão"],
        [[r.nome, str(r.quantidade), str(int(r.passageiros)),
          _fmt_valor(float(r.receita)), _fmt_valor(float(r.comissao))]
         for r in dados["vendedores"]],
        highlight_col=1,
    )))
    story.append(Spacer(1, 0.4 * cm))

    # 3. Ranking de passeios
    story.append(KeepTogether(_secao_ranking(
        "🗺️ PASSEIOS MAIS VENDIDOS",
        ["Passeio", "Vendas", "Passageiros", "Receita", "Comissão"],
        [[r.nome, str(r.quantidade), str(int(r.passageiros)),
          _fmt_valor(float(r.receita)), _fmt_valor(float(r.comissao))]
         for r in dados["passeios"]],
        highlight_col=1,
    )))
    story.append(Spacer(1, 0.4 * cm))

    # 4. Tipos de passeio
    story.append(KeepTogether(_secao_ranking(
        "🏷️ TIPOS DE PASSEIO",
        ["Tipo", "Vendas", "Receita"],
        [[r.nome, str(r.quantidade), _fmt_valor(float(r.receita))]
         for r in dados["tipos"]],
        highlight_col=1,
        col_widths=["50%", "25%", "25%"],
    )))
    story.append(Spacer(1, 0.4 * cm))

    # 5. Embarcações
    story.append(KeepTogether(_secao_ranking(
        "🚢 EMBARCAÇÕES MAIS UTILIZADAS",
        ["Embarcação", "Capacidade", "Embarques", "Passageiros"],
        [[r.nome, str(r.capacidade), str(r.quantidade), str(int(r.passageiros))]
         for r in dados["embarcacoes"]],
        highlight_col=2,
        col_widths=["40%", "20%", "20%", "20%"],
    )))
    story.append(Spacer(1, 0.4 * cm))

    # 6. Antecedência
    story.append(KeepTogether(_secao_antecedencia(dados["antecedencia"])))
    story.append(Spacer(1, 0.4 * cm))

    # 7. Horários populares + dias da semana lado a lado
    story.append(KeepTogether(_secao_horarios_dias(dados["horarios"], dados["dias_semana"])))
    story.append(Spacer(1, 0.4 * cm))

    # 8. Formas de pagamento
    story.append(KeepTogether(_secao_formas_pagamento(dados["formas_pagamento"])))
    story.append(Spacer(1, 0.4 * cm))

    # Rodapé
    story.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        _estilo(7, TA_RIGHT, color="#6C757D")
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# =============================================================================
# Seções
# =============================================================================

def _secao_resumo(resumo: dict) -> list:
    elementos = [_titulo_secao("📊 RESUMO GERAL")]

    linha1 = [
        [Paragraph("Total de Vendas", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Vendas Ativas", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Canceladas", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Taxa Cancelamento", _estilo(8, TA_CENTER, color="#6C757D"))],
        [Paragraph(str(resumo["total_vendas"]), _estilo(16, TA_CENTER, bold=True, color="#0D6EFD")),
         Paragraph(str(resumo["vendas_ativas"]), _estilo(16, TA_CENTER, bold=True, color="#198754")),
         Paragraph(str(resumo["canceladas"]), _estilo(16, TA_CENTER, bold=True, color="#DC3545")),
         Paragraph(f'{resumo["taxa_cancelamento"]}%', _estilo(16, TA_CENTER, bold=True, color="#FFC107"))],
    ]

    linha2 = [
        [Paragraph("Receita Total", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Total Comissões", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Ticket Médio", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Média Passageiros/Venda", _estilo(8, TA_CENTER, color="#6C757D"))],
        [Paragraph(_fmt_valor(resumo["receita_total"]), _estilo(13, TA_CENTER, bold=True, color="#198754")),
         Paragraph(_fmt_valor(resumo["comissao_total"]), _estilo(13, TA_CENTER, bold=True, color="#0D6EFD")),
         Paragraph(_fmt_valor(resumo["ticket_medio"]), _estilo(13, TA_CENTER, bold=True)),
         Paragraph(f'{resumo["media_passageiros"]:.1f}', _estilo(13, TA_CENTER, bold=True))],
    ]

    for linhas in [linha1, linha2]:
        t = Table(linhas, colWidths=["25%", "25%", "25%", "25%"])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
            ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
            ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elementos.append(t)
        elementos.append(Spacer(1, 0.2 * cm))

    return elementos


def _secao_ranking(titulo, cabecalho, linhas, highlight_col=1, col_widths=None) -> list:
    elementos = [_titulo_secao(titulo)]

    if not linhas:
        elementos.append(Paragraph("Nenhum dado encontrado no período.", _estilo(8, color="#6C757D")))
        return elementos

    col_widths = col_widths or (["40%"] + [f"{60 // (len(cabecalho)-1)}%" for _ in range(len(cabecalho)-1)])

    data = [[Paragraph(f"<b>{c}</b>", _estilo(8)) for c in cabecalho]]
    for i, linha in enumerate(linhas):
        medal = ["🥇", "🥈", "🥉"]
        prefix = medal[i] + " " if i < 3 else f"{i+1}. "
        row = [Paragraph(prefix + linha[0], _estilo(8))]
        for j, cel in enumerate(linha[1:], 1):
            row.append(Paragraph(
                f"<b>{cel}</b>" if j == highlight_col else cel,
                _estilo(8, TA_RIGHT if j >= highlight_col else TA_LEFT,
                        bold=(j == highlight_col),
                        color="#0D6EFD" if (j == highlight_col and i == 0) else "#212529")
            ))
        data.append(row)

    n = len(data)
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("BOX",            (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("INNERGRID",      (0, 0), (-1, -1), 0.3, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(t)
    return elementos


def _secao_antecedencia(ant: dict) -> list:
    elementos = [_titulo_secao("📅 ANTECEDÊNCIA DE RESERVA")]

    total = ant["no_dia"] + ant["ate_7_dias"] + ant["ate_30_dias"] + ant["mais_30_dias"]

    dados = [
        [Paragraph("Média de Antecedência", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("No mesmo dia", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Até 7 dias antes", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("8 a 30 dias antes", _estilo(8, TA_CENTER, color="#6C757D")),
         Paragraph("Mais de 30 dias", _estilo(8, TA_CENTER, color="#6C757D"))],
        [Paragraph(f'{ant["media_dias"]} dias', _estilo(14, TA_CENTER, bold=True, color="#0D6EFD")),
         Paragraph(_pct(ant["no_dia"], total), _estilo(13, TA_CENTER, bold=True)),
         Paragraph(_pct(ant["ate_7_dias"], total), _estilo(13, TA_CENTER, bold=True)),
         Paragraph(_pct(ant["ate_30_dias"], total), _estilo(13, TA_CENTER, bold=True)),
         Paragraph(_pct(ant["mais_30_dias"], total), _estilo(13, TA_CENTER, bold=True))],
    ]

    t = Table(dados, colWidths=["20%", "20%", "20%", "20%", "20%"])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#F8F9FA")),
        ("BACKGROUND",    (0, 0), (0, -1), colors.HexColor("#EBF3FF")),
        ("BOX",           (0, 0), (-1, -1), 1, colors.HexColor("#DEE2E6")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(t)
    return elementos


def _secao_horarios_dias(horarios: list, dias: list) -> list:
    elementos = []

    # Horários
    t_hor_data = [[Paragraph("<b>Horário</b>", _estilo(8)), Paragraph("<b>Embarques</b>", _estilo(8, TA_RIGHT))]]
    for h in horarios:
        t_hor_data.append([
            Paragraph(h.horario_saida.strftime("%H:%M"), _estilo(9)),
            Paragraph(str(h.quantidade), _estilo(9, TA_RIGHT, bold=True, color="#0D6EFD")),
        ])
    t_hor = Table(t_hor_data, colWidths=["60%", "40%"])
    t_hor.setStyle(_estilo_tabela_simples())

    # Dias da semana
    max_qtd = max((d["quantidade"] for d in dias), default=1) or 1
    t_dia_data = [[Paragraph("<b>Dia</b>", _estilo(8)), Paragraph("<b>Embarques</b>", _estilo(8, TA_RIGHT))]]
    for d in dias:
        destaque = d["quantidade"] == max_qtd and d["quantidade"] > 0
        t_dia_data.append([
            Paragraph(d["dia"], _estilo(9, bold=destaque)),
            Paragraph(str(d["quantidade"]), _estilo(9, TA_RIGHT, bold=destaque,
                      color="#0D6EFD" if destaque else "#212529")),
        ])
    t_dia = Table(t_dia_data, colWidths=["60%", "40%"])
    t_dia.setStyle(_estilo_tabela_simples())

    container = Table(
        [[
            [_titulo_secao("⏰ HORÁRIOS MAIS POPULARES"), t_hor],
            [_titulo_secao("📆 EMBARQUES POR DIA DA SEMANA"), t_dia],
        ]],
        colWidths=["48%", "52%"],
    )
    container.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("LINEBEFORE",   (1, 0), (1, -1), 0.5, colors.HexColor("#DEE2E6")),
    ]))
    elementos.append(container)
    return elementos


def _secao_formas_pagamento(formas: list) -> list:
    elementos = [_titulo_secao("💳 FORMAS DE PAGAMENTO")]

    if not formas:
        elementos.append(Paragraph("Nenhum dado encontrado no período.", _estilo(8, color="#6C757D")))
        return elementos

    total = sum(f.quantidade for f in formas)
    data = [[Paragraph("<b>Forma</b>", _estilo(8)),
             Paragraph("<b>Vendas</b>", _estilo(8, TA_CENTER)),
             Paragraph("<b>%</b>", _estilo(8, TA_CENTER)),
             Paragraph("<b>Receita</b>", _estilo(8, TA_RIGHT))]]

    for f in formas:
        label = FORMA_PAGAMENTO_LABELS.get(f.forma_pagamento, "Não informada") if f.forma_pagamento else "Não informada"
        data.append([
            Paragraph(label, _estilo(9)),
            Paragraph(str(f.quantidade), _estilo(9, TA_CENTER)),
            Paragraph(_pct(f.quantidade, total), _estilo(9, TA_CENTER)),
            Paragraph(_fmt_valor(float(f.receita)), _estilo(9, TA_RIGHT)),
        ])

    t = Table(data, colWidths=["40%", "20%", "15%", "25%"])
    t.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("BOX",            (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("INNERGRID",      (0, 0), (-1, -1), 0.3, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elementos.append(t)
    return elementos


# =============================================================================
# Helpers
# =============================================================================

def _titulo_secao(texto: str) -> Paragraph:
    return Paragraph(f"<b>{texto}</b>", ParagraphStyle(
        "secao", fontSize=9, textColor=colors.HexColor("#212529"),
        spaceBefore=2, spaceAfter=4,
        borderPad=4, backColor=colors.HexColor("#E9ECEF"),
        borderWidth=0, leftIndent=0,
    ))


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
    elementos.append(Paragraph(HOTEL_NOME, _estilo(14, TA_CENTER, bold=True, color="#0D6EFD")))
    if subtitulo:
        elementos.append(Paragraph(subtitulo, _estilo(10, TA_CENTER, color="#6C757D")))
    elementos.append(Spacer(1, 0.2 * cm))
    elementos.append(HRFlowable(width="100%", thickness=1.5, color=HOTEL_COR, spaceAfter=0))
    return elementos


def _estilo_tabela_simples():
    return TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), colors.HexColor("#E9ECEF")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
        ("BOX",            (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
        ("INNERGRID",      (0, 0), (-1, -1), 0.3, colors.HexColor("#DEE2E6")),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 5),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ])


def _fmt_valor(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_data(valor: str) -> str:
    if not valor:
        return "—"
    try:
        return date.fromisoformat(valor).strftime("%d/%m/%Y")
    except Exception:
        return valor


def _pct(valor: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{valor / total * 100:.1f}%"


def _estilo(size=10, align=TA_LEFT, bold=False, color="#212529") -> ParagraphStyle:
    return ParagraphStyle(
        "c", fontSize=size, leading=size * 1.3, alignment=align,
        textColor=colors.HexColor(color),
        fontName="Helvetica-Bold" if bold else "Helvetica",
    )
