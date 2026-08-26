from __future__ import annotations

import uuid
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.grupo_anexo_repository import GrupoAnexoRepository
from app.services.grupo_historico_service import GrupoHistoricoService, ENTIDADE_ANEXO
from app.core.constants import ANEXO_TIPO_CHOICES

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
ALLOWED_MIMETYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


class GrupoAnexoService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoAnexoRepository(db)
        self.historico_service = GrupoHistoricoService(db)

    def list_by_grupo(self, grupo_id: uuid.UUID, tipo: str = None) -> list:
        return self.repository.list_by_grupo(grupo_id, tipo=tipo)

    def get_by_id(self, anexo_id: uuid.UUID):
        return self.repository.find_by_id(anexo_id)

    async def upload(
        self,
        grupo_id: uuid.UUID,
        tipo: str,
        arquivo: UploadFile,
        usuario_id: uuid.UUID,
    ) -> tuple:
        """Valida e salva um anexo. Segue o mesmo padrão de app/services/receipt_service.py."""
        if tipo not in ANEXO_TIPO_CHOICES:
            tipo = "OUTRO"

        nome_original = arquivo.filename or ""
        extensao = nome_original.rsplit(".", 1)[-1].lower() if "." in nome_original else ""

        if extensao not in ALLOWED_EXTENSIONS:
            return None, ["Tipo de arquivo não permitido. Use: PDF, JPG, PNG."]

        content_type = arquivo.content_type or ""
        if content_type not in ALLOWED_MIMETYPES:
            return None, ["Tipo de arquivo inválido."]

        conteudo = await arquivo.read()
        tamanho = len(conteudo)

        if tamanho > settings.upload_max_size_bytes:
            return None, [f"Arquivo muito grande. Máximo: {settings.UPLOAD_MAX_SIZE_MB} MB."]

        if tamanho == 0:
            return None, ["Arquivo vazio."]

        nome_interno = f"{uuid.uuid4()}.{extensao}"

        agora = datetime.now()
        pasta_relativa = Path(settings.UPLOAD_PATH) / "grupos" / str(agora.year) / f"{agora.month:02d}"
        pasta_relativa.mkdir(parents=True, exist_ok=True)

        caminho_completo = pasta_relativa / nome_interno

        with open(caminho_completo, "wb") as f:
            f.write(conteudo)

        anexo = self.repository.create(
            grupo_id=grupo_id,
            tipo=tipo,
            nome_original=nome_original,
            nome_arquivo=nome_interno,
            caminho=str(caminho_completo),
            tipo_arquivo=extensao,
            tamanho_bytes=tamanho,
            usuario_id=usuario_id,
        )

        self.historico_service.registrar_criacao(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ANEXO,
            entidade_id=anexo.id,
            campo="nome_original",
            valor_novo=nome_original,
        )
        self.db.commit()

        return anexo, []

    def remover(self, grupo_id: uuid.UUID, anexo_id: uuid.UUID, usuario_id: uuid.UUID) -> tuple:
        anexo = self.repository.find_by_id(anexo_id)
        if not anexo or anexo.grupo_id != grupo_id:
            return False, ["Anexo não encontrado."]

        self.historico_service.registrar_exclusao(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=ENTIDADE_ANEXO,
            entidade_id=anexo.id,
            campo="nome_original",
            valor_anterior=anexo.nome_original,
        )
        self.repository.soft_delete(anexo)
        self.db.commit()

        return True, []
