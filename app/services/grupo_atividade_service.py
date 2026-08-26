from __future__ import annotations
import uuid
from sqlalchemy.orm import Session

from app.repositories.grupo_historico_repository import GrupoHistoricoRepository
from app.repositories.grupo_comentario_repository import GrupoComentarioRepository
from app.services.grupo_historico_service import ENTIDADE_COMENTARIO
from app.models.grupo_orcamento import GrupoOrcamento
from app.models.grupo_pagamento import GrupoPagamento
from app.models.grupo_roomlist import GrupoRoomlist
from app.models.grupo_anexo import GrupoAnexo
from app.core.constants import GRUPO_STATUS_LABELS, ORCAMENTO_STATUS_LABELS

ENTIDADE_LABELS = {
    "GRUPO": "Grupo",
    "ORCAMENTO": "Orçamento",
    "PAGAMENTO": "Pagamento",
    "ROOMLIST": "Roomlist",
    "ANEXO": "Anexo",
    "COMENTARIO": "Comentário",
}

CAMPO_LABELS = {
    "nome": "Nome",
    "responsavel": "Responsável",
    "telefone": "Telefone",
    "email": "E-mail",
    "agencia": "Agência",
    "guia": "Guia",
    "data_entrada": "Data de Entrada",
    "data_saida": "Data de Saída",
    "qtd_hospedes": "Qtd. Hóspedes",
    "qtd_apartamentos": "Apartamentos Faturados",
    "qtd_apartamentos_cortesia": "Apartamentos de Cortesia",
    "valor_total_net": "Valor Total Net",
    "valor_total_net_manual": "Valor Total Net Manual",
    "valor_total_sistema": "Valor Total Sistema",
    "valor_total_sistema_manual": "Valor Total Sistema Manual",
    "prazo_deadline": "Prazo Deadline",
    "prazo_roomlist": "Prazo Roomlist",
    "observacao": "Observação",
    "status": "Status",
    "versao": "Versão",
    "valor": "Valor",
    "desatualizado": "Desatualizado",
    "hospede_nome": "Hóspede",
    "nome_original": "Arquivo",
}


class GrupoAtividadeService:
    """
    Une comentários e o histórico de alterações (grupos_historico) numa
    única linha do tempo, em ordem cronológica. Não gera dados novos —
    apenas lê e formata o que já foi gravado pelas demais camadas de
    service desde a Fase 3.

    RN-G026: cada linha do histórico mostra um identificador específico do
    registro afetado (buscado por join a partir de `entidade_id`), não só o
    nome genérico da entidade — senão duas versões de orçamento editadas em
    sequência aparecem como eventos indistinguíveis.
    """

    def __init__(self, db: Session):
        self.db = db
        self.historico_repository = GrupoHistoricoRepository(db)
        self.comentario_repository = GrupoComentarioRepository(db)

    def list_timeline(self, grupo_id: uuid.UUID, apenas_comentarios: bool = False) -> list[dict]:
        comentarios = self.comentario_repository.list_by_grupo(grupo_id)
        eventos = [
            {
                "tipo": "comentario",
                "criado_em": c.criado_em,
                "usuario_nome": c.usuario.nome if c.usuario else "—",
                "identificador": None,
                "descricao": c.texto,
            }
            for c in comentarios
        ]

        if not apenas_comentarios:
            # COMENTARIO já aparece acima com o texto completo — evita duplicar
            # a mesma criação como uma segunda linha genérica do histórico.
            historico = [
                h for h in self.historico_repository.list_by_grupo(grupo_id)
                if h.entidade != ENTIDADE_COMENTARIO
            ]
            identificadores = self._resolver_identificadores(grupo_id, historico)
            eventos += [
                {
                    "tipo": "historico",
                    "criado_em": h.criado_em,
                    "usuario_nome": h.usuario.nome if h.usuario else "—",
                    "identificador": identificadores.get(h.id, ENTIDADE_LABELS.get(h.entidade, h.entidade)),
                    "descricao": self._descrever(h),
                }
                for h in historico
            ]

        eventos.sort(key=lambda e: e["criado_em"], reverse=True)
        return eventos

    def _resolver_identificadores(self, grupo_id: uuid.UUID, historico: list) -> dict:
        """
        Monta, num único lote de queries por entidade (não uma por linha do
        histórico), o texto que identifica de forma inequívoca cada registro
        afetado: "Orçamento v{versao}", "Pagamento de {data} — R$ {valor}",
        "Roomlist — {hospede_nome}", "Anexo — {nome_original}".
        """
        orcamentos = {
            row.id: f"Orçamento v{row.versao}"
            for row in self.db.query(GrupoOrcamento).filter(GrupoOrcamento.grupo_id == grupo_id)
        }
        pagamentos = {
            row.id: f"Pagamento de {row.data_pagamento.strftime('%d/%m/%Y')} — R$ {float(row.valor):.2f}"
            for row in self.db.query(GrupoPagamento).filter(GrupoPagamento.grupo_id == grupo_id)
        }
        # Roomlist é excluída fisicamente — o nome pode não existir mais.
        roomlist = {
            row.id: f"Roomlist — {row.hospede_nome}"
            for row in self.db.query(GrupoRoomlist).filter(GrupoRoomlist.grupo_id == grupo_id)
        }
        # Anexo usa soft delete — inclui removidos, o registro nunca some fisicamente.
        anexos = {
            row.id: f"Anexo — {row.nome_original}"
            for row in self.db.query(GrupoAnexo).filter(GrupoAnexo.grupo_id == grupo_id)
        }

        mapas = {
            "ORCAMENTO": orcamentos,
            "PAGAMENTO": pagamentos,
            "ROOMLIST": roomlist,
            "ANEXO": anexos,
        }

        resultado = {}
        for h in historico:
            if h.entidade == "GRUPO":
                resultado[h.id] = "Dados do Grupo"
                continue
            mapa = mapas.get(h.entidade)
            if mapa and h.entidade_id in mapa:
                resultado[h.id] = mapa[h.entidade_id]
                continue
            # RN-G026 na prática: roomlist removida fisicamente não está mais
            # no mapa acima — usa o que a própria linha de EXCLUSAO/CRIACAO
            # já gravou (hospede_nome) como último recurso.
            if h.entidade == "ROOMLIST" and h.campo == "hospede_nome":
                nome = h.valor_anterior or h.valor_novo
                if nome:
                    resultado[h.id] = f"Roomlist — {nome}"
                    continue
            resultado[h.id] = ENTIDADE_LABELS.get(h.entidade, h.entidade)

        return resultado

    def _descrever(self, h) -> str:
        campo_label = CAMPO_LABELS.get(h.campo, h.campo or "")

        if h.acao == "CRIACAO":
            return "Criado"
        if h.acao == "EXCLUSAO":
            return "Removido"
        if h.acao == "STATUS":
            anterior = self._traduzir_status(h.entidade, h.valor_anterior)
            novo = self._traduzir_status(h.entidade, h.valor_novo)
            return f"Status alterado de {anterior} para {novo}"

        # EDICAO
        anterior = h.valor_anterior or "—"
        novo = h.valor_novo or "—"
        return f"{campo_label} alterado de {anterior} para {novo}"

    def _traduzir_status(self, entidade: str, valor: str | None) -> str:
        if not valor:
            return "—"
        if entidade == "GRUPO":
            return GRUPO_STATUS_LABELS.get(valor, valor)
        if entidade == "ORCAMENTO":
            return ORCAMENTO_STATUS_LABELS.get(valor, valor)
        return valor
