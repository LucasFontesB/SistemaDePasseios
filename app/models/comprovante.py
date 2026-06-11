import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Comprovante(Base):
    __tablename__ = "comprovantes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    venda_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendas.id"), nullable=False
    )
    nome_original: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    caminho: Mapped[str] = mapped_column(String(500), nullable=False)
    tipo_arquivo: Mapped[str] = mapped_column(String(50), nullable=False)
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    enviado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    # Relacionamentos
    venda: Mapped["Venda"] = relationship("Venda", back_populates="comprovantes")

    def __repr__(self) -> str:
        return f"<Comprovante id={self.id} venda_id={self.venda_id} arquivo={self.nome_original}>"
