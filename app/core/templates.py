from __future__ import annotations

import json
from fastapi.templating import Jinja2Templates

from app.core.constants import (
    STATUS_LABELS, PERFIL_LABELS, FORMA_PAGAMENTO_LABELS,
    GRUPO_STATUS_LABELS, ORCAMENTO_STATUS_LABELS, ANEXO_TIPO_LABELS,
)

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["status_labels"] = STATUS_LABELS
templates.env.globals["perfil_labels"] = PERFIL_LABELS
templates.env.globals["forma_pagamento_labels"] = FORMA_PAGAMENTO_LABELS
templates.env.globals["grupo_status_labels"] = GRUPO_STATUS_LABELS
templates.env.globals["orcamento_status_labels"] = ORCAMENTO_STATUS_LABELS
templates.env.globals["anexo_tipo_labels"] = ANEXO_TIPO_LABELS
templates.env.filters["from_json"] = lambda s: json.loads(s) if s else []