# Repository guidance

This FastAPI project exposes public `profile` and `enterprise` APIs from `src/main.py`. Features live under `src/modules/<module>/features/`; persistence and Alembic live under `src/shared/database/`.

The `profile.User` table is a local ownership anchor. A single row with `is_anonymous=true` owns new Profile, Link, Experience, Education and Certificate records. Existing records retain their `user_id` values and remain publicly accessible. Enterprise has no user dependency.

Import every active SQLAlchemy model in `src/shared/database/alembic/env.py` for autogeneration. Historical migrations create an `auth` schema during a fresh upgrade; revision `a03e20261003` deletes it. Do not modify old revisions or reintroduce authentication code.

Run `.venv/bin/python -m pytest tests/unit` and `.venv/bin/python scripts/generate_json_schemas.py --check` for local checks. Database tests require a disposable PostgreSQL instance and the `TEST_DATABASE_URL` / `TEST_DATABASE_SYNC_URL` environment variables. See `README.md`.
