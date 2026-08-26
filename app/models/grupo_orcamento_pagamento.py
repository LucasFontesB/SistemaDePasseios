from __future__ import annotations
import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GrupoOrcamentoPagamento(Base):
    """RN-G013: um pagamento congelado por linha, existente até o momento
    da geração da versão. Independe de grupos_pagamentos continuar mudando
    depois — este registro nunca é alterado."""

    __tablename__ = "grupos_orcamentos_pagamentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orcamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos_orcamentos.id"), nullable=False
    )
    valor: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    data_pagamento: Mapped[date] = mapped_column(Date, nullable=False)
    forma_pagamento: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relacionamentos
    orcamento: Mapped["GrupoOrcamento"] = relationship("GrupoOrcamento", back_populates="pagamentos")

    def __repr__(self) -> str:
        return f"<GrupoOrcamentoPagamento orcamento={self.orcamento_id} valor={self.valor}>"
