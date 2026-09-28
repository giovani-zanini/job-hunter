"""Auth Module - Main Application Entry Point."""

import importlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from src.shared.database import sql_client


# Feature registry: maps feature names to their router module paths
FEATURES = {
    "account": "src.modules.auth.features.account.router",
    "identity": "src.modules.auth.features.identity.router",
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup - Database tables are managed by Alembic migrations
    sql_client.connect_to_database()
    await sql_client.test_sql_connection()
    yield
    # Shutdown
    await sql_client.disconnect_from_database()


def start_app(
    app: FastAPI | None = None,
    features: list[str] | str | None = None,
):
    """Start the auth module with specified features.

    Args:
        app: FastAPI application instance. If None, creates a standalone app.
        features: List of feature names to load, or '*' to load all. If None, loads all features.
    """
    if not app:
        app = FastAPI(
            title="Job Finder Auth API",
            description="API de autenticação e autorização do Job Finder",
            version="1.0.0",
            lifespan=lifespan,
        )

    # Determine which features to load
    if features is None or features == "*":
        features_to_load = list(FEATURES.keys())
    else:
        features_to_load = features

    # Dynamically import and register routers for selected features
    for feature_name in features_to_load:
        if feature_name not in FEATURES:
            raise ValueError(f"Unknown auth feature: {feature_name}")

        module_path = FEATURES[feature_name]
        module = importlib.import_module(module_path)
        router: APIRouter = module.router
        app.include_router(router, prefix="/api/v1")
