"""Ponto de entrada da API."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.deps import DbSession
from app.core.exceptions import ErroAplicacao
from app.routers import auth, caixa, produtos, usuarios, vendas

app = FastAPI(
    title="PDV API",
    description="API de um sistema de ponto de venda para padaria/mercado.",
    version="0.4.0",
)


@app.exception_handler(ErroAplicacao)
def tratar_erro_aplicacao(_request: Request, erro: ErroAplicacao) -> JSONResponse:
    """Converte os erros lançados pelos services em respostas HTTP."""
    headers = {"WWW-Authenticate": "Bearer"} if erro.status_code == 401 else None
    return JSONResponse(
        status_code=erro.status_code, content={"detail": erro.mensagem}, headers=headers
    )


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(produtos.router)
app.include_router(caixa.router)
app.include_router(vendas.router)


@app.get("/health", tags=["Saúde"])
def health(db: DbSession) -> dict[str, str]:
    """Confirma que a API está no ar e que consegue falar com o banco."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "ok"}
