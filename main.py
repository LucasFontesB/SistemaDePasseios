import os
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.templates import templates
from app.controllers.auth_controller import router as auth_router
from app.controllers.dashboard_controller import router as dashboard_router
from app.controllers.sale_controller import router as sale_router
from app.controllers.receipt_controller import router as receipt_router
from app.controllers.cadastro_controller import router as cadastro_router
from app.controllers.user_controller import router as user_router
from app.controllers.report_controller import router as report_router

# =============================================================================
# Aplicação
# =============================================================================

app = FastAPI(
    title="Sistema de Gestão de Passeios",
    docs_url=None,   # desabilita /docs em produção
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
# Rotas
# =============================================================================

# Routers
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(sale_router)
app.include_router(receipt_router)
app.include_router(cadastro_router)
app.include_router(user_router)
app.include_router(report_router)


# Redireciona raiz para login
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)


# Health check
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