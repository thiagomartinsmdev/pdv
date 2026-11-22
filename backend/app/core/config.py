"""Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Pasta "backend/". Usamos um caminho absoluto para que o .env seja encontrado
# independentemente da pasta de onde o comando foi executado.
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str


settings = Settings()
