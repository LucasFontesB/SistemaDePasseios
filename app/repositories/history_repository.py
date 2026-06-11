from __future__ import annotations

import uuid
from sqlalchemy.orm import Session

from app.models.venda_historico import VendaHistorico


class HistoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def registrar(
        self,
        venda_id: uuid.UUID,
        usuario_id: uuid.UUID,
        campo: str,
        valor_anterior: str | None,
        valor_novo: str | None,
    ) -> VendaHistorico:
        registro = VendaHistorico(
            id=uuid.uuid4(),
            venda_id=venda_id,
            usuario_id=usuario_id,
            campo=campo,
            valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
            valor_novo=str(valor_novo) if valor_novo is not None else None,
        )
        self.db.add(registro)
        # Não faz commit aqui — quem chama controla a transação
        return registro

    def registrar_multiplos(
        self,
        venda_id: uuid.UUID,
        usuario_id: uuid.UUID,
        alteracoes: list[dict],
    ) -> None:
        """
        Registra múltiplas alterações de uma vez.
        alteracoes: lista de dicts com chaves campo, valor_anterior, valor_novo
        """
        for alt in alteracoes:
            self.registrar(
                venda_id=venda_id,
                usuario_id=usuario_id,
                campo=alt["campo"],
                valor_anterior=alt.get("valor_anterior"),
                valor_novo=alt.get("valor_novo"),
            )
