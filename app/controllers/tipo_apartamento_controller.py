from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.core.flash import set_flash
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.services.tipo_apartamento_service import TipoApartamentoService

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


def _require_gerencia(session: dict) -> bool:
    """Cadastro fixo do hotel — restrito a ADMIN e GERENCIA, igual a Passeios."""
    return session is not None and session.get("perfil") in ("ADMIN", "GERENCIA")


@router.get("/tipos-apartamento", response_class=HTMLResponse)
async def tipos_apartamento_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    tipos = TipoApartamentoService(db).list()

    return templates.TemplateResponse("cadastros/tipos_apartamento.html", {
        "request": request,
        "usuario": usuario,
        "active": "tipos_apartamento",
        "tipos": tipos,
        "editando": None,
        "erros": [],
    })


@router.post("/tipos-apartamento", response_class=HTMLResponse)
async def tipo_apartamento_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = TipoApartamentoService(db)
    tipo, erros = service.create(form)

    if erros:
        return templates.TemplateResponse("cadastros/tipos_apartamento.html", {
            "request": request,
            "usuario": usuario,
            "active": "tipos_apartamento",
            "tipos": service.list(),
            "editando": None,
            "erros": erros,
            "form_values": form,
        })

    response = RedirectResponse(url="/tipos-apartamento", status_code=302)
    set_flash(response, "Tipo de apartamento cadastrado com sucesso!")
    return response


@router.get("/tipos-apartamento/{tipo_id}/editar", response_class=HTMLResponse)
async def tipo_apartamento_editar(request: Request, tipo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    service = TipoApartamentoService(db)
    tipo = service.get_by_id(uuid.UUID(tipo_id))

    if not tipo:
        return RedirectResponse(url="/tipos-apartamento")

    return templates.TemplateResponse("cadastros/tipos_apartamento.html", {
        "request": request,
        "usuario": usuario,
        "active": "tipos_apartamento",
        "tipos": service.list(),
        "editando": tipo,
        "erros": [],
    })


@router.post("/tipos-apartamento/{tipo_id}/editar", response_class=HTMLResponse)
async def tipo_apartamento_update(request: Request, tipo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    service = TipoApartamentoService(db)
    tipo, erros = service.update(uuid.UUID(tipo_id), form)

    if erros:
        return templates.TemplateResponse("cadastros/tipos_apartamento.html", {
            "request": request,
            "usuario": usuario,
            "active": "tipos_apartamento",
            "tipos": service.list(),
            "editando": service.get_by_id(uuid.UUID(tipo_id)),
            "erros": erros,
            "form_values": form,
        })

    response = RedirectResponse(url="/tipos-apartamento", status_code=302)
    set_flash(response, "Tipo de apartamento atualizado com sucesso!")
    return response


@router.post("/tipos-apartamento/{tipo_id}/desativar")
async def tipo_apartamento_desativar(request: Request, tipo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    TipoApartamentoService(db).desativar(uuid.UUID(tipo_id))
    response = RedirectResponse(url="/tipos-apartamento", status_code=302)
    set_flash(response, "Tipo de apartamento desativado.", "warning")
    return response
