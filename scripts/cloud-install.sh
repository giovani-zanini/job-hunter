#!/usr/bin/env bash
set -euo pipefail

# Use the existing isolated cloud checkout; do not create a worktree.
cd /workspace/job-hunter
test -f pyproject.toml
test -f poetry.lock
setup_dir=/workspace/.cloud-setup/job-hunter
mkdir -p "$setup_dir/resolver"
export POETRY_CACHE_DIR=/workspace/.cloud-setup/poetry-cache
export POETRY_CONFIG_DIR=/workspace/.cloud-setup/poetry-config
export PIP_CACHE_DIR=/workspace/.cloud-setup/pip-cache
export PIP_DISABLE_PIP_VERSION_CHECK=1

# pip only bootstraps Poetry itself in a separate tooling environment.
# Poetry manages all application dependencies and the editable project install.
python3 -m venv "$setup_dir/tools"
"$setup_dir/tools/bin/python" -m pip install --no-input 'poetry==2.2.1'
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -c 'import sys; assert sys.version_info >= (3, 12)'

# The tracked lock is stale. Resolve only in an external metadata copy,
# retaining existing locked versions and reusing that result until inputs change.
python3 - <<'PY'
import hashlib
import shutil
from pathlib import Path

root = Path('/workspace/job-hunter')
resolver = Path('/workspace/.cloud-setup/job-hunter/resolver')
digest = hashlib.sha256(b''.join((root / p).read_bytes() for p in ['pyproject.toml', 'poetry.lock'])).hexdigest()
stamp = resolver / 'inputs.sha256'
if not stamp.exists() or stamp.read_text().strip() != digest:
    for name in ['pyproject.toml', 'poetry.lock', 'README.md']:
        shutil.copy2(root / name, resolver / name)
    stamp.unlink(missing_ok=True)
(resolver / 'pending.sha256').write_text(digest + '\n')
# Link the real source so Poetry can install the project from this external
# metadata copy without copying or modifying application code.
source_link = resolver / 'src'
if source_link.is_symlink():
    if source_link.resolve() != root / 'src':
        raise RuntimeError('Unexpected source link in external resolver')
elif source_link.exists():
    raise RuntimeError('Preserve unexpected existing resolver/src directory')
else:
    source_link.symlink_to(root / 'src', target_is_directory=True)
PY
export VIRTUAL_ENV=/workspace/job-hunter/.venv
export POETRY_VIRTUALENVS_CREATE=false
if [ ! -f "$setup_dir/resolver/inputs.sha256" ]; then
  "$setup_dir/tools/bin/poetry" -C "$setup_dir/resolver" lock --no-interaction
fi
mv "$setup_dir/resolver/pending.sha256" "$setup_dir/resolver/inputs.sha256"
"$setup_dir/tools/bin/poetry" -C "$setup_dir/resolver" check --lock
"$setup_dir/tools/bin/poetry" -C "$setup_dir/resolver" install --all-extras --no-interaction

# Development-only signing keys are generated locally, never embedded or logged.
# Preserve any existing local configuration and injected key bindings.
python3 - <<'PY'
import json
import os
import secrets
from pathlib import Path

p = Path('.env')
if not p.exists():
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write('DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/job_finder\n')
        f.write('DATABASE_SYNC_URL=postgresql+psycopg2://user:password@localhost:5432/job_finder\n')
        for name in ['SECRET_KEY', 'REFRESH_SECRET_KEY']:
            if not os.environ.get(name):
                f.write(name + '=' + secrets.token_hex(32) + '\n')
roles = Path('/workspace/.cloud-setup/job-hunter/roles.json')
if not roles.exists():
    roles.write_text(json.dumps([
        {'name': 'admin', 'description': 'Administrator role'},
        {'name': 'default', 'description': 'Default user role'},
    ]) + '\n')
PY
docker compose -f docker/docker-compose.yml pull postgres
git diff --exit-code
git diff --cached --exit-code
