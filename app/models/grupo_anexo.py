from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GrupoAnexo(Base):
    __tablename__ = "grupos_anexos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    orcamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos_orcamentos.id"), nullable=True
    )
    pagamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos_pagamentos.id"), nullable=True
    )

    # COMPROVANTE_PAGAMENTO, ORCAMENTO_ASSINADO, OUTRO
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, default="OUTRO")
    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_arquivo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tamanho_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    enviado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    removido_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, default=None)

    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo")
    usuario: Mapped["Usuario"] = relationship("Usuario")

    def __repr__(self) -> str:
        return f"<GrupoAnexo id={self.id} grupo_id={self.grupo_id} arquivo={self.nome_original}>"
