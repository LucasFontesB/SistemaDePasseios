from __future__ import annotations
import uuid
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_historico import GrupoHistorico


class GrupoHistoricoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list[GrupoHistorico]:
        return (
            self.db.query(GrupoHistorico)
            .options(joinedload(GrupoHistorico.usuario))
            .filter(GrupoHistorico.grupo_id == grupo_id)
            .order_by(GrupoHistorico.criado_em.desc())
            .all()
        )

    def registrar(
        self,
        grupo_id: uuid.UUID,
        usuario_id: uuid.UUID,
        entidade: str,
        entidade_id: uuid.UUID | None,
        acao: str,
        campo: str | None,
        valor_anterior: str | None,
        valor_novo: str | None,
    ) -> GrupoHistorico:
        registro = GrupoHistorico(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=entidade,
            entidade_id=entidade_id,
            acao=acao,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
        )
        self.db.add(registro)
        # Não faz commit aqui — quem chama controla a transação.
        return registro
