from __future__ import annotations
import uuid
from sqlalchemy.orm import Session, joinedload

from app.models.grupo_comentario import GrupoComentario


class GrupoComentarioRepository:

    def __init__(self, db: Session):
        self.db = db

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list[GrupoComentario]:
        return (
            self.db.query(GrupoComentario)
            .options(joinedload(GrupoComentario.usuario))
            .filter(GrupoComentario.grupo_id == grupo_id)
            .order_by(GrupoComentario.criado_em.desc())
            .all()
        )

    def create(self, grupo_id: uuid.UUID, texto: str, usuario_id: uuid.UUID) -> GrupoComentario:
        comentario = GrupoComentario(
            id=uuid.uuid4(),
            grupo_id=grupo_id,
            texto=texto,
            usuario_id=usuario_id,
        )
        self.db.add(comentario)
        self.db.commit()
        self.db.refresh(comentario)
        return comentario
