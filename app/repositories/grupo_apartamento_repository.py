from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_apartamento import GrupoApartamento
from app.models.tipo_apartamento import TipoApartamento


class GrupoApartamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list[GrupoApartamento]:
        return (
            self.db.query(GrupoApartamento)
            .options(joinedload(GrupoApartamento.tipo_apartamento))
            .join(TipoApartamento)
            .filter(GrupoApartamento.grupo_id == grupo_id)
            .order_by(TipoApartamento.ordem, TipoApartamento.nome)
            .all()
        )

    def find_by_id(self, item_id: uuid.UUID) -> GrupoApartamento | None:
        return (
            self.db.query(GrupoApartamento)
            .options(joinedload(GrupoApartamento.tipo_apartamento))
            .filter(GrupoApartamento.id == item_id)
            .first()
        )

    def find_by_grupo_e_tipo(self, grupo_id: uuid.UUID, tipo_apartamento_id: uuid.UUID) -> GrupoApartamento | None:
        return (
            self.db.query(GrupoApartamento)
            .filter(
                GrupoApartamento.grupo_id == grupo_id,
                GrupoApartamento.tipo_apartamento_id == tipo_apartamento_id,
            )
            .first()
        )

    def create(
        self,
        grupo_id: uuid.UUID,
        tipo_apartamento_id: uuid.UUID,
        quantidade: int,
        valor_diaria_net: float,
        valor_diaria_sistema: float,
    ) -> GrupoApartamento:
        item = GrupoApartamento(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            tipo_apartamento_id=tipo_apartamento_id,
            quantidade=quantidade,
            valor_diaria_net=valor_diaria_net,
            valor_diaria_sistema=valor_diaria_sistema,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(
        self,
        item: GrupoApartamento,
        quantidade: int,
        valor_diaria_net: float,
        valor_diaria_sistema: float,
    ) -> GrupoApartamento:
        item.quantidade = quantidade
        item.valor_diaria_net = valor_diaria_net
        item.valor_diaria_sistema = valor_diaria_sistema
        item.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: GrupoApartamento) -> None:
        self.db.delete(item)
        self.db.commit()

    def delete_by_grupo(self, grupo_id: uuid.UUID) -> None:
        """Usado na aprovação de orçamento (RN-G007): a composição atual é
        substituída pelas linhas congeladas na versão aprovada."""
        self.db.query(GrupoApartamento).filter(GrupoApartamento.grupo_id == grupo_id).delete()
