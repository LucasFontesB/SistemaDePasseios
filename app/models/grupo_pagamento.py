from __future__ import annotations
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GrupoPagamento(Base):
    __tablename__ = "grupos_pagamentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )

    # Valor pode ser negativo apenas para lançamentos de ajuste/correção.
    # Pagamentos nunca são excluídos (RN-G008).
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=False)

    # DINHEIRO, PIX, CARTAO_DEBITO, CARTAO_CREDITO
    forma_pagamento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo", back_populates="pagamentos")
    usuario: Mapped["Usuario"] = relationship("Usuario")

    def __repr__(self) -> str:
        return f"<GrupoPagamento id={self.id} grupo_id={self.grupo_id} valor={self.valor}>"
