from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GrupoHistorico(Base):
    __tablename__ = "grupos_historico"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )
    # GRUPO, ORCAMENTO, PAGAMENTO, ROOMLIST, ANEXO, COMENTARIO
    entidade: Mapped[str] = mapped_column(String(30), nullable=False)
    entidade_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    # CRIACAO, EDICAO, EXCLUSAO, STATUS
    acao: Mapped[str] = mapped_column(String(30), nullable=False)
    campo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    valor_anterior: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor_novo: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo")
    usuario: Mapped["Usuario"] = relationship("Usuario")

    def __repr__(self) -> str:
        return f"<GrupoHistorico grupo={self.grupo_id} entidade={self.entidade} campo={self.campo}>"
