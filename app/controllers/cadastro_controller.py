from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.tour_repository import TourRepository

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


def _require_gerencia(session: dict) -> bool:
    """Apenas ADMIN e GERENCIA acessam cadastros."""
    return session and session.get("perfil") in ("ADMIN", "GERENCIA")


# =============================================================================
# Passeios
# =============================================================================

@router.get("/passeios", response_class=HTMLResponse)
async def passeios_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_gerencia(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    passeios = TourRepository(db).list_passeios()

    return templates.TemplateResponse("cadastros/passeios.html", {
        "request": request,
        "usuario": usuario,
        "active": "passeios",
        "passeios": passeios,
        "editando": None,
        "erros": [],
    })


@router.post("/passeios", response_class=HTMLResponse)
async def passeio_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    erros = _validar_passeio(form)

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)

    if erros:
        return templates.TemplateResponse("cadastros/passeios.html", {
            "request": request,
            "usuario": usuario,
            "active": "passeios",
            "passeios": repo.list_passeios(),
            "editando": None,
            "erros": erros,
            "form_values": form,
        })

    repo.create_passeio(
        nome=form["nome"].strip(),
        descricao=form.get("descricao", "").strip(),
        percentual_comissao=float(form["percentual_comissao"]),
    )
    return RedirectResponse(url="/passeios", status_code=302)


@router.get("/passeios/{passeio_id}/editar", response_class=HTMLResponse)
async def passeio_editar(request: Request, passeio_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)
    passeio = repo.find_passeio_by_id(uuid.UUID(passeio_id))

    if not passeio:
        return RedirectResponse(url="/passeios")

    return templates.TemplateResponse("cadastros/passeios.html", {
        "request": request,
        "usuario": usuario,
        "active": "passeios",
        "passeios": repo.list_passeios(),
        "editando": passeio,
        "erros": [],
    })


@router.post("/passeios/{passeio_id}/editar", response_class=HTMLResponse)
async def passeio_update(request: Request, passeio_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    erros = _validar_passeio(form)

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)
    passeio = repo.find_passeio_by_id(uuid.UUID(passeio_id))

    if erros or not passeio:
        return templates.TemplateResponse("cadastros/passeios.html", {
            "request": request,
            "usuario": usuario,
            "active": "passeios",
            "passeios": repo.list_passeios(),
            "editando": passeio,
            "erros": erros,
            "form_values": form,
        })

    repo.update_passeio(
        passeio=passeio,
        nome=form["nome"].strip(),
        descricao=form.get("descricao", "").strip(),
        percentual_comissao=float(form["percentual_comissao"]),
    )
    return RedirectResponse(url="/passeios", status_code=302)


@router.post("/passeios/{passeio_id}/desativar")
async def passeio_desativar(request: Request, passeio_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    repo = TourRepository(db)
    passeio = repo.find_passeio_by_id(uuid.UUID(passeio_id))
    if passeio:
        repo.soft_delete_passeio(passeio)
    return RedirectResponse(url="/passeios", status_code=302)


# =============================================================================
# Tipos de Passeio
# =============================================================================

@router.get("/tipos-passeio", response_class=HTMLResponse)
async def tipos_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    tipos = TourRepository(db).list_tipos()

    return templates.TemplateResponse("cadastros/tipos_passeio.html", {
        "request": request,
        "usuario": usuario,
        "active": "tipos_passeio",
        "tipos": tipos,
        "editando": None,
        "erros": [],
    })


@router.post("/tipos-passeio", response_class=HTMLResponse)
async def tipo_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    erros = []
    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)

    if erros:
        return templates.TemplateResponse("cadastros/tipos_passeio.html", {
            "request": request,
            "usuario": usuario,
            "active": "tipos_passeio",
            "tipos": repo.list_tipos(),
            "editando": None,
            "erros": erros,
            "form_values": form,
        })

    repo.create_tipo(nome=form["nome"].strip())
    return RedirectResponse(url="/tipos-passeio", status_code=302)


@router.get("/tipos-passeio/{tipo_id}/editar", response_class=HTMLResponse)
async def tipo_editar(request: Request, tipo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)
    tipo = repo.find_tipo_by_id(uuid.UUID(tipo_id))

    if not tipo:
        return RedirectResponse(url="/tipos-passeio")

    return templates.TemplateResponse("cadastros/tipos_passeio.html", {
        "request": request,
        "usuario": usuario,
        "active": "tipos_passeio",
        "tipos": repo.list_tipos(),
        "editando": tipo,
        "erros": [],
    })


