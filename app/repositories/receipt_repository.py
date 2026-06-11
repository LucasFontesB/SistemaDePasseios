from __future__ import annotations

import uuid
from sqlalchemy.orm import Session

from app.models.comprovante import Comprovante


class ReceiptRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, comprovante_id: uuid.UUID) -> Comprovante | None:
        return (
            self.db.query(Comprovante)
            .filter(Comprovante.id == comprovante_id)
            .first()
        )

    def create(
        self,
        venda_id: uuid.UUID,
        nome_original: str,
        nome_arquivo: str,
        caminho: str,
        tipo_arquivo: str,
        tamanho_bytes: int,
    ) -> Comprovante:
        comprovante = Comprovante(
            id=uuid.uuid4(),
            venda_id=venda_id,
            nome_original=nome_original,
            nome_arquivo=nome_arquivo,
            caminho=caminho,
            tipo_arquivo=tipo_arquivo,
            tamanho_bytes=tamanho_bytes,
        )
        self.db.add(comprovante)
        self.db.commit()
        self.db.refresh(comprovante)
        return comprovante

    def delete(self, comprovante: Comprovante) -> None:
        """Remoção física do registro — o arquivo já foi removido pelo service."""
        self.db.delete(comprovante)
        self.db.commit()
