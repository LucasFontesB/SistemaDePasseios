from __future__ import annotations

import uuid
import os

from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.templates import templates
from app.database.connection import get_db
from app.services.receipt_service import ReceiptService
from app.repositories.user_repository import UserRepository
from app.repositories.sale_repository import SaleRepository

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


# =============================================================================
# Upload
# =============================================================================

@router.post("/vendas/{venda_id}/comprovantes", response_class=HTMLResponse)
async def comprovante_upload(
    request: Request,
    venda_id: str,
    db: Session = Depends(get_db),
    arquivo: UploadFile = File(...),
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    service = ReceiptService(db)
    comprovante, erros = await service.upload(
        venda_id=uuid.UUID(venda_id),
        arquivo=arquivo,
    )

    if erros:
        # Busca venda para re-renderizar detalhes com erro
        usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
        venda = SaleRepository(db).find_by_id(uuid.UUID(venda_id))
        from app.core.constants import STATUS_CHOICES
        return templates.TemplateResponse("vendas/detalhes.html", {
            "request": request,
            "usuario": usuario,
            "active": "vendas",
            "venda": venda,
            "status_choices": STATUS_CHOICES,
            "erro_upload": erros[0],
        }, status_code=400)

    return RedirectResponse(url=f"/vendas/{venda_id}", status_code=302)


# =============================================================================
# Download
# =============================================================================

@router.get("/comprovantes/{comprovante_id}")
async def comprovante_download(
    request: Request,
    comprovante_id: str,
    db: Session = Depends(get_db),
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    service = ReceiptService(db)
    comprovante = service.get_by_id(uuid.UUID(comprovante_id))

    if not comprovante or not os.path.exists(comprovante.caminho):
        return RedirectResponse(url="/vendas")

    return FileResponse(
        path=comprovante.caminho,
        filename=comprovante.nome_original,
        media_type=_media_type(comprovante.tipo_arquivo),
    )


# =============================================================================
# Remoção
# =============================================================================

@router.post("/comprovantes/{comprovante_id}/remover")
async def comprovante_remover(
    request: Request,
    comprovante_id: str,
    db: Session = Depends(get_db),
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    service = ReceiptService(db)
    sucesso, venda_id = service.remover(uuid.UUID(comprovante_id))

    if sucesso:
        return RedirectResponse(url=f"/vendas/{venda_id}", status_code=302)

    return RedirectResponse(url="/vendas", status_code=302)


# =============================================================================
# Helpers
# =============================================================================

def _media_type(extensao: str) -> str:
    return {
        "pdf":  "application/pdf",
        "jpg":  "image/jpeg",
        "jpeg": "image/jpeg",
        "png":  "image/png",
    }.get(extensao.lower(), "application/octet-stream")
