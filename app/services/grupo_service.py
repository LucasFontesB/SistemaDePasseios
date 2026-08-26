from __future__ import annotations

import uuid
from datetime import date
from sqlalchemy.orm import Session

from app.repositories.grupo_repository import GrupoRepository
from app.repositories.grupo_apartamento_repository import GrupoApartamentoRepository
from app.repositories.grupo_roomlist_repository import GrupoRoomlistRepository
from app.repositories.agencia_repository import AgenciaRepository
from app.repositories.guia_repository import GuiaRepository
from app.repositories.tipo_apartamento_repository import TipoApartamentoRepository
from app.services.grupo_historico_service import GrupoHistoricoService, ENTIDADE_GRUPO
from app.services.orcamento_service import OrcamentoService
from app.core.constants import GRUPO_STATUS_CHOICES, GRUPO_STATUS_CANCELADO


class GrupoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoRepository(db)
        self.apartamento_repository = GrupoApartamentoRepository(db)
        self.roomlist_repository = GrupoRoomlistRepository(db)
        self.agencia_repository = AgenciaRepository(db)
        self.guia_repository = GuiaRepository(db)
        self.tipo_apartamento_repository = TipoApartamentoRepository(db)
        self.historico_service = GrupoHistoricoService(db)
        self.orcamento_service = OrcamentoService(db)

    def get_form_data(self) -> dict:
        return {
            "agencias": self.agencia_repository.list_active(),
            "guias": self.guia_repository.list_active(),
            "status_choices": GRUPO_STATUS_CHOICES,
        }

    def list(self, **filtros) -> list:
        return self.repository.list(**filtros)

    def get_by_id(self, grupo_id: uuid.UUID):
        return self.repository.find_by_id(grupo_id)

    def list_apartamentos(self, grupo_id: uuid.UUID) -> list:
        return self.apartamento_repository.list_by_grupo(grupo_id)

    def get_alertas(self, grupo, tem_roomlist_vazia: bool) -> list[str]:
        """
        Avisos não-bloqueantes exibidos em Dados Gerais.

        RN-G028: composição já passou da quantidade prevista na criação.
        RN-G029: prazo de roomlist a vencer/vencido com linha ainda vazia;
        prazo de pagamento a vencer/vencido com saldo (RN-G027) > 0.
        """
        alertas = []
        hoje = date.today()

        if grupo.qtd_apartamentos_prevista and grupo.qtd_apartamentos > grupo.qtd_apartamentos_prevista:
            alertas.append(
                f"Composição atual ({grupo.qtd_apartamentos} apartamentos) já passou da "
                f"quantidade prevista na criação ({grupo.qtd_apartamentos_prevista})."
            )

        if grupo.prazo_roomlist and tem_roomlist_vazia:
            dias = (grupo.prazo_roomlist - hoje).days
            if dias < 0:
                alertas.append(f"Prazo de roomlist vencido há {abs(dias)} dia(s).")
            elif dias <= 7:
                alertas.append(f"Prazo de envio da roomlist vence em {dias} dia(s).")

        if grupo.prazo_deadline and grupo.saldo > 0:
            dias = (grupo.prazo_deadline - hoje).days
            if dias < 0:
                alertas.append(f"Prazo de pagamento vencido há {abs(dias)} dia(s).")
            elif dias <= 7:
                alertas.append(f"Prazo de pagamento vence em {dias} dia(s).")

        return alertas

    def create(self, form: dict, usuario_id: uuid.UUID):
        erros = self._validar(form)
        if erros:
            return None, erros

        grupo = self.repository.create(
            nome=form["nome"].strip(),
            responsavel=form.get("responsavel", "").strip() or None,
            telefone=form.get("telefone", "").strip() or None,
            email=form.get("email", "").strip() or None,
            agencia_id=uuid.UUID(form["agencia_id"]) if form.get("agencia_id") else None,
            guia_id=uuid.UUID(form["guia_id"]) if form.get("guia_id") else None,
            data_entrada=date.fromisoformat(form["data_entrada"]),
            data_saida=date.fromisoformat(form["data_saida"]),
            qtd_hospedes=self._parse_int(form.get("qtd_hospedes")),
            qtd_apartamentos_cortesia=self._parse_int(form.get("qtd_apartamentos_cortesia")),
            qtd_apartamentos_prevista=self._parse_int(form.get("qtd_apartamentos_prevista")) or None,
            prazo_deadline=self._parse_date(form.get("prazo_deadline")),
            prazo_roomlist=self._parse_date(form.get("prazo_roomlist")),
            observacao=form.get("observacao", "").strip() or None,
            usuario_id=usuario_id,
        )

        self.historico_service.registrar_criacao(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_GRUPO,
            entidade_id=grupo.id,
            campo="status",
            valor_novo=grupo.status,
        )
        self.db.commit()

        return grupo, []

    def update(self, grupo_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        erros = self._validar(form)
        if erros:
            return None, erros

        antes = self._snapshot(grupo)

        grupo = self.repository.update(
            grupo=grupo,
            nome=form["nome"].strip(),
            responsavel=form.get("responsavel", "").strip() or None,
            telefone=form.get("telefone", "").strip() or None,
            email=form.get("email", "").strip() or None,
            agencia_id=uuid.UUID(form["agencia_id"]) if form.get("agencia_id") else None,
            guia_id=uuid.UUID(form["guia_id"]) if form.get("guia_id") else None,
            data_entrada=date.fromisoformat(form["data_entrada"]),
            data_saida=date.fromisoformat(form["data_saida"]),
            qtd_hospedes=self._parse_int(form.get("qtd_hospedes")),
            qtd_apartamentos_cortesia=self._parse_int(form.get("qtd_apartamentos_cortesia")),
            prazo_deadline=self._parse_date(form.get("prazo_deadline")),
            prazo_roomlist=self._parse_date(form.get("prazo_roomlist")),
            observacao=form.get("observacao", "").strip() or None,
        )

        # RN-G003: alterar datas nunca sobrescreve um total marcado como
        # manual, mas datas mudam `noites`, então os totais automáticos
        # precisam ser resincronizados a partir da composição atual.
        grupo = self._recalcular_agregados(grupo)

        depois = self._snapshot(grupo)
        self.historico_service.registrar_diff(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_GRUPO,
            entidade_id=grupo.id,
            antes=antes,
            depois=depois,
        )
        self.db.commit()
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return grupo, []

    def update_status(self, grupo_id: uuid.UUID, status: str, perfil: str, usuario_id: uuid.UUID):
        if status not in GRUPO_STATUS_CHOICES:
            return None, ["Status inválido."]

        # RN-G010: cancelamento restrito a ADMIN e GERENCIA.
        if status == GRUPO_STATUS_CANCELADO and perfil not in ("ADMIN", "GERENCIA"):
            return None, ["Apenas ADMIN e GERENCIA podem cancelar um grupo."]

        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        status_anterior = grupo.status
        grupo = self.repository.update_status(grupo, status)

        self.historico_service.registrar_status(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_GRUPO,
            entidade_id=grupo.id,
            valor_anterior=status_anterior,
            valor_novo=status,
        )
        self.db.commit()

        return grupo, []

    # =========================================================================
    # Composição de tarifa por tipo de apartamento (RN-G019/RN-G020)
    # =========================================================================

    def adicionar_apartamento(self, grupo_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        erros, tipo_apartamento_id, quantidade, diaria_net, diaria_sistema = self._validar_linha(form)
        if erros:
            return None, erros

        if self.apartamento_repository.find_by_grupo_e_tipo(grupo_id, tipo_apartamento_id):
            return None, ["Este tipo de apartamento já foi adicionado - edite a linha existente."]

        antes = self._snapshot(grupo)

        linha = self.apartamento_repository.create(
            grupo_id=grupo_id,
            tipo_apartamento_id=tipo_apartamento_id,
            quantidade=quantidade,
            valor_diaria_net=diaria_net,
            valor_diaria_sistema=diaria_sistema,
        )

        # RN-G032: nova linha de composição gera N linhas vazias na roomlist.
        self.roomlist_repository.criar_vazias(grupo_id, tipo_apartamento_id, quantidade)

        grupo = self._recalcular_agregados(grupo)
        self._registrar_diff_agregados(grupo, usuario_id, antes)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return linha, []

    def atualizar_apartamento(self, grupo_id: uuid.UUID, linha_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        linha = self.apartamento_repository.find_by_id(linha_id)
        if not linha or linha.grupo_id != grupo_id:
            return None, ["Linha da composição não encontrada."]

        erros, _tipo_ignorado, quantidade, diaria_net, diaria_sistema = self._validar_linha(form, exigir_tipo=False)
        if erros:
            return None, erros

        # RN-G032: valida a redução ANTES de mexer em qualquer coisa — nunca
        # apaga hóspede já cadastrado. Só a diferença de quantidade importa
        # aqui; diárias podem sempre ser editadas livremente.
        quantidade_anterior = linha.quantidade
        delta = quantidade - quantidade_anterior
        vazias_removiveis = []
        if delta < 0:
            vazias = self.roomlist_repository.list_vazias_by_grupo_e_tipo(grupo_id, linha.tipo_apartamento_id)
            if len(vazias) < abs(delta):
                faltam = abs(delta) - len(vazias)
                return None, [
                    f"Não é possível reduzir para {quantidade}: há {len(vazias)} linha(s) vazia(s) na "
                    f"roomlist para este tipo, mas a redução exige liberar {abs(delta)}. Remova "
                    f"manualmente {faltam} hóspede(s) já cadastrado(s) deste tipo antes de reduzir a quantidade."
                ]
            vazias_removiveis = vazias[:abs(delta)]

        antes = self._snapshot(grupo)

        linha = self.apartamento_repository.update(
            item=linha,
            quantidade=quantidade,
            valor_diaria_net=diaria_net,
            valor_diaria_sistema=diaria_sistema,
        )

        if delta > 0:
            self.roomlist_repository.criar_vazias(grupo_id, linha.tipo_apartamento_id, delta)
        elif delta < 0:
            self.roomlist_repository.remover_itens(vazias_removiveis)

        grupo = self._recalcular_agregados(grupo)
        self._registrar_diff_agregados(grupo, usuario_id, antes)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return linha, []

    def remover_apartamento(self, grupo_id: uuid.UUID, linha_id: uuid.UUID, usuario_id: uuid.UUID):
        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return False, ["Grupo não encontrado."]

        linha = self.apartamento_repository.find_by_id(linha_id)
        if not linha or linha.grupo_id != grupo_id:
            return False, ["Linha da composição não encontrada."]

        # RN-G032: só remove a linha inteira se todas as linhas de roomlist
        # daquele tipo ainda estiverem vazias — senão pede para o usuário
        # remover os hóspedes manualmente primeiro.
        todas = self.roomlist_repository.list_by_grupo_e_tipo(grupo_id, linha.tipo_apartamento_id)
        preenchidas = [r for r in todas if r.hospede_nome is not None]
        if preenchidas:
            return False, [
                f"Não é possível remover este tipo: há {len(preenchidas)} hóspede(s) já cadastrado(s) "
                f"na roomlist para ele. Remova os hóspedes manualmente primeiro."
            ]

        antes = self._snapshot(grupo)

        self.roomlist_repository.remover_itens(todas)
        self.apartamento_repository.delete(linha)

        grupo = self._recalcular_agregados(grupo)
        self._registrar_diff_agregados(grupo, usuario_id, antes)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return True, []

    def definir_valor_manual(self, grupo_id: uuid.UUID, campo: str, valor_form: str, usuario_id: uuid.UUID):
        """Ativa o override manual de valor_total_net ou valor_total_sistema
        com o valor digitado (RN-G020 — flags atuam sobre o agregado)."""
        if campo not in ("net", "sistema"):
            return None, ["Campo inválido."]

        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        valor = self._parse_float(valor_form)
        antes = self._snapshot(grupo)

        if campo == "net":
            grupo = self.repository.update_agregados(
                grupo, qtd_apartamentos=grupo.qtd_apartamentos,
                valor_total_net=valor, valor_total_sistema=float(grupo.valor_total_sistema),
                valor_total_net_manual=True,
            )
        else:
            grupo = self.repository.update_agregados(
                grupo, qtd_apartamentos=grupo.qtd_apartamentos,
                valor_total_net=float(grupo.valor_total_net), valor_total_sistema=valor,
                valor_total_sistema_manual=True,
            )

        self._registrar_diff_agregados(grupo, usuario_id, antes)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return grupo, []

    def recalcular_net(self, grupo_id: uuid.UUID, usuario_id: uuid.UUID):
        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        antes = self._snapshot(grupo)
        grupo = self._recalcular_agregados(grupo, forcar_net=True)
        self._registrar_diff_agregados(grupo, usuario_id, antes)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return grupo, []

    def recalcular_sistema(self, grupo_id: uuid.UUID, usuario_id: uuid.UUID):
        grupo = self.repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        antes = self._snapshot(grupo)
        grupo = self._recalcular_agregados(grupo, forcar_sistema=True)
        self._registrar_diff_agregados(grupo, usuario_id, antes)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return grupo, []

    def _recalcular_agregados(self, grupo, forcar_net: bool = False, forcar_sistema: bool = False):
        """RN-G020: recalcula qtd_apartamentos/valor_total_net/valor_total_sistema
        a partir das linhas de grupos_apartamentos. RN-G003: só sobrescreve os
        totais quando a respectiva flag manual está desligada (ou `forcar_*`
        pede explicitamente para voltar ao automático)."""
        linhas = self.apartamento_repository.list_by_grupo(grupo.id)
        noites = grupo.noites

        qtd_apartamentos = sum(l.quantidade for l in linhas)
        total_net_calc = sum(l.subtotal_net(noites) for l in linhas)
        total_sistema_calc = sum(l.subtotal_sistema(noites) for l in linhas)

        valor_total_net = total_net_calc if (forcar_net or not grupo.valor_total_net_manual) else float(grupo.valor_total_net)
        valor_total_sistema = total_sistema_calc if (forcar_sistema or not grupo.valor_total_sistema_manual) else float(grupo.valor_total_sistema)

        return self.repository.update_agregados(
            grupo,
            qtd_apartamentos=qtd_apartamentos,
            valor_total_net=valor_total_net,
            valor_total_sistema=valor_total_sistema,
            valor_total_net_manual=False if forcar_net else None,
            valor_total_sistema_manual=False if forcar_sistema else None,
        )

    def _registrar_diff_agregados(self, grupo, usuario_id: uuid.UUID, antes: dict) -> None:
        depois = self._snapshot(grupo)
        self.historico_service.registrar_diff(
            grupo_id=grupo.id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_GRUPO,
            entidade_id=grupo.id,
            antes=antes,
            depois=depois,
        )
        self.db.commit()

    def _snapshot(self, grupo) -> dict:
        """Estado atual do grupo formatado para exibição, usado no diff do histórico."""
        return {
            "nome": grupo.nome,
            "responsavel": grupo.responsavel or "",
            "telefone": grupo.telefone or "",
            "email": grupo.email or "",
            "agencia": grupo.agencia.nome if grupo.agencia else "",
            "guia": grupo.guia.nome if grupo.guia else "",
            "data_entrada": grupo.data_entrada.strftime("%d/%m/%Y"),
            "data_saida": grupo.data_saida.strftime("%d/%m/%Y"),
            "qtd_hospedes": str(grupo.qtd_hospedes),
            "qtd_apartamentos": str(grupo.qtd_apartamentos),
            "qtd_apartamentos_cortesia": str(grupo.qtd_apartamentos_cortesia),
            "valor_total_net": f"R$ {float(grupo.valor_total_net):.2f}",
            "valor_total_net_manual": "Sim" if grupo.valor_total_net_manual else "Não",
            "valor_total_sistema": f"R$ {float(grupo.valor_total_sistema):.2f}",
            "valor_total_sistema_manual": "Sim" if grupo.valor_total_sistema_manual else "Não",
            "prazo_deadline": grupo.prazo_deadline.strftime("%d/%m/%Y") if grupo.prazo_deadline else "",
            "prazo_roomlist": grupo.prazo_roomlist.strftime("%d/%m/%Y") if grupo.prazo_roomlist else "",
            "observacao": grupo.observacao or "",
        }

    def _parse_float(self, valor: str | None) -> float:
        if not valor:
            return 0.0
        try:
            return float(str(valor).replace(",", "."))
        except ValueError:
            return 0.0

    def _parse_int(self, valor: str | None) -> int:
        if not valor:
            return 0
        try:
            return int(valor)
        except ValueError:
            return 0

    def _parse_date(self, valor: str | None) -> date | None:
        if not valor:
            return None
        try:
            return date.fromisoformat(valor)
        except ValueError:
            return None

    def _validar(self, form: dict) -> list:
        erros = []
        if not form.get("nome", "").strip():
            erros.append("Nome do grupo é obrigatório.")
        if not form.get("data_entrada"):
            erros.append("Informe a data de entrada.")
        if not form.get("data_saida"):
            erros.append("Informe a data de saída.")
        if form.get("data_entrada") and form.get("data_saida"):
            try:
                data_entrada = date.fromisoformat(form["data_entrada"])
                data_saida = date.fromisoformat(form["data_saida"])
                if data_saida <= data_entrada:
                    erros.append("A data de saída deve ser posterior à data de entrada.")
            except ValueError:
                erros.append("Datas inválidas.")
        return erros

    def _validar_linha(self, form: dict, exigir_tipo: bool = True):
        erros = []
        tipo_apartamento_id = None

        if exigir_tipo:
            if not form.get("tipo_apartamento_id"):
                erros.append("Selecione o tipo de apartamento.")
            else:
                try:
                    tipo_apartamento_id = uuid.UUID(form["tipo_apartamento_id"])
                except ValueError:
                    erros.append("Tipo de apartamento inválido.")
                else:
                    if not self.tipo_apartamento_repository.find_by_id(tipo_apartamento_id):
                        erros.append("Tipo de apartamento não encontrado.")

        quantidade = self._parse_int(form.get("quantidade"))
        if quantidade < 1:
            erros.append("Quantidade deve ser pelo menos 1.")

        diaria_net = self._parse_float(form.get("valor_diaria_net"))
        diaria_sistema = self._parse_float(form.get("valor_diaria_sistema"))

        return erros, tipo_apartamento_id, quantidade, diaria_net, diaria_sistema
