# Auth settings now come from src.shared.config.
# Re-export for backward compatibility.
from src.shared.config import Settings, get_settings

AuthSettings = Settings
settings = get_settings()

__all__ = ["AuthSettings", "settings"]
