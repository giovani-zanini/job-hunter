"""FastAPI dependencies for the enterprise module.

Re-exports auth module dependencies. Enterprise endpoints use JWT auth
directly without requiring a module-local user record.
"""

from src.modules.auth.shared.adapters import get_current_user
from src.modules.auth.shared.adapters import require_role  # re-export

__all__ = ["get_current_user", "require_role"]
