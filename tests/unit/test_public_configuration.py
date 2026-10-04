"""Contracts for running the application without authentication."""

from src.shared.config import Settings


def test_settings_do_not_require_authentication_secrets(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("REFRESH_SECRET_KEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.ENABLED_MODULES == ["profile", "enterprise"]
    assert "SECRET_KEY" not in type(settings).model_fields
    assert "REFRESH_SECRET_KEY" not in type(settings).model_fields


def test_openapi_has_no_authentication_routes_or_security_scheme():
    from src.main import app

    schema = app.openapi()
    paths = schema["paths"]

    assert "/api/v1/auth/token" not in paths
    assert "/api/v1/account/" not in paths
    assert not schema.get("components", {}).get("securitySchemes")
    for operations in paths.values():
        for operation in operations.values():
            if isinstance(operation, dict):
                assert not operation.get("security")


def test_anonymous_user_marker_is_part_of_profile_model():
    from src.modules.profile.features.user.models import User

    assert "is_anonymous" in User.__table__.columns
    assert "external_id" not in User.__table__.columns
