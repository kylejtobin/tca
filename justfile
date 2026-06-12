# TCA — operational commands for the stack.
# `just` (no args) lists recipes. Most recipes take an env (prod | dev),
# defaulting to both.

set shell := ["bash", "-c"]

# ----------------------------------------------------------------------------
# Discovery
# ----------------------------------------------------------------------------

default:
    @just --list --unsorted

# ----------------------------------------------------------------------------
# Private helpers
# ----------------------------------------------------------------------------

_compose env *args:
    scripts/compose.sh {{ env }} {{ args }}

_each envs action:
    for e in {{ envs }}; do \
      just _compose "$e" {{ action }}; \
    done

# ----------------------------------------------------------------------------
# Bring up / down
# ----------------------------------------------------------------------------

# Bring up envs (default: both, in dependency order). Waits for healthy.
up *envs="dev prod":
    just _each "{{ envs }}" "up -d --wait --wait-timeout 120 --remove-orphans"

# Bring down envs (default: both, in reverse order). Volumes preserved.
down *envs="prod dev":
    just _each "{{ envs }}" "down --remove-orphans"

# Restart a single service in an env.
restart env service:
    just _compose {{ env }} restart {{ service }}

# ----------------------------------------------------------------------------
# Observation
# ----------------------------------------------------------------------------

# Container status + health across envs (default: both).
status *envs="dev prod":
    for e in {{ envs }}; do \
      echo "== $e =="; \
      just _compose "$e" ps; \
    done

# Tail logs from an env, optionally narrowed to a single service.
logs env service="":
    just _compose {{ env }} logs -f {{ service }}

# ----------------------------------------------------------------------------
# Build / pull
# ----------------------------------------------------------------------------

# Pre-pull images for envs (default: both).
pull *envs="dev prod":
    just _each "{{ envs }}" "pull"

# Rebuild a service (or all services in an env when service omitted).
build env service="":
    just _compose {{ env }} build {{ service }}

# ----------------------------------------------------------------------------
# Shell / exec
# ----------------------------------------------------------------------------

# Drop into a running container.
shell env service cmd="bash":
    just _compose {{ env }} exec {{ service }} {{ cmd }}

# ----------------------------------------------------------------------------
# Destructive — explicit verb, no "all" default
# ----------------------------------------------------------------------------

# Wipe an env: down + volumes + orphan containers. Single env required.
nuke env:
    just _compose {{ env }} down --volumes --remove-orphans
