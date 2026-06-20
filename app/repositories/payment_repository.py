from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.pagamento import Pagamento


class PaymentRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_venda(self, venda_id: uuid.UUID) -> list[Pagamento]:
        return (
            self.db.query(Pagamento)
            .filter(Pagamento.venda_id == venda_id)
            .order_by(Pagamento.criado_em.desc())
            .all()
        )

    def find_by_id(self, pagamento_id: uuid.UUID) -> Pagamento | None:
        return (
            self.db.query(Pagamento)
            .filter(Pagamento.id == pagamento_id)
            .first()
        )

    def create(
        self,
        venda_id: uuid.UUID,
        valor: float,
        forma_pagamento: str,
        observacao: str | None,
        usuario_id: uuid.UUID,
    ) -> Pagamento:
        pagamento = Pagamento(
            id=uuid.uuid4(),
            venda_id=venda_id,
            valor=valor,
            forma_pagamento=forma_pagamento,
            observacao=observacao,
            usuario_id=usuario_id,
        )
        self.db.add(pagamento)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento
