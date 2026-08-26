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
from app.services.agencia_service import AgenciaService

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

@router.get("/agencias", response_class=HTMLResponse)
async def agencias_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    agencias = AgenciaService(db).list()

    return templates.TemplateResponse("agencias/listagem.html", {
        "request": request,
        "usuario": usuario,
        "active": "agencias",
        "agencias": agencias,
    })


# =============================================================================
# Nova agência
# =============================================================================

@router.get("/agencias/nova", response_class=HTMLResponse)
async def agencia_nova(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))

    return templates.TemplateResponse("agencias/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "agencias",
        "agencia": None,
        "erros": [],
    })


@router.post("/agencias", response_class=HTMLResponse)
async def agencia_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    ajax = _is_ajax(request)

    if not session:
        return JSONResponse({"erros": ["Não autenticado."]}, status_code=401) if ajax else RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return JSONResponse({"erros": ["Sem permissão."]}, status_code=403) if ajax else RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    agencia, erros = AgenciaService(db).create(form)

    if ajax:
        if erros:
            return JSONResponse({"erros": erros}, status_code=400)
        return JSONResponse({"id": str(agencia.id), "nome": agencia.nome})

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))

    if erros:
        return templates.TemplateResponse("agencias/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "agencias",
            "agencia": None,
            "erros": erros,
            "form_values": form,
        })

    response = RedirectResponse(url="/agencias", status_code=302)
    set_flash(response, "Agência cadastrada com sucesso!")
    return response


# =============================================================================
# Editar agência
# =============================================================================

@router.get("/agencias/{agencia_id}/editar", response_class=HTMLResponse)
async def agencia_editar(request: Request, agencia_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    agencia = AgenciaService(db).get_by_id(uuid.UUID(agencia_id))

    if not agencia:
        return RedirectResponse(url="/agencias")

    return templates.TemplateResponse("agencias/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "agencias",
        "agencia": agencia,
        "erros": [],
    })


@router.post("/agencias/{agencia_id}/editar", response_class=HTMLResponse)
async def agencia_update(request: Request, agencia_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = AgenciaService(db)
    agencia, erros = service.update(uuid.UUID(agencia_id), form)

    if erros:
        agencia_atual = service.get_by_id(uuid.UUID(agencia_id))
        return templates.TemplateResponse("agencias/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "agencias",
            "agencia": agencia_atual,
            "erros": erros,
            "form_values": form,
        })

    response = RedirectResponse(url="/agencias", status_code=302)
    set_flash(response, "Agência atualizada com sucesso!")
    return response


# =============================================================================
# Desativar agência
# =============================================================================

@router.post("/agencias/{agencia_id}/desativar")
async def agencia_desativar(request: Request, agencia_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    AgenciaService(db).desativar(uuid.UUID(agencia_id))
    response = RedirectResponse(url="/agencias", status_code=302)
    set_flash(response, "Agência desativada.", "warning")
    return response
