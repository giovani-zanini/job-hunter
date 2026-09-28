# Copilot Instructions - Job Finder

## Project Overview

FastAPI application for automating job applications using AI. The backend is split into independent **modules** (`profile` and `auth`), each with its own FastAPI app, sharing a global `src/shared/` package.

**Stack:** Python 3.12+, FastAPI, SQLAlchemy 2.x (async), PostgreSQL, Alembic migrations, Pydantic v2

## Architecture

### Module Structure

```
src/
├── shared/                    # Global shared utilities (all modules use this)
│   ├── config.py              # DATABASE_URL, dotenv loading
│   ├── dtos.py                # Shared NamedTuples (Association, Message)
│   ├── exceptions.py          # AppException hierarchy (404, 409, 422, 401, 403)
│   ├── handlers.py            # FastAPI exception handlers
│   ├── services.py            # Generic CRUD helpers
│   └── database/
│       ├── sql_client.py      # Base, async engine, session management
│       └── sql_mixins.py      # SoftDeleteMixin, TimestampMixin
├── profile/                   # Profile module (manages professional data)
│   ├── main.py                # FastAPI app entry point
│   └── features/              # Feature packages
│       ├── user/              # Anchor user for profile data
│       ├── profile/
│       ├── skill/
│       ├── company/
│       ├── link/
│       ├── experience/
│       ├── education/
│       └── certificate/
└── auth/                      # Auth module (authentication & authorization)
    ├── main.py                # FastAPI app entry point
    ├── shared/                # Auth-specific shared utilities
    │   ├── config.py          # AuthSettings (JWT secrets, lockout config)
    │   ├── security.py        # Password hashing, JWT creation/decode
    │   └── dependencies.py    # get_current_user, require_role
    └── features/
        ├── role/
        ├── access_policy/
        ├── user/
        ├── auth/
        └── session/
```

### Feature-Based Module Structure

Each feature in `src/{module}/features/` follows a strict layered pattern:

```
src/{module}/features/{feature}/
├── models.py    # SQLAlchemy models (extend Base + mixins)
├── dtos.py      # Pydantic schemas (Request/Response/Filter patterns)
├── services.py  # Database operations (query building, CRUD)
├── handlers.py  # Business logic orchestration (calls services, manages transactions)
├── router.py    # FastAPI endpoints (calls usecases, handles HTTP concerns)
```

**Data flow:** `router.py` → `handlers.py` → `services.py` → `models.py`

### PostgreSQL Schema Separation

Each module uses its own PostgreSQL schema to isolate tables within the same database:

- **`profile`** schema: All profile module tables (`User`, `Profile`, `Skill`, etc.)
- **`auth`** schema: All auth module tables (`User`, `Role`, `Auth`, `Session`, `AccessPolicy`)

```python
# Profile models
class Skill(Base, SoftDeleteMixin):
    __tablename__ = "Skill"
    __table_args__ = {"schema": "profile"}

# Auth models
class Role(Base):
    __tablename__ = "Role"
    __table_args__ = {"schema": "auth"}
```

ForeignKey references must be schema-qualified:
```python
role_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth.Role.id"))
user_id: Mapped[int] = mapped_column(Integer, ForeignKey("profile.User.id"))
```

### Key Conventions

**Models** (`models.py`):
- Inherit from `Base` (from `src.shared.database.sql_client`)
- Profile models use `SoftDeleteMixin` for soft delete support
- Auth models use `TimestampMixin` where needed (no soft delete)
- Use `Mapped[T]` and `mapped_column()` for type hints
- Table names are PascalCase: `__tablename__ = "Skill"`
- Always include `__table_args__` with the module's schema

**DTOs** (`dtos.py`):
- `*CreateRequest`, `*UpdateRequest` for input
- `*Response`, `*DetailResponse` for output
- `*FilterParams` for list endpoints
- Use `ConfigDict(from_attributes=True)` for ORM serialization

**Handlers** (`handlers.py`):
- Orchestrate validation + service calls
- Always call `` at end
- Use shared helpers: `ensure_exists()`, `ensure_unique()`, `ensure_association()`
- Return Pydantic response models

