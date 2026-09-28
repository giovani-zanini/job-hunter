#!/usr/bin/env bash
# scripts/test.sh – Run the full E2E test suite.
#
# Usage:
#   ./scripts/test.sh              # Run all tests
#   ./scripts/test.sh -k "skill"   # Filter by keyword
#   ./scripts/test.sh -v --tb=long # Extra verbosity
#
# Prerequisites:
#   • PostgreSQL must be accessible (started via Docker Compose below)
#   • .env.test must exist at the project root
#   • Python virtual-env must be active with test dependencies installed:
#       pip install -e ".[test]"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# 1. Ensure PostgreSQL is running
# ---------------------------------------------------------------------------
echo "==> Starting PostgreSQL (if not already running)..."
docker compose -f docker/docker-compose.yml up postgres -d

# Give it a moment to be ready
echo "==> Waiting for PostgreSQL to be ready..."
sleep 3

# ---------------------------------------------------------------------------
# 2. Apply latest migrations
# ---------------------------------------------------------------------------
echo "==> Running Alembic migrations..."
alembic -c src/shared/database/alembic.ini upgrade head

# ---------------------------------------------------------------------------
# 3. Seed roles (idempotent – safe to re-run)
# ---------------------------------------------------------------------------
echo "==> Seeding roles..."
job-finder role create --json roles.json || true

# ---------------------------------------------------------------------------
# 4. Run tests
# ---------------------------------------------------------------------------
echo "==> Running E2E tests..."
pytest tests/ -v --tb=short "$@"
