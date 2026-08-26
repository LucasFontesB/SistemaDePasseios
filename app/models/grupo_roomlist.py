from __future__ import annotations
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GrupoRoomlist(Base):
    __tablename__ = "grupos_roomlist"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    apartamento: Mapped[str | None] = mapped_column(String(30), nullable=True)
    hospede_nome: Mapped[str] = mapped_column(String(200), nullable=False)
    documento: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # RN-G023: deixa de ser texto livre — mesmo cadastro usado na composição
    # de tarifa do grupo, para manter os nomes consistentes entre roomlist e cobrança.
    tipo_apartamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tipos_apartamento.id"), nullable=True
    )
    # RN-G015: cortesia entra na ocupação, nunca em cálculo de valor.
    cortesia: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    check_in: Mapped[date | None] = mapped_column(Date, nullable=True)
    check_out: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo")
    tipo_apartamento: Mapped["TipoApartamento"] = relationship("TipoApartamento")

    def __repr__(self) -> str:
        return f"<GrupoRoomlist id={self.id} grupo_id={self.grupo_id} hospede={self.hospede_nome}>"
