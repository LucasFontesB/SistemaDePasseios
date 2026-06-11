from __future__ import annotations
import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.venda import Venda
from app.models.passeio import Passeio
from app.models.venda_historico import VendaHistorico
from app.core.constants import STATUS_CHOICES


class SaleRepository:

    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        contratante: str = None,
        telefone: str = None,
        numero_venda: str = None,
        passeio_id: str = None,
        status: str = None,
        data_inicial: date = None,
        data_final: date = None,
    ) -> list[Venda]:
        query = (
            self.db.query(Venda)
            .options(
                joinedload(Venda.passeio),
                joinedload(Venda.tipo_passeio),
                joinedload(Venda.embarcacao),
                joinedload(Venda.usuario),
            )
        )

        if contratante:
            query = query.filter(Venda.contratante.ilike(f"%{contratante}%"))
        if telefone:
            query = query.filter(Venda.telefone.ilike(f"%{telefone}%"))
        if numero_venda:
            query = query.filter(Venda.numero_venda.ilike(f"%{numero_venda}%"))
        if passeio_id:
            query = query.filter(Venda.passeio_id == passeio_id)
        if status:
            query = query.filter(Venda.status == status)
        if data_inicial:
            query = query.filter(Venda.data_saida >= data_inicial)
        if data_final:
            query = query.filter(Venda.data_saida <= data_final)

        return query.order_by(Venda.criado_em.desc()).all()

    def find_by_id(self, venda_id: uuid.UUID) -> Venda | None:
        return (
            self.db.query(Venda)
            .options(
                joinedload(Venda.passeio),
                joinedload(Venda.tipo_passeio),
                joinedload(Venda.embarcacao),
                joinedload(Venda.usuario),
                joinedload(Venda.comprovantes),
                joinedload(Venda.historico).joinedload(VendaHistorico.usuario),
            )
            .filter(Venda.id == venda_id)
            .first()
        )

    def generate_numero_venda(self) -> str:
        """Gera número sequencial no formato VND-YYYYMMDD-XXXX."""
        hoje = datetime.now().strftime("%Y%m%d")
        prefixo = f"VND-{hoje}-"
        ultimo = (
            self.db.query(Venda)
            .filter(Venda.numero_venda.like(f"{prefixo}%"))
            .order_by(Venda.numero_venda.desc())
            .first()
        )
        if ultimo:
            seq = int(ultimo.numero_venda.split("-")[-1]) + 1
        else:
            seq = 1
        return f"{prefixo}{seq:04d}"

    def create(
        self,
        contratante: str,
        telefone: str,
        adultos: int,
        criancas: int,
        passeio_id: uuid.UUID,
        tipo_passeio_id: uuid.UUID,
        embarcacao_id: uuid.UUID | None,
        valor_total: float,
        percentual_comissao: float,
        valor_comissao: float,
        data_saida: date,
        horario_saida,
        observacao: str,
        forma_pagamento: str | None,
        usuario_id: uuid.UUID,
    ) -> Venda:
        venda = Venda(
            id=uuid.uuid4(),
            numero_venda=self.generate_numero_venda(),
            contratante=contratante,
            telefone=telefone,
            adultos=adultos,
            criancas=criancas,
            passeio_id=passeio_id,
            tipo_passeio_id=tipo_passeio_id,
            embarcacao_id=embarcacao_id,
            valor_total=valor_total,
            percentual_comissao=percentual_comissao,
            valor_comissao=valor_comissao,
            data_saida=data_saida,
            horario_saida=horario_saida,
            observacao=observacao,
            forma_pagamento=forma_pagamento,
            usuario_id=usuario_id,
            status="PENDENTE",
        )
        self.db.add(venda)
        self.db.commit()
        self.db.refresh(venda)
        return venda

    def update(
        self,
        venda: Venda,
        contratante: str,
        telefone: str,
        adultos: int,
        criancas: int,
        passeio_id: uuid.UUID,
        tipo_passeio_id: uuid.UUID,
        embarcacao_id: uuid.UUID | None,
        valor_total: float,
        percentual_comissao: float,
        valor_comissao: float,
        data_saida: date,
        horario_saida,
        observacao: str,
        forma_pagamento: str | None,
    ) -> Venda:
        venda.contratante = contratante
        venda.telefone = telefone
        venda.adultos = adultos
        venda.criancas = criancas
        venda.passeio_id = passeio_id
        venda.tipo_passeio_id = tipo_passeio_id
        venda.embarcacao_id = embarcacao_id
        venda.valor_total = valor_total
        venda.percentual_comissao = percentual_comissao
        venda.valor_comissao = valor_comissao
        venda.data_saida = data_saida
        venda.horario_saida = horario_saida
        venda.observacao = observacao
        venda.forma_pagamento = forma_pagamento
        venda.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(venda)
        return venda

    def update_status(self, venda: Venda, status: str) -> Venda:
        venda.status = status
        venda.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(venda)
        return venda