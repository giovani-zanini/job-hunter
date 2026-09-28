---
name: Git Conventions
description: Enforces Conventional Commits, Git Flow branch naming, and semantic versioning across the project
applyTo: '**'
---

# Git Conventions — Quick Reference

## Conventional Commits

Format: `<type>(<scope>): <description>`

| Type | Purpose |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring (no behavior change) |
| `docs` | Documentation |
| `style` | Formatting only |
| `test` | Tests |
| `chore` | Maintenance |
| `perf` | Performance |
| `ci` | CI/CD |
| `build` | Build system |
| `revert` | Revert previous commit |

Breaking changes: `feat(scope)!: description` + `BREAKING CHANGE:` footer.

## Scopes (matching project modules)

| Scope | Maps to |
|---|---|
| `auth` | `src/modules/auth/` |
| `profile` | `src/modules/profile/` |
| `enterprise` | `src/modules/enterprise/` |
| `config` | `src/modules/config/` |
| `shared` | `src/shared/` |
| `auth/session` | `src/modules/auth/features/session/` |
| `profile/skill` | `src/modules/profile/features/skill/` |
| `enterprise/vacancy` | `src/modules/enterprise/features/vacancy/` |
| `db` | Migrations (`alembic/`) |
| `docker` | Docker configs |
| `deps` | Dependency changes (`pyproject.toml`) |
| `tests` | Test files |

## Branch Naming (Git Flow)

| Prefix | Base | Target | Example |
|---|---|---|---|
| `feat/` | `dev` | `dev` | `feat/add-vacancy-filter` |
| `fix/` | `dev` | `dev` | `fix/auth-token-refresh` |
| `hotfix/` | `master` | `master` + `dev` | `hotfix/critical-login-bug` |
| `release/` | `dev` | `master` + `dev` | `release/1.2.0` |
| `support/` | `master` | `master` | `support/legacy-api-compat` |

Rules:
- Lowercase kebab-case
- Include issue number if available: `feat/42-add-vacancy-filter`
- Max ~50 characters

## Semantic Versioning

Format: `vMAJOR.MINOR.PATCH`

- `BREAKING CHANGE` → MAJOR
- `feat` → MINOR
- `fix`, `perf`, `refactor` → PATCH
