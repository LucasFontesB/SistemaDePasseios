from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response, FileResponse
from sqlalchemy.orm import Session
import os

from app.core.security import get_current_user
from app.core.templates import templates
from app.core.flash import set_flash
from app.database.connection import get_db
from app.repositories.user_repository import UserRepository
from app.services.grupo_service import GrupoService
from app.services.orcamento_service import OrcamentoService
from app.services.grupo_pagamento_service import GrupoPagamentoService
from app.services.grupo_roomlist_service import GrupoRoomlistService
from app.services.grupo_anexo_service import GrupoAnexoService
from app.services.grupo_comentario_service import GrupoComentarioService
from app.services.grupo_atividade_service import GrupoAtividadeService
from app.repositories.tipo_apartamento_repository import TipoApartamentoRepository
from app.utils.pdf_orcamento import gerar_pdf_orcamento
from app.utils.pdf_roomlist import gerar_pdf_roomlist
from app.utils.excel_roomlist import gerar_excel_roomlist
from app.core.constants import (
    GRUPO_STATUS_CHOICES, ORCAMENTO_STATUS_CHOICES, FORMA_PAGAMENTO_CHOICES, ANEXO_TIPO_CHOICES,
)

router = APIRouter()

TABS_DISPONIVEIS = {"dados", "orcamentos", "pagamentos", "roomlist", "anexos", "atividade"}
TABS_ATIVAS = TABS_DISPONIVEIS  # todas as abas ativas a partir da Fase 6


def _get_session(request: Request):
    try:
        return get_current_user(request)
    except Exception:
        return None


def _tem_acesso(session: dict) -> bool:
    """Módulo de grupos é liberado para ADMIN, GERENCIA e RECEPCAO (RN-G010 é exceção pontual)."""
    return session is not None and session.get("perfil") in ("ADMIN", "GERENCIA", "RECEPCAO")


# =============================================================================
# Listagem
# =============================================================================

