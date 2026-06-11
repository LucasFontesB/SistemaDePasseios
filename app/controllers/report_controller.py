from __future__ import annotations

import uuid
import os
from datetime import date, datetime

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.core.constants import STATUS_CHOICES
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.tour_repository import TourRepository
from app.services.report_pdf_service import gerar_relatorio_vendas, gerar_relatorio_comissoes

router = APIRouter()

LOGO_PATH = "app/static/img/logo.png"


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


def _require_gerencia(session: dict) -> bool:
    return session and session.get("perfil") in ("ADMIN", "GERENCIA")


def _parse_date(valor: str) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return None


# =============================================================================
# Relatório de Vendas
# =============================================================================

@router.get("/relatorios/vendas", response_class=HTMLResponse)
async def relatorio_vendas(
    request: Request,
    db: Session = Depends(get_db),
    data_inicial: str = None,
    data_final: str = None,
    passeio_id: str = None,
    status: str = None,
    usuario_id: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = ReportRepository(db)

    # Período padrão: mês atual
    hoje = date.today()
    di = _parse_date(data_inicial) or date(hoje.year, hoje.month, 1)
    df = _parse_date(data_final) or hoje

    vendas = repo.vendas(
        data_inicial=di,
        data_final=df,
        passeio_id=passeio_id or None,
        status=status or None,
        usuario_id=usuario_id or None,
    )

    totais = repo.totais_vendas(vendas)
    passeios = TourRepository(db).list_passeios()
    usuarios = repo.list_usuarios_ativos()

    return templates.TemplateResponse("relatorios/vendas.html", {
        "request": request,
        "usuario": usuario,
        "active": "rel_vendas",
        "vendas": vendas,
        "totais": totais,
        "passeios": passeios,
        "usuarios": usuarios,
        "status_choices": STATUS_CHOICES,
        "filtros": {
            "data_inicial": di.isoformat(),
            "data_final": df.isoformat(),
            "passeio_id": passeio_id or "",
            "status": status or "",
            "usuario_id": usuario_id or "",
        },
    })


# =============================================================================
# Relatório de Comissões
# =============================================================================

@router.get("/relatorios/comissoes", response_class=HTMLResponse)
async def relatorio_comissoes(
    request: Request,
    db: Session = Depends(get_db),
    data_inicial: str = None,
    data_final: str = None,
    usuario_id: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = ReportRepository(db)

    # Período padrão: mês atual
    hoje = date.today()
    di = _parse_date(data_inicial) or date(hoje.year, hoje.month, 1)
    df = _parse_date(data_final) or hoje

    comissoes = repo.comissoes_por_usuario(
        data_inicial=di,
        data_final=df,
        usuario_id=usuario_id or None,
    )

    # Totais gerais
    total_vendido = sum(float(c.total_vendido or 0) for c in comissoes)
    total_comissao = sum(float(c.total_comissao or 0) for c in comissoes)
    total_vendas = sum(c.quantidade_vendas for c in comissoes)

    usuarios = repo.list_usuarios_ativos()
    qtd_recepcionistas_ativos = max(repo.count_recepcionistas_ativos(), 1)

    return templates.TemplateResponse("relatorios/comissoes.html", {
        "request": request,
        "usuario": usuario,
        "active": "rel_comissoes",
        "comissoes": comissoes,
        "usuarios": usuarios,
        "total_vendido": total_vendido,
        "total_comissao": total_comissao,
        "total_vendas": total_vendas,
        "qtd_recepcionistas_ativos": qtd_recepcionistas_ativos,
        "filtros": {
            "data_inicial": di.isoformat(),
            "data_final": df.isoformat(),
            "usuario_id": usuario_id or "",
        },
    })


# =============================================================================
# PDF — Relatório de Vendas
# =============================================================================

@router.get("/relatorios/vendas/pdf")
async def relatorio_vendas_pdf(
    request: Request,
    db: Session = Depends(get_db),
    data_inicial: str = None,
    data_final: str = None,
    passeio_id: str = None,
    status: str = None,
    usuario_id: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    repo = ReportRepository(db)
    hoje = date.today()
    di = _parse_date(data_inicial) or date(hoje.year, hoje.month, 1)
    df = _parse_date(data_final) or hoje

    vendas = repo.vendas(
        data_inicial=di,
        data_final=df,
        passeio_id=passeio_id or None,
        status=status or None,
        usuario_id=usuario_id or None,
    )
    totais = repo.totais_vendas(vendas)

    logo = LOGO_PATH if os.path.exists(LOGO_PATH) else None
    pdf_bytes = gerar_relatorio_vendas(
        vendas=vendas,
        totais=totais,
        filtros={
            "data_inicial": di.isoformat(),
            "data_final": df.isoformat(),
        },
        logo_path=logo,
    )

    nome = f"relatorio_vendas_{di.strftime('%Y%m%d')}_{df.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nome}"'},
    )


# =============================================================================
# PDF — Relatório de Comissões
# =============================================================================

@router.get("/relatorios/comissoes/pdf")
async def relatorio_comissoes_pdf(
    request: Request,
    db: Session = Depends(get_db),
    data_inicial: str = None,
    data_final: str = None,
    usuario_id: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    repo = ReportRepository(db)
    hoje = date.today()
    di = _parse_date(data_inicial) or date(hoje.year, hoje.month, 1)
    df = _parse_date(data_final) or hoje

    comissoes = repo.comissoes_por_usuario(
        data_inicial=di,
        data_final=df,
        usuario_id=usuario_id or None,
    )

    total_vendido = sum(float(c.total_vendido or 0) for c in comissoes)
    total_comissao = sum(float(c.total_comissao or 0) for c in comissoes)
    total_vendas = sum(c.quantidade_vendas for c in comissoes)
    qtd_recepcionistas_ativos = max(repo.count_recepcionistas_ativos(), 1)

    logo = LOGO_PATH if os.path.exists(LOGO_PATH) else None
    pdf_bytes = gerar_relatorio_comissoes(
        comissoes=comissoes,
        total_vendido=total_vendido,
        total_comissao=total_comissao,
        total_vendas=total_vendas,
        qtd_recepcionistas_ativos=qtd_recepcionistas_ativos,
        filtros={
            "data_inicial": di.isoformat(),
            "data_final": df.isoformat(),
        },
        logo_path=logo,
    )

    nome = f"relatorio_comissoes_{di.strftime('%Y%m%d')}_{df.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nome}"'},
    )