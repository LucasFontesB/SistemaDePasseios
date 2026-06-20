from __future__ import annotations

import uuid

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.flash import set_flash
from app.database.connection import get_db
from app.services.payment_service import PaymentService

router = APIRouter()


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


# =============================================================================
# Registrar pagamento
# =============================================================================

@router.post("/vendas/{venda_id}/pagamentos", response_class=RedirectResponse)
async def pagamento_create(request: Request, venda_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")

    form = dict(await request.form())
    service = PaymentService(db)
    pagamento, erros = service.register(
        uuid.UUID(venda_id), form, uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/vendas/{venda_id}", status_code=302)

    if erros:
        set_flash(response, "; ".join(erros), categoria="erro")
        return response

    set_flash(response, "Pagamento registrado com sucesso!")
    return response
