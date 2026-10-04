"""Application configuration and module loading.

This module provides a unified Settings class loaded from environment variables,
a singleton get_settings() function, module loading utilities, and app setup helpers.

Usage:
    from src.shared.config import get_settings, load_modules, setup_app

    settings = get_settings()
    load_modules(app)
    setup_app(app)
"""

from functools import lru_cache
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.shared import adapters


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/job_finder"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False

    CORS_ORIGINS: List[str] = ["*"]
    CORS_CREDENTIALS: bool = True

    ENABLED_MODULES: List[str] = ["profile", "enterprise"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def load_modules(app: FastAPI) -> None:
    import importlib

    settings = get_settings()
    module_registry = {
        "profile": "src.modules.profile.main",
        "enterprise": "src.modules.enterprise.main",
    }

    for module_name in settings.ENABLED_MODULES:
        if module_name not in module_registry:
            raise ValueError(
                f"Unknown module '{module_name}'. "
                f"Available modules: {list(module_registry.keys())}"
            )
        module = importlib.import_module(module_registry[module_name])
        module.start_app(app)


def setup_app(app: FastAPI) -> None:
    settings = get_settings()

    adapters.setup_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
