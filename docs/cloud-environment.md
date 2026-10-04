# Ambiente de desenvolvimento cloud

Use o checkout isolado existente em `/workspace/job-hunter`. Preserve a branch e os arquivos do usuário; não crie outro worktree nem troque de branch automaticamente.

Os módulos ativos são `profile` e `enterprise`. A aplicação é servida por `src.main:app`. Poetry gerencia as dependências do projeto; pip apenas prepara a instalação separada do próprio Poetry.

## Instalação

```bash
cd /workspace/job-hunter
bash scripts/cloud-install.sh
```

O script prepara Poetry 2.2.1, `.venv` e uma cópia externa dos metadados em `/workspace/.cloud-setup/job-hunter/resolver`. Usa `poetry.lock` do checkout quando disponível; sem ele, resolve e mantém o lock somente no cache externo. Uma resolução sem lock versionado pode variar entre ambientes. O cache só é marcado como válido após instalação bem-sucedida, e mudanças nos inputs invalidam a resolução anterior.

`poetry sync --all-extras` instala dependências de aplicação, testes e desenvolvimento e remove pacotes que deixaram de fazer parte dessa resolução. Arquivos versionados e configurações locais existentes são preservados. O instalador não exige uma árvore Git limpa, não aplica migrações, não gera chaves de autenticação e não semeia papéis.

Se `.env` ainda não existe e não há URLs de banco injetadas, cria apenas as duas URLs para o PostgreSQL local de desenvolvimento definido no Compose. Bindings existentes têm precedência e nunca são persistidos pelo setup. Quando houver bindings injetados, configure `DATABASE_URL` (asyncpg) e `DATABASE_SYNC_URL` (psycopg2) para o mesmo banco; não misture o banco remoto com defaults locais. Não imprima credenciais.

O setup é relocável: `JOB_HUNTER_CLOUD_SETUP_DIR` seleciona o cache externo e o checkout é determinado pela localização do script. No CI ele usa o diretório temporário do runner.

## Startup

Confira o estado dos serviços restaurados antes de iniciá-los. O Compose usa credenciais exclusivamente locais de desenvolvimento.

```bash
docker compose -f docker/docker-compose.yml up -d postgres --wait --wait-timeout 90
# Apenas no banco de desenvolvimento previamente conferido:
.venv/bin/alembic -c src/shared/database/alembic.ini upgrade head
.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
```

A migração de remoção do módulo antigo é irreversível sem backup. Nunca a aplique a um banco com dados úteis sem revisar destino, impacto e recuperação. Use os controles de preview da plataforma para compartilhar a aplicação; loopback serve apenas para validação interna.

## Verificações sem PostgreSQL

```bash
.venv/bin/ruff check src scripts tests
.venv/bin/python -m pytest tests/unit -q
.venv/bin/python scripts/generate_json_schemas.py --check
PRE_COMMIT_HOME=/tmp/job-hunter-pre-commit-cache .venv/bin/pre-commit validate-config
git diff --check
```

## Integração e E2E

Os testes fazem `TRUNCATE` e criam/removem bancos. Use a instância PostgreSQL local e o banco descartável `job_finder_test`. A conta local `user` precisa de `CREATEDB`. Confira se já existe esse banco antes de criá-lo:

```bash
docker exec job_finder_postgres psql -U user -d postgres -Atqc "SELECT datname FROM pg_database WHERE datname = 'job_finder_test'"
# Se o banco ainda não existe:
docker exec job_finder_postgres createdb -U user job_finder_test
```

A sequência abaixo define explicitamente as URLs de teste locais e executa migrações e a suíte nesse destino:

```bash
TEST_DATABASE_URL=postgresql+asyncpg://user:password@127.0.0.1:5432/job_finder_test \
TEST_DATABASE_SYNC_URL=postgresql+psycopg2://user:password@127.0.0.1:5432/job_finder_test \
bash scripts/test.sh
```

`.env.test` é carregado sem sobrescrever bindings já definidos. Evite carregar `.env` indiscriminadamente no shell; não reutilize a URL do banco de desenvolvimento como URL de teste. Os testes de integração criam bancos temporários adicionais e os removem ao terminar.

Informe resultados efetivamente medidos na tarefa. Números de execuções anteriores não comprovam o estado atual; testes pulados por falta de configuração de banco são cobertura incompleta.

Instruções do agente e ativação de ferramentas: [AGENTS.md](../AGENTS.md) e [docs/codex.md](codex.md).
