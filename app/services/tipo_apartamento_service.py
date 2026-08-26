from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.repositories.tipo_apartamento_repository import TipoApartamentoRepository


class TipoApartamentoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = TipoApartamentoRepository(db)

    def list(self) -> list:
        return self.repository.list_active()

    def get_by_id(self, tipo_id: uuid.UUID):
        return self.repository.find_by_id(tipo_id)

    def create(self, form: dict):
        erros = self._validar(form, tipo_atual=None)
        if erros:
            return None, erros

        tipo = self.repository.create(
            nome=form["nome"].strip(),
            ordem=self._parse_int(form.get("ordem")),
            valor_diaria_net_padrao=self._parse_float(form.get("valor_diaria_net_padrao")),
            valor_diaria_sistema_padrao=self._parse_float(form.get("valor_diaria_sistema_padrao")),
            observacao=form.get("observacao", "").strip() or None,
        )
        return tipo, []

    def update(self, tipo_id: uuid.UUID, form: dict):
        tipo = self.repository.find_by_id(tipo_id)
        if not tipo:
            return None, ["Tipo de apartamento não encontrado."]

        erros = self._validar(form, tipo_atual=tipo)
        if erros:
            return None, erros

        tipo = self.repository.update(
            tipo=tipo,
            nome=form["nome"].strip(),
            ordem=self._parse_int(form.get("ordem")),
            valor_diaria_net_padrao=self._parse_float(form.get("valor_diaria_net_padrao")),
            valor_diaria_sistema_padrao=self._parse_float(form.get("valor_diaria_sistema_padrao")),
            observacao=form.get("observacao", "").strip() or None,
        )
        return tipo, []

    def desativar(self, tipo_id: uuid.UUID) -> bool:
        tipo = self.repository.find_by_id(tipo_id)
        if not tipo:
            return False
        self.repository.soft_delete(tipo)
        return True

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

    def _validar(self, form: dict, tipo_atual) -> list:
        erros = []
        nome = form.get("nome", "").strip()
        if not nome:
            erros.append("Nome é obrigatório.")
        else:
            existente = self.repository.find_by_nome(nome)
            if existente and (tipo_atual is None or existente.id != tipo_atual.id):
                erros.append("Já existe um tipo de apartamento com esse nome.")
        return erros
