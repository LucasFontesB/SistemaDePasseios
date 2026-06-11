from __future__ import annotations

import uuid
import os

from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.connection import get_db
from app.repositories.sale_repository import SaleRepository
from app.services.pdf_service import gerar_voucher_recibo

router = APIRouter()

# Caminho da logo — ajuste conforme necessário
LOGO_PATH = "app/static/img/logo.png"


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


@router.get("/vendas/{venda_id}/pdf")
async def gerar_pdf(
    request: Request,
    venda_id: str,
    db: Session = Depends(get_db),
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    venda = SaleRepository(db).find_by_id(uuid.UUID(venda_id))
    if not venda:
        return RedirectResponse(url="/vendas")

    # Usa logo se existir
    logo = LOGO_PATH if os.path.exists(LOGO_PATH) else None

    pdf_bytes = gerar_voucher_recibo(venda, logo_path=logo)

    nome_arquivo = f"voucher_{venda.numero_venda}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{nome_arquivo}"',
        },
    )
