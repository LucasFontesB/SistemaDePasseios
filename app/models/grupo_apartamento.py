from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GrupoApartamento(Base):
    """
    RN-G020: fonte de verdade da composição de tarifa do grupo — uma linha
    por tipo de apartamento usado. Não guarda valor_total: assim como
    `Grupo.noites`, o subtotal é calculado em tempo real a partir de
    quantidade × diária × noites, nunca persistido, para não dessincronizar.
    """

    __tablename__ = "grupos_apartamentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    tipo_apartamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tipos_apartamento.id"), nullable=False
    )
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valor_diaria_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    valor_diaria_sistema: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo", back_populates="apartamentos")
    tipo_apartamento: Mapped["TipoApartamento"] = relationship("TipoApartamento")

    def subtotal_net(self, noites: int) -> float:
        return self.quantidade * float(self.valor_diaria_net) * noites

    def subtotal_sistema(self, noites: int) -> float:
        return self.quantidade * float(self.valor_diaria_sistema) * noites

    def __repr__(self) -> str:
        return f"<GrupoApartamento id={self.id} grupo_id={self.grupo_id} tipo={self.tipo_apartamento_id}>"
