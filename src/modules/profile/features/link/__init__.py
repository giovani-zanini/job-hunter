"""Link feature module."""

from src.modules.profile.features.link.models import Link, ProfileLink
from src.modules.profile.features.link.router import router

__all__ = ["Link", "ProfileLink", "router"]
