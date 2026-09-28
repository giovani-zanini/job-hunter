"""Job Finder CLI — administrative operations."""

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, AsyncGenerator

import typer

from src.shared.database import sql_client

from src.modules.auth.features.role.models import Role  # noqa: F401
from src.modules.auth.features.account.models import UserAccount  # noqa: F401
from src.modules.auth.features.identity.models import Auth  # noqa: F401
from src.modules.auth.features.session.models import Session  # noqa: F401

app = typer.Typer(
    name="job-finder",
    help="Job Finder administrative CLI.",
    no_args_is_help=True,
    invoke_without_command=True,
)

role_app = typer.Typer(help="Manage roles.", no_args_is_help=True)
app.add_typer(role_app, name="role")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _db_session() -> AsyncGenerator:
    """Set up a write DB session, yield it, then tear down the engine."""
    sql_client.connect_to_database()
    try:
        async with sql_client.get_session("write") as session:
            yield session
    finally:
        await sql_client.disconnect_from_database()


def _load_json(path: Path) -> list:
    if not path.exists():
        typer.echo(f"Error: file not found: {path}", err=True)
        raise typer.Exit(code=1)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# role commands
# ---------------------------------------------------------------------------


@role_app.command("create")
def role_create(
    json_path: Annotated[
        Path,
        typer.Option("--json", help="Path to JSON file with an array of role objects."),
    ] = Path("roles.json"),
) -> None:
    """Create roles from a JSON file.

    Example:
        job-finder role create --json roles.json

    JSON format:
        [{"name": "admin", "description": "Administrator role"}]
    """
    from src.modules.auth.features.role.dtos import CreateRoleRequest
    from src.modules.auth.seed import seed_roles

    raw = _load_json(json_path)
    roles = [CreateRoleRequest(**item) for item in raw]

    async def _run() -> None:
        async with _db_session() as session:
            await seed_roles(session, roles)

    asyncio.run(_run())
    typer.echo(f"✓ {len(roles)} role(s) processed.")


if __name__ == "__main__":
    app()
