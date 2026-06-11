from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, SESSION_COOKIE
from app.core.templates import templates
from app.database.connection import get_db
from app.services.dashboard_service import DashboardService
from app.repositories.user_repository import UserRepository
import uuid

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Valida sessão
    try:
        session = get_current_user(request)
    except Exception:
        return RedirectResponse(url="/login")

    # Busca usuário logado
    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    if not usuario:
        return RedirectResponse(url="/login")

    # Busca dados do dashboard
    service = DashboardService(db)
    dados = service.get_dados(
        usuario_id=uuid.UUID(session["user_id"]),
        perfil=usuario.perfil,
    )

    return templates.TemplateResponse(
        "dashboard/index.html",
        {
            "request": request,
            "usuario": usuario,
            "hoje": dados["hoje"],
            "mes": dados["mes"],
            "proximos_embarques": dados["proximos_embarques"],
            "pendencias": dados["pendencias"],
            "comissao_recepcao": dados["comissao_recepcao"],
        },
    )