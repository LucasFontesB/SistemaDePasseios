"""
Seed inicial do banco de dados.

Execução:
    python -m app.database.seed

Cria:
    - Usuário administrador padrão
    - Tipos de passeio padrão
"""

import uuid
from datetime import datetime

import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.base import Base
from app.models import Usuario, TipoPasseio, Passeio


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed(session: Session) -> None:
    agora = datetime.utcnow()

    # -------------------------------------------------------------------------
    # Usuário administrador padrão
    # -------------------------------------------------------------------------
    admin_existente = session.query(Usuario).filter_by(email="admin@hotel.com").first()
    if not admin_existente:
        admin = Usuario(
            id=uuid.uuid4(),
            nome="Administrador",
            email="admin@hotel.com",
            senha_hash=hash_senha("admin123"),
            perfil="ADMIN",
            criado_em=agora,
            atualizado_em=agora,
        )
        session.add(admin)
        print("✓ Usuário administrador criado  (email: admin@hotel.com / senha: admin123)")
    else:
        print("— Usuário administrador já existe, ignorando.")

    # -------------------------------------------------------------------------
    # Tipos de passeio padrão
    # -------------------------------------------------------------------------
    tipos_padrao = ["Compartilhado", "Privativo", "Catamarã", "Lancha"]
    for nome in tipos_padrao:
        existe = session.query(TipoPasseio).filter_by(nome=nome).first()
        if not existe:
            tipo = TipoPasseio(
                id=uuid.uuid4(),
                nome=nome,
                criado_em=agora,
                atualizado_em=agora,
            )
            session.add(tipo)
            print(f"✓ Tipo de passeio criado: {nome}")
        else:
            print(f"— Tipo de passeio já existe: {nome}")

    session.commit()
    print("\nSeed concluído.")


if __name__ == "__main__":
    engine = create_engine(settings.DATABASE_URL)
    with Session(engine) as session:
        seed(session)
