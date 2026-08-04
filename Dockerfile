FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml README.md ./
COPY app ./app
COPY service ./service
COPY schemas ./schemas
COPY utils ./utils
COPY logger ./logger
COPY main.py init.py ./

RUN uv sync --no-dev --no-install-project \
    && uv run init.py \
    && uv sync --no-dev --extra speedups

RUN mkdir -p /app/data

VOLUME ["/app/data"]

CMD ["uv", "run", "python", "main.py"]
