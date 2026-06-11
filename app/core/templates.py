from fastapi.templating import Jinja2Templates

from app.core.constants import STATUS_LABELS, PERFIL_LABELS, FORMA_PAGAMENTO_LABELS

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["status_labels"] = STATUS_LABELS
templates.env.globals["perfil_labels"] = PERFIL_LABELS
templates.env.globals["forma_pagamento_labels"] = FORMA_PAGAMENTO_LABELS