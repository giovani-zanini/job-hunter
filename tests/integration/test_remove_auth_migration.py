"""Upgrade an existing database without losing domain rows."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


ROOT = Path(__file__).resolve().parents[2]


def test_upgrade_preserves_domain_records(disposable_database, monkeypatch):
    sync_url, _ = disposable_database
    monkeypatch.setenv("DATABASE_SYNC_URL", sync_url)
    config = Config(str(ROOT / "src/shared/database/alembic.ini"))
    command.upgrade(config, "1448ab8c1969")
    engine = create_engine(sync_url)
    with engine.begin() as connection:
        old_user_id = connection.scalar(
            text('INSERT INTO profile."User" (external_id) VALUES (31415) RETURNING id')
        )
        profile_id = connection.scalar(
            text('INSERT INTO profile."Profile" '
                 '(user_id, slug, full_name, title, bio) '
                 'VALUES (:user_id, :slug, :name, :title, :bio) RETURNING id'),
            {"user_id": old_user_id, "slug": "legacy", "name": "Legacy", "title": "Dev", "bio": "Bio"},
        )
        segment_id = connection.scalar(
            text('INSERT INTO enterprise."Segment" (name) VALUES (:name) RETURNING id'),
            {"name": "Legacy Segment"},
        )

    command.upgrade(config, "head")
    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM information_schema.schemata WHERE schema_name='auth'")) == 0
        assert connection.scalar(text('SELECT count(*) FROM profile."User" WHERE is_anonymous')) == 1
        assert connection.scalar(text('SELECT is_anonymous FROM profile."User" WHERE id=:id'), {"id": old_user_id}) is False
        assert connection.scalar(text('SELECT user_id FROM profile."Profile" WHERE id=:id'), {"id": profile_id}) == old_user_id
        assert connection.scalar(text('SELECT name FROM enterprise."Segment" WHERE id=:id'), {"id": segment_id}) == "Legacy Segment"
    engine.dispose()


def test_fresh_database_and_repeated_upgrade(disposable_database, monkeypatch):
    sync_url, _ = disposable_database
    monkeypatch.setenv("DATABASE_SYNC_URL", sync_url)
    config = Config(str(ROOT / "src/shared/database/alembic.ini"))
    command.upgrade(config, "head")
    command.upgrade(config, "head")
    engine = create_engine(sync_url)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT count(*) FROM information_schema.schemata WHERE schema_name='auth'")) == 0
        assert connection.scalar(text('SELECT count(*) FROM profile."User" WHERE is_anonymous AND deleted_at IS NULL')) == 1
    engine.dispose()
