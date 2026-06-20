from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.models.pagamento import Pagamento
from app.repositories.payment_repository import PaymentRepository
from app.repositories.sale_repository import SaleRepository

FORMAS_PAGAMENTO_VALIDAS = {"DINHEIRO", "PIX", "CARTAO_DEBITO", "CARTAO_CREDITO"}


class PaymentService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = PaymentRepository(db)
        self.sale_repository = SaleRepository(db)

    def list_by_venda(self, venda_id: uuid.UUID) -> list[Pagamento]:
        return self.repository.list_by_venda(venda_id)

    def register(
        self,
        venda_id: uuid.UUID,
        form: dict,
        usuario_id: uuid.UUID,
    ) -> tuple[Pagamento | None, list[str]]:
        erros: list[str] = []

        venda = self.sale_repository.find_by_id(venda_id)
        if not venda:
            erros.append("Venda não encontrada.")
            return None, erros

        valor_str = (form.get("valor") or "").replace(",", ".").strip()
        forma_pagamento = (form.get("forma_pagamento") or "").strip()
        observacao = (form.get("observacao") or "").strip() or None

        try:
            valor = float(valor_str)
        except ValueError:
            erros.append("Valor informado é inválido.")
            valor = None

        if valor is not None and valor == 0:
            erros.append("O valor do pagamento não pode ser zero.")

        if forma_pagamento not in FORMAS_PAGAMENTO_VALIDAS:
            erros.append("Forma de pagamento inválida.")

        if erros:
            return None, erros

        pagamento = self.repository.create(
            venda_id=venda_id,
            valor=valor,
            forma_pagamento=forma_pagamento,
            observacao=observacao,
            usuario_id=usuario_id,
        )
        return pagamento, []
