import subprocess
import uuid
from pathlib import Path

import pytest
from _pytest.tmpdir import TempPathFactory
from flytekit.configuration import Config, PlatformConfig
from flytekit.remote import FlyteRemote

_THIS_DIR = Path(__file__).parent
_PROJECT_ROOT = _THIS_DIR.parent
_DOCKERFILE = _PROJECT_ROOT / "docker" / "Dockerfile"
_DOCKER_REGISTRY = "localhost:30000"

_FLYTE_HOST = "localhost:30080"
_FLYTE_PROJECT = "dask-testing"
_FLYTE_DOMAIN = "development"


@pytest.fixture(scope="session")
def flyte_version() -> str:
    return f"pytest-{str(uuid.uuid4())[:8]}"


@pytest.fixture(scope="session")
def docker_image(flyte_version: str) -> str:
    docker_image_name = f"{_DOCKER_REGISTRY}/dask-e2e:{flyte_version}"
    subprocess.run(
        [
            "docker",
            "build",
            "--push",
            "-t",
            docker_image_name,
            "-f",
            str(_DOCKERFILE),
            str(_PROJECT_ROOT),
        ],
        check=True,
    )
    return docker_image_name


@pytest.fixture(scope="session")
def register_workflows(
    docker_image: str, flyte_version: str, tmp_path_factory: TempPathFactory
) -> None:
    package_directory = tmp_path_factory.mktemp("workflows")
    package_file = package_directory / "package.tgz"
    subprocess.run(
        [
            "pyflyte",
            "--pkgs",
            "flyte_dev_setup",
            "package",
            "--fast",
            "--image",
            docker_image,
            "-o",
            str(package_file),
        ],
        check=True,
    )
    subprocess.run(
        [
            "flytectl",
            "--admin.endpoint",
            _FLYTE_HOST,
            "--admin.insecure",
            "-p",
            _FLYTE_PROJECT,
            "-d",
            _FLYTE_DOMAIN,
            "register",
            "files",
            "--archive",
            "--version",
            flyte_version,
            str(package_file),
        ]
    )


@pytest.fixture(scope="session")
def flyte_remote() -> FlyteRemote:
    return FlyteRemote(
        config=Config(
            platform=PlatformConfig(
                endpoint=_FLYTE_HOST,
                insecure=True,
            )
        ),
        default_project=_FLYTE_PROJECT,
        default_domain=_FLYTE_DOMAIN,
    )
