from __future__ import annotations
import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_roomlist import GrupoRoomlist


class GrupoRoomlistRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list[GrupoRoomlist]:
        return (
            self.db.query(GrupoRoomlist)
            .options(joinedload(GrupoRoomlist.tipo_apartamento))
            .filter(GrupoRoomlist.grupo_id == grupo_id)
            .order_by(GrupoRoomlist.criado_em)
            .all()
        )

    def find_by_id(self, item_id: uuid.UUID) -> GrupoRoomlist | None:
        return (
            self.db.query(GrupoRoomlist)
            .options(joinedload(GrupoRoomlist.tipo_apartamento))
            .filter(GrupoRoomlist.id == item_id)
            .first()
        )

    def create(
        self,
        grupo_id: uuid.UUID,
        apartamento: str | None,
        hospede_nome: str,
        documento: str | None,
        tipo_apartamento_id: uuid.UUID | None,
        cortesia: bool,
        check_in: date | None,
        check_out: date | None,
        observacao: str | None,
    ) -> GrupoRoomlist:
        item = GrupoRoomlist(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            apartamento=apartamento,
            hospede_nome=hospede_nome,
            documento=documento,
            tipo_apartamento_id=tipo_apartamento_id,
            cortesia=cortesia,
            check_in=check_in,
            check_out=check_out,
            observacao=observacao,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(
        self,
        item: GrupoRoomlist,
        apartamento: str | None,
        hospede_nome: str,
        documento: str | None,
        tipo_apartamento_id: uuid.UUID | None,
        cortesia: bool,
        check_in: date | None,
        check_out: date | None,
        observacao: str | None,
    ) -> GrupoRoomlist:
        item.apartamento = apartamento
        item.hospede_nome = hospede_nome
        item.documento = documento
        item.tipo_apartamento_id = tipo_apartamento_id
        item.cortesia = cortesia
        item.check_in = check_in
        item.check_out = check_out
        item.observacao = observacao
        item.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: GrupoRoomlist) -> None:
        self.db.delete(item)
        self.db.commit()

    # =========================================================================
    # Sincronização com a composição por tipo (RN-G032)
    # =========================================================================

    def list_by_grupo_e_tipo(self, grupo_id: uuid.UUID, tipo_apartamento_id: uuid.UUID) -> list[GrupoRoomlist]:
        return (
            self.db.query(GrupoRoomlist)
            .filter(
                GrupoRoomlist.grupo_id == grupo_id,
                GrupoRoomlist.tipo_apartamento_id == tipo_apartamento_id,
            )
            .all()
        )

    def list_vazias_by_grupo_e_tipo(self, grupo_id: uuid.UUID, tipo_apartamento_id: uuid.UUID) -> list[GrupoRoomlist]:
        return (
            self.db.query(GrupoRoomlist)
            .filter(
                GrupoRoomlist.grupo_id == grupo_id,
                GrupoRoomlist.tipo_apartamento_id == tipo_apartamento_id,
                GrupoRoomlist.hospede_nome.is_(None),
            )
            .all()
        )

    def criar_vazias(self, grupo_id: uuid.UUID, tipo_apartamento_id: uuid.UUID, quantidade: int) -> None:
        """RN-G032: linhas 'aguardando preenchimento' geradas pela composição."""
        for _ in range(quantidade):
            self.db.add(GrupoRoomlist(
                id=uuid.uuid4(),
                grupo_id=grupo_id,
                tipo_apartamento_id=tipo_apartamento_id,
                hospede_nome=None,
                cortesia=False,
            ))
        self.db.commit()

    def remover_itens(self, itens: list[GrupoRoomlist]) -> None:
        for item in itens:
            self.db.delete(item)
        self.db.commit()
