# Orientações do repositório

Siga a arquitetura, os comandos e as decisões documentados em `AGENTS.md`.
Este projeto FastAPI expõe APIs públicas de `profile` e `enterprise` por
`src/main.py`. Features ficam em `src/modules/<module>/features/` e persistência
e Alembic em `src/shared/database/`.

`profile.User` é uma âncora local: um único proprietário anônimo vincula novos
registros de perfil. Registros anteriores preservam seus vínculos e acesso
público. Preserve esse contrato.

Importe modelos ativos em `src/shared/database/alembic/env.py` para autogeração.
Preserve migrações históricas e avalie o estado final do upgrade.

Commits são escritos em inglês no padrão Conventional Commits; documentação e
revisões são escritas em português brasileiro. Consulte também `SECURITY.md`.
Use `tests/unit` e o check de JSON Schemas para validações sem PostgreSQL.
Testes de banco exigem um destino descartável e as variáveis `TEST_DATABASE_URL`
e `TEST_DATABASE_SYNC_URL`, conforme `docs/cloud-environment.md`.
