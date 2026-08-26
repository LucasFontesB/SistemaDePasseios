from __future__ import annotations
import uuid
from datetime import date
from sqlalchemy.orm import Session

from app.repositories.grupo_pagamento_repository import GrupoPagamentoRepository
from app.repositories.grupo_repository import GrupoRepository
from app.services.grupo_historico_service import GrupoHistoricoService, ENTIDADE_PAGAMENTO
from app.services.orcamento_service import OrcamentoService
from app.core.constants import FORMA_PAGAMENTO_CHOICES


class GrupoPagamentoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoPagamentoRepository(db)
        self.grupo_repository = GrupoRepository(db)
        self.historico_service = GrupoHistoricoService(db)
        self.orcamento_service = OrcamentoService(db)

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list:
        return self.repository.list_by_grupo(grupo_id)

    def registrar(self, grupo_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        grupo = self.grupo_repository.find_by_id(grupo_id)
        if not grupo:
            return None, ["Grupo não encontrado."]

        erros = self._validar(form)
        if erros:
            return None, erros

        valor = self._parse_float(form.get("valor"))
        data_raw = (form.get("data_pagamento") or "").strip()
        data_pagamento = date.fromisoformat(data_raw) if data_raw else date.today()
        forma_pagamento = (form.get("forma_pagamento") or "").strip() or None
        observacao = (form.get("observacao") or "").strip() or None

        pagamento = self.repository.create(
            grupo_id=grupo_id,
            valor=valor,
            data_pagamento=data_pagamento,
            forma_pagamento=forma_pagamento,
            observacao=observacao,
            usuario_id=usuario_id,
        )

        self.historico_service.registrar_criacao(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_PAGAMENTO,
            entidade_id=pagamento.id,
            campo="valor",
            valor_novo=f"R$ {valor:.2f}",
        )
        self.db.commit()

        # RN-G017: todo pagamento — mesmo sem mudança estrutural — dispara a
        # verificação de divergência, pois valor_pago_snapshot/saldo_snapshot
        # deixam de refletir a realidade a partir do primeiro pagamento
        # seguinte à geração da versão vigente.
        self.db.refresh(grupo)
        self.orcamento_service.sinalizar_se_divergente(grupo, usuario_id)

        return pagamento, []

    def _parse_float(self, valor: str | None) -> float:
        if not valor:
            return 0.0
        try:
            return float(str(valor).replace(",", "."))
        except ValueError:
            return 0.0

    def _validar(self, form: dict) -> list:
        erros = []
        valor_raw = (form.get("valor") or "").replace(",", ".").strip()
        if not valor_raw:
            erros.append("Informe o valor do pagamento.")
        else:
            try:
                v = float(valor_raw)
                if v == 0:
                    erros.append("O valor do pagamento não pode ser zero.")
            except ValueError:
                erros.append("Valor informado é inválido.")

        forma_pagamento = (form.get("forma_pagamento") or "").strip()
        if forma_pagamento and forma_pagamento not in FORMA_PAGAMENTO_CHOICES:
            erros.append("Forma de pagamento inválida.")

        return erros
