from pydantic import BaseModel, ConfigDict


class AuthenticatedUser(BaseModel):
    """Lightweight identity payload returned by auth dependencies.

    This is the contract other modules depend on — not SQLAlchemy models.
    If auth becomes a microservice, this DTO stays the same and the
    dependency implementation changes to an HTTP call.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role_name: str
    is_active: bool
