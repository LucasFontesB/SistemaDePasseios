from __future__ import annotations
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Grupo(Base):
    __tablename__ = "grupos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    codigo: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    responsavel: Mapped[str | None] = mapped_column(String(200), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)

    agencia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agencias.id"), nullable=True
    )
    guia_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("guias.id"), nullable=True
    )

    data_entrada: Mapped[date] = mapped_column(Date, nullable=False)
    data_saida: Mapped[date] = mapped_column(Date, nullable=False)
    qtd_hospedes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # RN-G020: qtd_apartamentos e os dois totais abaixo são agregados
    # calculados a partir de grupos_apartamentos — não são mais digitados
    # diretamente (exceto os totais, que aceitam override manual).
    qtd_apartamentos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qtd_apartamentos_cortesia: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # RN-G028: puramente informativo — a composição real (qtd_apartamentos) é
    # sempre a fonte de verdade, isto é só referência de planejamento.
    qtd_apartamentos_prevista: Mapped[int | None] = mapped_column(Integer, nullable=True)

    valor_total_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    valor_total_net_manual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    valor_total_sistema: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    valor_total_sistema_manual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # PROSPECCAO, ORCAMENTO_ENVIADO, EM_NEGOCIACAO, CONFIRMADO, HOSPEDADO, FINALIZADO, CANCELADO, PERDIDO
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PROSPECCAO")
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    # RN-G021: informativos, não entram na verificação de divergência do orçamento.
    prazo_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    prazo_roomlist: Mapped[date | None] = mapped_column(Date, nullable=True)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    agencia: Mapped["Agencia"] = relationship("Agencia")
    guia: Mapped["Guia"] = relationship("Guia")
    usuario: Mapped["Usuario"] = relationship("Usuario")
    pagamentos: Mapped[list["GrupoPagamento"]] = relationship(
        "GrupoPagamento", back_populates="grupo", order_by="GrupoPagamento.criado_em.desc()"
    )
    apartamentos: Mapped[list["GrupoApartamento"]] = relationship(
        "GrupoApartamento", back_populates="grupo"
    )

    @property
    def noites(self) -> int:
        return (self.data_saida - self.data_entrada).days

    @property
    def apartamentos_ocupados(self) -> int:
        """RN-G015: cortesia entra na ocupação, mas não em cálculo de valor."""
        return self.qtd_apartamentos + self.qtd_apartamentos_cortesia

    @property
    def valor_comissao(self) -> float:
        return float(self.valor_total_sistema) - float(self.valor_total_net)

    @property
    def percentual_efetivo(self) -> float:
        total_sistema = float(self.valor_total_sistema)
        if total_sistema <= 0:
            return 0.0
        return self.valor_comissao / total_sistema * 100

    @property
    def valor_pago(self) -> float:
        return sum((float(p.valor) for p in self.pagamentos), 0.0)

    @property
    def saldo(self) -> float:
        """RN-G027: base financeira é o valor sistema — o que o hotel
        efetivamente recebe/controla. Net é referência de agência/comissão,
        não mais a base de pagamento/saldo (RN-G001, revogada)."""
        return float(self.valor_total_sistema) - self.valor_pago

    def __repr__(self) -> str:
        return f"<Grupo id={self.id} codigo={self.codigo} nome={self.nome}>"
