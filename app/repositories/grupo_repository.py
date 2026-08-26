from __future__ import annotations
import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload

from app.models.grupo import Grupo


class GrupoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list(
        self,
        nome: str = None,
        status: str = None,
        data_inicial: date = None,
        data_final: date = None,
    ) -> list[Grupo]:
        query = self.db.query(Grupo).options(
            joinedload(Grupo.agencia),
            joinedload(Grupo.guia),
            joinedload(Grupo.usuario),
        )

        if nome:
            query = query.filter(Grupo.nome.ilike(f"%{nome}%"))
        if status:
            query = query.filter(Grupo.status == status)
        if data_inicial:
            query = query.filter(Grupo.data_entrada >= data_inicial)
        if data_final:
            query = query.filter(Grupo.data_entrada <= data_final)

        return query.order_by(Grupo.data_entrada.desc()).all()

    def find_by_id(self, grupo_id: uuid.UUID) -> Grupo | None:
        return (
            self.db.query(Grupo)
            .options(
                joinedload(Grupo.agencia),
                joinedload(Grupo.guia),
                joinedload(Grupo.usuario),
            )
            .filter(Grupo.id == grupo_id)
            .first()
        )

    def generate_codigo(self) -> str:
        """Gera código sequencial no formato GRP-YYYYMMDD-XXXX."""
        hoje = datetime.now().strftime("%Y%m%d")
        prefixo = f"GRP-{hoje}-"
        ultimo = (
            self.db.query(Grupo)
            .filter(Grupo.codigo.like(f"{prefixo}%"))
            .order_by(Grupo.codigo.desc())
            .first()
        )
        if ultimo:
            seq = int(ultimo.codigo.split("-")[-1]) + 1
        else:
            seq = 1
        return f"{prefixo}{seq:04d}"

    def create(
        self,
        nome: str,
        responsavel: str | None,
        telefone: str | None,
        email: str | None,
        agencia_id: uuid.UUID | None,
        guia_id: uuid.UUID | None,
        data_entrada: date,
        data_saida: date,
        qtd_hospedes: int,
        qtd_apartamentos_cortesia: int,
        qtd_apartamentos_prevista: int | None,
        prazo_deadline: date | None,
        prazo_roomlist: date | None,
        observacao: str | None,
        usuario_id: uuid.UUID,
    ) -> Grupo:
        """
        qtd_apartamentos, valor_total_net e valor_total_sistema nascem
        zerados — só existem depois que a composição por tipo de
        apartamento (grupos_apartamentos) é montada na Aba Dados Gerais
        (RN-G020).
        """
        grupo = Grupo(
            id=uuid.uuid4(),
            codigo=self.generate_codigo(),
            nome=nome,
            responsavel=responsavel,
            telefone=telefone,
            email=email,
            agencia_id=agencia_id,
            guia_id=guia_id,
            data_entrada=data_entrada,
            data_saida=data_saida,
            qtd_hospedes=qtd_hospedes,
            qtd_apartamentos=0,
            qtd_apartamentos_cortesia=qtd_apartamentos_cortesia,
            qtd_apartamentos_prevista=qtd_apartamentos_prevista,
            valor_total_net=0,
            valor_total_net_manual=False,
            valor_total_sistema=0,
            valor_total_sistema_manual=False,
            observacao=observacao,
            prazo_deadline=prazo_deadline,
            prazo_roomlist=prazo_roomlist,
            usuario_id=usuario_id,
            status="PROSPECCAO",
        )
        self.db.add(grupo)
        self.db.commit()
        self.db.refresh(grupo)
        return grupo

    def update(
        self,
        grupo: Grupo,
        nome: str,
        responsavel: str | None,
        telefone: str | None,
        email: str | None,
        agencia_id: uuid.UUID | None,
        guia_id: uuid.UUID | None,
        data_entrada: date,
        data_saida: date,
        qtd_hospedes: int,
        qtd_apartamentos_cortesia: int,
        prazo_deadline: date | None,
        prazo_roomlist: date | None,
        observacao: str | None,
    ) -> Grupo:
        grupo.nome = nome
        grupo.responsavel = responsavel
        grupo.telefone = telefone
        grupo.email = email
        grupo.agencia_id = agencia_id
        grupo.guia_id = guia_id
        grupo.data_entrada = data_entrada
        grupo.data_saida = data_saida
        grupo.qtd_hospedes = qtd_hospedes
        grupo.qtd_apartamentos_cortesia = qtd_apartamentos_cortesia
        grupo.prazo_deadline = prazo_deadline
        grupo.prazo_roomlist = prazo_roomlist
        grupo.observacao = observacao
        grupo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grupo)
        return grupo

    def update_agregados(
        self,
        grupo: Grupo,
        qtd_apartamentos: int,
        valor_total_net: float,
        valor_total_sistema: float,
        valor_total_net_manual: bool | None = None,
        valor_total_sistema_manual: bool | None = None,
    ) -> Grupo:
        """RN-G020: sincroniza os agregados a partir de grupos_apartamentos.

        As flags `_manual` só são alteradas quando o chamador passa um
        valor explícito — do contrário permanecem como estavam (RN-G003).
        """
        grupo.qtd_apartamentos = qtd_apartamentos
        grupo.valor_total_net = valor_total_net
        grupo.valor_total_sistema = valor_total_sistema
        if valor_total_net_manual is not None:
            grupo.valor_total_net_manual = valor_total_net_manual
        if valor_total_sistema_manual is not None:
            grupo.valor_total_sistema_manual = valor_total_sistema_manual
        grupo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grupo)
        return grupo

    def update_status(self, grupo: Grupo, status: str) -> Grupo:
        grupo.status = status
        grupo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grupo)
        return grupo

    def update_valores_orcamento(
        self,
        grupo: Grupo,
        qtd_hospedes: int,
        qtd_apartamentos_cortesia: int,
        valor_total_net: float,
        valor_total_sistema: float,
    ) -> Grupo:
        """RN-G007: aprovar um orçamento copia seus valores para o grupo.

        Os totais entram marcados como manuais para preservar exatamente o
        valor aprovado. A recomposição da tabela grupos_apartamentos a
        partir do breakdown congelado do orçamento é tratada na Fase 7.3
        (junto com o restante do snapshot completo) — por ora só os
        totais agregados e as contagens simples são copiados.
        """
        grupo.qtd_hospedes = qtd_hospedes
        grupo.qtd_apartamentos_cortesia = qtd_apartamentos_cortesia
        grupo.valor_total_net = valor_total_net
        grupo.valor_total_net_manual = True
        grupo.valor_total_sistema = valor_total_sistema
        grupo.valor_total_sistema_manual = True
        grupo.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grupo)
        return grupo

