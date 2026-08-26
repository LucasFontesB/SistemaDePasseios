from __future__ import annotations
import uuid
from datetime import date
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_pagamento import GrupoPagamento


class GrupoPagamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list[GrupoPagamento]:
        return (
            self.db.query(GrupoPagamento)
            .options(joinedload(GrupoPagamento.usuario))
            .filter(GrupoPagamento.grupo_id == grupo_id)
            .order_by(GrupoPagamento.criado_em.desc())
            .all()
        )

    def create(
        self,
        grupo_id: uuid.UUID,
        valor: float,
        data_pagamento: date,
        forma_pagamento: str | None,
        observacao: str | None,
        usuario_id: uuid.UUID,
    ) -> GrupoPagamento:
        pagamento = GrupoPagamento(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            valor=valor,
            data_pagamento=data_pagamento,
            forma_pagamento=forma_pagamento,
            observacao=observacao,
            usuario_id=usuario_id,
        )
        self.db.add(pagamento)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento
