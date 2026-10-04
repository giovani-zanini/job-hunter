#!/usr/bin/env bash
set -euo pipefail

# Reuse the isolated cloud checkout and keep dependency metadata outside Git.
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
test -f pyproject.toml
setup_dir="${JOB_HUNTER_CLOUD_SETUP_DIR:-/workspace/.cloud-setup/job-hunter}"
mkdir -p "$setup_dir"
export POETRY_CACHE_DIR="$setup_dir/poetry-cache"
export POETRY_CONFIG_DIR="$setup_dir/poetry-config"
export PIP_CACHE_DIR="$setup_dir/pip-cache"
export PIP_DISABLE_PIP_VERSION_CHECK=1

# pip bootstraps Poetry only; Poetry manages the application and dev dependencies.
if [ ! -x "$setup_dir/tools/bin/poetry" ] || [ "$("$setup_dir/tools/bin/poetry" --version)" != 'Poetry (version 2.2.1)' ]; then
  python3 -m venv "$setup_dir/tools"
  "$setup_dir/tools/bin/python" -m pip install --no-input 'poetry==2.2.1'
fi
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi
.venv/bin/python -c 'import sys; assert sys.version_info >= (3, 12)'
python3 scripts/cloud_setup.py --project-root "$project_root" --setup-dir "$setup_dir"

export VIRTUAL_ENV="$project_root/.venv"
export POETRY_VIRTUALENVS_CREATE=false
if [ ! -f "$setup_dir/resolver/inputs.sha256" ] || [ ! -f "$setup_dir/resolver/poetry.lock" ]; then
  "$setup_dir/tools/bin/poetry" -C "$setup_dir/resolver" lock --no-interaction
fi
"$setup_dir/tools/bin/poetry" -C "$setup_dir/resolver" check --lock
"$setup_dir/tools/bin/poetry" -C "$setup_dir/resolver" sync --all-extras --no-interaction
# Mark the cache valid only after both resolution and installation succeed.
mv "$setup_dir/resolver/pending.sha256" "$setup_dir/resolver/inputs.sha256"
