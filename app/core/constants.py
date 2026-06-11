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
