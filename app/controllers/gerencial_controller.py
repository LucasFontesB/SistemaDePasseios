from __future__ import annotations

import uuid
import os
from datetime import date

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.gerencial_repository import GerencialRepository
from app.services.gerencial_pdf_service import gerar_relatorio_gerencial

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


def _montar_dados(repo: GerencialRepository, di: date, df: date) -> dict:
    return {
        "resumo":          repo.resumo_geral(di, df),
        "vendedores":      repo.ranking_vendedores(di, df),
        "passeios":        repo.ranking_passeios(di, df),
        "tipos":           repo.ranking_tipos(di, df),
        "embarcacoes":     repo.ranking_embarcacoes(di, df),
        "antecedencia":    repo.antecedencia_reserva(di, df),
        "horarios":        repo.horarios_populares(di, df),
        "dias_semana":     repo.vendas_por_dia_semana(di, df),
        "formas_pagamento": repo.formas_pagamento(di, df),
    }


@router.get("/relatorios/gerencial", response_class=HTMLResponse)
async def relatorio_gerencial(
    request: Request,
    db: Session = Depends(get_db),
    data_inicial: str = None,
    data_final: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    hoje = date.today()
    di = _parse_date(data_inicial) or date(hoje.year, hoje.month, 1)
    df = _parse_date(data_final) or hoje

    repo = GerencialRepository(db)
    dados = _montar_dados(repo, di, df)

    return templates.TemplateResponse("relatorios/gerencial.html", {
        "request": request,
        "usuario": usuario,
        "active": "rel_gerencial",
        "dados": dados,
        "filtros": {
            "data_inicial": di.isoformat(),
            "data_final": df.isoformat(),
        },
    })


@router.get("/relatorios/gerencial/pdf")
async def relatorio_gerencial_pdf(
    request: Request,
    db: Session = Depends(get_db),
    data_inicial: str = None,
    data_final: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    hoje = date.today()
    di = _parse_date(data_inicial) or date(hoje.year, hoje.month, 1)
    df = _parse_date(data_final) or hoje

    repo = GerencialRepository(db)
    dados = _montar_dados(repo, di, df)

    logo = LOGO_PATH if os.path.exists(LOGO_PATH) else None
    pdf_bytes = gerar_relatorio_gerencial(
        dados=dados,
        filtros={"data_inicial": di.isoformat(), "data_final": df.isoformat()},
        logo_path=logo,
    )

    nome = f"relatorio_gerencial_{di.strftime('%Y%m%d')}_{df.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nome}"'},
    )
