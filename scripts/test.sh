#!/usr/bin/env bash
# scripts/test.sh – Run the full E2E test suite.
#
# Usage:
#   ./scripts/test.sh              # Run all tests
#   ./scripts/test.sh -k "skill"   # Filter by keyword
#   ./scripts/test.sh -v --tb=long # Extra verbosity
#
# Prerequisites:
#   • PostgreSQL de teste deve estar acessível
#   • TEST_DATABASE_URL and TEST_DATABASE_SYNC_URL must target a disposable database
#   • Python virtual-env must be active with test dependencies installed:
#       pip install -e ".[test]"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# 1. Require a disposable test database
# ---------------------------------------------------------------------------
: "${TEST_DATABASE_URL:?Set TEST_DATABASE_URL to a disposable PostgreSQL database}"
: "${TEST_DATABASE_SYNC_URL:?Set TEST_DATABASE_SYNC_URL to the same disposable database}"
export DATABASE_URL="$TEST_DATABASE_URL"
export DATABASE_SYNC_URL="$TEST_DATABASE_SYNC_URL"

# ---------------------------------------------------------------------------
# 2. Apply latest migrations
# ---------------------------------------------------------------------------
echo "==> Running Alembic migrations..."
.venv/bin/alembic -c src/shared/database/alembic.ini upgrade head

# ---------------------------------------------------------------------------
# 3. Run tests
# ---------------------------------------------------------------------------
echo "==> Running E2E tests..."
.venv/bin/python -m pytest tests/ -v --tb=short "$@"
