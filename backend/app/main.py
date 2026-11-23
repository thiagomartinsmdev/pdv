"""Ponto de entrada da API."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from starlette.types import Receive, Scope, Send

from app.core.config import settings
from app.core.deps import DbSession
from app.core.exceptions import ErroAplicacao
from app.routers import auth, caixa, categorias, produtos, relatorios, usuarios, vendas
from app.services.imagem_service import pasta_produtos

app = FastAPI(
    title="PDV API",
    description="API de um sistema de ponto de venda para padaria/mercado.",
    version="0.8.0",
)

# Permite que o frontend (outra porta = outra "origem") chame a API pelo navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origens,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
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
app.include_router(categorias.router)
app.include_router(produtos.router)
app.include_router(caixa.router)
app.include_router(vendas.router)
app.include_router(relatorios.router)


class ImagensEstaticas(StaticFiles):
    """Arquivos estáticos com o cabeçalho "nosniff": o navegador usa o tipo informado
    (image/jpeg etc.) e não tenta adivinhar outro a partir do conteúdo."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def enviar(mensagem: dict) -> None:
            if mensagem["type"] == "http.response.start":
                mensagem.setdefault("headers", []).append((b"x-content-type-options", b"nosniff"))
            await send(mensagem)

        await super().__call__(scope, receive, enviar)


# Só a subpasta das fotos é pública. Outros arquivos em uploads/ (ex.: relatórios dos
# scripts) não ficam acessíveis pela web.
app.mount("/uploads/produtos", ImagensEstaticas(directory=pasta_produtos()), name="fotos")


@app.get("/health", tags=["Saúde"])
def health(db: DbSession) -> dict[str, str]:
    """Confirma que a API está no ar e que consegue falar com o banco."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "banco": "ok"}
