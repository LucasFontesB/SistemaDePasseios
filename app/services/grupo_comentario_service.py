from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.repositories.grupo_comentario_repository import GrupoComentarioRepository
from app.services.grupo_historico_service import GrupoHistoricoService, ENTIDADE_COMENTARIO


class GrupoComentarioService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoComentarioRepository(db)
        self.historico_service = GrupoHistoricoService(db)

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list:
        return self.repository.list_by_grupo(grupo_id)

    def registrar(self, grupo_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        texto = (form.get("texto") or "").strip()
        if not texto:
            return None, ["O comentário não pode ser vazio."]

        comentario = self.repository.create(grupo_id=grupo_id, texto=texto, usuario_id=usuario_id)

        self.historico_service.registrar_criacao(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_COMENTARIO,
            entidade_id=comentario.id,
        )
        self.db.commit()

        return comentario, []
