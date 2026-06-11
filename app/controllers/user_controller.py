from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, hash_password
from app.core.flash import set_flash
from app.core.templates import templates
from app.core.constants import PERFIL_CHOICES
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


def _require_admin(session: dict) -> bool:
    return session and session.get("perfil") == "ADMIN"


# =============================================================================
# Listagem
# =============================================================================

@router.get("/usuarios", response_class=HTMLResponse)
async def usuarios_list(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _require_admin(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    usuarios = UserRepository(db).list_active()

    return templates.TemplateResponse("usuarios/listagem.html", {
        "request": request,
        "usuario": usuario,
        "active": "usuarios",
        "usuarios": usuarios,
        "editando": None,
        "erros": [],
        "perfil_choices": PERFIL_CHOICES,
    })


# =============================================================================
# Criar
# =============================================================================

@router.post("/usuarios", response_class=HTMLResponse)
async def usuario_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_admin(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    repo = UserRepository(db)
    erros = _validar_criacao(form, repo)

    usuario_logado = repo.find_by_id(uuid.UUID(session["user_id"]))

    if erros:
        return templates.TemplateResponse("usuarios/listagem.html", {
            "request": request,
            "usuario": usuario_logado,
            "active": "usuarios",
            "usuarios": repo.list_active(),
            "editando": None,
            "erros": erros,
            "form_values": form,
            "perfil_choices": PERFIL_CHOICES,
        })

    repo.create(
        nome=form["nome"].strip(),
        email=form["email"].strip().lower(),
        senha_hash=hash_password(form["senha"]),
        perfil=form["perfil"],
    )
    response = RedirectResponse(url="/usuarios", status_code=302)
    set_flash(response, "Usuario cadastrado com sucesso!")
    return response


# =============================================================================
# Editar
# =============================================================================

@router.get("/usuarios/{usuario_id}/editar", response_class=HTMLResponse)
async def usuario_editar(request: Request, usuario_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_admin(session):
        return RedirectResponse(url="/login")

    repo = UserRepository(db)
    usuario_logado = repo.find_by_id(uuid.UUID(session["user_id"]))
    editando = repo.find_by_id(uuid.UUID(usuario_id))

    if not editando:
        return RedirectResponse(url="/usuarios")

    return templates.TemplateResponse("usuarios/listagem.html", {
        "request": request,
        "usuario": usuario_logado,
        "active": "usuarios",
        "usuarios": repo.list_active(),
        "editando": editando,
        "erros": [],
        "perfil_choices": PERFIL_CHOICES,
    })


@router.post("/usuarios/{usuario_id}/editar", response_class=HTMLResponse)
async def usuario_update(request: Request, usuario_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_admin(session):
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    repo = UserRepository(db)
    editando = repo.find_by_id(uuid.UUID(usuario_id))
    usuario_logado = repo.find_by_id(uuid.UUID(session["user_id"]))

    if not editando:
        return RedirectResponse(url="/usuarios")

    erros = _validar_edicao(form, repo, uuid.UUID(usuario_id))

    if erros:
        return templates.TemplateResponse("usuarios/listagem.html", {
            "request": request,
            "usuario": usuario_logado,
            "active": "usuarios",
            "usuarios": repo.list_active(),
            "editando": editando,
            "erros": erros,
            "form_values": form,
            "perfil_choices": PERFIL_CHOICES,
        })

    kwargs = {
        "nome": form["nome"].strip(),
        "email": form["email"].strip().lower(),
        "perfil": form["perfil"],
    }

    # Só atualiza senha se foi preenchida
    if form.get("senha", "").strip():
        kwargs["senha_hash"] = hash_password(form["senha"])

    repo.update(editando, **kwargs)
    response = RedirectResponse(url="/usuarios", status_code=302)
    set_flash(response, "Usuario atualizado com sucesso!")
    return response


# =============================================================================
# Desativar
# =============================================================================

@router.post("/usuarios/{usuario_id}/desativar")
async def usuario_desativar(request: Request, usuario_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session or not _require_admin(session):
        return RedirectResponse(url="/login")

    # Não permite desativar o próprio usuário
    if usuario_id == session["user_id"]:
        return RedirectResponse(url="/usuarios", status_code=302)

    repo = UserRepository(db)
    usuario = repo.find_by_id(uuid.UUID(usuario_id))
    if usuario:
        repo.soft_delete(usuario)

    response = RedirectResponse(url="/usuarios", status_code=302)
    set_flash(response, "Usuario desativado.", "warning")
    return response


# =============================================================================
# Validações
# =============================================================================

def _validar_criacao(form: dict, repo: UserRepository) -> list:
    erros = []
    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")
    if not form.get("email", "").strip():
        erros.append("E-mail é obrigatório.")
    elif repo.find_by_email(form["email"].strip().lower()):
        erros.append("Este e-mail já está em uso.")
    if not form.get("senha", "").strip():
        erros.append("Senha é obrigatória.")
    elif len(form["senha"]) < 8:
        erros.append("Senha deve ter pelo menos 8 caracteres.")
    if form.get("perfil") not in PERFIL_CHOICES:
        erros.append("Perfil inválido.")
    return erros


def _validar_edicao(form: dict, repo: UserRepository, usuario_id: uuid.UUID) -> list:
    erros = []
    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")
    if not form.get("email", "").strip():
        erros.append("E-mail é obrigatório.")
    else:
        existente = repo.find_by_email(form["email"].strip().lower())
        if existente and existente.id != usuario_id:
            erros.append("Este e-mail já está em uso por outro usuário.")
    if form.get("senha", "").strip() and len(form["senha"]) < 8:
        erros.append("Senha deve ter pelo menos 8 caracteres.")
    if form.get("perfil") not in PERFIL_CHOICES:
        erros.append("Perfil inválido.")
    return erros