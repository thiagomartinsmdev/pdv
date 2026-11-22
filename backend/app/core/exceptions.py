"""Erros da aplicação.

Os services lançam estas exceções (e não HTTPException), para que as regras de
negócio não dependam do FastAPI. Um handler em main.py as converte em respostas
HTTP com o formato padrão {"detail": "mensagem"}.
"""


class ErroAplicacao(Exception):
    status_code = 400

    def __init__(self, mensagem: str) -> None:
        super().__init__(mensagem)
        self.mensagem = mensagem


class NaoAutenticado(ErroAplicacao):
    """Credenciais ausentes, inválidas ou token expirado."""

    status_code = 401


class AcessoNegado(ErroAplicacao):
    """Usuário autenticado, mas sem permissão para a ação."""

    status_code = 403


class NaoEncontrado(ErroAplicacao):
    status_code = 404


class Conflito(ErroAplicacao):
    """A ação conflita com o estado atual (ex.: e-mail já cadastrado)."""

    status_code = 409


class RegraNegocio(ErroAplicacao):
    """A requisição é válida, mas uma regra de negócio impede a ação."""

    status_code = 422
