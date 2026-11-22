"""Funções de segurança: hash de senha (bcrypt).

A geração e validação de tokens JWT entra aqui na etapa 2.
"""

import bcrypt


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha. O salt é aleatório e fica embutido no hash."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha informada corresponde ao hash salvo no banco."""
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