@router.post("/tipos-passeio/{tipo_id}/editar", response_class=HTMLResponse)
async def tipo_update(request: Request, tipo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    erros = []
    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)
    tipo = repo.find_tipo_by_id(uuid.UUID(tipo_id))

    if erros or not tipo:
        return templates.TemplateResponse("cadastros/tipos_passeio.html", {
            "request": request,
            "usuario": usuario,
            "active": "tipos_passeio",
            "tipos": repo.list_tipos(),
            "editando": tipo,
            "erros": erros,
            "form_values": form,
        })

    repo.update_tipo(tipo=tipo, nome=form["nome"].strip())
    return RedirectResponse(url="/tipos-passeio", status_code=302)


@router.post("/tipos-passeio/{tipo_id}/desativar")
async def tipo_desativar(request: Request, tipo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    repo = TourRepository(db)
    tipo = repo.find_tipo_by_id(uuid.UUID(tipo_id))
    if tipo:
        repo.soft_delete_tipo(tipo)
    return RedirectResponse(url="/tipos-passeio", status_code=302)


# =============================================================================
# Embarcações
# =============================================================================

@router.get("/embarcacoes", response_class=HTMLResponse)
async def embarcacoes_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    embarcacoes = TourRepository(db).list_embarcacoes()

    return templates.TemplateResponse("cadastros/embarcacoes.html", {
        "request": request,
        "usuario": usuario,
        "active": "embarcacoes",
        "embarcacoes": embarcacoes,
        "editando": None,
        "erros": [],
    })


@router.post("/embarcacoes", response_class=HTMLResponse)
async def embarcacao_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    erros = _validar_embarcacao(form)

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)

    if erros:
        return templates.TemplateResponse("cadastros/embarcacoes.html", {
            "request": request,
            "usuario": usuario,
            "active": "embarcacoes",
            "embarcacoes": repo.list_embarcacoes(),
            "editando": None,
            "erros": erros,
            "form_values": form,
        })

    repo.create_embarcacao(
        nome=form["nome"].strip(),
        capacidade=int(form["capacidade"]),
        observacao=form.get("observacao", "").strip(),
    )
    return RedirectResponse(url="/embarcacoes", status_code=302)


@router.get("/embarcacoes/{embarcacao_id}/editar", response_class=HTMLResponse)
async def embarcacao_editar(request: Request, embarcacao_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)
    embarcacao = repo.find_embarcacao_by_id(uuid.UUID(embarcacao_id))

    if not embarcacao:
        return RedirectResponse(url="/embarcacoes")

    return templates.TemplateResponse("cadastros/embarcacoes.html", {
        "request": request,
        "usuario": usuario,
        "active": "embarcacoes",
        "embarcacoes": repo.list_embarcacoes(),
        "editando": embarcacao,
        "erros": [],
    })


@router.post("/embarcacoes/{embarcacao_id}/editar", response_class=HTMLResponse)
async def embarcacao_update(request: Request, embarcacao_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    erros = _validar_embarcacao(form)

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    repo = TourRepository(db)
    embarcacao = repo.find_embarcacao_by_id(uuid.UUID(embarcacao_id))

    if erros or not embarcacao:
        return templates.TemplateResponse("cadastros/embarcacoes.html", {
            "request": request,
            "usuario": usuario,
            "active": "embarcacoes",
            "embarcacoes": repo.list_embarcacoes(),
            "editando": embarcacao,
            "erros": erros,
            "form_values": form,
        })

    repo.update_embarcacao(
        embarcacao=embarcacao,
        nome=form["nome"].strip(),
        capacidade=int(form["capacidade"]),
        observacao=form.get("observacao", "").strip(),
    )
    return RedirectResponse(url="/embarcacoes", status_code=302)


@router.post("/embarcacoes/{embarcacao_id}/desativar")
async def embarcacao_desativar(request: Request, embarcacao_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_gerencia(session):
        return RedirectResponse(url="/login")

    repo = TourRepository(db)
    embarcacao = repo.find_embarcacao_by_id(uuid.UUID(embarcacao_id))
    if embarcacao:
        repo.soft_delete_embarcacao(embarcacao)
    return RedirectResponse(url="/embarcacoes", status_code=302)


# =============================================================================
# Validações
# =============================================================================

def _validar_passeio(form: dict) -> list:
    erros = []
    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")
    if not form.get("percentual_comissao"):
        erros.append("Percentual de comissão é obrigatório.")
    else:
        try:
            v = float(form["percentual_comissao"])
            if v < 0 or v > 100:
                erros.append("Percentual deve estar entre 0 e 100.")
        except ValueError:
            erros.append("Percentual de comissão inválido.")
    return erros


def _validar_embarcacao(form: dict) -> list:
    erros = []
    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")
    if not form.get("capacidade"):
        erros.append("Capacidade é obrigatória.")
    else:
        try:
            v = int(form["capacidade"])
            if v <= 0:
                erros.append("Capacidade deve ser maior que zero.")
        except ValueError:
            erros.append("Capacidade inválida.")
    return erros
