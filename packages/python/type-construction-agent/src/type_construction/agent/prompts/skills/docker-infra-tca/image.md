---
type: Construct
description: "The environment the code is built and checked in, layered from the base out, with the locked dependencies installed before the code. Holds the base, the system packages, the user, the dependencies and the code. Lives in Dockerfile."
---

```dockerfile
# Dockerfile
FROM python:slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update \
    && apt-get install --yes --no-install-recommends ripgrep \
    && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
RUN groupadd --gid "${GID}" dev \
    && useradd --uid "${UID}" --gid "${GID}" --create-home dev \
    && install --directory --owner dev --group dev /opt/venv /workspace

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

USER dev
WORKDIR /workspace

COPY --chown=dev:dev pyproject.toml uv.lock README.md ./
COPY --chown=dev:dev packages/python/type-construction-agent/pyproject.toml packages/python/type-construction-agent/
COPY --chown=dev:dev packages/python/type-construction-eval/pyproject.toml packages/python/type-construction-eval/
RUN --mount=type=cache,target=/home/dev/.cache/uv,uid=${UID},gid=${GID} \
    uv sync --frozen --all-packages --no-install-workspace

COPY --chown=dev:dev . .
RUN --mount=type=cache,target=/home/dev/.cache/uv,uid=${UID},gid=${GID} \
    uv sync --frozen --all-packages
```
