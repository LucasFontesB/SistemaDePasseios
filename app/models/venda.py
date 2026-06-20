from __future__ import annotations
import uuid
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Venda(Base):
    __tablename__ = "vendas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    numero_venda: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    contratante: Mapped[str] = mapped_column(String(200), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    adultos: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    criancas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    passeio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("passeios.id"), nullable=False
    )
    tipo_passeio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tipos_passeio.id"), nullable=False
    )
    embarcacao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("embarcacoes.id"), nullable=True
    )

    valor_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    percentual_comissao: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    valor_comissao: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    data_saida: Mapped[date] = mapped_column(Date, nullable=False)
    horario_saida: Mapped[time | None] = mapped_column(Time, nullable=True)

    # PENDENTE, AGUARDANDO_PAGAMENTO, CONFIRMADO, EMBARCADO, FINALIZADO, CANCELADO, REEMBOLSADO
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDENTE")
    forma_pagamento: Mapped[str | None] = mapped_column(String(30), nullable=True)

    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    passeio: Mapped["Passeio"] = relationship("Passeio", back_populates="vendas")
    tipo_passeio: Mapped["TipoPasseio"] = relationship("TipoPasseio", back_populates="vendas")
    embarcacao: Mapped["Embarcacao"] = relationship("Embarcacao", back_populates="vendas")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="vendas")
    comprovantes: Mapped[list["Comprovante"]] = relationship("Comprovante", back_populates="venda")
    historico: Mapped[list["VendaHistorico"]] = relationship("VendaHistorico", back_populates="venda", order_by="VendaHistorico.criado_em.desc()")
    comprovantes: Mapped[list["Comprovante"]] = relationship("Comprovante", back_populates="venda")
    pagamentos: Mapped[list["Pagamento"]] = relationship(
        "Pagamento", back_populates="venda", order_by="Pagamento.criado_em.desc()"
    )
    historico: Mapped[list["VendaHistorico"]] = relationship("VendaHistorico", back_populates="venda",
                                                             order_by="VendaHistorico.criado_em.desc()")

    @property
    def valor_pago(self) -> float:
        return sum((float(p.valor) for p in self.pagamentos), 0.0)

    @property
    def saldo_restante(self) -> float:
        return float(self.valor_total) - self.valor_pago

    @property
    def status_pagamento(self) -> str:
        pago = self.valor_pago
        if pago <= 0:
            return "NAO_PAGO"
        if pago < float(self.valor_total):
            return "PARCIAL"
        return "PAGO"

    def __repr__(self) -> str:
        return f"<Venda id={self.id} numero={self.numero_venda} status={self.status}>"