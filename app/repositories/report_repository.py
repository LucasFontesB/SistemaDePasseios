from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.models.venda import Venda
from app.models.usuario import Usuario
from app.models.passeio import Passeio
from app.core.constants import STATUS_CANCELADO, STATUS_REEMBOLSADO


class ReportRepository:

    def __init__(self, db: Session):
        self.db = db

    def vendas(
        self,
        data_inicial: date = None,
        data_final: date = None,
        passeio_id: str = None,
        status: str = None,
        usuario_id: str = None,
    ) -> list:
        """Retorna vendas com filtros aplicados."""
        query = (
            self.db.query(Venda)
            .options(
                joinedload(Venda.passeio),
                joinedload(Venda.tipo_passeio),
                joinedload(Venda.usuario),
            )
        )

        if data_inicial:
            query = query.filter(Venda.data_saida >= data_inicial)
        if data_final:
            query = query.filter(Venda.data_saida <= data_final)
        if passeio_id:
            query = query.filter(Venda.passeio_id == passeio_id)
        if status:
            query = query.filter(Venda.status == status)
        if usuario_id:
            query = query.filter(Venda.usuario_id == usuario_id)

        return query.order_by(Venda.data_saida.desc(), Venda.criado_em.desc()).all()

    def totais_vendas(self, vendas: list) -> dict:
        """Calcula totais a partir da lista já filtrada."""
        # Exclui cancelados e reembolsados dos totais financeiros
        ativas = [v for v in vendas if v.status not in (STATUS_CANCELADO, STATUS_REEMBOLSADO)]

        total_vendido = sum(float(v.valor_total) for v in ativas)
        total_comissao = sum(float(v.valor_comissao) for v in ativas)
        total_passageiros = sum(v.adultos + v.criancas for v in ativas)

        return {
            "quantidade": len(vendas),
            "quantidade_ativas": len(ativas),
            "total_vendido": total_vendido,
            "total_comissao": total_comissao,
            "total_passageiros": total_passageiros,
        }

    def comissoes_por_usuario(
        self,
        data_inicial: date = None,
        data_final: date = None,
        usuario_id: str = None,
    ) -> list:
        """Retorna comissões agrupadas por recepcionista."""
        query = (
            self.db.query(
                Usuario.id,
                Usuario.nome,
                func.count(Venda.id).label("quantidade_vendas"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("total_vendido"),
                func.coalesce(func.sum(Venda.valor_comissao), 0).label("total_comissao"),
            )
            .join(Venda, Venda.usuario_id == Usuario.id)
            .filter(
                Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]),
                Usuario.deletado_em.is_(None),
            )
        )

        if data_inicial:
            query = query.filter(Venda.data_saida >= data_inicial)
        if data_final:
            query = query.filter(Venda.data_saida <= data_final)
        if usuario_id:
            query = query.filter(Venda.usuario_id == usuario_id)

        return (
            query
            .group_by(Usuario.id, Usuario.nome)
            .order_by(func.sum(Venda.valor_comissao).desc())
            .all()
        )

    def count_recepcionistas_ativos(self) -> int:
        """Retorna quantidade de recepcionistas ativos."""
        return (
            self.db.query(func.count(Usuario.id))
            .filter(
                Usuario.perfil == "RECEPCAO",
                Usuario.deletado_em.is_(None),
            )
            .scalar() or 1
        )

    def list_usuarios_ativos(self) -> list:
        """Lista usuários ativos para popular o filtro de recepcionista."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.deletado_em.is_(None))
            .order_by(Usuario.nome)
            .all()
        )