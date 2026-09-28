"""Enterprise module — main entry point.

Manages the job vacancy domain: companies, locations, segments, contracts,
requirements, responsabilities, vacancies and scraping metadata.
"""

import importlib

from fastapi import FastAPI, APIRouter

from src.shared.database import sql_client


FEATURES = {
    "location": "src.modules.enterprise.features.location.router",
    "segment": "src.modules.enterprise.features.segment.router",
    "company": "src.modules.enterprise.features.company.router",
    "contract": "src.modules.enterprise.features.contract.router",
    "requirement": "src.modules.enterprise.features.requirement.router",
    "responsability": "src.modules.enterprise.features.responsability.router",
    "vacancy": "src.modules.enterprise.features.vacancy.router",
    "meta": "src.modules.enterprise.features.meta.router",
}


def start_app(app: FastAPI, features: list[str] | str | None = None):
    """Start the enterprise module with the specified features.

    Args:
        app: FastAPI application instance.
        features: List of feature names to load, or '*' to load all.
    """
    if features is None or features == "*":
        features_to_load = list(FEATURES.keys())
    else:
        features_to_load = features

    for feature_name in features_to_load:
        if feature_name not in FEATURES:
            raise ValueError(
                f"Unknown feature '{feature_name}' in enterprise module. "
                f"Available features: {list(FEATURES.keys())}"
            )
        module_path = FEATURES[feature_name]
        module = importlib.import_module(module_path)
        router: APIRouter = module.router
        app.include_router(router, prefix="/api/v1")