**Routers** (`router.py`):
- Use dependency injection for sessions:
  - `sql_client.get_sql_default_session` for write operations
  - `sql_client.get_sql_read_session` for read-only queries
- All routes under `/api/v1` prefix

### Global Shared Utilities (`src/shared/`)

**Database** (`shared/database/`):
- `sql_client.py`: Async engine, session management, `Base` class
- `sql_mixins.py`: `SoftDeleteMixin`, `TimestampMixin`

**Services** (`shared/services.py`):
- `ensure_exists(session, Model, id)` - Raise 404 if not found
- `ensure_unique(session, Model, field, value)` - Raise 409 if duplicate
- `ensure_association(session, Model, config, type)` - Validate relationships
- `get_one_by_field()`, `get_many_by_field()` - Generic queries
- `create()`, `delete()` - Generic CRUD

**Exceptions** (`shared/exceptions.py`):
- `NotFoundException` (404), `ConflictException` (409), `ValidationException` (422)
- `UnauthorizedException` (401), `ForbiddenException` (403), `BadRequestException` (400)
- All inherit from `AppException` with `status_code` and `detail`

### Auth Module Shared (`src/auth/shared/`)

- `config.py`: `AuthSettings` via pydantic-settings (JWT secret, expiration, lockout)
- `security.py`: `hash_password()`, `verify_password()` (Argon2), `create_access_token()`, `create_refresh_token()` (HS256), `decode_token()`, `hash_refresh_token()` (SHA-256), `generate_recovery_token()`
- `dependencies.py`: `get_current_user` (Bearer JWT → User), `require_role(name)` (RBAC guard)

## Database & Migrations

```bash
# Start PostgreSQL
docker compose -f docker/docker-compose.yml up postgres -d

# Run migrations (use helper script)
./migrate.sh upgrade          # Apply pending
./migrate.sh create "message" # New migration (autogenerate)
./migrate.sh downgrade        # Rollback last

# Or use alembic directly
alembic upgrade head
alembic revision --autogenerate -m "Description"
```

**Important:** Models must be imported in `alembic/env.py` for autogenerate to detect changes. Schemas `profile` and `auth` are auto-created in `run_migrations_online()`.

## Development Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Run profile module
uvicorn src.profile.main:app --reload --port 8000

# Run auth module
uvicorn src.auth.main:app --reload --port 8001

# API docs
# Profile: http://localhost:8000/docs
# Auth:    http://localhost:8001/docs
```

## Code Patterns

### Adding a New Feature

1. Create `src/{module}/features/{name}/` with: `models.py`, `dtos.py`, `services.py`, `handlers.py`, `router.py`
2. Add `__table_args__ = {"schema": "{module}"}` to every model
3. Add model import to `alembic/env.py`
4. Create migration: `./migrate.sh create "Add {name} model"`
5. Register router in `src/{module}/main.py`

### Soft Delete Pattern (Profile module)

```python
# Models use SoftDeleteMixin
skill.soft_delete()  # Sets deleted_at timestamp
skill.restore()      # Clears deleted_at

# Queries respect soft delete
await get_one_by_field(session, Skill, "id", 1, include_deleted=False)
```

### Association Tables

Many-to-many relationships use explicit join models (e.g., `ProfileSkills`, `ExperienceSkills`) with their own columns like `level`, `experience_years`.

## Import Conventions

```python
# Global shared utilities
from src.shared import services as shared_services
from src.shared import dtos as shared_dtos
from src.shared import exceptions
from src.shared.database import sql_client
from src.shared.database.sql_client import Base
from src.shared.database.sql_mixins import SoftDeleteMixin, TimestampMixin

# Within module features
from src.profile.features.skill import dtos
from src.profile.features.skill import services
from src.profile.features.skill.models import Skill

from src.auth.features.role import dtos
from src.auth.features.role import services
from src.auth.features.role.models import Role

# Auth module shared
from src.auth.shared.config import auth_settings
from src.auth.shared.security import hash_password, verify_password
from src.auth.shared.dependencies import get_current_user, require_role
```
