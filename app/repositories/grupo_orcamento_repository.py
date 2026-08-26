from __future__ import annotations
import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_orcamento import GrupoOrcamento
from app.models.grupo import Grupo


class GrupoOrcamentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list[GrupoOrcamento]:
        return (
            self.db.query(GrupoOrcamento)
            .options(joinedload(GrupoOrcamento.usuario))
            .filter(GrupoOrcamento.grupo_id == grupo_id)
            .order_by(GrupoOrcamento.versao.desc())
            .all()
        )

    def find_by_id(self, orcamento_id: uuid.UUID) -> GrupoOrcamento | None:
        return (
            self.db.query(GrupoOrcamento)
            .options(
                joinedload(GrupoOrcamento.usuario),
                joinedload(GrupoOrcamento.grupo).joinedload(Grupo.agencia),
                joinedload(GrupoOrcamento.grupo).joinedload(Grupo.guia),
            )
            .filter(GrupoOrcamento.id == orcamento_id)
            .first()
        )

    def find_ultima_versao(self, grupo_id: uuid.UUID) -> GrupoOrcamento | None:
        return (
            self.db.query(GrupoOrcamento)
            .filter(GrupoOrcamento.grupo_id == grupo_id)
            .order_by(GrupoOrcamento.versao.desc())
            .first()
        )

    def proxima_versao(self, grupo_id: uuid.UUID) -> int:
        ultima = self.find_ultima_versao(grupo_id)
        return (ultima.versao + 1) if ultima else 1

    def create(
        self,
        grupo_id: uuid.UUID,
        versao: int,
        qtd_hospedes: int,
        qtd_apartamentos: int,
        qtd_apartamentos_cortesia: int,
        noites: int,
        valor_total_net: float,
        valor_total_sistema: float,
        valor_pago_snapshot: float,
        saldo_snapshot: float,
        motivo: str | None,
        validade: date | None,
        condicoes: str | None,
        usuario_id: uuid.UUID,
        data_entrada_snapshot: date,
        data_saida_snapshot: date,
        status_snapshot: str,
        prazo_deadline_snapshot: date | None,
        prazo_roomlist_snapshot: date | None,
    ) -> GrupoOrcamento:
        """
        Não commita — o service grava orçamento + composição + pagamentos
        itemizados numa única transação (RN-G013: tudo congelado junto).
        """
        orcamento = GrupoOrcamento(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            versao=versao,
            qtd_hospedes=qtd_hospedes,
            qtd_apartamentos=qtd_apartamentos,
            qtd_apartamentos_cortesia=qtd_apartamentos_cortesia,
            noites=noites,
            valor_total_net=valor_total_net,
            valor_total_sistema=valor_total_sistema,
            valor_pago_snapshot=valor_pago_snapshot,
            saldo_snapshot=saldo_snapshot,
            motivo=motivo,
            validade=validade,
            condicoes=condicoes,
            usuario_id=usuario_id,
            status="RASCUNHO",
            desatualizado=False,
            data_entrada_snapshot=data_entrada_snapshot,
            data_saida_snapshot=data_saida_snapshot,
            status_snapshot=status_snapshot,
            prazo_deadline_snapshot=prazo_deadline_snapshot,
            prazo_roomlist_snapshot=prazo_roomlist_snapshot,
        )
        self.db.add(orcamento)
        return orcamento

    def update_status(self, orcamento: GrupoOrcamento, status: str) -> GrupoOrcamento:
        orcamento.status = status
        orcamento.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(orcamento)
        return orcamento

    def marcar_desatualizado(self, orcamento: GrupoOrcamento) -> GrupoOrcamento:
        orcamento.desatualizado = True
        orcamento.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(orcamento)
        return orcamento
