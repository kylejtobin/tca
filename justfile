set shell := ["bash", "-euo", "pipefail", "-c"]
set positional-arguments

export UID := `id -u`
export GID := `id -g`

dev := "docker compose run --rm dev"

# The NATS integration is an installation extra of the workspace package; every environment
# selects it explicitly. uv resolves extras for all workspace members only with --all-packages.
extras := "--all-packages --extra nats"

# Generated development material lives outside the repository tree so the application
# container's workspace mount cannot reach the provisioning partition. Compose reads the same
# variable.
secrets := env("TCA_SECRETS", home_directory() / ".local/state/tca/secrets")

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

# Generate the secured NATS development material under TCA_SECRETS, partitioned by consumer
# (application, server, provisioning). Existing complete material is preserved; incomplete
# material fails without changes. Runs openssl and the pinned nats-box on the host.
secrets:
    uv run python -I scripts/generate_nats_material.py "{{secrets}}"

# Reset the development identities: remove the Compose project's containers and its JetStream
# volume, then generate new material. The volume goes with the material because data persisted
# under the previous account cannot be reached by the new identities.
reset:
    docker compose down --volumes
    uv run python -I scripts/generate_nats_material.py "{{secrets}}" --replace

packages := "packages/python"

# The gate: every check the commit hook and CI run, and nothing they do not. It runs `uv run`
# in the current environment: the host, CI, or a `just shell`.
check:
    python scripts/check_test_standards.py
    uv run {{extras}} ruff check {{packages}}
    uv run {{extras}} ruff format --check {{packages}}
    uv run {{extras}} basedpyright {{packages}}
    uv run {{extras}} bandit -c pyproject.toml -q -r {{packages}}
    uv run {{extras}} pytest -q

# The supply chain: the lockfile, known vulnerabilities, code patterns, pinned images. It runs
# `uv run` in the current environment, like check. semgrep runs from its own locked group in an
# isolated environment, so its pins never share an environment with the dev group.
audit:
    uv lock --check
    uv run {{extras}} pip-audit
    uv run --isolated --only-group audit semgrep scan --config p/python --config p/secrets --error --quiet -j 1 {{packages}}
    ! grep -hE "^FROM |^COPY --from=|image: " Dockerfile compose.yaml | grep -vE "@sha256:[0-9a-f]{64}"
