from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.core.flash import set_flash
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.services.guia_service import GuiaService

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


def _tem_acesso(session: dict) -> bool:
    """Módulo de grupos é liberado para ADMIN, GERENCIA e RECEPCAO."""
    return session is not None and session.get("perfil") in ("ADMIN", "GERENCIA", "RECEPCAO")


def _is_ajax(request: Request) -> bool:
    """RN-G030: criação rápida a partir do formulário de grupo — mesma rota
    de sempre, só a resposta muda de HTML/redirect para JSON."""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


# =============================================================================
# Listagem
# =============================================================================

@router.get("/guias", response_class=HTMLResponse)
async def guias_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    guias = GuiaService(db).list()

    return templates.TemplateResponse("guias/listagem.html", {
        "request": request,
        "usuario": usuario,
        "active": "guias",
        "guias": guias,
    })


# =============================================================================
# Novo guia
# =============================================================================

@router.get("/guias/novo", response_class=HTMLResponse)
async def guia_novo(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))

    return templates.TemplateResponse("guias/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "guias",
        "guia": None,
        "erros": [],
    })


@router.post("/guias", response_class=HTMLResponse)
async def guia_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    ajax = _is_ajax(request)

    if not session:
        return JSONResponse({"erros": ["Não autenticado."]}, status_code=401) if ajax else RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return JSONResponse({"erros": ["Sem permissão."]}, status_code=403) if ajax else RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    guia, erros = GuiaService(db).create(form)

    if ajax:
        if erros:
            return JSONResponse({"erros": erros}, status_code=400)
        return JSONResponse({"id": str(guia.id), "nome": guia.nome})

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))

    if erros:
        return templates.TemplateResponse("guias/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "guias",
            "guia": None,
            "erros": erros,
            "form_values": form,
        })

    response = RedirectResponse(url="/guias", status_code=302)
    set_flash(response, "Guia cadastrado com sucesso!")
    return response


# =============================================================================
# Editar guia
# =============================================================================

@router.get("/guias/{guia_id}/editar", response_class=HTMLResponse)
async def guia_editar(request: Request, guia_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    guia = GuiaService(db).get_by_id(uuid.UUID(guia_id))

    if not guia:
        return RedirectResponse(url="/guias")

    return templates.TemplateResponse("guias/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "guias",
        "guia": guia,
        "erros": [],
    })


@router.post("/guias/{guia_id}/editar", response_class=HTMLResponse)
async def guia_update(request: Request, guia_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = GuiaService(db)
    guia, erros = service.update(uuid.UUID(guia_id), form)

    if erros:
        guia_atual = service.get_by_id(uuid.UUID(guia_id))
        return templates.TemplateResponse("guias/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "guias",
            "guia": guia_atual,
            "erros": erros,
            "form_values": form,
        })

    response = RedirectResponse(url="/guias", status_code=302)
    set_flash(response, "Guia atualizado com sucesso!")
    return response


# =============================================================================
# Desativar guia
# =============================================================================

@router.post("/guias/{guia_id}/desativar")
async def guia_desativar(request: Request, guia_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    GuiaService(db).desativar(uuid.UUID(guia_id))
    response = RedirectResponse(url="/guias", status_code=302)
    set_flash(response, "Guia desativado.", "warning")
    return response
