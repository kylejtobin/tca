"""Development setup preserves identities and persistent state; reset replaces both explicitly.

Governing requirements: docs/architecture/DESIGN.md section 7 (development and tests follow the
security contract with generated material kept out of commits and images; secret material has
restricted access; persistent JetStream data belongs to the generated account identities) and
the repository's setup recipes. Ordinary setup must be repeatable without rotating identities,
incomplete material must fail without destroying anything, and the reset operation must remove
the JetStream data persisted under the identities it replaces. The recipes run against a
disposable material directory and a disposable Compose project; the development project is never
touched. Prerequisites: ``openssl``, ``docker`` and the environment's ``just``.
"""

import hashlib
import os
import shutil
import stat
import subprocess
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

type Generate = Callable[..., subprocess.CompletedProcess[str]]
RECIPE_TIMEOUT = 300.0

EXPECTED = {
    "application": {"application.creds", "ca.pem"},
    "server": {"server.pem", "server.key", "nats-server.conf", "resolver.conf"},
    "provisioning": {"setup.creds", "ca.key", "ca.pem", "ca.srl", "nsc"},
    "untrusted": {"ca.pem", "ca.key", "application.creds"},
}
PRIVATE = (
    "application/application.creds",
    "server/server.key",
    "provisioning/setup.creds",
    "provisioning/ca.key",
    "untrusted/ca.key",
    "untrusted/application.creds",
)


def _digests(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _account_identity(root: Path) -> str:
    """The account public key the resolver carries; it changes with every generation."""
    for line in (root / "server" / "resolver.conf").read_text().splitlines():
        if line.strip().startswith("A") and ":" in line:
            return line.split(":")[0].strip()
    pytest.fail("no account entry in the generated resolver")


@pytest.fixture
def output(tmp_path: Path) -> Path:
    return tmp_path / "secrets"


def test_generation_partitions_material_by_consumer_with_owner_only_access(
    output: Path, generator: Generate
) -> None:
    result = generator(output)

    assert result.returncode == 0, result.stderr
    assert {child.name for child in output.iterdir()} == set(EXPECTED)
    for partition, names in EXPECTED.items():
        assert {child.name for child in (output / partition).iterdir()} == names
        assert stat.S_IMODE((output / partition).stat().st_mode) == 0o700
    assert stat.S_IMODE(output.stat().st_mode) == 0o700
    for name in PRIVATE:
        assert stat.S_IMODE((output / name).stat().st_mode) == 0o600, name
    header = (output / "provisioning" / "ca.key").read_text().splitlines()[0]
    assert header.startswith("-----BEGIN") and header.endswith("PRIVATE KEY-----")
    assert not list((output / "server").glob("ca.*")), "the signing key never reaches the server"


def test_repeated_setup_preserves_complete_material(output: Path, generator: Generate) -> None:
    first = generator(output)
    before = _digests(output)

    again = generator(output)

    assert first.returncode == 0 and again.returncode == 0, again.stderr
    assert "preserved" in again.stdout
    assert _digests(output) == before


def test_incomplete_material_fails_without_changes(output: Path, generator: Generate) -> None:
    assert generator(output).returncode == 0
    (output / "application" / "application.creds").unlink()
    (output / "server" / "resolver.conf").unlink()
    before = _digests(output)

    result = generator(output)

    assert result.returncode == 1
    assert "application/application.creds" in result.stderr
    assert "server/resolver.conf" in result.stderr
    assert "just reset" in result.stderr
    assert _digests(output) == before, "a failed ordinary setup changes nothing"
    assert not list(output.parent.glob(".secrets.generating"))


def test_replace_generates_new_identities(output: Path, generator: Generate) -> None:
    assert generator(output).returncode == 0
    before = _digests(output)
    identity = _account_identity(output)

    result = generator(output, "--replace")

    assert result.returncode == 0, result.stderr
    after = _digests(output)
    assert {name for name in after if not name.endswith(".nk")} == {
        name for name in before if not name.endswith(".nk")
    }, "the same files apart from the key store, whose names are the new public keys"
    assert all(after[name] != before[name] for name in PRIVATE), "new private material"
    assert _account_identity(output) != identity


@pytest.fixture
def disposable_project(tmp_path: Path, repository: Path) -> Iterator[dict[str, str]]:
    """Environment selecting a disposable Compose project and material directory for just."""
    project = f"tcatest{uuid.uuid4().hex[:10]}"
    environment = {
        **os.environ,
        "COMPOSE_PROJECT_NAME": project,
        "TCA_SECRETS": str(tmp_path / "secrets"),
    }
    try:
        yield environment
    finally:
        subprocess.run(
            ["docker", "compose", "down", "--volumes", "--remove-orphans"],  # noqa: S607
            cwd=repository,
            env=environment,
            check=False,
            capture_output=True,
            timeout=120,
        )


def _just(
    recipe: str, environment: dict[str, str], repository: Path
) -> subprocess.CompletedProcess[str]:
    just = shutil.which("just")
    if just is None:
        pytest.fail("the environment's just is required to exercise the setup recipes")
    return subprocess.run(  # noqa: S603 - the recipe name is a fixed test input
        [just, recipe],
        cwd=repository,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=RECIPE_TIMEOUT,
    )


def _volume_exists(name: str) -> bool:
    result = subprocess.run(  # noqa: S603 - fixed docker invocation with a test-controlled name
        ["docker", "volume", "inspect", name],  # noqa: S607
        capture_output=True,
        check=False,
        timeout=60,
    )
    return result.returncode == 0


def test_reset_recipe_replaces_identities_together_with_the_projects_jetstream_volume(
    disposable_project: dict[str, str], repository: Path, docker_command: Callable[..., str]
) -> None:
    """``just secrets`` twice keeps the identities; ``just reset`` removes the project's JetStream
    volume and generates new identities, because data persisted under the previous account is
    unreachable by the new one."""
    secrets = Path(disposable_project["TCA_SECRETS"])
    volume = f"{disposable_project['COMPOSE_PROJECT_NAME']}_nats-data"

    setup = _just("secrets", disposable_project, repository)
    assert setup.returncode == 0, setup.stderr
    identity = _account_identity(secrets)
    repeated = _just("secrets", disposable_project, repository)
    assert repeated.returncode == 0 and "preserved" in repeated.stdout
    assert _account_identity(secrets) == identity

    subprocess.run(
        ["docker", "compose", "up", "--no-start", "nats"],  # noqa: S607
        cwd=repository,
        env=disposable_project,
        check=True,
        capture_output=True,
        timeout=120,
    )
    assert _volume_exists(volume)
    docker_command("run", "--rm", "--volume", f"{volume}:/data", "alpine", "touch", "/data/kept")

    reset = _just("reset", disposable_project, repository)

    assert reset.returncode == 0, reset.stderr
    assert not _volume_exists(volume), "the persisted JetStream data goes with the identities"
    assert _account_identity(secrets) != identity
