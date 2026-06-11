from __future__ import annotations

import uuid
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def get_dados(self, usuario_id: uuid.UUID = None, perfil: str = None) -> dict:
        """Retorna todos os dados necessários para o dashboard."""
        dados = {
            "hoje": self.repository.get_indicadores_hoje(),
            "mes": self.repository.get_indicadores_mes(),
            "proximos_embarques": self.repository.get_proximos_embarques(),
            "pendencias": self.repository.get_pendencias(),
            "comissao_recepcao": None,
        }

        if perfil == "RECEPCAO" and usuario_id:
            dados["comissao_recepcao"] = self.repository.get_comissao_recepcao(usuario_id)

        return dados