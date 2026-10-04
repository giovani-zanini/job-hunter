# Cloud development environment

Use the existing checkout at `/workspace/job-hunter`. Cloud tasks are already isolated; do not create a Git worktree unless the user explicitly requests one. This workflow was validated on the `development` branch. Preserve task branch changes and user files; do not reset or automatically switch branches.

Python 3.12+, Docker Engine and Compose are available. Use Poetry as the project's dependency manager and command runner. Installed dependencies are in `/workspace/job-hunter/.venv`; Poetry 2.2.1 is at `/workspace/.cloud-setup/job-hunter/tools/bin/poetry`. The tracked poetry.lock is stale. The installation script uses Poetry to resolve and install an external metadata copy, with a source link to the real checkout, keeping hashes enabled and tracked manifests and lockfiles unchanged. Python's venv module and pip only bootstrap the separate Poetry tool environment; project packages are installed with Poetry. Re-run the saved installation script when manifests change or dependencies are missing.

The ignored `.env` contains local development database configuration and locally generated signing keys. Preserve this file and any injected `SECRET_KEY`, `REFRESH_SECRET_KEY`, `DATABASE_URL` and `DATABASE_SYNC_URL` bindings. Do not print key values. Do not copy `.env.sample` directly: it contains empty database URLs and empty optional integer settings. For this snapshot the development database is `job_finder` and the separate test database is `job_finder_test` on the repository's local PostgreSQL container.

## Installation

From `/workspace/job-hunter`, run the versioned installation script:

```bash
bash scripts/cloud-install.sh
```

It prepares the Poetry tooling, project virtual environment, external dependency metadata, local development configuration and PostgreSQL image. The startup and test commands below use those prepared files.

## Startup

Live processes and Docker state must be checked after restoration. From `/workspace/job-hunter`, run:

```bash
set -euo pipefail
cd /workspace/job-hunter
export PATH="/workspace/.cloud-setup/job-hunter/tools/bin:$PATH"
docker compose -f docker/docker-compose.yml up postgres -d --wait --wait-timeout 90
poetry run alembic -c src/shared/database/alembic.ini upgrade head
poetry run job-finder role create --json /workspace/.cloud-setup/job-hunter/roles.json
```

The role seed and migrations are repeatable. If an existing API process is healthy and runs this checkout, reuse it. Otherwise run this command in a persistent tool session; keep the session available and check its startup output:

```bash
cd /workspace/job-hunter
export PATH="/workspace/.cloud-setup/job-hunter/tools/bin:$PATH"
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

This is the unified entry point for auth, profile and enterprise. Older module-only commands in README.md are outdated. In another tool call, validate the service with this internal request. Do not present loopback URLs as user-facing previews.

```bash
cd /workspace/job-hunter
export PATH="/workspace/.cloud-setup/job-hunter/tools/bin:$PATH"
poetry run python - <<'PY'
import json
import time
import urllib.request

for attempt in range(40):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2) as response:
            assert response.status == 200
            assert json.load(response) == {'status': 'healthy'}
        break
    except OSError:
        if attempt == 39:
            raise
        time.sleep(0.5)
with urllib.request.urlopen('http://127.0.0.1:8000/openapi.json', timeout=3) as response:
    schema = json.load(response)
for route in ['/api/v1/account/', '/api/v1/skills/', '/api/v1/vacancies/']:
    assert route in schema['paths'], route
print('API health and all three module route registries verified.')
PY
```

## Running the existing E2E suite

The tests truncate auth, profile and enterprise tables. Use the dedicated local test database. The following sequence has been executed against this checkout. If the user adds `.env.test`, inspect its database destination before running, because tests/conftest.py loads it with override=True. Do not run this sequence against a user-supplied remote database.

```bash
set -euo pipefail
cd /workspace/job-hunter
export PATH="/workspace/.cloud-setup/job-hunter/tools/bin:$PATH"
docker compose -f docker/docker-compose.yml up postgres -d --wait --wait-timeout 90
if ! docker exec job_finder_postgres psql -U user -d postgres -Atqc "SELECT 1 FROM pg_database WHERE datname = 'job_finder_test'" | rg -q '^1$'; then
  docker exec job_finder_postgres createdb -U user job_finder_test
fi
set -a
source .env
set +a
export DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/job_finder_test
export DATABASE_SYNC_URL=postgresql+psycopg2://user:password@localhost:5432/job_finder_test
poetry run alembic -c src/shared/database/alembic.ini upgrade head
poetry run pytest tests/ -q --tb=short
```

The application package installs in editable mode using Poetry, the external metadata and lock checks pass, PostgreSQL 17 is reachable, all six migrations apply, roles seed repeatedly, and API health and OpenAPI checks pass. The full suite executed 187 tests during initial setup: 173 passed, 13 failed, and 1 skipped. Failures were traced to account deletion relationships, refresh JWTs generated within the same second, profile deletion response serialization, lazy async relationship loading, soft-deletion of association models lacking soft_delete, a wrong ensure_exists keyword, and API/test response contract mismatches. The recovery test skips because a recovery token is not exposed. Keep these outcomes distinct; do not disable assertions or change application code as part of environment setup.

After switching the setup commands to Poetry, installation, CLI commands, migrations, role seeding and API restart were revalidated. The health and vacancy E2E subset ran through `poetry run pytest`: 12 passed, zero failed or skipped. The full-suite counts above belong to the earlier full run; the Poetry subset does not replace that report.

Publication is performed by the product. Current-machine validation and a saved draft do not establish publication or restoration in a new task.
