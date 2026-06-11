from __future__ import annotations

import uuid
from datetime import date, datetime, time
from sqlalchemy.orm import Session

from app.repositories.sale_repository import SaleRepository
from app.repositories.tour_repository import TourRepository
from app.repositories.history_repository import HistoryRepository
from app.core.constants import STATUS_CHOICES

# Labels legíveis para o histórico
CAMPO_LABELS = {
    "status":      "Status",
    "valor_total": "Valor Total",
    "data_saida":  "Data de Saída",
    "passeio_id":  "Passeio",
    "contratante": "Contratante",
    "telefone":    "Telefone",
    "adultos":     "Adultos",
    "criancas":    "Crianças",
    "observacao":  "Observação",
}


class SaleService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = SaleRepository(db)
        self.tour_repository = TourRepository(db)
        self.history_repository = HistoryRepository(db)

    def get_form_data(self) -> dict:
        return {
            "passeios": self.tour_repository.list_passeios(),
            "tipos": self.tour_repository.list_tipos(),
            "embarcacoes": self.tour_repository.list_embarcacoes(),
            "status_choices": STATUS_CHOICES,
        }

    def list(self, **filtros) -> list:
        return self.repository.list(**filtros)

    def get_by_id(self, venda_id: uuid.UUID):
        return self.repository.find_by_id(venda_id)

    def create(self, form: dict, usuario_id: uuid.UUID):
        """Valida e cria uma nova venda."""
        erros = self._validar(form)
        if erros:
            return None, erros

        passeio = self.tour_repository.find_passeio_by_id(uuid.UUID(form["passeio_id"]))
        if not passeio:
            return None, ["Passeio não encontrado."]

        valor_total = float(form["valor_total"])
        percentual_comissao = float(passeio.percentual_comissao)
        valor_comissao = round(valor_total * percentual_comissao / 100, 2)
        horario_saida = self._parse_horario(form.get("horario_saida"))

        venda = self.repository.create(
            contratante=form["contratante"].strip(),
            telefone=form.get("telefone", "").strip(),
            adultos=int(form.get("adultos", 1)),
            criancas=int(form.get("criancas", 0)),
            passeio_id=uuid.UUID(form["passeio_id"]),
            tipo_passeio_id=uuid.UUID(form["tipo_passeio_id"]),
            embarcacao_id=uuid.UUID(form["embarcacao_id"]) if form.get("embarcacao_id") else None,
            valor_total=valor_total,
            percentual_comissao=percentual_comissao,
            valor_comissao=valor_comissao,
            data_saida=date.fromisoformat(form["data_saida"]),
            horario_saida=horario_saida,
            observacao=form.get("observacao", "").strip(),
            usuario_id=usuario_id,
        )

        # Registra criação no histórico
        self.history_repository.registrar(
            venda_id=venda.id,
            usuario_id=usuario_id,
            campo="status",
            valor_anterior=None,
            valor_novo="PENDENTE",
        )
        self.db.commit()

        return venda, []

    def update(self, venda_id: uuid.UUID, form: dict, usuario_id: uuid.UUID):
        """Valida, detecta alterações e atualiza uma venda."""
        venda = self.repository.find_by_id(venda_id)
        if not venda:
            return None, ["Venda não encontrada."]

        erros = self._validar(form)
        if erros:
            return None, erros

        passeio = self.tour_repository.find_passeio_by_id(uuid.UUID(form["passeio_id"]))
        if not passeio:
            return None, ["Passeio não encontrado."]

        valor_total = float(form["valor_total"])
        percentual_comissao = float(passeio.percentual_comissao)
        valor_comissao = round(valor_total * percentual_comissao / 100, 2)
        horario_saida = self._parse_horario(form.get("horario_saida"))
        nova_data = date.fromisoformat(form["data_saida"])
        novo_passeio_id = uuid.UUID(form["passeio_id"])

        # Detecta alterações para registrar no histórico
        alteracoes = []

        if float(venda.valor_total) != valor_total:
            alteracoes.append({
                "campo": "valor_total",
                "valor_anterior": f"R$ {float(venda.valor_total):.2f}",
                "valor_novo": f"R$ {valor_total:.2f}",
            })

        if venda.data_saida != nova_data:
            alteracoes.append({
                "campo": "data_saida",
                "valor_anterior": venda.data_saida.strftime("%d/%m/%Y"),
                "valor_novo": nova_data.strftime("%d/%m/%Y"),
            })

        if venda.passeio_id != novo_passeio_id:
            passeio_anterior = self.tour_repository.find_passeio_by_id(venda.passeio_id)
            alteracoes.append({
                "campo": "passeio_id",
                "valor_anterior": passeio_anterior.nome if passeio_anterior else str(venda.passeio_id),
                "valor_novo": passeio.nome,
            })

        if venda.contratante != form["contratante"].strip():
            alteracoes.append({
                "campo": "contratante",
                "valor_anterior": venda.contratante,
                "valor_novo": form["contratante"].strip(),
            })

        venda = self.repository.update(
            venda=venda,
            contratante=form["contratante"].strip(),
            telefone=form.get("telefone", "").strip(),
            adultos=int(form.get("adultos", 1)),
            criancas=int(form.get("criancas", 0)),
            passeio_id=novo_passeio_id,
            tipo_passeio_id=uuid.UUID(form["tipo_passeio_id"]),
            embarcacao_id=uuid.UUID(form["embarcacao_id"]) if form.get("embarcacao_id") else None,
            valor_total=valor_total,
            percentual_comissao=percentual_comissao,
            valor_comissao=valor_comissao,
            data_saida=nova_data,
            horario_saida=horario_saida,
            observacao=form.get("observacao", "").strip(),
        )

        if alteracoes:
            self.history_repository.registrar_multiplos(
                venda_id=venda.id,
                usuario_id=usuario_id,
                alteracoes=alteracoes,
            )
            self.db.commit()

        return venda, []

    def update_status(self, venda_id: uuid.UUID, status: str, usuario_id: uuid.UUID):
        """Atualiza o status de uma venda e registra no histórico."""
        if status not in STATUS_CHOICES:
            return None, ["Status inválido."]

        venda = self.repository.find_by_id(venda_id)
        if not venda:
            return None, ["Venda não encontrada."]

        status_anterior = venda.status
        venda = self.repository.update_status(venda, status)

        self.history_repository.registrar(
            venda_id=venda.id,
            usuario_id=usuario_id,
            campo="status",
            valor_anterior=status_anterior,
            valor_novo=status,
        )
        self.db.commit()

        return venda, []

    def _parse_horario(self, valor: str) -> time | None:
        if not valor:
            return None
        try:
            h, m = valor.split(":")
            return time(int(h), int(m))
        except Exception:
            return None

    def _validar(self, form: dict) -> list:
        erros = []
        if not form.get("contratante", "").strip():
            erros.append("Nome do contratante é obrigatório.")
        if not form.get("passeio_id"):
            erros.append("Selecione um passeio.")
        if not form.get("tipo_passeio_id"):
            erros.append("Selecione o tipo de passeio.")
        if not form.get("valor_total"):
            erros.append("Informe o valor total.")
        else:
            try:
                v = float(form["valor_total"])
                if v <= 0:
                    erros.append("Valor total deve ser maior que zero.")
            except ValueError:
                erros.append("Valor total inválido.")
        if not form.get("data_saida"):
            erros.append("Informe a data de saída.")
        return erros
