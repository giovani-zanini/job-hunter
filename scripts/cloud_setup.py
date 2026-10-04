"""Prepare external Poetry metadata while preserving checkout and runtime settings."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil


def prepare_metadata(root: Path, setup: Path) -> None:
    resolver = setup / "resolver"
    resolver.mkdir(parents=True, exist_ok=True)
    source = resolver / "src"
    if source.is_symlink():
        if source.resolve() != root / "src":
            raise RuntimeError(
                "Unexpected resolver source link; preserve it and inspect setup"
            )
    elif source.exists():
        raise RuntimeError(
            "Unexpected resolver source directory; preserve it and inspect setup"
        )
    else:
        source.symlink_to(root / "src", target_is_directory=True)

    inputs = ["pyproject.toml", "README.md"]
    if (root / "poetry.lock").is_file():
        inputs.append("poetry.lock")
    digest = hashlib.sha256()
    for name in inputs:
        digest.update(name.encode() + b"\0" + (root / name).read_bytes())
    fingerprint = digest.hexdigest() + "\n"
    stamp = resolver / "inputs.sha256"
    if not stamp.is_file() or stamp.read_text() != fingerprint:
        for name in inputs:
            shutil.copy2(root / name, resolver / name)
        if "poetry.lock" not in inputs:
            (resolver / "poetry.lock").unlink(missing_ok=True)
        stamp.unlink(missing_ok=True)
    (resolver / "pending.sha256").write_text(fingerprint)


def prepare_environment(root: Path) -> None:
    # Runtime bindings take precedence. Never persist injected credentials.
    if os.getenv("DATABASE_URL") or os.getenv("DATABASE_SYNC_URL"):
        return
    try:
        descriptor = os.open(root / ".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return
    with os.fdopen(descriptor, "w") as environment:
        environment.write(
            "DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/job_finder\n"
            "DATABASE_SYNC_URL=postgresql+psycopg2://user:password@localhost:5432/job_finder\n"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--setup-dir", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    prepare_metadata(root, args.setup_dir.resolve())
    prepare_environment(root)


if __name__ == "__main__":
    main()
