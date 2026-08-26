from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.models.grupo_orcamento_apartamento import GrupoOrcamentoApartamento


class GrupoOrcamentoApartamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_orcamento(self, orcamento_id: uuid.UUID) -> list[GrupoOrcamentoApartamento]:
        return (
            self.db.query(GrupoOrcamentoApartamento)
            .filter(GrupoOrcamentoApartamento.orcamento_id == orcamento_id)
            .order_by(GrupoOrcamentoApartamento.tipo_apartamento_nome)
            .all()
        )

    def create(
        self,
        orcamento_id: uuid.UUID,
        tipo_apartamento_nome: str,
        quantidade: int,
        valor_diaria_net: float,
        valor_diaria_sistema: float,
        valor_total_net: float,
        valor_total_sistema: float,
    ) -> GrupoOrcamentoApartamento:
        item = GrupoOrcamentoApartamento(
            id=uuid.uuid4(),
            orcamento_id=orcamento_id,
            tipo_apartamento_nome=tipo_apartamento_nome,
            quantidade=quantidade,
            valor_diaria_net=valor_diaria_net,
            valor_diaria_sistema=valor_diaria_sistema,
            valor_total_net=valor_total_net,
            valor_total_sistema=valor_total_sistema,
        )
        self.db.add(item)
        # Sem commit — o service grava a versão inteira numa única transação.
        return item
