from __future__ import annotations
import uuid
from datetime import date
from sqlalchemy.orm import Session

from app.repositories.grupo_roomlist_repository import GrupoRoomlistRepository
from app.repositories.tipo_apartamento_repository import TipoApartamentoRepository
from app.services.grupo_historico_service import GrupoHistoricoService, ENTIDADE_ROOMLIST


class GrupoRoomlistService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoRoomlistRepository(db)
        self.tipo_apartamento_repository = TipoApartamentoRepository(db)
        self.historico_service = GrupoHistoricoService(db)

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list:
        return self.repository.list_by_grupo(grupo_id)

    def agrupar_por_tipo(self, roomlist: list) -> list[tuple[str, list]]:
        """RN-G033: agrupa por tipo de apartamento, na ordem do cadastro
        (`ordem`). Itens sem tipo definido ficam num grupo à parte, ao
        final. Usado pelas exportações em PDF e Excel."""
        SEM_TIPO_LABEL = "Sem tipo definido"
        grupos: dict[str, list] = {}
        ordens: dict[str, int] = {}

        for item in roomlist:
            if item.tipo_apartamento:
                nome = item.tipo_apartamento.nome
                ordem = item.tipo_apartamento.ordem
            else:
                nome = SEM_TIPO_LABEL
                ordem = 999999
            grupos.setdefault(nome, [])
            grupos[nome].append(item)
            ordens[nome] = ordem

        nomes_ordenados = sorted(grupos.keys(), key=lambda n: (ordens[n], n))
        return [(nome, grupos[nome]) for nome in nomes_ordenados]

    def create(self, grupo_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        erros, tipo_apartamento_id = self._validar(form)
        if erros:
            return None, erros

        item = self.repository.create(
            grupo_id=grupo_id,
            apartamento=form.get("apartamento", "").strip() or None,
            hospede_nome=form["hospede_nome"].strip(),
            documento=form.get("documento", "").strip() or None,
            tipo_apartamento_id=tipo_apartamento_id,
            cortesia=form.get("cortesia") == "on",
            check_in=self._parse_date(form.get("check_in")),
            check_out=self._parse_date(form.get("check_out")),
            observacao=form.get("observacao", "").strip() or None,
        )

        self.historico_service.registrar_criacao(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ROOMLIST,
            entidade_id=item.id,
            campo="hospede_nome",
            valor_novo=item.hospede_nome,
        )
        self.db.commit()

        return item, []

    def update(self, grupo_id: uuid.UUID, item_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        item = self.repository.find_by_id(item_id)
        if not item or item.grupo_id != grupo_id:
            return None, ["Registro não encontrado."]

        erros, tipo_apartamento_id = self._validar(form)
        if erros:
            return None, erros

        antes = self._snapshot(item)

        item = self.repository.update(
            item=item,
            apartamento=form.get("apartamento", "").strip() or None,
            hospede_nome=form["hospede_nome"].strip(),
            documento=form.get("documento", "").strip() or None,
            tipo_apartamento_id=tipo_apartamento_id,
            cortesia=form.get("cortesia") == "on",
            check_in=self._parse_date(form.get("check_in")),
            check_out=self._parse_date(form.get("check_out")),
            observacao=form.get("observacao", "").strip() or None,
        )

        depois = self._snapshot(item)
        self.historico_service.registrar_diff(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ROOMLIST,
            entidade_id=item.id,
            antes=antes,
            depois=depois,
        )
        self.db.commit()

        return item, []

    def remover(self, grupo_id: uuid.UUID, item_id: uuid.UUID, usuario_id: uuid.UUID):
        item = self.repository.find_by_id(item_id)
        if not item or item.grupo_id != grupo_id:
            return False, ["Registro não encontrado."]

        self.historico_service.registrar_exclusao(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ROOMLIST,
            entidade_id=item.id,
            campo="hospede_nome",
            valor_anterior=item.hospede_nome,
        )
        self.repository.delete(item)
        self.db.commit()

        return True, []

    def _snapshot(self, item) -> dict:
        return {
            "apartamento": item.apartamento or "",
            "hospede_nome": item.hospede_nome,
            "documento": item.documento or "",
            "tipo_apartamento": item.tipo_apartamento.nome if item.tipo_apartamento else "",
            "cortesia": "Sim" if item.cortesia else "Não",
            "check_in": item.check_in.strftime("%d/%m/%Y") if item.check_in else "",
            "check_out": item.check_out.strftime("%d/%m/%Y") if item.check_out else "",
            "observacao": item.observacao or "",
        }

    def _parse_date(self, valor: str | None) -> date | None:
        if not valor:
            return None
        try:
            return date.fromisoformat(valor)
        except ValueError:
            return None

    def _validar(self, form: dict):
        erros = []
        if not form.get("hospede_nome", "").strip():
            erros.append("Nome do hóspede é obrigatório.")

        tipo_apartamento_id = None
        tipo_raw = form.get("tipo_apartamento_id")
        if tipo_raw:
            try:
                tipo_apartamento_id = uuid.UUID(tipo_raw)
            except ValueError:
                erros.append("Tipo de apartamento inválido.")
            else:
                if not self.tipo_apartamento_repository.find_by_id(tipo_apartamento_id):
                    erros.append("Tipo de apartamento não encontrado.")

        return erros, tipo_apartamento_id
