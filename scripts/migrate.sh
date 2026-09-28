#!/bin/bash
# Alembic Migration Helper Script

set -e

VENV_ALEMBIC=".venv/bin/alembic"
ALEMBIC_CONFIG="src/shared/database/alembic.ini"

case "$1" in
    "create")
        if [ -z "$2" ]; then
            echo "Usage: ./migrate.sh create <message>"
            exit 1
        fi
        echo "Creating new migration: $2"
        $VENV_ALEMBIC -c $ALEMBIC_CONFIG revision --autogenerate -m "$2"
        ;;
    
    "upgrade")
        echo "Upgrading database to latest migration..."
        $VENV_ALEMBIC -c $ALEMBIC_CONFIG upgrade head
        ;;
    
    "downgrade")
        if [ -z "$2" ]; then
            echo "Downgrading one revision..."
            $VENV_ALEMBIC -c $ALEMBIC_CONFIG downgrade -1
        else
            echo "Downgrading to: $2"
            $VENV_ALEMBIC -c $ALEMBIC_CONFIG downgrade "$2"
        fi
        ;;
    
    "history")
        echo "Migration history:"
        $VENV_ALEMBIC -c $ALEMBIC_CONFIG history
        ;;
    
    "current")
        echo "Current migration:"
        $VENV_ALEMBIC -c $ALEMBIC_CONFIG current
        ;;
    
    "stamp")
        if [ -z "$2" ]; then
            echo "Usage: ./migrate.sh stamp <revision>"
            exit 1
        fi
        echo "Stamping database to revision: $2"
        $VENV_ALEMBIC -c $ALEMBIC_CONFIG stamp "$2"
        ;;
    
    *)
        echo "Alembic Migration Helper"
        echo ""
        echo "Usage:"
        echo "  ./migrate.sh create <message>       - Create new migration with autogenerate"
        echo "  ./migrate.sh upgrade                - Apply all pending migrations"
        echo "  ./migrate.sh downgrade [revision]   - Rollback migrations (default: -1)"
        echo "  ./migrate.sh history                - Show migration history"
        echo "  ./migrate.sh current                - Show current migration"
        echo "  ./migrate.sh stamp <revision>       - Stamp database to specific revision"
        echo ""
        echo "Examples:"
        echo "  ./migrate.sh create \"Add user table\""
        echo "  ./migrate.sh upgrade"
        echo "  ./migrate.sh downgrade"
        echo "  ./migrate.sh downgrade base"
        echo "  ./migrate.sh history"
        exit 1
        ;;
esac
