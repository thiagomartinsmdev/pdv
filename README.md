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

## Usuários de teste

| Perfil   | E-mail           | Senha       |
|----------|------------------|-------------|
| admin    | admin@pdv.com    | admin123    |
| operador | operador@pdv.com | operador123 |
