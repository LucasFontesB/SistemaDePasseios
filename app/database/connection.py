import os
os.environ["PGSYSCONFDIR"] = ""
os.environ["PGPASSFILE"] = ""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # reconecta automaticamente se a conexão cair
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency para injetar sessão do banco nas rotas do FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()