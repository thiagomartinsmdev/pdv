"""Ponto de entrada da API."""

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

app = FastAPI(
    title="PDV API",
    description="API de um sistema de ponto de venda para padaria/mercado.",
    version="0.1.0",
)


@app.get("/health", tags=["Saúde"])
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    """Confirma que a API está no ar e que consegue falar com o banco."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "ok"}
