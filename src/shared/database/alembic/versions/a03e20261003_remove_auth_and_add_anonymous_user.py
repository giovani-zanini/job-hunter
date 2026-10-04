"""Remove auth storage and introduce a local anonymous profile owner.

Revision ID: a03e20261003
Revises: 1448ab8c1969
"""

from alembic import op
import sqlalchemy as sa

revision = "a03e20261003"
down_revision = "1448ab8c1969"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "User",
        sa.Column(
            "is_anonymous", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        schema="profile",
    )
    op.create_index(
        "uq_profile_User_anonymous",
        "User",
        ["is_anonymous"],
        unique=True,
        schema="profile",
        postgresql_where=sa.text("is_anonymous IS TRUE"),
    )
    op.drop_index("ix_profile_User_external_id", table_name="User", schema="profile")
    op.drop_column("User", "external_id", schema="profile")
    op.execute('INSERT INTO profile."User" (is_anonymous) VALUES (true)')

    for table in ("Session", "Auth", "User", "Role"):
        op.drop_table(table, schema="auth")
    op.execute("DROP SCHEMA auth")


def downgrade() -> None:
    raise RuntimeError(
        "Auth data and profile external IDs were deleted. "
        "Restore a database backup to reverse this migration."
    )
