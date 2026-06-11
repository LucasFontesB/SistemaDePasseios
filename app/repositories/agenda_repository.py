from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session, joinedload

from app.models.venda import Venda
from app.core.constants import STATUS_CANCELADO, STATUS_REEMBOLSADO, STATUS_FINALIZADO


class AgendaRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_embarques(self, data: date) -> list[Venda]:
        """Retorna todas as vendas com saída na data informada, exceto canceladas, reembolsadas e finalizadas."""
        return (
            self.db.query(Venda)
            .options(
                joinedload(Venda.passeio),
                joinedload(Venda.tipo_passeio),
                joinedload(Venda.embarcacao),
                joinedload(Venda.usuario),
                joinedload(Venda.comprovantes),
            )
            .filter(
                Venda.data_saida == data,
                Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO, STATUS_FINALIZADO]),
            )
            .order_by(Venda.horario_saida.asc().nullslast(), Venda.contratante.asc())
            .all()
        )

    def get_totais(self, vendas: list[Venda]) -> dict:
        """Calcula totais do dia."""
        return {
            "quantidade": len(vendas),
            "passageiros": sum(v.adultos + v.criancas for v in vendas),
            "valor_total": sum(float(v.valor_total) for v in vendas),
            "sem_comprovante": sum(1 for v in vendas if not v.comprovantes),
        }
