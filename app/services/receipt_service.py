from __future__ import annotations

import uuid
import os
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.receipt_repository import ReceiptRepository

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
ALLOWED_MIMETYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}


class ReceiptService:

    def __init__(self, db: Session):
        self.repository = ReceiptRepository(db)

    async def upload(self, venda_id: uuid.UUID, arquivo: UploadFile) -> tuple:
        """
        Valida e salva um comprovante.
        Retorna (comprovante, erros).
        """
        # Validar extensão
        nome_original = arquivo.filename or ""
        extensao = nome_original.rsplit(".", 1)[-1].lower() if "." in nome_original else ""

        if extensao not in ALLOWED_EXTENSIONS:
            return None, [f"Tipo de arquivo não permitido. Use: PDF, JPG, PNG."]

        # Validar MIME type
        content_type = arquivo.content_type or ""
        if content_type not in ALLOWED_MIMETYPES:
            return None, [f"Tipo de arquivo inválido."]

        # Ler conteúdo e validar tamanho
        conteudo = await arquivo.read()
        tamanho = len(conteudo)

        if tamanho > settings.upload_max_size_bytes:
            return None, [f"Arquivo muito grande. Máximo: {settings.UPLOAD_MAX_SIZE_MB} MB."]

        if tamanho == 0:
            return None, ["Arquivo vazio."]

        # Gerar nome interno com UUID
        nome_interno = f"{uuid.uuid4()}.{extensao}"

        # Pasta organizada por ano/mês
        agora = datetime.now()
        pasta_relativa = Path(settings.UPLOAD_PATH) / str(agora.year) / f"{agora.month:02d}"
        pasta_relativa.mkdir(parents=True, exist_ok=True)

        caminho_completo = pasta_relativa / nome_interno

        # Salvar arquivo
        with open(caminho_completo, "wb") as f:
            f.write(conteudo)

        # Registrar no banco
        comprovante = self.repository.create(
            venda_id=venda_id,
            nome_original=nome_original,
            nome_arquivo=nome_interno,
            caminho=str(caminho_completo),
            tipo_arquivo=extensao,
            tamanho_bytes=tamanho,
        )

        return comprovante, []

    def get_by_id(self, comprovante_id: uuid.UUID):
        return self.repository.find_by_id(comprovante_id)

    def remover(self, comprovante_id: uuid.UUID) -> tuple:
        """Remove o arquivo do disco e o registro do banco."""
        comprovante = self.repository.find_by_id(comprovante_id)
        if not comprovante:
            return False, ["Comprovante não encontrado."]

        # Remover arquivo do disco se existir
        try:
            if os.path.exists(comprovante.caminho):
                os.remove(comprovante.caminho)
        except Exception:
            pass  # Não bloquear remoção do registro se arquivo já não existir

        venda_id = comprovante.venda_id
        self.repository.delete(comprovante)
        return True, str(venda_id)
