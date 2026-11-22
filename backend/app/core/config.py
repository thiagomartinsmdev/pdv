"""Configurações da aplicação, lidas de variáveis de ambiente ou do arquivo .env."""

from pathlib import Path

from pydantic import Field
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

    # Sem valor padrão de propósito: a aplicação não sobe sem uma chave configurada.
    jwt_secret_key: str = Field(min_length=32)
    jwt_algoritmo: str = "HS256"
    jwt_expira_minutos: int = Field(default=480, gt=0)

    # Fuso usado para interpretar filtros por data (ex.: "vendas do dia 05/11").
    fuso_horario: str = "America/Sao_Paulo"

    # Endereços do frontend autorizados a chamar a API pelo navegador (CORS).
    # No .env, use JSON: CORS_ORIGENS=["http://localhost:5173"]
    cors_origens: list[str] = ["http://localhost:5173"]


settings = Settings()
