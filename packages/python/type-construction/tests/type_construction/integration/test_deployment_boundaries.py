"""Each development container receives only the material its role requires.

Governing requirements: docs/architecture/DESIGN.md section 7 (application credentials confer no
provisioning authority; secret mounts are read-only and restricted; private material stays out of
images) and the deployment layout in ``compose.yaml``. The application container must read its
restricted credentials and public trust bundle and nothing stronger: no setup credentials, no
certificate authority signing key, no operator or account signing keys, through neither its
secrets mount nor its workspace mount. The NATS container must read its certificate, key and
configuration and nothing else. Access is verified from the actual containers under their
configured users, in a disposable Compose project pointed at disposable material.
"""

import json
import os
import subprocess
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest

COMPOSE_TIMEOUT = 600.0


@pytest.fixture
def project(material: dict[str, Path], repository: Path) -> Iterator[dict[str, str]]:
    """A disposable Compose project using the session material and the current user's ids."""
    name = f"tcatest{uuid.uuid4().hex[:10]}"
    environment = {
        **os.environ,
        "COMPOSE_PROJECT_NAME": name,
        "TCA_SECRETS": str(material["root"]),
        "TCA_REPOSITORY": str(repository),
        "UID": str(os.getuid()),
        "GID": str(os.getgid()),
    }
    try:
        yield environment
    finally:
        subprocess.run(
            ["docker", "compose", "down", "--volumes", "--rmi", "local", "--remove-orphans"],  # noqa: S607
            cwd=repository,
            env=environment,
            check=False,
            capture_output=True,
            timeout=COMPOSE_TIMEOUT,
        )


def _compose(*arguments: str, environment: dict[str, str]) -> str:
    result = subprocess.run(  # noqa: S603 - fixed compose invocation with test-controlled arguments
        ["docker", "compose", *arguments],  # noqa: S607
        cwd=environment["TCA_REPOSITORY"],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
        timeout=COMPOSE_TIMEOUT,
    )
    return result.stdout


def _in_container(service: str, script: str, environment: dict[str, str]) -> dict[str, str]:
    """Run a shell script in the service's container as configured and return its report."""
    output = _compose(
        "run",
        "--rm",
        "--no-deps",
        "--quiet-pull",
        service,
        "sh",
        "-c",
        script,
        environment=environment,
    )
    return dict(line.split("=", 1) for line in output.splitlines() if "=" in line)


def test_compose_mounts_give_each_container_only_its_own_partition(project: dict[str, str]) -> None:
    configuration = json.loads(_compose("config", "--format", "json", environment=project))
    root = project["TCA_SECRETS"]

    dev = {mount["target"]: mount for mount in configuration["services"]["dev"]["volumes"]}
    nats = {mount["target"]: mount for mount in configuration["services"]["nats"]["volumes"]}

    assert set(dev) == {"/workspace", "/run/secrets/tca"}
    assert dev["/run/secrets/tca"]["source"] == f"{root}/application"
    assert dev["/run/secrets/tca"]["read_only"] is True
    assert dev["/run/secrets/tca"]["bind"] == {"create_host_path": False}
    assert set(nats) == {"/etc/nats", "/data"}
    assert nats["/etc/nats"]["source"] == f"{root}/server"
    assert nats["/etc/nats"]["read_only"] is True
    assert nats["/etc/nats"]["bind"] == {"create_host_path": False}
    assert nats["/data"]["type"] == "volume"
    sources = [
        mount.get("source", "")
        for service in configuration["services"].values()
        for mount in service["volumes"]
    ]
    assert not any("provisioning" in source or "untrusted" in source for source in sources)


def test_application_container_reads_its_material_and_nothing_stronger(
    project: dict[str, str], material: dict[str, Path]
) -> None:
    setup_jwt = material["setup_credentials"].read_text().splitlines()[1]
    report = _in_container(
        "dev",
        f"""
        echo user=$(id -u):$(id -g)
        echo secrets=$(ls -A /run/secrets/tca | sort | tr '\\n' ' ')
        echo creds_head=$(head -c 24 /run/secrets/tca/application.creds)
        echo ca_head=$(head -c 27 /run/secrets/tca/ca.pem)
        echo writable=$(touch /run/secrets/tca/probe 2>/dev/null && echo yes || echo no)
        echo stronger_files=$(find / -xdev \\( -name setup.creds -o -name ca.key \
          -o -name '*.nk' \\) 2>/dev/null | wc -l)
        echo setup_jwt_copies=$(grep -rl --exclude-dir=.venv --exclude-dir=.git -- '{setup_jwt}' \
          /workspace /run/secrets 2>/dev/null | wc -l)
        echo workspace_secrets=$(ls -d /workspace/.secrets 2>/dev/null | wc -l)
        """,
        project,
    )

    assert report["user"] == f"{os.getuid()}:{os.getgid()}", "runs as the configured user"
    assert report["secrets"].split() == ["application.creds", "ca.pem"]
    assert report["creds_head"] == "-----BEGIN NATS USER JWT"
    assert report["ca_head"] == "-----BEGIN CERTIFICATE-----"
    assert report["writable"] == "no"
    assert report["stronger_files"] == "0"
    assert report["setup_jwt_copies"] == "0"
    assert report["workspace_secrets"] == "0"


def test_server_container_reads_only_the_server_material(project: dict[str, str]) -> None:
    report = _in_container(
        "nats",
        """
        echo user=$(id -u)
        echo files=$(ls -A /etc/nats | sort | tr '\\n' ' ')
        echo key_head=$(head -c 30 /etc/nats/server.key)
        echo config_ok=$(grep -c handshake_first /etc/nats/nats-server.conf)
        echo writable=$(touch /etc/nats/probe 2>/dev/null && echo yes || echo no)
        echo stronger_files=$(find / -xdev \\( -name ca.key -o -name '*.creds' -o -name '*.nk' \\) \
          2>/dev/null | wc -l)
        """,
        project,
    )

    assert report["user"] == "0", "the pinned image runs its server as root"
    assert report["files"].split() == [
        "nats-server.conf",
        "resolver.conf",
        "server.key",
        "server.pem",
    ]
    assert report["key_head"].startswith("-----BEGIN")
    assert report["config_ok"] == "1"
    assert report["writable"] == "no"
    assert report["stronger_files"] == "0"
