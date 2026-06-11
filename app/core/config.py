from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Banco de dados
    DATABASE_URL: str

    # Segurança
    SECRET_KEY: str

    # Sessão
    SESSION_MAX_AGE: int = 28800  # 8 horas em segundos

    # Uploads
    UPLOAD_PATH: str = "uploads"
    UPLOAD_MAX_SIZE_MB: int = 10
    UPLOAD_ALLOWED_EXTENSIONS: list[str] = ["pdf", "jpg", "jpeg", "png"]
    UPLOAD_ALLOWED_MIMETYPES: list[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
    ]

    # Ambiente
    APP_ENV: str = "development"

    # Servidor
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def upload_max_size_bytes(self) -> int:
        return self.UPLOAD_MAX_SIZE_MB * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()