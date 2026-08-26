from __future__ import annotations
import uuid
from datetime import date
from sqlalchemy.orm import Session

from app.repositories.grupo_orcamento_repository import GrupoOrcamentoRepository
from app.repositories.grupo_orcamento_apartamento_repository import GrupoOrcamentoApartamentoRepository
from app.repositories.grupo_orcamento_pagamento_repository import GrupoOrcamentoPagamentoRepository
from app.repositories.grupo_repository import GrupoRepository
from app.repositories.grupo_apartamento_repository import GrupoApartamentoRepository
from app.repositories.grupo_pagamento_repository import GrupoPagamentoRepository
from app.repositories.tipo_apartamento_repository import TipoApartamentoRepository
from app.services.grupo_historico_service import (
    GrupoHistoricoService, ENTIDADE_ORCAMENTO, ENTIDADE_GRUPO,
)
from app.core.constants import (
    ORCAMENTO_STATUS_RASCUNHO, ORCAMENTO_STATUS_ENVIADO,
    ORCAMENTO_STATUS_APROVADO, ORCAMENTO_STATUS_RECUSADO,
)


class OrcamentoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoOrcamentoRepository(db)
        self.apartamento_snapshot_repository = GrupoOrcamentoApartamentoRepository(db)
        self.pagamento_snapshot_repository = GrupoOrcamentoPagamentoRepository(db)
        self.grupo_repository = GrupoRepository(db)
        self.apartamento_repository = GrupoApartamentoRepository(db)
        self.pagamento_repository = GrupoPagamentoRepository(db)
        self.tipo_apartamento_repository = TipoApartamentoRepository(db)
        self.historico_service = GrupoHistoricoService(db)

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list:
        return self.repository.list_by_grupo(grupo_id)

    def get_by_id(self, orcamento_id: uuid.UUID):
        return self.repository.find_by_id(orcamento_id)

    def list_apartamentos_snapshot(self, orcamento_id: uuid.UUID) -> list:
        return self.apartamento_snapshot_repository.list_by_orcamento(orcamento_id)

    def list_pagamentos_snapshot(self, orcamento_id: uuid.UUID) -> list:
        return self.pagamento_snapshot_repository.list_by_orcamento(orcamento_id)

    def gerar_nova_versao(self, grupo_id: uuid.UUID, usuario_id: uuid.UUID, form: dict):
        """RN-G012: geração de nova versão é sempre ação manual do usuário —
        o sistema nunca cria uma versão sozinho.

        RN-G013: o snapshot congela tudo que pode mudar depois — datas,
        status, prazos, a composição completa por tipo de apartamento e os
        pagamentos itemizados, além de valor pago e saldo. Nada disso é
        recalculado ao reimprimir; o PDF de uma versão antiga só lê das
        tabelas de snapshot dessa versão.
        """
        grupo = self.grupo_repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        validade_raw = (form.get("validade") or "").strip()
        try:
            validade = date.fromisoformat(validade_raw) if validade_raw else None
        except ValueError:
            return None, ["Data de validade inválida."]

        versao = self.repository.proxima_versao(grupo_id)
        noites = grupo.noites

        orcamento = self.repository.create(
            grupo_id=grupo.id,
            versao=versao,
            qtd_hospedes=grupo.qtd_hospedes,
            qtd_apartamentos=grupo.qtd_apartamentos,
            qtd_apartamentos_cortesia=grupo.qtd_apartamentos_cortesia,
            noites=noites,
            valor_total_net=float(grupo.valor_total_net),
            valor_total_sistema=float(grupo.valor_total_sistema),
            valor_pago_snapshot=grupo.valor_pago,
            saldo_snapshot=grupo.saldo,
            motivo=(form.get("motivo") or "").strip() or None,
            validade=validade,
            condicoes=(form.get("condicoes") or "").strip() or None,
            usuario_id=usuario_id,
            data_entrada_snapshot=grupo.data_entrada,
            data_saida_snapshot=grupo.data_saida,
            status_snapshot=grupo.status,
            prazo_deadline_snapshot=grupo.prazo_deadline,
            prazo_roomlist_snapshot=grupo.prazo_roomlist,
        )

        for linha in self.apartamento_repository.list_by_grupo(grupo.id):
            self.apartamento_snapshot_repository.create(
                orcamento_id=orcamento.id,
                tipo_apartamento_nome=linha.tipo_apartamento.nome,
                quantidade=linha.quantidade,
                valor_diaria_net=float(linha.valor_diaria_net),
                valor_diaria_sistema=float(linha.valor_diaria_sistema),
                valor_total_net=linha.subtotal_net(noites),
                valor_total_sistema=linha.subtotal_sistema(noites),
            )

        for pagamento in self.pagamento_repository.list_by_grupo(grupo.id):
            self.pagamento_snapshot_repository.create(
                orcamento_id=orcamento.id,
                valor=float(pagamento.valor),
                data_pagamento=pagamento.data_pagamento,
                forma_pagamento=pagamento.forma_pagamento,
            )

        self.historico_service.registrar_criacao(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ORCAMENTO,
            entidade_id=orcamento.id,
            campo="versao",
            valor_novo=str(versao),
        )
        self.db.commit()
        self.db.refresh(orcamento)

        return orcamento, []

    def marcar_enviado(self, orcamento_id: uuid.UUID, usuario_id: uuid.UUID):
        orcamento = self.repository.find_by_id(orcamento_id)
        if not orcamento:
            return None, ["Orçamento não encontrado."]
        if orcamento.status != ORCAMENTO_STATUS_RASCUNHO:
            return None, ["Apenas orçamentos em rascunho podem ser marcados como enviados."]

        orcamento = self._alterar_status(orcamento, ORCAMENTO_STATUS_ENVIADO, usuario_id)
        return orcamento, []

    def aprovar(self, orcamento_id: uuid.UUID, usuario_id: uuid.UUID):
        orcamento = self.repository.find_by_id(orcamento_id)
        if not orcamento:
            return None, ["Orçamento não encontrado."]
        if orcamento.status in (ORCAMENTO_STATUS_APROVADO, ORCAMENTO_STATUS_RECUSADO):
            return None, ["Este orçamento já foi finalizado."]

        linhas_snapshot = self.apartamento_snapshot_repository.list_by_orcamento(orcamento.id)

        # Resolve todos os tipos antes de mudar qualquer coisa — a
        # reconstituição da composição é tudo ou nada.
        resolvidos = []
        for linha in linhas_snapshot:
            tipo = self.tipo_apartamento_repository.find_by_nome_qualquer(linha.tipo_apartamento_nome)
            if not tipo:
                return None, [
                    f"Tipo de apartamento '{linha.tipo_apartamento_nome}' não existe mais no "
                    "cadastro - não é possível reconstituir a composição do grupo."
                ]
            resolvidos.append((tipo, linha))

        orcamento = self._alterar_status(orcamento, ORCAMENTO_STATUS_APROVADO, usuario_id)

        # RN-G007: aprovar copia os valores do orçamento para o grupo — e a
        # composição por tipo é substituída pela congelada nesta versão, não
        # só os totais agregados (senão o grupo fica com o total certo mas a
        # composição desatualizada).
        grupo = orcamento.grupo
        antes = self._snapshot_grupo_valores(grupo)

        grupo = self.grupo_repository.update_valores_orcamento(
            grupo=grupo,
            qtd_hospedes=orcamento.qtd_hospedes,
            qtd_apartamentos_cortesia=orcamento.qtd_apartamentos_cortesia,
            valor_total_net=float(orcamento.valor_total_net),
            valor_total_sistema=float(orcamento.valor_total_sistema),
        )

        self.apartamento_repository.delete_by_grupo(grupo.id)
        self.db.commit()

        qtd_total = 0
        for tipo, linha in resolvidos:
            self.apartamento_repository.create(
                grupo_id=grupo.id,
                tipo_apartamento_id=tipo.id,
                quantidade=linha.quantidade,
                valor_diaria_net=float(linha.valor_diaria_net),
                valor_diaria_sistema=float(linha.valor_diaria_sistema),
            )
            qtd_total += linha.quantidade

        # Mantém os totais e as flags _manual definidos acima, mesmo que a
        # soma da composição restaurada já bata — o valor aprovado é a fonte
        # de verdade, não algo para recalcular por cima.
        grupo = self.grupo_repository.update_agregados(
            grupo,
            qtd_apartamentos=qtd_total,
            valor_total_net=float(grupo.valor_total_net),
            valor_total_sistema=float(grupo.valor_total_sistema),
        )

        depois = self._snapshot_grupo_valores(grupo)
        self.historico_service.registrar_diff(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_GRUPO,
            entidade_id=grupo.id,
            antes=antes,
            depois=depois,
        )
        self.db.commit()

        return orcamento, []

    def recusar(self, orcamento_id: uuid.UUID, usuario_id: uuid.UUID):
        orcamento = self.repository.find_by_id(orcamento_id)
        if not orcamento:
            return None, ["Orçamento não encontrado."]
        if orcamento.status in (ORCAMENTO_STATUS_APROVADO, ORCAMENTO_STATUS_RECUSADO):
            return None, ["Este orçamento já foi finalizado."]

        orcamento = self._alterar_status(orcamento, ORCAMENTO_STATUS_RECUSADO, usuario_id)
        return orcamento, []

    def sinalizar_se_divergente(self, grupo, usuario_id: uuid.UUID) -> None:
        """RN-G012: quando o grupo diverge do último orçamento gerado, marca-o
        como desatualizado. Não cria versão nova — isso é sempre manual."""
        ultima = self.repository.find_ultima_versao(grupo.id)
        if not ultima or ultima.desatualizado:
            return

        divergiu = (
            ultima.qtd_hospedes != grupo.qtd_hospedes
            or ultima.qtd_apartamentos != grupo.qtd_apartamentos
            or ultima.qtd_apartamentos_cortesia != grupo.qtd_apartamentos_cortesia
            or float(ultima.valor_total_net) != float(grupo.valor_total_net)
            or float(ultima.valor_total_sistema) != float(grupo.valor_total_sistema)
            or float(ultima.valor_pago_snapshot) != grupo.valor_pago
        )
        if not divergiu:
            return

        self.repository.marcar_desatualizado(ultima)
        self.historico_service.registrar_diff(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ORCAMENTO,
            entidade_id=ultima.id,
            antes={"desatualizado": "Não"},
            depois={"desatualizado": "Sim"},
        )
        self.db.commit()

    def _alterar_status(self, orcamento, status_novo: str, usuario_id: uuid.UUID):
        status_anterior = orcamento.status
        orcamento = self.repository.update_status(orcamento, status_novo)
        self.historico_service.registrar_status(
            grupo_id=orcamento.grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ORCAMENTO,
            entidade_id=orcamento.id,
            valor_anterior=status_anterior,
            valor_novo=status_novo,
        )
        self.db.commit()
        return orcamento

    def _snapshot_grupo_valores(self, grupo) -> dict:
        return {
            "qtd_hospedes": str(grupo.qtd_hospedes),
            "qtd_apartamentos_cortesia": str(grupo.qtd_apartamentos_cortesia),
            "valor_total_net": f"R$ {float(grupo.valor_total_net):.2f}",
            "valor_total_net_manual": "Sim" if grupo.valor_total_net_manual else "Não",
            "valor_total_sistema": f"R$ {float(grupo.valor_total_sistema):.2f}",
            "valor_total_sistema_manual": "Sim" if grupo.valor_total_sistema_manual else "Não",
        }
