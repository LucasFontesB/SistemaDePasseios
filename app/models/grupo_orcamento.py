from __future__ import annotations
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GrupoOrcamento(Base):
    __tablename__ = "grupos_orcamentos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    grupo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=False
    )
    versao: Mapped[int] = mapped_column(Integer, nullable=False)

    # Snapshot congelado no momento da geração (RN-G006/RN-G013) — nunca editado.
    qtd_hospedes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qtd_apartamentos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    qtd_apartamentos_cortesia: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    noites: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Totais agregados congelados — RN-G020 já era composição por tipo
    # quando esta versão foi gerada; o detalhamento por tipo vive em
    # grupos_orcamentos_apartamentos, não aqui.
    valor_total_net: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    valor_total_sistema: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    valor_pago_snapshot: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    saldo_snapshot: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    motivo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    validade: Mapped[date | None] = mapped_column(Date, nullable=True)
    condicoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # RASCUNHO, ENVIADO, APROVADO, RECUSADO — únicos campos que mudam após a criação.
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="RASCUNHO")
    desatualizado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # RN-G013: demais campos que podem mudar depois e por isso são congelados.
    data_entrada_snapshot: Mapped[date | None] = mapped_column(Date, nullable=True)
    data_saida_snapshot: Mapped[date | None] = mapped_column(Date, nullable=True)
    status_snapshot: Mapped[str | None] = mapped_column(String(30), nullable=True)
    prazo_deadline_snapshot: Mapped[date | None] = mapped_column(Date, nullable=True)
    prazo_roomlist_snapshot: Mapped[date | None] = mapped_column(Date, nullable=True)

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    grupo: Mapped["Grupo"] = relationship("Grupo")
    usuario: Mapped["Usuario"] = relationship("Usuario")
    apartamentos: Mapped[list["GrupoOrcamentoApartamento"]] = relationship(
        "GrupoOrcamentoApartamento", back_populates="orcamento"
    )
    pagamentos: Mapped[list["GrupoOrcamentoPagamento"]] = relationship(
        "GrupoOrcamentoPagamento", back_populates="orcamento", order_by="GrupoOrcamentoPagamento.data_pagamento"
    )

    @property
    def apartamentos_ocupados(self) -> int:
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

    def __repr__(self) -> str:
        return f"<GrupoOrcamento grupo={self.grupo_id} versao={self.versao} status={self.status}>"
