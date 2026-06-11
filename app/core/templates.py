from fastapi.templating import Jinja2Templates

from app.core.constants import STATUS_LABELS, PERFIL_LABELS

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["status_labels"] = STATUS_LABELS
templates.env.globals["perfil_labels"] = PERFIL_LABELS