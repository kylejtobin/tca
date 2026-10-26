set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

export UID := `id -u`
export GID := `id -g`

dev := "docker compose run --rm dev"

# List the recipes.
default:
    @just --list

# Build the development image with the locked dependencies. Runs docker compose on the host.
build:
    docker compose build

# Resolve the declared dependencies into the lockfile. Runs in the development container.
lock:
    {{dev}} uv lock

# Open a shell in the development container.
shell:
    {{dev}} bash

packages := "packages/python"

# The gate: every check the commit hook and CI run, and nothing they do not. It runs `uv run`
# in the current environment: the host, CI, or a `just shell`.
check:
    python scripts/check_test_standards.py
    uv run ruff check {{packages}}
    uv run ruff format --check {{packages}}
    uv run basedpyright {{packages}}
    uv run bandit -c pyproject.toml -q -r {{packages}}
    uv run --all-packages pytest -q

# The supply chain: the lockfile, known vulnerabilities, code patterns, pinned images. It runs
# `uv run` in the current environment, like check. semgrep runs from its own locked group in an
# isolated environment, so its pins never share an environment with the dev group.
audit:
    uv lock --check
    uv run pip-audit
    uv run --isolated --only-group audit semgrep scan --config p/python --config p/secrets --error --quiet -j 1 {{packages}}
    ! grep -hE "^FROM |^COPY --from=|image: " Dockerfile compose.yaml | grep -vE "@sha256:[0-9a-f]{64}"
