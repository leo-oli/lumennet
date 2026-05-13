FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

COPY src/ ./src/
COPY models/ ./models/

EXPOSE ${BACKEND_PORT:-8000}

CMD uv run uvicorn src.api:app --host 0.0.0.0 --port ${BACKEND_PORT:-8000}
