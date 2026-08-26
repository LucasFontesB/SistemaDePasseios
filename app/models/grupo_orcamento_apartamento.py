from __future__ import annotations
import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class GrupoOrcamentoApartamento(Base):
    """
    RN-G013: linha congelada da composição por tipo, uma por tipo usado na
    versão. `tipo_apartamento_nome` é texto, não FK — deliberado: se o
    cadastro for renomeado ou desativado depois, este documento continua
    mostrando o nome de quando foi gerado. Diferente de grupos_apartamentos,
    aqui o subtotal É persistido, porque é documento congelado, não dado vivo.
    """

    __tablename__ = "grupos_orcamentos_apartamentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    orcamento_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos_orcamentos.id"), nullable=False
    )
    tipo_apartamento_nome: Mapped[str] = mapped_column(String(50), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_diaria_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valor_diaria_sistema: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valor_total_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    valor_total_sistema: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relacionamentos
    orcamento: Mapped["GrupoOrcamento"] = relationship("GrupoOrcamento", back_populates="apartamentos")

    def __repr__(self) -> str:
        return f"<GrupoOrcamentoApartamento orcamento={self.orcamento_id} tipo={self.tipo_apartamento_nome}>"
