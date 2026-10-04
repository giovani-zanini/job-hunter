"""A fresh database can replay the historical Auth migrations and remove them."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]


def test_offline_upgrade_bootstraps_and_removes_auth_schema():
    result = subprocess.run(
        [
            str(ROOT / ".venv/bin/alembic"),
            "-c",
            "src/shared/database/alembic.ini",
            "upgrade",
            "head",
            "--sql",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    sql = result.stdout
    assert "CREATE SCHEMA IF NOT EXISTS auth" in sql
    assert sql.index("CREATE SCHEMA IF NOT EXISTS auth") < sql.index('CREATE TABLE auth."Role"')
    assert 'DROP TABLE auth."Session"' in sql
    assert "DROP SCHEMA auth" in sql
    assert sql.index('DROP TABLE auth."Session"') < sql.index("DROP SCHEMA auth")
    assert 'CREATE TABLE profile."User"' in sql
    assert 'CREATE TABLE enterprise."Company"' in sql
