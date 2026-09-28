"""Pydantic schemas for Auth feature."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Request Schemas ---


class LoginRequest(BaseModel):
    """Schema for login request."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class ChangePasswordRequest(BaseModel):
    """Schema for changing password."""

    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing a token."""

    refresh_token: str = Field(..., description="Current refresh token")


class RequestRecoveryRequest(BaseModel):
    """Schema for requesting a password recovery token."""

    email: EmailStr = Field(..., description="User email address")


class ResetPasswordRequest(BaseModel):
    """Schema for resetting password with recovery token."""

    email: EmailStr = Field(..., description="User email address")
    recovery_token: str = Field(..., description="Recovery token received")
    new_password: str = Field(
        ..., min_length=8, max_length=128, description="New password"
    )


# --- Response Schemas ---


class TokenResponse(BaseModel):
    """Schema for token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RecoveryTokenResponse(BaseModel):
    """Schema for password recovery response."""

    message: str


# --- Token Payload ---


class AccessTokenPayload(BaseModel):
    """Schema for decoded JWT access token payload."""

    sub: int = Field(..., description="User ID (subject)")
    role: str = Field(..., description="User role name")
    type: str = Field(..., description="Token type (must be 'access')")
