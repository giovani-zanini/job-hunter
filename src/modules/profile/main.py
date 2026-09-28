"""Job Finder API - Main Application Entry Point."""

import importlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from src.shared.database import sql_client


# Feature registry: maps feature names to their router module paths
FEATURES = {
    "skill": "src.modules.profile.features.skill.router",
    "company": "src.modules.profile.features.company.router",
    "link": "src.modules.profile.features.link.router",
    "profile": "src.modules.profile.features.profile.router",
    "experience": "src.modules.profile.features.experience.router",
    "education": "src.modules.profile.features.education.router",
    "certificate": "src.modules.profile.features.certificate.router",
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


def start_app(app: FastAPI, features: list[str] | str | None = None):
    """Start the profile module with specified features.

    Args:
        app: FastAPI application instance. If None, creates a standalone app.
        features: List of feature names to load, or '*' to load all. If None, loads all features.
    """

    # Determine which features to load
    if features is None or features == "*":
        features_to_load = list(FEATURES.keys())
    else:
        features_to_load = features

    # Dynamically import and register routers for selected features
    for feature_name in features_to_load:
        if feature_name not in FEATURES:
            raise ValueError(f"Unknown profile feature: {feature_name}")

        module_path = FEATURES[feature_name]
        module = importlib.import_module(module_path)
        router: APIRouter = module.router
        app.include_router(router, prefix="/api/v1")
