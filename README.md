# PDV — Sistema de Caixa para Padaria/Mercado

Sistema de ponto de venda (PDV) com controle de caixa, vendas, estoque e relatórios.

> 🚧 Em desenvolvimento. Este README será completado ao final do projeto.

## Tecnologias

- **Backend:** Python, FastAPI, SQLAlchemy 2, PostgreSQL, Alembic, JWT, bcrypt, pytest
- **Frontend:** React 19, Vite, React Router, Axios

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

## Como rodar o frontend

Pré-requisito: Node.js 20+. Com a API rodando em outro terminal:

```cmd
cd frontend
npm install
npm run dev
```

Acesse http://localhost:5173. Se a API estiver em outro endereço, copie
`frontend/.env.example` para `frontend/.env` e ajuste `VITE_API_URL`.

Testes de unidade (Vitest) e linter (ESLint) do frontend:

```cmd
npm test
npm run lint
```

## Tela de caixa

O campo de código fica sempre com o foco, para funcionar com leitor de código de barras
(que "digita" o código e aperta Enter).

| Tecla / entrada   | Ação                                                  |
|-------------------|-------------------------------------------------------|
| `código` + Enter  | Adiciona 1 unidade do produto                         |
| `5*código`        | Adiciona 5 unidades                                   |
| `nome` + Enter    | Busca por nome (se houver vários, mostra uma lista)   |
| **F2**            | Abre o pagamento / confirma a venda                   |
| **F4**            | Remove o último item                                  |
| **Esc**           | Cancela a venda em andamento (pede confirmação)       |

## Área administrativa

- **Produtos:** cadastro, edição, busca, desativação e reativação; destaque para estoque baixo.
- **Vendas:** histórico com filtro por período e status, detalhes de cada venda e cancelamento
  (devolve os itens ao estoque; bloqueado para vendas de caixa já fechado).
- **Relatórios:** total vendido, quantidade de vendas, ticket médio, canceladas, gráfico de
  vendas por dia (com visão em tabela), recebido por forma de pagamento e produtos mais vendidos.

As telas de admin são carregadas sob demanda (`React.lazy`): o operador de caixa não baixa o
código delas nem a biblioteca de gráficos.

No pagamento é possível combinar formas (ex.: parte no crédito, parte em dinheiro); o troco
é calculado na hora e só existe em dinheiro. O fechamento do caixa é feito "às cegas": o
operador informa o dinheiro contado antes de ver o valor esperado pelo sistema.

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
