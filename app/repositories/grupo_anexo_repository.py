from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_anexo import GrupoAnexo


class GrupoAnexoRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID, tipo: str = None) -> list[GrupoAnexo]:
        query = (
            self.db.query(GrupoAnexo)
            .options(joinedload(GrupoAnexo.usuario))
            .filter(GrupoAnexo.grupo_id == grupo_id, GrupoAnexo.removido_em.is_(None))
        )
        if tipo:
            query = query.filter(GrupoAnexo.tipo == tipo)
        return query.order_by(GrupoAnexo.enviado_em.desc()).all()

    def find_by_id(self, anexo_id: uuid.UUID) -> GrupoAnexo | None:
        return (
            self.db.query(GrupoAnexo)
            .filter(GrupoAnexo.id == anexo_id, GrupoAnexo.removido_em.is_(None))
            .first()
        )

    def create(
        self,
        grupo_id: uuid.UUID,
        tipo: str,
        nome_original: str,
        nome_arquivo: str,
        caminho: str,
        tipo_arquivo: str,
        tamanho_bytes: int,
        usuario_id: uuid.UUID,
    ) -> GrupoAnexo:
        anexo = GrupoAnexo(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            tipo=tipo,
            nome_original=nome_original,
            nome_arquivo=nome_arquivo,
            caminho=caminho,
            tipo_arquivo=tipo_arquivo,
            tamanho_bytes=tamanho_bytes,
            usuario_id=usuario_id,
        )
        self.db.add(anexo)
        self.db.commit()
        self.db.refresh(anexo)
        return anexo

    def soft_delete(self, anexo: GrupoAnexo) -> None:
        anexo.removido_em = datetime.utcnow()
        self.db.commit()
