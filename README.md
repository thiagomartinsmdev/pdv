# PDV — Sistema de Caixa para Padaria/Mercado

Sistema de ponto de venda (PDV) com controle de caixa, vendas, estoque e relatórios.

> 🚧 Em desenvolvimento. Este README será completado ao final do projeto.

## Tecnologias

- **Backend:** Python, FastAPI, SQLAlchemy 2, PostgreSQL, Alembic
- **Frontend:** React + Vite (em breve)

## Como rodar o backend (sem Docker)

Pré-requisitos: Python 3.12+ e PostgreSQL com um banco chamado `pdv`.

```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edite o `.env` com o usuário e a senha do seu PostgreSQL e gere uma chave para o JWT:

```cmd
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cole o resultado em `JWT_SECRET_KEY` no `.env`. Depois:

```cmd
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

A documentação interativa da API fica em http://localhost:8000/docs. Para testar rotas
protegidas, faça `POST /auth/login`, copie o `access_token` e cole no botão **Authorize**.

## Autenticação e perfis

- Login com e-mail e senha devolve um token JWT (validade padrão: 8 horas).
- O token é enviado no cabeçalho `Authorization: Bearer <token>`.
- Perfis: **admin** (acesso total) e **operador** (opera o caixa).
- O perfil e o status ativo são lidos do banco a cada requisição, então desativar um
  usuário bloqueia o acesso na hora, mesmo que o token ainda não tenha expirado.

## Testes

Os testes usam um banco PostgreSQL separado, `pdv_test` (crie-o vazio no pgAdmin). Ele é
apagado e recriado a cada execução, então nunca aponte os testes para o banco principal.
Por segurança, o `conftest.py` se recusa a rodar se o nome do banco não terminar em `_test`.

```cmd
cd backend
pip install -r requirements-dev.txt
pytest -v
```

Por padrão os testes usam o mesmo servidor e senha do `DATABASE_URL`, trocando o banco por
`pdv_test`. Para usar outro banco, defina `TEST_DATABASE_URL` no `.env`.

Os testes rodam em PostgreSQL (e não em SQLite) porque as regras testadas dependem dele:
`SELECT ... FOR UPDATE`, índice único parcial e CHECK constraints.

## Usuários de teste

| Perfil   | E-mail           | Senha       |
|----------|------------------|-------------|
| admin    | admin@pdv.com    | admin123    |
| operador | operador@pdv.com | operador123 |
