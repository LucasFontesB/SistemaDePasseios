from __future__ import annotations
from sqlalchemy.orm import Session

from app.core.security import verify_password, create_session
from app.models.usuario import Usuario
from app.repositories.user_repository import UserRepository


class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def authenticate(self, email: str, senha: str) -> tuple[bool, str, Usuario | None]:
        """
        Valida credenciais do usuário.

        Retorna uma tupla (sucesso, mensagem, usuario).
        """
        if not email or not senha:
            return False, "Preencha e-mail e senha.", None

        usuario = self.repository.find_by_email(email.strip().lower())

        if not usuario:
            return False, "E-mail ou senha incorretos.", None

        if not verify_password(senha, usuario.senha_hash):
            return False, "E-mail ou senha incorretos.", None

        return True, "Login realizado com sucesso.", usuario

    def create_session_token(self, usuario: Usuario) -> str:
        """Gera token de sessão para o usuário autenticado."""
        return create_session(
            user_id=str(usuario.id),
            perfil=usuario.perfil,
        )