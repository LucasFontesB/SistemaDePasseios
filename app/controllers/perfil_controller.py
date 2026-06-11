from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user, hash_password, verify_password
from app.core.templates import templates
from app.core.flash import set_flash
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


@router.get("/perfil", response_class=HTMLResponse)
async def perfil_page(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    return templates.TemplateResponse("perfil/index.html", {
        "request": request,
        "usuario": usuario,
        "active": "",
        "erros": [],
    })


@router.post("/perfil", response_class=HTMLResponse)
async def perfil_update(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    repo = UserRepository(db)
    usuario = repo.find_by_id(uuid.UUID(session["user_id"]))

    erros = []

    if not form.get("nome", "").strip():
        erros.append("Nome é obrigatório.")

    # Validação de senha apenas se preenchida
    senha_atual = form.get("senha_atual", "").strip()
    nova_senha = form.get("nova_senha", "").strip()
    confirmar_senha = form.get("confirmar_senha", "").strip()

    alterar_senha = bool(senha_atual or nova_senha or confirmar_senha)

    if alterar_senha:
        if not senha_atual:
            erros.append("Informe a senha atual para alterá-la.")
        elif not verify_password(senha_atual, usuario.senha_hash):
            erros.append("Senha atual incorreta.")

        if not nova_senha:
            erros.append("Informe a nova senha.")
        elif len(nova_senha) < 8:
            erros.append("A nova senha deve ter pelo menos 8 caracteres.")

        if nova_senha and nova_senha != confirmar_senha:
            erros.append("A confirmação não confere com a nova senha.")

    if erros:
        return templates.TemplateResponse("perfil/index.html", {
            "request": request,
            "usuario": usuario,
            "active": "",
            "erros": erros,
        })

    kwargs = {"nome": form["nome"].strip()}
    if alterar_senha and not erros:
        kwargs["senha_hash"] = hash_password(nova_senha)

    repo.update(usuario, **kwargs)

    response = RedirectResponse(url="/perfil", status_code=302)
    set_flash(response, "Perfil atualizado com sucesso!")
    return response
