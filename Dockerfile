# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY service ./service
COPY schemas ./schemas
COPY repository ./repository
COPY utils ./utils
COPY logger ./logger
COPY main.py init.py ./

RUN uv sync --no-dev --extra speedups \
    && uv run init.py


FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/app /app/app
COPY --from=builder --chown=appuser:appuser /app/service /app/service
COPY --from=builder --chown=appuser:appuser /app/schemas /app/schemas
COPY --from=builder --chown=appuser:appuser /app/repository /app/repository
COPY --from=builder --chown=appuser:appuser /app/utils /app/utils
COPY --from=builder --chown=appuser:appuser /app/logger /app/logger
COPY --from=builder --chown=appuser:appuser /app/main.py /app/main.py

USER appuser

VOLUME ["/app/data"]

CMD ["python", "main.py"]
