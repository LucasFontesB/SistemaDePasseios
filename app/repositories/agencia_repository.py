from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.agencia import Agencia


class AgenciaRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> list[Agencia]:
        return (
            self.db.query(Agencia)
            .filter(Agencia.deletado_em.is_(None))
            .order_by(Agencia.nome)
            .all()
        )

    def find_by_id(self, agencia_id: uuid.UUID) -> Agencia | None:
        return (
            self.db.query(Agencia)
            .filter(Agencia.id == agencia_id, Agencia.deletado_em.is_(None))
            .first()
        )

    def create(
        self,
        nome: str,
        nome_fantasia: str | None,
        cnpj: str | None,
        contato: str | None,
        telefone: str | None,
        email: str | None,
        percentual_comissao_padrao: float,
        observacao: str | None,
    ) -> Agencia:
        agencia = Agencia(
            id=uuid.uuid4(),
            nome=nome,
            nome_fantasia=nome_fantasia,
            cnpj=cnpj,
            contato=contato,
            telefone=telefone,
            email=email,
            percentual_comissao_padrao=percentual_comissao_padrao,
            observacao=observacao,
        )
        self.db.add(agencia)
        self.db.commit()
        self.db.refresh(agencia)
        return agencia

    def update(
        self,
        agencia: Agencia,
        nome: str,
        nome_fantasia: str | None,
        cnpj: str | None,
        contato: str | None,
        telefone: str | None,
        email: str | None,
        percentual_comissao_padrao: float,
        observacao: str | None,
    ) -> Agencia:
        agencia.nome = nome
        agencia.nome_fantasia = nome_fantasia
        agencia.cnpj = cnpj
        agencia.contato = contato
        agencia.telefone = telefone
        agencia.email = email
        agencia.percentual_comissao_padrao = percentual_comissao_padrao
        agencia.observacao = observacao
        agencia.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(agencia)
        return agencia

    def soft_delete(self, agencia: Agencia) -> None:
        agencia.deletado_em = datetime.utcnow()
        self.db.commit()
