from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.repositories.grupo_historico_repository import GrupoHistoricoRepository

# Entidades rastreadas (GRUPOS.md — Log de Alterações)
ENTIDADE_GRUPO = "GRUPO"
ENTIDADE_ORCAMENTO = "ORCAMENTO"
ENTIDADE_PAGAMENTO = "PAGAMENTO"
ENTIDADE_ROOMLIST = "ROOMLIST"
ENTIDADE_ANEXO = "ANEXO"
ENTIDADE_COMENTARIO = "COMENTARIO"

ACAO_CRIACAO = "CRIACAO"
ACAO_EDICAO = "EDICAO"
ACAO_EXCLUSAO = "EXCLUSAO"
ACAO_STATUS = "STATUS"


class GrupoHistoricoService:
    """
    RN-G009: toda alteração em qualquer entidade do grupo gera registro em
    grupos_historico, uma linha por campo alterado. Chamado sempre pela
    camada de service das entidades do grupo (nunca por event listener do
    SQLAlchemy, que não tem acesso ao usuário da sessão).
    """

    def __init__(self, db: Session):
        self.db = db
        self.repository = GrupoHistoricoRepository(db)

    def list_by_grupo(self, grupo_id: uuid.UUID) -> list:
        return self.repository.list_by_grupo(grupo_id)

    def registrar_criacao(
        self,
        grupo_id: uuid.UUID,
        usuario_id: uuid.UUID,
        entidade: str,
        entidade_id: uuid.UUID | None,
        campo: str | None = None,
        valor_novo: str | None = None,
    ) -> None:
        self.repository.registrar(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=entidade,
            entidade_id=entidade_id,
            acao=ACAO_CRIACAO,
            campo=campo,
            valor_anterior=None,
            valor_novo=valor_novo,
        )

    def registrar_exclusao(
        self,
        grupo_id: uuid.UUID,
        usuario_id: uuid.UUID,
        entidade: str,
        entidade_id: uuid.UUID | None,
        campo: str | None = None,
        valor_anterior: str | None = None,
    ) -> None:
        self.repository.registrar(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=entidade,
            entidade_id=entidade_id,
            acao=ACAO_EXCLUSAO,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_novo=None,
        )

    def registrar_status(
        self,
        grupo_id: uuid.UUID,
        usuario_id: uuid.UUID,
        entidade: str,
        entidade_id: uuid.UUID | None,
        valor_anterior: str | None,
        valor_novo: str | None,
    ) -> None:
        self.repository.registrar(
            grupo_id=grupo_id,
            usuario_id=usuario_id,
            entidade=entidade,
            entidade_id=entidade_id,
            acao=ACAO_STATUS,
            campo="status",
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
        )

    def registrar_diff(
        self,
        grupo_id: uuid.UUID,
        usuario_id: uuid.UUID,
        entidade: str,
        entidade_id: uuid.UUID | None,
        antes: dict,
        depois: dict,
    ) -> list[str]:
        """
        Compara dois snapshots (campo -> valor já formatado para exibição) e
        grava uma linha em grupos_historico para cada campo que mudou.
        Retorna a lista de campos alterados.
        """
        campos_alterados = []
        for campo, valor_novo in depois.items():
            valor_anterior = antes.get(campo)
            if valor_anterior != valor_novo:
                self.repository.registrar(
                    grupo_id=grupo_id,
                    usuario_id=usuario_id,
                    entidade=entidade,
                    entidade_id=entidade_id,
                    acao=ACAO_EDICAO,
                    campo=campo,
                    valor_anterior=valor_anterior,
                    valor_novo=valor_novo,
                )
                campos_alterados.append(campo)
        return campos_alterados
