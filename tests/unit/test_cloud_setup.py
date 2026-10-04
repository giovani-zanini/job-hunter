"""Exercise cloud setup against disposable checkouts without network access."""

import os
from pathlib import Path
import subprocess
import sys
import tomllib

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "cloud_setup.py"


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_SYNC_URL", raising=False)
    root = tmp_path / "project"
    root.mkdir()
    (root / "src").mkdir()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "example"\nversion = "0.0.0"\n'
    )
    (root / "README.md").write_text("Example project\n")
    return root, tmp_path / "setup"


def prepare(root, setup):
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--project-root",
            str(root),
            "--setup-dir",
            str(setup),
        ],
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )


def test_setup_supports_checkout_without_lockfile(checkout):
    root, setup = checkout
    result = prepare(root, setup)

    assert result.returncode == 0, result.stderr
    manifest = tomllib.loads((setup / "resolver" / "pyproject.toml").read_text())
    assert manifest["project"]["name"] == "example"
    assert (setup / "resolver" / "src").resolve() == root / "src"
    assert not (root / "poetry.lock").exists()
    assert not (setup / "resolver" / "inputs.sha256").exists()
    environment = dict(
        line.split("=", 1) for line in (root / ".env").read_text().splitlines()
    )
    assert set(environment) == {"DATABASE_URL", "DATABASE_SYNC_URL"}
    assert not (setup / "roles.json").exists()


def test_setup_preserves_existing_local_environment(checkout):
    root, setup = checkout
    original = b"# Existing settings must survive installation\nDEBUG=true\n"
    (root / ".env").write_bytes(original)

    result = prepare(root, setup)

    assert result.returncode == 0, result.stderr
    assert (root / ".env").read_bytes() == original


def test_setup_does_not_mask_injected_database_settings(checkout, monkeypatch):
    root, setup = checkout
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/injected")

    result = prepare(root, setup)

    assert result.returncode == 0, result.stderr
    assert not (root / ".env").exists()


def test_removed_source_lock_invalidates_cached_resolution(checkout):
    root, setup = checkout
    (root / "poetry.lock").write_text("old external resolution\n")
    assert prepare(root, setup).returncode == 0
    resolver = setup / "resolver"
    (resolver / "inputs.sha256").write_bytes((resolver / "pending.sha256").read_bytes())
    (root / "poetry.lock").unlink()

    result = prepare(root, setup)

    assert result.returncode == 0, result.stderr
    assert not (resolver / "poetry.lock").exists()
    assert not (resolver / "inputs.sha256").exists()


def test_setup_refuses_to_replace_unexpected_resolver_source(checkout):
    root, setup = checkout
    source = setup / "resolver" / "src"
    source.mkdir(parents=True)
    preserved = source / "user-file.txt"
    preserved.write_text("Preserve this directory\n")

    result = prepare(root, setup)

    assert result.returncode != 0
    assert "Unexpected resolver source" in result.stderr
    assert preserved.read_text() == "Preserve this directory\n"
