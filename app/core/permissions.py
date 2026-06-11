from __future__ import annotations
from fastapi import HTTPException, status

# =============================================================================
# Perfis
# =============================================================================

ADMIN    = "ADMIN"
GERENCIA = "GERENCIA"
RECEPCAO = "RECEPCAO"

# =============================================================================
# Permissões por perfil
# =============================================================================

PERMISSIONS: dict[str, list[str]] = {
    ADMIN: [
        "dashboard",
        "vendas",
        "cadastros",
        "relatorios",
        "usuarios",
    ],
    GERENCIA: [
        "dashboard",
        "vendas",
        "cadastros",
        "relatorios",
    ],
    RECEPCAO: [
        "dashboard",
        "vendas",
    ],
}


def require_permission(perfil: str, modulo: str) -> None:
    """
    Verifica se o perfil tem acesso ao módulo.
    Lança HTTPException 403 se não tiver.
    """
    permitidos = PERMISSIONS.get(perfil, [])
    if modulo not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado.",
        )


def has_permission(perfil: str, modulo: str) -> bool:
    """Retorna True se o perfil tem acesso ao módulo."""
    return modulo in PERMISSIONS.get(perfil, [])