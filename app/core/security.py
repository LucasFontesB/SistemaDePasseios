import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request, HTTPException, status

from app.core.config import settings

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

# =============================================================================
# Senhas
# =============================================================================

def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verifica se a senha confere com o hash armazenado."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# =============================================================================
# Sessão
# =============================================================================

SESSION_COOKIE = "session"


def create_session(user_id: str, perfil: str) -> str:
    """Gera token de sessão assinado."""
    return _serializer.dumps({"user_id": user_id, "perfil": perfil})


def decode_session(token: str) -> dict:
    """
    Decodifica e valida token de sessão.
    Lança exceção se inválido ou expirado.
    """
    try:
        data = _serializer.loads(token, max_age=settings.SESSION_MAX_AGE)
        return data
    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada. Faça login novamente.",
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida.",
        )


def get_current_user(request: Request) -> dict:
    """
    Retorna os dados do usuário logado a partir do cookie de sessão.
    Redireciona para login se não autenticado.
    """
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado.",
        )
    return decode_session(token)
