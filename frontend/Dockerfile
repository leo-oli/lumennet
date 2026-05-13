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
COPY samples/ ./samples/

EXPOSE ${FRONTEND_PORT:-7860}

ENV GRADIO_SERVER_NAME="0.0.0.0" \
    GRADIO_SERVER_PORT=${FRONTEND_PORT:-7860}

CMD ["uv", "run", "python", "src/app.py"]
