from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.tipo_apartamento import TipoApartamento


class TipoApartamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> list[TipoApartamento]:
        return (
            self.db.query(TipoApartamento)
            .filter(TipoApartamento.deletado_em.is_(None))
            .order_by(TipoApartamento.ordem, TipoApartamento.nome)
            .all()
        )

    def find_by_id(self, tipo_id: uuid.UUID) -> TipoApartamento | None:
        return (
            self.db.query(TipoApartamento)
            .filter(TipoApartamento.id == tipo_id, TipoApartamento.deletado_em.is_(None))
            .first()
        )

    def find_by_nome(self, nome: str) -> TipoApartamento | None:
        return (
            self.db.query(TipoApartamento)
            .filter(TipoApartamento.nome == nome, TipoApartamento.deletado_em.is_(None))
            .first()
        )

    def find_by_nome_qualquer(self, nome: str) -> TipoApartamento | None:
        """Busca por nome ignorando soft delete — usado para reconstituir a
        composição do grupo a partir do snapshot de um orçamento aprovado
        (RN-G007), mesmo que o tipo tenha sido desativado depois."""
        return (
            self.db.query(TipoApartamento)
            .filter(TipoApartamento.nome == nome)
            .first()
        )

    def create(
        self,
        nome: str,
        ordem: int,
        valor_diaria_net_padrao: float,
        valor_diaria_sistema_padrao: float,
        observacao: str | None,
    ) -> TipoApartamento:
        tipo = TipoApartamento(
            id=uuid.uuid4(),
            nome=nome,
            ordem=ordem,
            valor_diaria_net_padrao=valor_diaria_net_padrao,
            valor_diaria_sistema_padrao=valor_diaria_sistema_padrao,
            observacao=observacao,
        )
        self.db.add(tipo)
        self.db.commit()
        self.db.refresh(tipo)
        return tipo

    def update(
        self,
        tipo: TipoApartamento,
        nome: str,
        ordem: int,
        valor_diaria_net_padrao: float,
        valor_diaria_sistema_padrao: float,
        observacao: str | None,
    ) -> TipoApartamento:
        tipo.nome = nome
        tipo.ordem = ordem
        tipo.valor_diaria_net_padrao = valor_diaria_net_padrao
        tipo.valor_diaria_sistema_padrao = valor_diaria_sistema_padrao
        tipo.observacao = observacao
        tipo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tipo)
        return tipo

    def soft_delete(self, tipo: TipoApartamento) -> None:
        tipo.deletado_em = datetime.utcnow()
        self.db.commit()
