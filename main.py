import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.templates import templates
from app.controllers.auth_controller import router as auth_router
from app.controllers.dashboard_controller import router as dashboard_router
from app.controllers.sale_controller import router as sale_router
from app.controllers.receipt_controller import router as receipt_router
from app.controllers.cadastro_controller import router as cadastro_router
from app.controllers.user_controller import router as user_router
from app.controllers.report_controller import router as report_router
from app.controllers.agenda_controller import router as agenda_router
from app.controllers.pdf_controller import router as pdf_router
from app.controllers.perfil_controller import router as perfil_router
from app.controllers.gerencial_controller import router as gerencial_router

# =============================================================================
# Aplicação
# =============================================================================

app = FastAPI(
    title="Sistema de Gestão de Passeios",
    docs_url=None,
    redoc_url=None,
)

# =============================================================================
# Arquivos estáticos
# =============================================================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)

# =============================================================================
# Pasta de uploads
# =============================================================================

Path(settings.UPLOAD_PATH).mkdir(parents=True, exist_ok=True)

# =============================================================================
# Handlers de erro
# =============================================================================

ERROS = {
    400: ("400", "Requisição Inválida",      "Os dados enviados são inválidos. Verifique as informações e tente novamente."),
    401: ("401", "Não Autorizado",           "Você precisa estar logado para acessar esta página."),
    403: ("403", "Acesso Negado",            "Você não tem permissão para acessar esta página."),
    404: ("404", "Página Não Encontrada",    "A página que você está procurando não existe ou foi movida."),
    500: ("500", "Erro Interno",             "Ocorreu um erro inesperado. Por favor, tente novamente. Se o problema persistir, contate o suporte."),
}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # 401 e 403 redirecionam para login
    if exc.status_code in (401, 403):
        return RedirectResponse(url="/login", status_code=302)

    codigo, titulo, descricao = ERROS.get(
        exc.status_code,
        (str(exc.status_code), "Erro", "Ocorreu um erro inesperado.")
    )
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "codigo": codigo, "titulo": titulo, "descricao": descricao},
        status_code=exc.status_code,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    codigo, titulo, descricao = ERROS[400]
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "codigo": codigo, "titulo": titulo, "descricao": descricao},
        status_code=400,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    codigo, titulo, descricao = ERROS[500]
    return templates.TemplateResponse(
        "errors/error.html",
        {"request": request, "codigo": codigo, "titulo": titulo, "descricao": descricao},
        status_code=500,
    )

# =============================================================================
# Rotas
# =============================================================================

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(sale_router)
app.include_router(receipt_router)
app.include_router(cadastro_router)
app.include_router(user_router)
app.include_router(report_router)
app.include_router(agenda_router)
app.include_router(pdf_router)
app.include_router(perfil_router)
app.include_router(gerencial_router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


@app.get("/health")
async def health():
    return {"status": "ok"}


# =============================================================================
# Inicialização
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=not settings.is_production,
    )