from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.guia import Guia


class GuiaRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> list[Guia]:
        return (
            self.db.query(Guia)
            .filter(Guia.deletado_em.is_(None))
            .order_by(Guia.nome)
            .all()
        )

    def find_by_id(self, guia_id: uuid.UUID) -> Guia | None:
        return (
            self.db.query(Guia)
            .filter(Guia.id == guia_id, Guia.deletado_em.is_(None))
            .first()
        )

    def create(
        self,
        nome: str,
        cpf: str | None,
        cadastur: str | None,
        telefone: str | None,
        email: str | None,
        percentual_comissao_padrao: float,
        observacao: str | None,
    ) -> Guia:
        guia = Guia(
            id=uuid.uuid4(),
            nome=nome,
            cpf=cpf,
            cadastur=cadastur,
            telefone=telefone,
            email=email,
            percentual_comissao_padrao=percentual_comissao_padrao,
            observacao=observacao,
        )
        self.db.add(guia)
        self.db.commit()
        self.db.refresh(guia)
        return guia

    def update(
        self,
        guia: Guia,
        nome: str,
        cpf: str | None,
        cadastur: str | None,
        telefone: str | None,
        email: str | None,
        percentual_comissao_padrao: float,
        observacao: str | None,
    ) -> Guia:
        guia.nome = nome
        guia.cpf = cpf
        guia.cadastur = cadastur
        guia.telefone = telefone
        guia.email = email
        guia.percentual_comissao_padrao = percentual_comissao_padrao
        guia.observacao = observacao
        guia.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(guia)
        return guia

    def soft_delete(self, guia: Guia) -> None:
        guia.deletado_em = datetime.utcnow()
        self.db.commit()
