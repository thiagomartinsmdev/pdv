# Imagem do backend (API FastAPI).
# Mesma versão do Python usada no desenvolvimento.
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE: não cria arquivos .pyc dentro do container.
# PYTHONUNBUFFERED: os logs aparecem na hora no "docker compose logs".
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# As dependências são copiadas e instaladas ANTES do código: assim o Docker
# reaproveita esta camada (cache) quando só o código muda, e o build fica rápido.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Roda como usuário comum, e não como root: se a aplicação for comprometida,
# o invasor não tem poderes de administrador dentro do container.
RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 8000

# O Docker considera o container saudável quando a rota /health (API + banco) responde.
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

# Ao subir: aplica as migrations pendentes e inicia a API.
# "exec" faz o uvicorn substituir o shell e receber os sinais de parada do Docker.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
