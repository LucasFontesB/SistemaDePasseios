from __future__ import annotations
import uuid
from datetime import date
from sqlalchemy.orm import Session

from app.models.grupo_orcamento_pagamento import GrupoOrcamentoPagamento


class GrupoOrcamentoPagamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_orcamento(self, orcamento_id: uuid.UUID) -> list[GrupoOrcamentoPagamento]:
        return (
            self.db.query(GrupoOrcamentoPagamento)
            .filter(GrupoOrcamentoPagamento.orcamento_id == orcamento_id)
            .order_by(GrupoOrcamentoPagamento.data_pagamento)
            .all()
        )

    def create(
        self,
        orcamento_id: uuid.UUID,
        valor: float,
        data_pagamento: date,
        forma_pagamento: str | None,
    ) -> GrupoOrcamentoPagamento:
        item = GrupoOrcamentoPagamento(
            id=uuid.uuid4(),
            orcamento_id=orcamento_id,
            valor=valor,
            data_pagamento=data_pagamento,
            forma_pagamento=forma_pagamento,
        )
        self.db.add(item)
        # Sem commit — o service grava a versão inteira numa única transação.
        return item
