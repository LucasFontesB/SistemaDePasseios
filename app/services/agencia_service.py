from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.repositories.agencia_repository import AgenciaRepository


class AgenciaService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = AgenciaRepository(db)

    def list(self) -> list:
        return self.repository.list_active()

    def get_by_id(self, agencia_id: uuid.UUID):
        return self.repository.find_by_id(agencia_id)

    def create(self, form: dict):
        erros = self._validar(form)
        if erros:
            return None, erros

        agencia = self.repository.create(
            nome=form["nome"].strip(),
            nome_fantasia=form.get("nome_fantasia", "").strip() or None,
            cnpj=form.get("cnpj", "").strip() or None,
            contato=form.get("contato", "").strip() or None,
            telefone=form.get("telefone", "").strip() or None,
            email=form.get("email", "").strip() or None,
            percentual_comissao_padrao=self._parse_percentual(form.get("percentual_comissao_padrao")),
            observacao=form.get("observacao", "").strip() or None,
        )
        return agencia, []

    def update(self, agencia_id: uuid.UUID, form: dict):
        agencia = self.repository.find_by_id(agencia_id)
        if not agencia:
            return None, ["Agência não encontrada."]

        erros = self._validar(form)
        if erros:
            return None, erros

        agencia = self.repository.update(
            agencia=agencia,
            nome=form["nome"].strip(),
            nome_fantasia=form.get("nome_fantasia", "").strip() or None,
            cnpj=form.get("cnpj", "").strip() or None,
            contato=form.get("contato", "").strip() or None,
            telefone=form.get("telefone", "").strip() or None,
            email=form.get("email", "").strip() or None,
            percentual_comissao_padrao=self._parse_percentual(form.get("percentual_comissao_padrao")),
            observacao=form.get("observacao", "").strip() or None,
        )
        return agencia, []

    def desativar(self, agencia_id: uuid.UUID) -> bool:
        agencia = self.repository.find_by_id(agencia_id)
        if not agencia:
            return False
        self.repository.soft_delete(agencia)
        return True

    def _parse_percentual(self, valor: str | None) -> float:
        if not valor:
            return 0.0
        try:
            return float(valor)
        except ValueError:
            return 0.0

    def _validar(self, form: dict) -> list:
        erros = []
        if not form.get("nome", "").strip():
            erros.append("Nome é obrigatório.")
        percentual = form.get("percentual_comissao_padrao")
        if percentual:
            try:
                v = float(percentual)
                if v < 0 or v > 100:
                    erros.append("Percentual de comissão deve estar entre 0 e 100.")
            except ValueError:
                erros.append("Percentual de comissão inválido.")
        return erros
