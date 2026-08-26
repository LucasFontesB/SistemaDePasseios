from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.repositories.guia_repository import GuiaRepository


class GuiaService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GuiaRepository(db)

    def list(self) -> list:
        return self.repository.list_active()

    def get_by_id(self, guia_id: uuid.UUID):
        return self.repository.find_by_id(guia_id)

    def create(self, form: dict):
        erros = self._validar(form)
        if erros:
            return None, erros

        guia = self.repository.create(
            nome=form["nome"].strip(),
            cpf=form.get("cpf", "").strip() or None,
            cadastur=form.get("cadastur", "").strip() or None,
            telefone=form.get("telefone", "").strip() or None,
            email=form.get("email", "").strip() or None,
            percentual_comissao_padrao=self._parse_percentual(form.get("percentual_comissao_padrao")),
            observacao=form.get("observacao", "").strip() or None,
        )
        return guia, []

    def update(self, guia_id: uuid.UUID, form: dict):
        guia = self.repository.find_by_id(guia_id)
        if not guia:
            return None, ["Guia não encontrado."]

        erros = self._validar(form)
        if erros:
            return None, erros

        guia = self.repository.update(
            guia=guia,
            nome=form["nome"].strip(),
            cpf=form.get("cpf", "").strip() or None,
            cadastur=form.get("cadastur", "").strip() or None,
            telefone=form.get("telefone", "").strip() or None,
            email=form.get("email", "").strip() or None,
            percentual_comissao_padrao=self._parse_percentual(form.get("percentual_comissao_padrao")),
            observacao=form.get("observacao", "").strip() or None,
        )
        return guia, []

    def desativar(self, guia_id: uuid.UUID) -> bool:
        guia = self.repository.find_by_id(guia_id)
        if not guia:
            return False
        self.repository.soft_delete(guia)
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
