from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str) -> Usuario | None:
        """Busca usuário ativo pelo e-mail."""
        return (
            self.db.query(Usuario)
            .filter(
                Usuario.email == email,
                Usuario.deletado_em.is_(None),
            )
            .first()
        )

    def find_by_id(self, user_id: uuid.UUID) -> Usuario | None:
        """Busca usuário ativo pelo ID."""
        return (
            self.db.query(Usuario)
            .filter(
                Usuario.id == user_id,
                Usuario.deletado_em.is_(None),
            )
            .first()
        )

    def list_active(self) -> list[Usuario]:
        """Lista todos os usuários ativos."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.deletado_em.is_(None))
            .order_by(Usuario.nome)
            .all()
        )

    def create(self, nome: str, email: str, senha_hash: str, perfil: str) -> Usuario:
        """Cria novo usuário."""
        usuario = Usuario(
            id=uuid.uuid4(),
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            perfil=perfil,
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario, **kwargs) -> Usuario:
        """Atualiza campos do usuário."""
        for campo, valor in kwargs.items():
            setattr(usuario, campo, valor)
        usuario.atualizado_em = datetime.utcnow()
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def soft_delete(self, usuario: Usuario) -> None:
        """Desativa usuário (soft delete)."""
        usuario.deletado_em = datetime.utcnow()
        self.db.commit()