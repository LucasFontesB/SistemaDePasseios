from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendas.id"), nullable=False
    )

    # Valor pode ser negativo apenas para lançamentos de ajuste/correção.
    # Registros financeiros nunca são removidos (RN007 - DATABASE.md).
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # DINHEIRO, PIX, CARTAO_DEBITO, CARTAO_CREDITO
    forma_pagamento: Mapped[str] = mapped_column(String(30), nullable=False)

    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relacionamentos
    venda: Mapped["Venda"] = relationship("Venda", back_populates="pagamentos")
    usuario: Mapped["Usuario"] = relationship("Usuario")

    def __repr__(self) -> str:
        return f"<Pagamento id={self.id} venda_id={self.venda_id} valor={self.valor}>"