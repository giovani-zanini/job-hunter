from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.shared.config import get_settings, load_modules, setup_app
from src.shared.database import sql_client

# Load application configuration
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup - Database tables are managed by Alembic migrations
    sql_client.connect_to_database()
    await sql_client.test_sql_connection()

    yield

    await sql_client.disconnect_from_database()


app = FastAPI(
    title="Job Finder API",
    description="Plataforma de automação de candidaturas com IA.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register modules and apply app-wide configuration
load_modules(app)
setup_app(app)


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}
