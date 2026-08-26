# =============================================================================
# Status de venda
# =============================================================================

STATUS_PENDENTE              = "PENDENTE"
STATUS_AGUARDANDO_PAGAMENTO  = "AGUARDANDO_PAGAMENTO"
STATUS_CONFIRMADO            = "CONFIRMADO"
STATUS_EMBARCADO             = "EMBARCADO"
STATUS_FINALIZADO            = "FINALIZADO"
STATUS_CANCELADO             = "CANCELADO"
STATUS_REEMBOLSADO           = "REEMBOLSADO"

STATUS_CHOICES = [
    STATUS_PENDENTE,
    STATUS_AGUARDANDO_PAGAMENTO,
    STATUS_CONFIRMADO,
    STATUS_EMBARCADO,
    STATUS_FINALIZADO,
    STATUS_CANCELADO,
    STATUS_REEMBOLSADO,
]

# Labels para exibição nas telas
STATUS_LABELS = {
    STATUS_PENDENTE:             "Pendente",
    STATUS_AGUARDANDO_PAGAMENTO: "Aguardando Pagamento",
    STATUS_CONFIRMADO:           "Confirmado",
    STATUS_EMBARCADO:            "Embarcado",
    STATUS_FINALIZADO:           "Finalizado",
    STATUS_CANCELADO:            "Cancelado",
    STATUS_REEMBOLSADO:          "Reembolsado",
}

# =============================================================================
# Perfis de usuário
# =============================================================================

PERFIL_ADMIN    = "ADMIN"
PERFIL_GERENCIA = "GERENCIA"
PERFIL_RECEPCAO = "RECEPCAO"

PERFIL_CHOICES = [PERFIL_ADMIN, PERFIL_GERENCIA, PERFIL_RECEPCAO]

PERFIL_LABELS = {
    PERFIL_ADMIN:    "Administrador",
    PERFIL_GERENCIA: "Gerência",
    PERFIL_RECEPCAO: "Recepção",
}

# =============================================================================
# Uploads
# =============================================================================

UPLOAD_ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

UPLOAD_ALLOWED_MIMETYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

UPLOAD_MAX_SIZE_MB = 10

# =============================================================================
# Formas de pagamento
# =============================================================================

FORMA_PAGAMENTO_DINHEIRO        = "DINHEIRO"
FORMA_PAGAMENTO_PIX             = "PIX"
FORMA_PAGAMENTO_DEBITO          = "CARTAO_DEBITO"
FORMA_PAGAMENTO_CREDITO         = "CARTAO_CREDITO"

FORMA_PAGAMENTO_CHOICES = [
    FORMA_PAGAMENTO_DINHEIRO,
    FORMA_PAGAMENTO_PIX,
    FORMA_PAGAMENTO_DEBITO,
    FORMA_PAGAMENTO_CREDITO,
]

FORMA_PAGAMENTO_LABELS = {
    FORMA_PAGAMENTO_DINHEIRO: "Dinheiro",
    FORMA_PAGAMENTO_PIX:      "PIX",
    FORMA_PAGAMENTO_DEBITO:   "Cartão de Débito",
    FORMA_PAGAMENTO_CREDITO:  "Cartão de Crédito",
}

# =============================================================================
# Status de grupo (Módulo de Grupos)
# =============================================================================

GRUPO_STATUS_PROSPECCAO        = "PROSPECCAO"
GRUPO_STATUS_ORCAMENTO_ENVIADO = "ORCAMENTO_ENVIADO"
GRUPO_STATUS_EM_NEGOCIACAO     = "EM_NEGOCIACAO"
GRUPO_STATUS_CONFIRMADO        = "CONFIRMADO"
GRUPO_STATUS_HOSPEDADO         = "HOSPEDADO"
GRUPO_STATUS_FINALIZADO        = "FINALIZADO"
GRUPO_STATUS_CANCELADO         = "CANCELADO"
GRUPO_STATUS_PERDIDO           = "PERDIDO"

GRUPO_STATUS_CHOICES = [
    GRUPO_STATUS_PROSPECCAO,
    GRUPO_STATUS_ORCAMENTO_ENVIADO,
    GRUPO_STATUS_EM_NEGOCIACAO,
    GRUPO_STATUS_CONFIRMADO,
    GRUPO_STATUS_HOSPEDADO,
    GRUPO_STATUS_FINALIZADO,
    GRUPO_STATUS_CANCELADO,
    GRUPO_STATUS_PERDIDO,
]

GRUPO_STATUS_LABELS = {
    GRUPO_STATUS_PROSPECCAO:        "Prospecção",
    GRUPO_STATUS_ORCAMENTO_ENVIADO: "Orçamento Enviado",
    GRUPO_STATUS_EM_NEGOCIACAO:     "Em Negociação",
    GRUPO_STATUS_CONFIRMADO:        "Confirmado",
    GRUPO_STATUS_HOSPEDADO:         "Hospedado",
    GRUPO_STATUS_FINALIZADO:        "Finalizado",
    GRUPO_STATUS_CANCELADO:         "Cancelado",
    GRUPO_STATUS_PERDIDO:           "Perdido",
}

# =============================================================================
# Status de orçamento de grupo (Módulo de Grupos)
# =============================================================================

ORCAMENTO_STATUS_RASCUNHO = "RASCUNHO"
ORCAMENTO_STATUS_ENVIADO  = "ENVIADO"
ORCAMENTO_STATUS_APROVADO = "APROVADO"
ORCAMENTO_STATUS_RECUSADO = "RECUSADO"

ORCAMENTO_STATUS_CHOICES = [
    ORCAMENTO_STATUS_RASCUNHO,
    ORCAMENTO_STATUS_ENVIADO,
    ORCAMENTO_STATUS_APROVADO,
    ORCAMENTO_STATUS_RECUSADO,
]

ORCAMENTO_STATUS_LABELS = {
    ORCAMENTO_STATUS_RASCUNHO: "Rascunho",
    ORCAMENTO_STATUS_ENVIADO:  "Enviado",
    ORCAMENTO_STATUS_APROVADO: "Aprovado",
    ORCAMENTO_STATUS_RECUSADO: "Recusado",
}

# =============================================================================
# Tipo de anexo de grupo (Módulo de Grupos)
# =============================================================================

ANEXO_TIPO_COMPROVANTE_PAGAMENTO = "COMPROVANTE_PAGAMENTO"
ANEXO_TIPO_ORCAMENTO_ASSINADO = "ORCAMENTO_ASSINADO"
ANEXO_TIPO_ROOMLIST = "ROOMLIST"
ANEXO_TIPO_OUTRO = "OUTRO"

ANEXO_TIPO_CHOICES = [
    ANEXO_TIPO_COMPROVANTE_PAGAMENTO,
    ANEXO_TIPO_ORCAMENTO_ASSINADO,
    ANEXO_TIPO_ROOMLIST,
    ANEXO_TIPO_OUTRO,
]

ANEXO_TIPO_LABELS = {
    ANEXO_TIPO_COMPROVANTE_PAGAMENTO: "Comprovante de Pagamento",
    ANEXO_TIPO_ORCAMENTO_ASSINADO:    "Orçamento Assinado",
    ANEXO_TIPO_ROOMLIST:              "Roomlist",
    ANEXO_TIPO_OUTRO:                 "Outro",
}