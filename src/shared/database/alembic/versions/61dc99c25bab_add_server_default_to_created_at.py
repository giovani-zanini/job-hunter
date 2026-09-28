"""add_server_default_to_created_at

Revision ID: 61dc99c25bab
Revises: cdf43b63f5ff
Create Date: 2026-03-08 21:47:36.941912

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "61dc99c25bab"
down_revision: Union[str, Sequence[str], None] = "cdf43b63f5ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add server_default=now() to created_at on auth tables that use TimestampMixin."""
    for table in ("Role", "User", "Auth"):
        op.alter_column(
            table,
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            existing_nullable=False,
            schema="auth",
        )


def downgrade() -> None:
    """Remove server_default from created_at on auth tables."""
    for table in ("Role", "User", "Auth"):
        op.alter_column(
            table,
            "created_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=None,
            existing_nullable=False,
            schema="auth",
        )
