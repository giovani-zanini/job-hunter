"""DTOs for profile module shared dependencies."""

from pydantic import BaseModel, ConfigDict


class ProfileUser(BaseModel):
    """Authenticated user in the context of the profile module.

    This DTO is returned by the profile-specific ``get_current_profile_user``
    dependency. It represents the row from the ``profile.User`` table that was
    either retrieved or auto-created based on the incoming JWT token.

    Attributes:
        id: Primary key of the ``profile.User`` row.
        external_id: Foreign reference to ``auth.User.id`` (auth module PK).
        role_name: Role name extracted from the JWT (forwarded from auth).
        is_active: Whether the auth user account is active.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    role_name: str
    is_active: bool
