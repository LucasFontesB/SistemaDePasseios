import uuid
from datetime import date

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.services.sale_service import SaleService

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


# =============================================================================
# Listagem
# =============================================================================

@router.get("/vendas", response_class=HTMLResponse)
async def vendas_list(
    request: Request,
    db: Session = Depends(get_db),
    contratante: str = None,
    telefone: str = None,
    passeio_id: str = None,
    status: str = None,
    data_inicial: str = None,
    data_final: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    service = SaleService(db)

    vendas = service.list(
        contratante=contratante,
        telefone=telefone,
        passeio_id=passeio_id,
        status=status,
        data_inicial=date.fromisoformat(data_inicial) if data_inicial else None,
        data_final=date.fromisoformat(data_final) if data_final else None,
    )

    form_data = service.get_form_data()

    return templates.TemplateResponse("vendas/listagem.html", {
        "request": request,
        "usuario": usuario,
        "active": "vendas",
        "vendas": vendas,
        "passeios": form_data["passeios"],
        "filtros": {
            "contratante": contratante or "",
            "telefone": telefone or "",
            "passeio_id": passeio_id or "",
            "status": status or "",
            "data_inicial": data_inicial or "",
            "data_final": data_final or "",
        },
    })


# =============================================================================
# Nova venda
# =============================================================================

@router.get("/vendas/nova", response_class=HTMLResponse)
async def venda_nova(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form_data = SaleService(db).get_form_data()

    return templates.TemplateResponse("vendas/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "nova_venda",
        "venda": None,
        "erros": [],
        **form_data,
    })


@router.post("/vendas", response_class=HTMLResponse)
async def venda_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = SaleService(db)
    venda, erros = service.create(form, uuid.UUID(session["user_id"]))

    if erros:
        form_data = service.get_form_data()
        return templates.TemplateResponse("vendas/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "nova_venda",
            "venda": None,
            "erros": erros,
            "form_values": form,
            **form_data,
        })

    return RedirectResponse(url=f"/vendas/{venda.id}", status_code=302)


# =============================================================================
# Detalhes
# =============================================================================

@router.get("/vendas/{venda_id}", response_class=HTMLResponse)
async def venda_detalhes(request: Request, venda_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    venda = SaleService(db).get_by_id(uuid.UUID(venda_id))

    if not venda:
        return RedirectResponse(url="/vendas")

    from app.core.constants import STATUS_CHOICES
    return templates.TemplateResponse("vendas/detalhes.html", {
        "request": request,
        "usuario": usuario,
        "active": "vendas",
        "venda": venda,
        "status_choices": STATUS_CHOICES,
    })


# =============================================================================
# Editar venda
# =============================================================================

@router.get("/vendas/{venda_id}/editar", response_class=HTMLResponse)
async def venda_editar(request: Request, venda_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    service = SaleService(db)
    venda = service.get_by_id(uuid.UUID(venda_id))

    if not venda:
        return RedirectResponse(url="/vendas")

    form_data = service.get_form_data()
    return templates.TemplateResponse("vendas/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "vendas",
        "venda": venda,
        "erros": [],
        **form_data,
    })


@router.post("/vendas/{venda_id}/editar", response_class=HTMLResponse)
async def venda_update(request: Request, venda_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = SaleService(db)
    venda, erros = service.update(uuid.UUID(venda_id), form, uuid.UUID(session["user_id"]))

    if erros:
        form_data = service.get_form_data()
        venda_atual = service.get_by_id(uuid.UUID(venda_id))
        return templates.TemplateResponse("vendas/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "vendas",
            "venda": venda_atual,
            "erros": erros,
            "form_values": form,
            **form_data,
        })

    return RedirectResponse(url=f"/vendas/{venda_id}", status_code=302)


# =============================================================================
# Alterar status
# =============================================================================

@router.post("/vendas/{venda_id}/status", response_class=HTMLResponse)
async def venda_status(request: Request, venda_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    status = form.get("status", "")
    SaleService(db).update_status(uuid.UUID(venda_id), status, uuid.UUID(session["user_id"]))
    return RedirectResponse(url=f"/vendas/{venda_id}", status_code=302)
