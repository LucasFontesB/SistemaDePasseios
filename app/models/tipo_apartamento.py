from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database.base import Base


class TipoApartamento(Base):
    __tablename__ = "tipos_apartamento"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    valor_diaria_net_padrao: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    valor_diaria_sistema_padrao: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deletado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    def __repr__(self) -> str:
        return f"<TipoApartamento id={self.id} nome={self.nome}>"
