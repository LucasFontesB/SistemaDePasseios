from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Embarcacao(Base):
    __tablename__ = "embarcacoes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    capacidade: Mapped[int] = mapped_column(Integer, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deletado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    # Relacionamentos
    vendas: Mapped[list["Venda"]] = relationship("Venda", back_populates="embarcacao")

    def __repr__(self) -> str:
        return f"<Embarcacao id={self.id} nome={self.nome}>"