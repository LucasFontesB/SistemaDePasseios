from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.passeio import Passeio
from app.models.tipo_passeio import TipoPasseio
from app.models.embarcacao import Embarcacao


class TourRepository:

    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # Passeios
    # -------------------------------------------------------------------------

    def list_passeios(self) -> list[Passeio]:
        return (
            self.db.query(Passeio)
            .filter(Passeio.deletado_em.is_(None))
            .order_by(Passeio.nome)
            .all()
        )

    def find_passeio_by_id(self, passeio_id: uuid.UUID) -> Passeio | None:
        return (
            self.db.query(Passeio)
            .filter(Passeio.id == passeio_id, Passeio.deletado_em.is_(None))
            .first()
        )

    def create_passeio(self, nome: str, descricao: str, percentual_comissao: float) -> Passeio:
        passeio = Passeio(
            id=uuid.uuid4(),
            nome=nome,
            descricao=descricao,
            percentual_comissao=percentual_comissao,
        )
        self.db.add(passeio)
        self.db.commit()
        self.db.refresh(passeio)
        return passeio

    def update_passeio(self, passeio: Passeio, nome: str, descricao: str, percentual_comissao: float) -> Passeio:
        passeio.nome = nome
        passeio.descricao = descricao
        passeio.percentual_comissao = percentual_comissao
        passeio.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(passeio)
        return passeio

    def soft_delete_passeio(self, passeio: Passeio) -> None:
        passeio.deletado_em = datetime.utcnow()
        self.db.commit()

    # -------------------------------------------------------------------------
    # Tipos de Passeio
    # -------------------------------------------------------------------------

    def list_tipos(self) -> list[TipoPasseio]:
        return (
            self.db.query(TipoPasseio)
            .filter(TipoPasseio.deletado_em.is_(None))
            .order_by(TipoPasseio.nome)
            .all()
        )

    def find_tipo_by_id(self, tipo_id: uuid.UUID) -> TipoPasseio | None:
        return (
            self.db.query(TipoPasseio)
            .filter(TipoPasseio.id == tipo_id, TipoPasseio.deletado_em.is_(None))
            .first()
        )

    def create_tipo(self, nome: str) -> TipoPasseio:
        tipo = TipoPasseio(id=uuid.uuid4(), nome=nome)
        self.db.add(tipo)
        self.db.commit()
        self.db.refresh(tipo)
        return tipo

    def update_tipo(self, tipo: TipoPasseio, nome: str) -> TipoPasseio:
        tipo.nome = nome
        tipo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(tipo)
        return tipo

    def soft_delete_tipo(self, tipo: TipoPasseio) -> None:
        tipo.deletado_em = datetime.utcnow()
        self.db.commit()

    # -------------------------------------------------------------------------
    # Embarcações
    # -------------------------------------------------------------------------

    def list_embarcacoes(self) -> list[Embarcacao]:
        return (
            self.db.query(Embarcacao)
            .filter(Embarcacao.deletado_em.is_(None))
            .order_by(Embarcacao.nome)
            .all()
        )

    def find_embarcacao_by_id(self, embarcacao_id: uuid.UUID) -> Embarcacao | None:
        return (
            self.db.query(Embarcacao)
            .filter(Embarcacao.id == embarcacao_id, Embarcacao.deletado_em.is_(None))
            .first()
        )

    def create_embarcacao(self, nome: str, capacidade: int, observacao: str) -> Embarcacao:
        embarcacao = Embarcacao(
            id=uuid.uuid4(),
            nome=nome,
            capacidade=capacidade,
            observacao=observacao,
        )
        self.db.add(embarcacao)
        self.db.commit()
        self.db.refresh(embarcacao)
        return embarcacao

    def update_embarcacao(self, embarcacao: Embarcacao, nome: str, capacidade: int, observacao: str) -> Embarcacao:
        embarcacao.nome = nome
        embarcacao.capacidade = capacidade
        embarcacao.observacao = observacao
        embarcacao.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(embarcacao)
        return embarcacao

    def soft_delete_embarcacao(self, embarcacao: Embarcacao) -> None:
        embarcacao.deletado_em = datetime.utcnow()
        self.db.commit()