"""Education feature module."""

from src.modules.profile.features.education.models import (
    Education,
    EducationSkills,
    ProfileEducation,
)
from src.modules.profile.features.education.router import router

__all__ = ["Education", "EducationSkills", "ProfileEducation", "router"]
