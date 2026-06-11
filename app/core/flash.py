from __future__ import annotations

import json
from fastapi import Request, Response


FLASH_COOKIE = "flash_messages"


def set_flash(response: Response, mensagem: str, tipo: str = "success") -> None:
    """
    Salva uma mensagem flash no cookie.
    tipo: success | danger | warning | info
    """
    mensagens = [{"mensagem": mensagem, "tipo": tipo}]
    response.set_cookie(
        key=FLASH_COOKIE,
        value=json.dumps(mensagens, ensure_ascii=False),
        max_age=10,
        httponly=True,
        samesite="lax",
    )


def get_flash(request: Request) -> list[dict]:
    """Lê e retorna as mensagens flash do cookie."""
    valor = request.cookies.get(FLASH_COOKIE)
    if not valor:
        return []
    try:
        return json.loads(valor)
    except Exception:
        return []


def clear_flash(response: Response) -> None:
    """Remove o cookie de flash."""
    response.delete_cookie(FLASH_COOKIE)