@router.get("/grupos", response_class=HTMLResponse)
async def grupos_list(
    request: Request,
    db: Session = Depends(get_db),
    nome: str = None,
    status: str = None,
    data_inicial: str = None,
    data_final: str = None,
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    service = GrupoService(db)

    grupos = service.list(
        nome=nome,
        status=status,
        data_inicial=date.fromisoformat(data_inicial) if data_inicial else None,
        data_final=date.fromisoformat(data_final) if data_final else None,
    )
    form_data = service.get_form_data()

    return templates.TemplateResponse("grupos/listagem.html", {
        "request": request,
        "usuario": usuario,
        "active": "grupos",
        "grupos": grupos,
        "status_choices": form_data["status_choices"],
        "filtros": {
            "nome": nome or "",
            "status": status or "",
            "data_inicial": data_inicial or "",
            "data_final": data_final or "",
        },
    })


# =============================================================================
# Novo grupo
# =============================================================================

@router.get("/grupos/novo", response_class=HTMLResponse)
async def grupo_novo(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form_data = GrupoService(db).get_form_data()

    return templates.TemplateResponse("grupos/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "grupos",
        "grupo": None,
        "erros": [],
        **form_data,
    })


@router.post("/grupos", response_class=HTMLResponse)
async def grupo_create(request: Request, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = GrupoService(db)
    grupo, erros = service.create(form, uuid.UUID(session["user_id"]))

    if erros:
        form_data = service.get_form_data()
        return templates.TemplateResponse("grupos/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "grupos",
            "grupo": None,
            "erros": erros,
            "form_values": form,
            **form_data,
        })

    response = RedirectResponse(url=f"/grupos/{grupo.id}?tab=dados", status_code=302)
    set_flash(response, "Grupo cadastrado com sucesso!")
    return response


# =============================================================================
# Detalhes (abas)
# =============================================================================

@router.get("/grupos/{grupo_id}", response_class=HTMLResponse)
async def grupo_detalhes(request: Request, grupo_id: str, db: Session = Depends(get_db), tab: str = "dados"):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    if tab not in TABS_DISPONIVEIS:
        tab = "dados"

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    grupo = GrupoService(db).get_by_id(uuid.UUID(grupo_id))

    if not grupo:
        return RedirectResponse(url="/grupos")

    contexto = {
        "request": request,
        "usuario": usuario,
        "active": "grupos",
        "grupo": grupo,
        "tab": tab,
        "tabs_ativas": TABS_ATIVAS,
        "status_choices": GRUPO_STATUS_CHOICES,
    }

    if tab == "dados":
        grupo_service = GrupoService(db)
        contexto["apartamentos"] = grupo_service.list_apartamentos(grupo.id)
        contexto["tipos_apartamento"] = TipoApartamentoRepository(db).list_active()
        roomlist = GrupoRoomlistService(db).list_by_grupo(grupo.id)
        tem_roomlist_vazia = any(item.hospede_nome is None for item in roomlist)
        contexto["alertas"] = grupo_service.get_alertas(grupo, tem_roomlist_vazia)

    if tab == "orcamentos":
        contexto["orcamentos"] = OrcamentoService(db).list_by_grupo(grupo.id)
        contexto["orcamento_status_choices"] = ORCAMENTO_STATUS_CHOICES

    if tab == "pagamentos":
        contexto["pagamentos"] = GrupoPagamentoService(db).list_by_grupo(grupo.id)
        contexto["forma_pagamento_choices"] = FORMA_PAGAMENTO_CHOICES
        contexto["hoje"] = date.today().isoformat()

    if tab == "roomlist":
        contexto["roomlist"] = GrupoRoomlistService(db).list_by_grupo(grupo.id)
        contexto["tipos_apartamento"] = TipoApartamentoRepository(db).list_active()
        contexto["anexos_roomlist"] = GrupoAnexoService(db).list_by_grupo(grupo.id, tipo="ROOMLIST")

    if tab == "anexos":
        contexto["anexos"] = GrupoAnexoService(db).list_by_grupo(grupo.id)
        contexto["anexo_tipo_choices"] = ANEXO_TIPO_CHOICES

    if tab == "atividade":
        apenas_comentarios = request.query_params.get("filtro") == "comentarios"
        contexto["timeline"] = GrupoAtividadeService(db).list_timeline(grupo.id, apenas_comentarios)
        contexto["apenas_comentarios"] = apenas_comentarios

    return templates.TemplateResponse("grupos/detalhes.html", contexto)


# =============================================================================
# Editar grupo
# =============================================================================

@router.get("/grupos/{grupo_id}/editar", response_class=HTMLResponse)
async def grupo_editar(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    service = GrupoService(db)
    grupo = service.get_by_id(uuid.UUID(grupo_id))

    if not grupo:
        return RedirectResponse(url="/grupos")

    form_data = service.get_form_data()
    return templates.TemplateResponse("grupos/form.html", {
        "request": request,
        "usuario": usuario,
        "active": "grupos",
        "grupo": grupo,
        "erros": [],
        **form_data,
    })


@router.post("/grupos/{grupo_id}/editar", response_class=HTMLResponse)
async def grupo_update(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    usuario = UserRepository(db).find_by_id(uuid.UUID(session["user_id"]))
    form = dict(await request.form())
    service = GrupoService(db)
    grupo, erros = service.update(uuid.UUID(grupo_id), form, uuid.UUID(session["user_id"]))

    if erros:
        form_data = service.get_form_data()
        grupo_atual = service.get_by_id(uuid.UUID(grupo_id))
        return templates.TemplateResponse("grupos/form.html", {
            "request": request,
            "usuario": usuario,
            "active": "grupos",
            "grupo": grupo_atual,
            "erros": erros,
            "form_values": form,
            **form_data,
        })

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    set_flash(response, "Grupo atualizado com sucesso!")
    return response


# =============================================================================
# Alterar status
# =============================================================================

@router.post("/grupos/{grupo_id}/status", response_class=HTMLResponse)
async def grupo_status(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    status = form.get("status", "")
    grupo, erros = GrupoService(db).update_status(
        uuid.UUID(grupo_id), status, session.get("perfil"), uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Status atualizado com sucesso!")
    return response


# =============================================================================
# Recalcular totais (volta ao cálculo automático)
# =============================================================================

@router.post("/grupos/{grupo_id}/recalcular-net")
async def grupo_recalcular_net(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    GrupoService(db).recalcular_net(uuid.UUID(grupo_id), uuid.UUID(session["user_id"]))
    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    set_flash(response, "Valor total net recalculado.")
    return response


@router.post("/grupos/{grupo_id}/recalcular-sistema")
async def grupo_recalcular_sistema(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    GrupoService(db).recalcular_sistema(uuid.UUID(grupo_id), uuid.UUID(session["user_id"]))
    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    set_flash(response, "Valor total sistema recalculado.")
    return response


# =============================================================================
# Valor total manual (RN-G020: flags atuam sobre o agregado)
# =============================================================================

@router.post("/grupos/{grupo_id}/valor-total-net/manual")
async def grupo_valor_total_net_manual(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoService(db).definir_valor_manual(
        uuid.UUID(grupo_id), "net", form.get("valor"), uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Valor total net definido manualmente.")
    return response


@router.post("/grupos/{grupo_id}/valor-total-sistema/manual")
async def grupo_valor_total_sistema_manual(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoService(db).definir_valor_manual(
        uuid.UUID(grupo_id), "sistema", form.get("valor"), uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Valor total sistema definido manualmente.")
    return response


# =============================================================================
# Composição de tarifa por tipo de apartamento (RN-G019/RN-G020)
# =============================================================================

@router.post("/grupos/{grupo_id}/apartamentos")
async def grupo_apartamento_create(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoService(db).adicionar_apartamento(uuid.UUID(grupo_id), form, uuid.UUID(session["user_id"]))

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Tipo de apartamento adicionado à composição.")
    return response


@router.post("/grupos/{grupo_id}/apartamentos/{item_id}/editar")
async def grupo_apartamento_update(request: Request, grupo_id: str, item_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoService(db).atualizar_apartamento(
        uuid.UUID(grupo_id), uuid.UUID(item_id), form, uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Composição atualizada.")
    return response


@router.post("/grupos/{grupo_id}/apartamentos/{item_id}/remover")
async def grupo_apartamento_remover(request: Request, grupo_id: str, item_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    _, erros = GrupoService(db).remover_apartamento(uuid.UUID(grupo_id), uuid.UUID(item_id), uuid.UUID(session["user_id"]))
    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=dados", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Tipo de apartamento removido da composição.", "warning")
    return response


# =============================================================================
# Orçamentos
# =============================================================================

@router.post("/grupos/{grupo_id}/orcamentos")
async def orcamento_gerar(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    orcamento, erros = OrcamentoService(db).gerar_nova_versao(
        uuid.UUID(grupo_id), uuid.UUID(session["user_id"]), form
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=orcamentos", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, f"Orçamento versão {orcamento.versao} gerado com sucesso!")
    return response


@router.post("/grupos/{grupo_id}/orcamentos/{orcamento_id}/enviar")
async def orcamento_enviar(request: Request, grupo_id: str, orcamento_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    _, erros = OrcamentoService(db).marcar_enviado(uuid.UUID(orcamento_id), uuid.UUID(session["user_id"]))

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=orcamentos", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Orçamento marcado como enviado.")
    return response


@router.post("/grupos/{grupo_id}/orcamentos/{orcamento_id}/aprovar")
async def orcamento_aprovar(request: Request, grupo_id: str, orcamento_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    _, erros = OrcamentoService(db).aprovar(uuid.UUID(orcamento_id), uuid.UUID(session["user_id"]))

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=orcamentos", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Orçamento aprovado! Os valores foram copiados para o grupo - considere atualizar o status do grupo para Confirmado.")
    return response


@router.post("/grupos/{grupo_id}/orcamentos/{orcamento_id}/recusar")
async def orcamento_recusar(request: Request, grupo_id: str, orcamento_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    _, erros = OrcamentoService(db).recusar(uuid.UUID(orcamento_id), uuid.UUID(session["user_id"]))

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=orcamentos", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Orçamento recusado.")
    return response


@router.get("/grupos/{grupo_id}/orcamentos/{orcamento_id}/pdf")
async def orcamento_pdf(request: Request, grupo_id: str, orcamento_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    orcamento = OrcamentoService(db).get_by_id(uuid.UUID(orcamento_id))
    if not orcamento or str(orcamento.grupo_id) != grupo_id:
        return RedirectResponse(url=f"/grupos/{grupo_id}?tab=orcamentos")

    pdf_bytes = gerar_pdf_orcamento(orcamento)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="orcamento_{orcamento.grupo.codigo}_v{orcamento.versao}.pdf"'},
    )


# =============================================================================
# Pagamentos
# =============================================================================

@router.post("/grupos/{grupo_id}/pagamentos")
async def pagamento_registrar(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoPagamentoService(db).registrar(
        uuid.UUID(grupo_id), form, uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=pagamentos", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Pagamento registrado com sucesso!")
    return response


# =============================================================================
# Roomlist
# =============================================================================

@router.post("/grupos/{grupo_id}/roomlist")
async def roomlist_create(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoRoomlistService(db).create(uuid.UUID(grupo_id), form, uuid.UUID(session["user_id"]))

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=roomlist", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Hóspede adicionado à roomlist.")
    return response


@router.post("/grupos/{grupo_id}/roomlist/{item_id}/editar")
async def roomlist_update(request: Request, grupo_id: str, item_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoRoomlistService(db).update(
        uuid.UUID(grupo_id), uuid.UUID(item_id), form, uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=roomlist", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Roomlist atualizada.")
    return response


@router.post("/grupos/{grupo_id}/roomlist/{item_id}/remover")
async def roomlist_remover(request: Request, grupo_id: str, item_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    GrupoRoomlistService(db).remover(uuid.UUID(grupo_id), uuid.UUID(item_id), uuid.UUID(session["user_id"]))
    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=roomlist", status_code=302)
    set_flash(response, "Registro removido da roomlist.", "warning")
    return response


@router.get("/grupos/{grupo_id}/roomlist/pdf")
async def roomlist_pdf(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    service = GrupoRoomlistService(db)
    grupo = GrupoService(db).get_by_id(uuid.UUID(grupo_id))
    if not grupo:
        return RedirectResponse(url="/grupos")

    roomlist = service.list_by_grupo(grupo.id)
    roomlist_agrupada = service.agrupar_por_tipo(roomlist)
    pdf_bytes = gerar_pdf_roomlist(grupo, roomlist_agrupada)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="roomlist_{grupo.codigo}.pdf"'},
    )


@router.get("/grupos/{grupo_id}/roomlist/excel")
async def roomlist_excel(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    service = GrupoRoomlistService(db)
    grupo = GrupoService(db).get_by_id(uuid.UUID(grupo_id))
    if not grupo:
        return RedirectResponse(url="/grupos")

    roomlist = service.list_by_grupo(grupo.id)
    roomlist_agrupada = service.agrupar_por_tipo(roomlist)
    excel_bytes = gerar_excel_roomlist(grupo, roomlist_agrupada)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="roomlist_{grupo.codigo}.xlsx"'},
    )


# =============================================================================
# Anexos
# =============================================================================

@router.post("/grupos/{grupo_id}/anexos", response_class=HTMLResponse)
async def anexo_upload(
    request: Request,
    grupo_id: str,
    db: Session = Depends(get_db),
    tipo: str = Form("OUTRO"),
    arquivo: UploadFile = File(...),
):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    _, erros = await GrupoAnexoService(db).upload(
        uuid.UUID(grupo_id), tipo, arquivo, uuid.UUID(session["user_id"])
    )

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=anexos", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Anexo enviado com sucesso!")
    return response


@router.get("/grupos/{grupo_id}/anexos/{anexo_id}")
async def anexo_download(request: Request, grupo_id: str, anexo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    anexo = GrupoAnexoService(db).get_by_id(uuid.UUID(anexo_id))
    if not anexo or str(anexo.grupo_id) != grupo_id or not os.path.exists(anexo.caminho):
        return RedirectResponse(url=f"/grupos/{grupo_id}?tab=anexos")

    return FileResponse(
        path=anexo.caminho,
        filename=anexo.nome_original,
        media_type=_media_type(anexo.tipo_arquivo),
    )


@router.post("/grupos/{grupo_id}/anexos/{anexo_id}/remover")
async def anexo_remover(request: Request, grupo_id: str, anexo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    GrupoAnexoService(db).remover(uuid.UUID(grupo_id), uuid.UUID(anexo_id), uuid.UUID(session["user_id"]))
    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=anexos", status_code=302)
    set_flash(response, "Anexo removido.", "warning")
    return response


def _media_type(extensao: str | None) -> str:
    return {
        "pdf":  "application/pdf",
        "jpg":  "image/jpeg",
        "jpeg": "image/jpeg",
        "png":  "image/png",
    }.get((extensao or "").lower(), "application/octet-stream")


# =============================================================================
# Comentários (Atividade)
# =============================================================================

@router.post("/grupos/{grupo_id}/comentarios")
async def comentario_registrar(request: Request, grupo_id: str, db: Session = Depends(get_db)):
    session = _get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if not _tem_acesso(session):
        return RedirectResponse(url="/dashboard")

    form = dict(await request.form())
    _, erros = GrupoComentarioService(db).registrar(uuid.UUID(grupo_id), form, uuid.UUID(session["user_id"]))

    response = RedirectResponse(url=f"/grupos/{grupo_id}?tab=atividade", status_code=302)
    if erros:
        set_flash(response, "; ".join(erros), "danger")
        return response

    set_flash(response, "Comentário adicionado.")
    return response
