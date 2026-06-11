from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import SESSION_COOKIE
from app.core.templates import templates
from app.database.connection import get_db
from app.services.auth_service import AuthService

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Exibe a tela de login."""

    # Se já estiver logado, redireciona para o dashboard
    if request.cookies.get(SESSION_COOKIE):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "erro": None},
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, db: Session = Depends(get_db)):
    """Processa o formulário de login."""
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    senha = str(form.get("senha", ""))

    service = AuthService(db)
    sucesso, mensagem, usuario = service.authenticate(email, senha)

    if not sucesso:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "erro": mensagem},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = service.create_session_token(usuario)

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=settings.SESSION_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,  # True em produção (HTTPS), False em dev
    )
    return response


@router.get("/logout")
async def logout():
    """Encerra a sessão do usuário."""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_COOKIE)
    return response