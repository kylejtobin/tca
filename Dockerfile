# The full image, not slim, for git: the commit gate's test runs it in the service.
FROM python:3.14.8@sha256:12d187a59ecdeb95df0a78cd6107a84398455365a66cc2183db2be42b6067d33

COPY --from=ghcr.io/astral-sh/uv:0.13.0@sha256:cdc6093146eb3ff6a40107b38f008b789e050e77ad87865e381d9917da55a168 /uv /uvx /bin/

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
COPY --chown=dev:dev packages/python/type-construction-registrar/pyproject.toml packages/python/type-construction-registrar/
RUN --mount=type=cache,target=/home/dev/.cache/uv,uid=${UID},gid=${GID} \
    uv sync --frozen --all-packages --no-install-workspace

COPY --chown=dev:dev . .
RUN --mount=type=cache,target=/home/dev/.cache/uv,uid=${UID},gid=${GID} \
    uv sync --frozen --all-packages
