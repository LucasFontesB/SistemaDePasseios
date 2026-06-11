from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract

from app.models.venda import Venda
from app.models.usuario import Usuario
from app.models.passeio import Passeio
from app.models.tipo_passeio import TipoPasseio
from app.models.embarcacao import Embarcacao
from app.core.constants import STATUS_CANCELADO, STATUS_REEMBOLSADO


class GerencialRepository:

    def __init__(self, db: Session):
        self.db = db

    def _filtro_base(self, query, data_inicial, data_final):
        if data_inicial:
            query = query.filter(Venda.data_saida >= data_inicial)
        if data_final:
            query = query.filter(Venda.data_saida <= data_final)
        return query

    def _filtro_ativas(self, query):
        return query.filter(
            Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO])
        )

    # -------------------------------------------------------------------------
    # Resumo geral
    # -------------------------------------------------------------------------

    def resumo_geral(self, data_inicial: date = None, data_final: date = None) -> dict:
        base = self.db.query(Venda)
        base = self._filtro_base(base, data_inicial, data_final)

        total = base.count()
        ativas = self._filtro_ativas(base).count()
        canceladas = base.filter(Venda.status == STATUS_CANCELADO).count()

        financeiro = self._filtro_ativas(
            self._filtro_base(self.db.query(
                func.coalesce(func.sum(Venda.valor_total), 0).label("receita"),
                func.coalesce(func.sum(Venda.valor_comissao), 0).label("comissao"),
                func.coalesce(func.sum(Venda.adultos + Venda.criancas), 0).label("passageiros"),
            ), data_inicial, data_final)
        ).first()

        taxa_cancelamento = round(canceladas / total * 100, 1) if total > 0 else 0

        return {
            "total_vendas": total,
            "vendas_ativas": ativas,
            "canceladas": canceladas,
            "taxa_cancelamento": taxa_cancelamento,
            "receita_total": float(financeiro.receita or 0),
            "comissao_total": float(financeiro.comissao or 0),
            "total_passageiros": int(financeiro.passageiros or 0),
            "ticket_medio": float(financeiro.receita or 0) / ativas if ativas > 0 else 0,
            "media_passageiros": int(financeiro.passageiros or 0) / ativas if ativas > 0 else 0,
        }

    # -------------------------------------------------------------------------
    # Ranking de vendedores
    # -------------------------------------------------------------------------

    def ranking_vendedores(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                Usuario.nome,
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("receita"),
                func.coalesce(func.sum(Venda.valor_comissao), 0).label("comissao"),
                func.coalesce(func.sum(Venda.adultos + Venda.criancas), 0).label("passageiros"),
            )
            .join(Venda, Venda.usuario_id == Usuario.id)
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        return (
            query.group_by(Usuario.id, Usuario.nome)
            .order_by(func.count(Venda.id).desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Ranking de passeios
    # -------------------------------------------------------------------------

    def ranking_passeios(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                Passeio.nome,
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("receita"),
                func.coalesce(func.sum(Venda.valor_comissao), 0).label("comissao"),
                func.coalesce(func.sum(Venda.adultos + Venda.criancas), 0).label("passageiros"),
            )
            .join(Venda, Venda.passeio_id == Passeio.id)
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        return (
            query.group_by(Passeio.id, Passeio.nome)
            .order_by(func.count(Venda.id).desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Ranking de tipos de passeio
    # -------------------------------------------------------------------------

    def ranking_tipos(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                TipoPasseio.nome,
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("receita"),
            )
            .join(Venda, Venda.tipo_passeio_id == TipoPasseio.id)
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        return (
            query.group_by(TipoPasseio.id, TipoPasseio.nome)
            .order_by(func.count(Venda.id).desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Ranking de embarcações
    # -------------------------------------------------------------------------

    def ranking_embarcacoes(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                Embarcacao.nome,
                Embarcacao.capacidade,
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.adultos + Venda.criancas), 0).label("passageiros"),
            )
            .join(Venda, Venda.embarcacao_id == Embarcacao.id)
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        return (
            query.group_by(Embarcacao.id, Embarcacao.nome, Embarcacao.capacidade)
            .order_by(func.count(Venda.id).desc())
            .all()
        )

    # -------------------------------------------------------------------------
    # Antecedência de reserva
    # -------------------------------------------------------------------------

    def antecedencia_reserva(self, data_inicial: date = None, data_final: date = None) -> dict:
        query = (
            self.db.query(Venda.criado_em, Venda.data_saida)
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        vendas = query.all()

        if not vendas:
            return {"media_dias": 0, "no_dia": 0, "ate_7_dias": 0, "ate_30_dias": 0, "mais_30_dias": 0}

        antecedencias = []
        for v in vendas:
            dias = (v.data_saida - v.criado_em.date()).days
            antecedencias.append(max(dias, 0))

        total = len(antecedencias)
        return {
            "media_dias": round(sum(antecedencias) / total, 1),
            "no_dia":       sum(1 for d in antecedencias if d == 0),
            "ate_7_dias":   sum(1 for d in antecedencias if 1 <= d <= 7),
            "ate_30_dias":  sum(1 for d in antecedencias if 8 <= d <= 30),
            "mais_30_dias": sum(1 for d in antecedencias if d > 30),
        }

    # -------------------------------------------------------------------------
    # Horários mais populares
    # -------------------------------------------------------------------------

    def horarios_populares(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                Venda.horario_saida,
                func.count(Venda.id).label("quantidade"),
            )
            .filter(
                Venda.horario_saida.isnot(None),
                Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]),
            )
        )
        query = self._filtro_base(query, data_inicial, data_final)
        return (
            query.group_by(Venda.horario_saida)
            .order_by(func.count(Venda.id).desc())
            .limit(5)
            .all()
        )

    # -------------------------------------------------------------------------
    # Dias da semana
    # -------------------------------------------------------------------------

    def vendas_por_dia_semana(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                extract("dow", Venda.data_saida).label("dia_semana"),
                func.count(Venda.id).label("quantidade"),
            )
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        resultados = (
            query.group_by("dia_semana")
            .order_by("dia_semana")
            .all()
        )

        nomes = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        mapa = {int(r.dia_semana): r.quantidade for r in resultados}
        return [{"dia": nomes[i], "quantidade": mapa.get(i, 0)} for i in range(7)]

    # -------------------------------------------------------------------------
    # Formas de pagamento
    # -------------------------------------------------------------------------

    def formas_pagamento(self, data_inicial: date = None, data_final: date = None) -> list:
        query = (
            self.db.query(
                Venda.forma_pagamento,
                func.count(Venda.id).label("quantidade"),
                func.coalesce(func.sum(Venda.valor_total), 0).label("receita"),
            )
            .filter(Venda.status.notin_([STATUS_CANCELADO, STATUS_REEMBOLSADO]))
        )
        query = self._filtro_base(query, data_inicial, data_final)
        return (
            query.group_by(Venda.forma_pagamento)
            .order_by(func.count(Venda.id).desc())
            .all()
        )
