from __future__ import annotations

import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.venda import Venda
from app.models.usuario import Usuario
from app.models.comprovante import Comprovante
from app.core.constants import (
    STATUS_PENDENTE,
    STATUS_AGUARDANDO_PAGAMENTO,
    STATUS_CONFIRMADO,
    STATUS_EMBARCADO,
    STATUS_CANCELADO,
    STATUS_REEMBOLSADO,
)


class DashboardRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_indicadores_hoje(self) -> dict:
        """Retorna quantidade de vendas, valor total e passageiros do dia."""
        hoje = date.today()
        vendas_ativas = [STATUS_PENDENTE, STATUS_AGUARDANDO_PAGAMENTO, STATUS_CONFIRMADO, STATUS_EMBARCADO]

        resultado = (
            self.db.query(
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("valor_total"),
                func.coalesce(func.sum(Venda.adultos + Venda.criancas), 0).label("passageiros"),
            )
            .filter(
                func.date(Venda.criado_em) == hoje,
                Venda.status.in_(vendas_ativas),
            )
            .first()
        )

        return {
            "quantidade": resultado.quantidade or 0,
            "valor_total": float(resultado.valor_total or 0),
            "passageiros": resultado.passageiros or 0,
        }

    def get_indicadores_mes(self) -> dict:
        """Retorna quantidade de vendas, valor total e comissão do mês atual."""
        hoje = date.today()
        vendas_ativas = [STATUS_PENDENTE, STATUS_AGUARDANDO_PAGAMENTO, STATUS_CONFIRMADO, STATUS_EMBARCADO]

        resultado = (
            self.db.query(
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("valor_total"),
                func.coalesce(func.sum(Venda.valor_comissao), 0).label("valor_comissao"),
            )
            .filter(
                func.extract("month", Venda.criado_em) == hoje.month,
                func.extract("year", Venda.criado_em) == hoje.year,
                Venda.status.in_(vendas_ativas),
            )
            .first()
        )

        return {
            "quantidade": resultado.quantidade or 0,
            "valor_total": float(resultado.valor_total or 0),
            "valor_comissao": float(resultado.valor_comissao or 0),
        }

    def get_proximos_embarques(self, limite: int = 10) -> list:
        """Retorna próximos embarques a partir de hoje."""
        hoje = date.today()

        vendas = (
            self.db.query(Venda)
            .filter(
                Venda.data_saida >= hoje,
                Venda.status.in_([STATUS_CONFIRMADO, STATUS_AGUARDANDO_PAGAMENTO, STATUS_PENDENTE]),
            )
            .order_by(Venda.data_saida.asc(), Venda.horario_saida.asc())
            .limit(limite)
            .all()
        )

        return vendas

    def get_pendencias(self) -> dict:
        """Retorna contagem de pendências."""
        # Vendas aguardando pagamento
        aguardando_pagamento = (
            self.db.query(func.count(Venda.id))
            .filter(Venda.status == STATUS_AGUARDANDO_PAGAMENTO)
            .scalar() or 0
        )

        # Vendas confirmadas sem comprovante
        vendas_confirmadas = (
            self.db.query(Venda.id)
            .filter(Venda.status.in_([STATUS_CONFIRMADO, STATUS_AGUARDANDO_PAGAMENTO]))
            .subquery()
        )
        com_comprovante = (
            self.db.query(Comprovante.venda_id)
            .distinct()
            .subquery()
        )
        sem_comprovante = (
            self.db.query(func.count())
            .filter(
                Venda.id.in_(vendas_confirmadas),
                Venda.id.notin_(com_comprovante),
            )
            .scalar() or 0
        )

        return {
            "aguardando_pagamento": aguardando_pagamento,
            "sem_comprovante": sem_comprovante,
        }

    def get_comissao_recepcao(self, usuario_id: uuid.UUID) -> dict:
        """
        Retorna comissão individual e comissão pelo critério do hotel
        para o mês atual.

        Critério do hotel:
            total_comissao_geral ÷ 2 ÷ quantidade_recepcionistas_ativos
        """
        hoje = date.today()
        excluidos = [STATUS_CANCELADO, STATUS_REEMBOLSADO]

        filtro_mes = [
            func.extract("month", Venda.data_saida) == hoje.month,
            func.extract("year", Venda.data_saida) == hoje.year,
            Venda.status.notin_(excluidos),
        ]

        # Comissão individual — apenas vendas do próprio usuário
        individual = (
            self.db.query(
                func.coalesce(func.sum(Venda.valor_comissao), 0).label("total"),
                func.count(Venda.id).label("quantidade"),
            )
            .filter(Venda.usuario_id == usuario_id, *filtro_mes)
            .first()
        )

        # Total geral de comissões do mês (todos os usuários)
        total_geral = (
            self.db.query(
                func.coalesce(func.sum(Venda.valor_comissao), 0)
            )
            .filter(*filtro_mes)
            .scalar() or 0
        )

        # Quantidade de recepcionistas ativos
        qtd_recepcionistas = (
            self.db.query(func.count(Usuario.id))
            .filter(
                Usuario.perfil == "RECEPCAO",
                Usuario.deletado_em.is_(None),
            )
            .scalar() or 1
        )

        # Cálculo do hotel: total ÷ 2 ÷ recepcionistas
        parte_recepcionistas = float(total_geral) / 2
        comissao_hotel = parte_recepcionistas / qtd_recepcionistas

        return {
            "individual_total": float(individual.total or 0),
            "individual_quantidade": individual.quantidade or 0,
            "total_geral": float(total_geral),
            "parte_recepcionistas": parte_recepcionistas,
            "qtd_recepcionistas": qtd_recepcionistas,
            "comissao_hotel": comissao_hotel,
        }