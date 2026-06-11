from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Passeio(Base):
    __tablename__ = "passeios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    percentual_comissao: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deletado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    # Relacionamentos
    vendas: Mapped[list["Venda"]] = relationship("Venda", back_populates="passeio")

    def __repr__(self) -> str:
        return f"<Passeio id={self.id} nome={self.nome}>"