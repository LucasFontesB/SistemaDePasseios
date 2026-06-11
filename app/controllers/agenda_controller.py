from __future__ import annotations

import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.agenda_repository import AgendaRepository

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


@router.get("/agenda", response_class=HTMLResponse)
async def agenda(
    request: Request,
    db: Session = Depends(get_db),
    data: str = None,
    periodo: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    hoje = date.today()

    # Determina a data a exibir
    if data:
        try:
            data_selecionada = date.fromisoformat(data)
        except ValueError:
            data_selecionada = hoje
    elif periodo == "amanha":
        data_selecionada = hoje + timedelta(days=1)
    else:
        data_selecionada = hoje
        periodo = "hoje"

    repo = AgendaRepository(db)
    embarques = repo.get_embarques(data_selecionada)
    totais = repo.get_totais(embarques)

    return templates.TemplateResponse("agenda/index.html", {
        "request": request,
        "usuario": usuario,
        "active": "agenda",
        "embarques": embarques,
        "totais": totais,
        "data_selecionada": data_selecionada,
        "hoje": hoje,
        "amanha": hoje + timedelta(days=1),
        "periodo": periodo,
    })
