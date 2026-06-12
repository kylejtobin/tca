# TCA app container.
# Multi-stage build: base → builder → {prod, dev}.
# - base: minimal runtime; ca-certs + uv-managed Python preinstalled.
# - builder: adds build-essential + git, runs `uv sync` to materialize the venv.
# - prod: extends base (no build tools), copies the venv from builder, non-root.
# - dev: extends builder (build tools retained for runtime `uv add`), non-root.

ARG USER_UID=1000
ARG USER_GID=1000

# =============================================================================
# BASE — minimal runtime: ca-certs + uv binary + uv-managed Python
# =============================================================================
FROM debian:bookworm-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv python install 3.12

WORKDIR /app

# =============================================================================
# BUILDER — has build tools, materializes the venv
# =============================================================================
FROM base AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --no-install-project

# =============================================================================
# PROD — minimal runtime: no build tools, non-root, venv from builder
# =============================================================================
FROM base AS prod

ARG USER_UID
ARG USER_GID

RUN groupadd -g ${USER_GID} app \
 && useradd -m -u ${USER_UID} -g app -s /bin/bash app \
 && chown -R app:app /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app app /app/app

USER app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# DEV — extends builder, build tools retained for runtime `uv add`, non-root
# =============================================================================
FROM builder AS dev

ARG USER_UID
ARG USER_GID

RUN groupadd -g ${USER_GID} app \
 && useradd -m -u ${USER_UID} -g app -s /bin/bash app \
 && chown -R app:app /app /opt/uv-python

USER app
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
