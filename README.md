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

Edite o `.env` com o usuário e a senha do seu PostgreSQL. Depois:

```cmd
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

A documentação interativa da API fica em http://localhost:8000/docs.

## Usuários de teste

| Perfil   | E-mail           | Senha       |
|----------|------------------|-------------|
| admin    | admin@pdv.com    | admin123    |
| operador | operador@pdv.com | operador123 |
