# job-hunter

API FastAPI para dados de perfil profissional e empresas/vagas. As APIs de Profile e Enterprise são públicas: nenhuma rota exige login, token ou papel.

## Executar

Requisitos: Python 3.12+, Bash e PostgreSQL. O setup instala Poetry e as dependências em ambientes virtuais.

```bash
JOB_HUNTER_CLOUD_SETUP_DIR=/tmp/job-hunter-setup bash scripts/cloud-install.sh
# Defina DATABASE_URL (asyncpg) e DATABASE_SYNC_URL (psycopg2) para o mesmo banco.
./scripts/migrate.sh upgrade
.venv/bin/uvicorn src.main:app --reload
```

A documentação interativa fica em `http://localhost:8000/docs`. O projeto inclui um Compose para iniciar o PostgreSQL local: `docker compose -f docker/docker-compose.yml up -d postgres`.

A migração `a03e20261003` remove o schema `auth` e todos os dados de suas tabelas, além da antiga coluna `profile.User.external_id`. Ela preserva os IDs e vínculos existentes de Profile e os dados de Enterprise. Cria um único `profile.User` anônimo para as novas criações de Profile que precisam de `user_id`. Registros antigos continuam associados a seus usuários locais e ficam acessíveis publicamente. Essa migração é irreversível sem restauração de backup.

## Testes e contratos

Use um PostgreSQL de teste descartável e configure `TEST_DATABASE_URL` e `TEST_DATABASE_SYNC_URL` para ele. `./scripts/test.sh` executa as migrações e os testes. Os testes de integração criam bancos temporários separados na mesma instância PostgreSQL, então a conta de teste precisa de permissão `CREATEDB`.

Atualize os catálogos JSON Schema com `.venv/bin/python scripts/generate_json_schemas.py`; confira com `--check`. Veja [docs/json-schemas.md](docs/json-schemas.md).

## Codex e qualidade

As instruções do agente estão em [AGENTS.md](AGENTS.md) e a política de revisão de segurança em [SECURITY.md](SECURITY.md). Consulte [docs/codex.md](docs/codex.md) para instalar Codex/Superpowers, ativar os hooks e configurar as revisões no GitHub. [docs/cloud-environment.md](docs/cloud-environment.md) descreve o setup com Poetry e os bancos descartáveis.

Commits seguem [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) com mensagens em inglês. Documentação e revisões são escritas em português brasileiro. O CI verifica código, contratos, commits novos dos PRs, testes em PostgreSQL e vulnerabilidades conhecidas nas dependências.

Licença: GPL-3.0.
