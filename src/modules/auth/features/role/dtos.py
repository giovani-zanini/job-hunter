from pydantic import BaseModel, Field, field_validator


class CreateRoleRequest(BaseModel):

    name: str = Field(..., description="Role name")
    description: str | None = Field(None, description="Role description")
