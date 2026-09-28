"""Company feature module."""

from src.modules.profile.features.company.models import Company
from src.modules.profile.features.company.router import router

__all__ = ["Company", "router"]
