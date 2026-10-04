# Remoção de Auth e APIs públicas — Implementation Plan

> **Estado em 2026-10-03:** implementação preparada na branch `feat/remove-auth`.
> Testes unitários e SQL offline passaram; testes com PostgreSQL permanecem sem execução
> porque a instância de teste não está acessível neste ambiente. As referências abaixo
> à “etapa atual” descrevem a fase original de planejamento.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. A execução ainda não foi escolhida; a recomendação é execução nativa, com `executing-plans`, porque as mudanças de persistência, configuração e routers precisam ser integradas em conjunto.

**Goal:** Remover autenticação e autorização da aplicação e do banco de dados, mantendo Enterprise e Profile operacionais e usando um usuário anônimo para novos registros de Profile que exigem `user_id`.

**Architecture:** Enterprise será independente de qualquer identidade. Profile preservará sua tabela `User` e suas chaves estrangeiras, com um registro anônimo identificado por `is_anonymous`. Uma nova migração apagará o schema `auth` e removerá `profile.User.external_id`; routers e handlers deixarão de validar tokens, papéis e propriedade.

**Tech Stack:** Python >=3.12, FastAPI >=0.115.0, SQLAlchemy assíncrono >=2.0.0, PostgreSQL, Alembic >=1.13.0, Pydantic >=2.12.5,<3.0.0, pytest, pytest-asyncio e HTTPX.

**Spec:** [Especificação consolidada neste arquivo](#especificação-consolidada). O pedido do usuário define o escopo; os detalhes técnicos abaixo são a proposta para revisão antes da implementação.

## Global Constraints

- Python >=3.12; preservar as faixas de versão dos componentes que continuarem necessários.
- Não adicionar um provedor de identidade, login alternativo, token opcional ou modo de bypass.
- Enterprise e Profile devem funcionar sem headers de autenticação ou indicação de usuário na requisição.
- Excluir as tabelas e os dados antigos de `auth`, conforme decisão explícita do usuário.
- Preservar os dados, IDs, chaves estrangeiras e associações existentes de `profile` e `enterprise`.
- Usar um único usuário anônimo para novas criações de Profile que exigem `user_id`; Enterprise não recebe um usuário artificial.
- Preservar as validações de domínio, paginação, filtros explícitos, soft delete e respostas 404, 409 e 422.
- Preservar as revisões Alembic já existentes; referências históricas a Auth ficam restritas ao suporte de migrações e à documentação histórica identificada como tal.
- Nenhuma alteração de código, execução de migração ou exclusão de dados faz parte da etapa atual: o entregável atual é este plano.

## Review Focus

1. Banco já populado: apagar Auth não deve remover ou reassociar registros de Profile e Enterprise. Cobertura: tarefa 1, `test_upgrade_preserves_domain_records`.
2. Banco novo e segunda execução de `upgrade head`: as migrações devem funcionar e o schema `auth` não deve reaparecer. Cobertura: tarefa 1, `test_fresh_database_and_repeated_upgrade`.
3. Criações simultâneas e usuário anônimo soft deleted: o identificador deve continuar único e reutilizável. Cobertura: tarefa 2, testes de concorrência e restauração.
4. Registros ligados a usuários antigos: devem ser listados, alterados e associados sem verificação de proprietário. Cobertura: tarefa 2, `test_existing_records_are_public` e `test_associations_on_existing_profile`.
5. Execução sem segredos de JWT e geração de schemas sem DTOs de identidade: a aplicação e o gerador devem funcionar. Cobertura: tarefas 3 e 4, testes de configuração e geração real dos catálogos.

## Especificação consolidada

### Intenção e decisões confirmadas

O usuário solicitou a remoção completa do módulo `auth`, responsável por autenticação e autorização, e das dependências de tokens e autorização nos demais módulos. Enterprise e Profile ficam públicos neste momento. O usuário confirmou também a exclusão das tabelas e dos dados antigos de autenticação no PostgreSQL; a referência a “ALS” foi esclarecida no contexto como `auth`.

O usuário sugeriu manter um usuário anônimo para não quebrar os relacionamentos com usuários. A inspeção mostrou que somente Profile possui esses vínculos; Enterprise usa as dependências de autenticação, mas seus modelos não dependem de `auth.User` nem de `profile.User`.

### Situação atual observada

- Repositório: `/workspace/job-hunter`, branch `development`, revisão inspecionada `108fd3f`; sem alterações de código realizadas nesta conversa.
- `src/shared/config.py` exige `SECRET_KEY` e `REFRESH_SECRET_KEY` e carrega `auth`, `profile` e `enterprise` por padrão.
- Os sete routers de Profile e os oito routers de Enterprise dependem de identidade e papel.
- Profile resolve sua identidade por `profile.User.external_id`, um inteiro único e obrigatório que representa o ID de Auth. Não há uma FK entre essa coluna e o schema `auth`.
- Profile, Link, Experience, Education e Certificate possuem FKs obrigatórias para `profile.User.id`; Skill e Company não precisam desse vínculo.
- Os handlers de Profile verificam proprietário em alterações, exclusões e associações de perfis.
- O head Alembic atual é `1448ab8c1969`. As tabelas de Auth que permanecem nesse head são `Session`, `Auth`, `User` e `Role`. `AccessPolicy` já foi apagada em `cdf43b63f5ff`.
- O CLI `src/cli.py` contém somente administração de papéis. `scripts/test.sh` ainda chama esse CLI e o setup E2E registra um usuário e faz login.
- Catálogos JSON Schema incluem `AuthenticatedUser`, `ProfileUser` e campos de `external_id`; o gerador importa incondicionalmente os DTOs compartilhados dos dois módulos.
- Os `__init__.py` de Company, Link, Experience, Education e Certificate de Profile importam routers ao importar seus modelos. Essa carga indireta também traz Auth para o Alembic e precisa ser removida.
- A tentativa inicial de executar `.venv/bin/python -m pytest -q --maxfail=1` terminou em timeout durante o startup da aplicação, antes dos testes, na preparação da conexão com o banco. Isso não constitui uma baseline aprovada. A validação futura precisa de PostgreSQL de teste acessível.

### Persistência e usuário anônimo

Manter `profile.User.id`, `deleted_at` e todos os relacionamentos atuais. Remover `external_id` dos modelos, DTOs, filtros e serviços. Adicionar `is_anonymous: bool`, obrigatório, com default de aplicação e de servidor `false`; todos os usuários antigos permanecem com `false`.

Criar o índice único parcial `uq_profile_User_anonymous` sobre `is_anonymous`, com predicado `is_anonymous = true`. Isso permite vários usuários antigos e garante no máximo um usuário anônimo, inclusive se ele estiver soft deleted. Seu ID será gerado pela sequência existente, sem fixar valores como 0 ou 1 e sem reutilizar a identidade de uma pessoa antiga.

A migração cria o anônimo ativo. O serviço `get_or_create_anonymous_user(session: AsyncSession) -> User` reutiliza esse registro, cria quando ausente com proteção de conflito no PostgreSQL e restaura o mesmo registro se estiver soft deleted. Não faz commit próprio; a sessão da operação controla commit e rollback.

A dependência `get_anonymous_user_id(db_session: AsyncSession = Depends(sql_client.get_sql_default_session)) -> int` será usada somente nos cinco endpoints de criação que precisam de `user_id`. A sessão é a mesma dependência de escrita usada pelo endpoint. Leituras, atualizações, exclusões e associações não precisam resolver ou criar um usuário.

Os registros antigos mantêm seus `user_id` originais. Todos podem ser acessados sem autorização. O cliente não escolhe um proprietário para novas criações.

### Remoção de acesso e contratos

Remover `get_current_user`, `get_current_profile_user`, `require_role`, `_require_default_role`, `current_user`, `AuthenticatedUser` e `ProfileUser` dos fluxos ativos. Remover `_check_profile_ownership` e as comparações de `resource.user_id` com o usuário da requisição.

Handlers de criação de Profile, Link, Experience, Education e Certificate continuam recebendo `user_id: int` como vínculo de persistência. Handlers de alteração, exclusão e associação perdem o parâmetro usado exclusivamente para autorização. Antes de remover uma verificação de propriedade que também garantia existência, preservar a validação de existência no handler ou confirmar que o serviço já a executa.

As listagens deixam de atribuir implicitamente `filters.user_id` a uma identidade da requisição. Filtros internos de domínio por `user_id` podem permanecer se úteis aos serviços; não restringem acesso nem introduzem uma nova exigência na API pública.

Preservar os paths, métodos, payloads de domínio e `user_id` nas respostas dos recursos que já o expõem. Remover as rotas de conta, login, refresh, senha e recuperação. Remover requisitos e esquemas de segurança do OpenAPI.

### Migração e histórico

Criar `src/shared/database/alembic/versions/a03e20261003_remove_auth_and_add_anonymous_user.py`, com `revision = "a03e20261003"` e `down_revision = "1448ab8c1969"`.

Na mesma transação: adicionar o marcador e índice do anônimo; remover o índice de `external_id` e a coluna; inserir o anônimo; apagar `auth.Session`, `auth.Auth`, `auth.User` e `auth.Role`, nessa ordem; apagar o schema `auth`. Usar exclusões explícitas e `DROP SCHEMA auth` sem `CASCADE`, para que dependências ou objetos inesperados impeçam a execução em vez de serem apagados silenciosamente. Não alterar tabelas ou associações de Enterprise nem os dados existentes de Profile.

Remover os imports de modelos Auth do `alembic/env.py` e as importações antecipadas de routers nos cinco `__init__.py` de Profile; os routers já são carregados explicitamente pelo registro de features. Importar modelos para migração não deve registrar modelos de Auth indiretamente. As revisões antigas ainda precisam do schema `auth` ao migrar um banco vazio: criá-lo somente no bootstrap de um banco sem revisão Alembic. O upgrade completo o exclui ao chegar à nova revisão. Rodar `upgrade head`, `current` ou `check` em um banco já atualizado não deve recriá-lo. A geração SQL offline desde a base também deve incluir o bootstrap de `profile`, `enterprise` e `auth`, sem importar o módulo removido.

Essa migração apaga dados de autenticação e a antiga correspondência `external_id`. Seu `downgrade()` deve levantar `RuntimeError` antes de executar SQL, explicando que a reversão exige restauração de backup. Não apresentar uma recriação de tabelas vazias como recuperação dos dados. A exclusão já está autorizada pelo usuário; os ensaios serão feitos em bancos descartáveis de teste.

### Limpeza e documentação

Excluir o módulo Auth, seus testes exclusivos, os adapters de identidade de Enterprise e os DTOs compartilhados de identidade. Excluir o CLI de papéis e seu entry point. Remover configurações de JWT, expiração, lockout e segredos dos defaults e exemplos; manter a configuração de banco e CORS.

Remover `python-jose[cryptography]`, `passlib[argon2]` e `typer` das dependências e atualizar o lockfile com o gerenciador do projeto, sem atualizar desnecessariamente os demais pacotes. Remover o extra `email` de Pydantic se confirmado que nenhum DTO remanescente usa `EmailStr` ou outra capacidade desse extra.

Regenerar schemas. Atualizar README, instruções do repositório, DBML de Profile e a coleção pública de exemplos. Excluir o DBML de autenticação e a coleção `Job Finder Auth API`; remover exemplos de Users que apontem para rotas inexistentes. Preservar `docs/auth-service-research.md` como pesquisa histórica, identificando que o módulo foi removido e corrigindo referências locais quebradas.

## Tarefa 1: Persistência, migração e preservação dos dados

**Files:**

- Create: `src/shared/database/alembic/versions/a03e20261003_remove_auth_and_add_anonymous_user.py`.
- Modify: `src/shared/database/alembic/env.py` e `src/modules/profile/features/user/models.py`.
- Modify: `src/modules/profile/features/company/__init__.py`, `link/__init__.py`, `experience/__init__.py`, `education/__init__.py` e `certificate/__init__.py`.
- Create/Test: `tests/integration/conftest.py` e `tests/integration/test_remove_auth_migration.py`.
- Modify: `tests/conftest.py`; mover fixtures específicas de E2E para `tests/e2e/conftest.py`, mantendo o carregamento de ambiente global.

**Interfaces:** Consome a revisão `1448ab8c1969`. Produz a revisão `a03e20261003`, `User.is_anonymous`, o índice `uq_profile_User_anonymous` e um anônimo ativo. As fixtures de integração criam bancos PostgreSQL descartáveis, com URLs assíncrona e síncrona para o mesmo banco; a fixture de banco legado o prepara em `1448ab8c1969`. Não usam os truncates nem o cliente E2E.

- [ ] **Passo 1 — Preparar o ambiente de testes:** confirmar a conexão com PostgreSQL de teste e criar fixtures isoladas; impedir que os testes de migração utilizem o banco de dados normal da aplicação. Registrar a baseline e qualquer falha preexistente.
- [ ] **Passo 2 — Escrever `test_upgrade_preserves_domain_records`:** popular as quatro tabelas de Auth e um conjunto de dados de Profile e Enterprise com associações; salvar um snapshot dos registros previamente existentes; executar upgrade; verificar asserções abaixo. O snapshot compara os mesmos IDs e os campos de domínio preservados: para User, compara `id` e `deleted_at`, sem a coluna removida nem a nova linha anônima. Verificar separadamente que os usuários antigos receberam `is_anonymous = false`.

  ```python
  assert not schema_exists("auth")
  assert "external_id" not in table_columns("profile", "User")
  assert domain_snapshot_after == domain_snapshot_before
  assert len(anonymous_users) == 1
  assert anonymous_users[0]["deleted_at"] is None
  assert anonymous_users[0]["id"] not in legacy_user_ids
  ```

- [ ] **Passo 3 — Escrever `test_fresh_database_and_repeated_upgrade`:** migrar um banco vazio, executar novamente `upgrade head` e `alembic check`; verificar revisão `a03e20261003`, ausência do schema `auth`, exatamente um anônimo e nenhuma diferença de metadata.
- [ ] **Passo 4 — Escrever `test_downgrade_is_explicitly_irreversible`:** tentar downgrade após upgrade e verificar `RuntimeError`, revisão inalterada e dados de domínio preservados.
- [ ] **Passo 5 — Executar os testes novos:** `.venv/bin/python -m pytest tests/integration/test_remove_auth_migration.py -v --tb=short`. Antes da implementação, esperar falhas de comportamento por ausência da remoção, do marcador ou do bloqueio de downgrade; corrigir erros de infraestrutura antes de considerar o ciclo vermelho observado.
- [ ] **Passo 6 — Implementar a migração e o modelo:** seguir a especificação de persistência, sem reescrever revisões existentes.
- [ ] **Passo 7 — Ajustar a carga de modelos:** remover as importações de router dos cinco `__init__.py`, preservando seus exports de modelos; em `alembic/env.py`, carregar somente modelos remanescentes e preservar bootstrap histórico online e offline. Confirmar que a metadata de migração não contém tabelas de `auth` e que a nova revisão não recria seu schema.
- [ ] **Passo 8 — Executar os testes da tarefa:** esperar todos os testes de migração aprovados. Gerar também `upgrade head --sql` e confirmar que a sequência inclui a exclusão de Auth. O SQL offline emitido deve poder migrar um banco descartável vazio ao mesmo estado final.
- [ ] **Passo 9 — Registrar o conjunto validado:** commit local sugerido `feat(db)!: remove auth tables and add anonymous profile user`. Esta tarefa não torna os routers antigos compatíveis; nenhuma etapa intermediária deve ser implantada isoladamente.

## Tarefa 2: Profile público e resolução do usuário anônimo

**Files:**

- Modify: `src/modules/profile/features/user/services.py`, `handlers.py` e `dtos.py`; `src/modules/profile/shared/adapters.py`.
- Delete: `src/modules/profile/shared/dtos.py`.
- Modify routers: `src/modules/profile/features/profile/router.py`, `link/router.py`, `experience/router.py`, `education/router.py`, `certificate/router.py`, `skill/router.py` e `company/router.py`.
- Modify handlers: `src/modules/profile/features/profile/handlers.py`, `link/handlers.py`, `experience/handlers.py`, `education/handlers.py` e `certificate/handlers.py`.
- Create/Test: `tests/integration/test_anonymous_user.py` e `tests/e2e/profile/test_public_access.py`.
- Modify/Test: os sete arquivos de testes existentes em `tests/e2e/profile/` e `tests/e2e/conftest.py`.

**Interfaces:** Consome `User.is_anonymous` e a nova migração. Produz `services.get_or_create_anonymous_user(session: AsyncSession) -> User`, `handlers.resolve_anonymous_user(session: AsyncSession) -> User` e `adapters.get_anonymous_user_id(db_session: AsyncSession = Depends(sql_client.get_sql_default_session)) -> int`. As assinaturas dos handlers preservam os parâmetros de domínio e removem somente a identidade usada para autorização; os callers devem mudar no mesmo conjunto.

- [ ] **Passo 1 — Escrever regressões do serviço:** `test_reuses_seeded_anonymous_user`, `test_creates_missing_anonymous_user`, `test_restores_same_anonymous_user` e `test_concurrent_creation_has_one_anonymous_user`. Usar sessões reais separadas, com commit por operação concorrente; verificar IDs iguais, uma única linha com `is_anonymous = true` e `deleted_at is None`. Verificar também que rollback de uma criação abortada não deixa um segundo usuário ou recurso parcial.
- [ ] **Passo 2 — Escrever regressões da API:** criação válida de Profile, Link, Experience, Education e Certificate sem headers retorna 201 e o mesmo `user_id` do anônimo. Skill e Company funcionam sem identidade e não criam usuários adicionais.
- [ ] **Passo 3 — Escrever `test_existing_records_are_public`:** inserir recursos associados a um usuário antigo com `is_anonymous = false`; verificar presença em listagens, GET 200, PUT 200 e DELETE com o contrato já existente, sem fornecer identidade.
- [ ] **Passo 4 — Escrever `test_associations_on_existing_profile`:** executar inclusão, alteração e remoção de skills e inclusão/remoção de links, experiências, educações e certificados em um perfil antigo; verificar sucesso e manter 404 para entidade inexistente e 409 para associação duplicada.
- [ ] **Passo 5 — Adaptar as fixtures E2E:** retirar seed de papéis, cadastro, credenciais, login e `auth_headers`; chamadas e factories passam a usar o cliente diretamente. Manter a limpeza de domínio e preservar o anônimo. Em testes que semeiam usuários antigos, limpar seus recursos e usuários adicionais depois do caso.
- [ ] **Passo 6 — Executar o ciclo vermelho:** `.venv/bin/python -m pytest tests/integration/test_anonymous_user.py tests/e2e/profile/test_public_access.py -v --tb=short`; observar falhas por ausência da resolução anônima ou por 401/403 da implementação atual.
- [ ] **Passo 7 — Implementar o serviço e a dependência:** tratar conflito usando o índice parcial e reutilizar/restaurar a linha existente. Remover serviços por `external_id` e `get_me`; atualizar DTOs e filtros de User para a identidade local.
- [ ] **Passo 8 — Atualizar routers e handlers:** aplicar a dependência anônima somente às cinco criações; retirar guards, proprietário e filtro implícito de listagens; preservar validações de existência e regras de domínio.
- [ ] **Passo 9 — Atualizar os testes existentes:** remover headers e parâmetros de autenticação das factories; transformar casos que exigiam 401 em verificações públicas com payload válido. Casos que enviam `{}` devem verificar 422 por dados ausentes, sem confundir ausência de autenticação com validade do payload.
- [ ] **Passo 10 — Executar a cobertura de Profile:** `.venv/bin/python -m pytest tests/integration/test_anonymous_user.py tests/e2e/profile -v --tb=short`; esperar aprovação dos testes de usuário, CRUD e associações.
- [ ] **Passo 11 — Registrar o conjunto validado:** commit local sugerido `feat(profile)!: expose profile operations with anonymous persistence`.

## Tarefa 3: Enterprise público e remoção do módulo e das dependências

**Files:**

- Modify routers: `src/modules/enterprise/features/company/router.py`, `location/router.py`, `segment/router.py`, `contract/router.py`, `requirement/router.py`, `responsability/router.py`, `vacancy/router.py` e `meta/router.py`.
- Delete: `src/modules/enterprise/shared/adapters.py`, `src/modules/enterprise/shared/dtos.py`, todos os arquivos de `src/modules/auth/`, `src/cli.py` e todos os arquivos de `tests/e2e/auth/`.
- Modify: `src/shared/config.py`, `src/shared/exceptions.py`, `pyproject.toml`, `poetry.lock`, `.env.sample` e `scripts/test.sh`.
- Create/Test: `tests/unit/test_public_configuration.py` e `tests/e2e/test_public_api_contract.py`.
- Modify/Test: os oito arquivos de testes existentes em `tests/e2e/enterprise/`.

**Interfaces:** `Settings` mantém configuração da aplicação/banco/CORS e usa `ENABLED_MODULES = ["profile", "enterprise"]`. `load_modules` aceita os módulos remanescentes. Nenhuma API de Enterprise consome identidade. Não há entry point `job-finder` nem configuração de segredos de autenticação.

- [ ] **Passo 1 — Escrever teste de configuração isolado:** limpar as variáveis `SECRET_KEY` e `REFRESH_SECRET_KEY` no processo de teste e instanciar `Settings(_env_file=None)`. Asserções: construção bem-sucedida e `settings.ENABLED_MODULES == ["profile", "enterprise"]`.
- [ ] **Passo 2 — Escrever teste de contrato público:** inspecionar o OpenAPI real e verificar ausência de `security` nas operações e de esquemas de segurança; chamar uma rota removida de login e uma de conta e verificar 404.
- [ ] **Passo 3 — Adaptar os oito conjuntos E2E de Enterprise:** retirar `auth_headers` de requests e factories; criação válida sem headers retorna 201, demais operações preservam seus contratos. Para Vacancy, CompanyUnit e Meta, criar os vínculos obrigatórios antes de testar o sucesso público.
- [ ] **Passo 4 — Executar o ciclo vermelho:** `.venv/bin/python -m pytest tests/unit/test_public_configuration.py tests/e2e/test_public_api_contract.py tests/e2e/enterprise -v --tb=short`; observar falhas por segredos obrigatórios, esquemas de segurança e guards atuais.
- [ ] **Passo 5 — Remover as dependências dos routers de Enterprise:** excluir identidade, guards, imports e DTOs sem introduzir dependência do usuário anônimo.
- [ ] **Passo 6 — Remover o módulo Auth e o CLI:** excluir arquivos e registrar somente Profile e Enterprise; remover exceções 401/403 que se tornarem sem uso.
- [ ] **Passo 7 — Limpar configuração e packaging:** retirar as configurações de JWT/lockout, o entry point e as dependências exclusivas indicadas na especificação; regenerar o lockfile sem upgrades amplos. Confirmar por busca os usos remanescentes antes de remover o extra `email`.
- [ ] **Passo 8 — Atualizar `scripts/test.sh`:** retirar o seed de papéis; garantir que o carregamento da configuração de teste acontece antes das migrações e que migração e pytest usam o mesmo banco descartável/de teste.
- [ ] **Passo 9 — Executar os testes da tarefa:** esperar configuração sem segredos, contratos públicos e CRUD de Enterprise aprovados; verificar instalação do projeto em ambiente limpo sem os pacotes removidos.
- [ ] **Passo 10 — Registrar o conjunto validado:** commit local sugerido `feat(shared)!: remove auth module and expose enterprise API`.

## Tarefa 4: Schemas, exemplos e documentação coerentes com a API pública

**Files:**

- Modify: `scripts/generate_json_schemas.py`, `src/modules/profile/schema.json`, `src/modules/enterprise/schema.json` e `src/modules/profile/features/user/schema.json`.
- Create/Test: `tests/unit/test_schema_generation.py`.
- Modify: `README.md`, `docs/json-schemas.md`, `docs/database/Perfil Profissional.dbml`, `.github/copilot-instructions.md`, `.github/instructions/git-conventions.instructions.md` e `.github/agents/git-manager.agent.md`.
- Modify: requests afetados em `docs/Job Finder API/collections/Job Finder API/`.
- Delete: `docs/database/Autenticação e Autorização.dbml`, `docs/Job Finder API/collections/Job Finder Auth API/` e requests de Users sem rota correspondente na coleção pública.
- Modify: `docs/auth-service-research.md`, identificando o documento como histórico e retirando links locais que deixam de existir.

**Interfaces:** `load_dtos(module_name: str) -> dict[str, list[type[BaseModel]]]` preserva o contrato do gerador, mas importa DTOs compartilhados somente quando o arquivo existir. Os catálogos continuam autocontidos e não incluem modelos de identidade removidos.

- [ ] **Passo 1 — Escrever teste do gerador real:** executar `generated_files()` em processo isolado após remoção dos DTOs compartilhados; carregar todos os documentos como JSON e verificar referências locais resolvidas, ausência de `AuthenticatedUser`/`ProfileUser` e ausência de `external_id` no catálogo de User. Não simular imports ou respostas do gerador.
- [ ] **Passo 2 — Executar o ciclo vermelho:** `.venv/bin/python -m pytest tests/unit/test_schema_generation.py -v`; observar a falha atual pelo import obrigatório dos DTOs compartilhados removidos.
- [ ] **Passo 3 — Ajustar a descoberta opcional e regenerar os arquivos:** `.venv/bin/python scripts/generate_json_schemas.py`. Manter catálogos de features não alteradas consistentes com seus DTOs.
- [ ] **Passo 4 — Atualizar os documentos e exemplos:** documentar API pública, usuário anônimo, preservação de vínculos antigos, exclusão de Auth e irreversibilidade da migração; corrigir o comando de inicialização para `uvicorn src.main:app --reload`. Requests públicos usam a coleção sem autenticação e não fornecem `user_id` na criação.
- [ ] **Passo 5 — Verificar os schemas:** `.venv/bin/python -m pytest tests/unit/test_schema_generation.py -v` e `.venv/bin/python scripts/generate_json_schemas.py --check`; esperar aprovação e nenhum arquivo desatualizado.
- [ ] **Passo 6 — Registrar o conjunto validado:** commit local sugerido `docs: align schemas and examples with public APIs`.

## Tarefa 5: Verificação final e entrega

**Files:** Todos os arquivos alterados nas tarefas anteriores; este plano recebe somente atualização de progresso e evidências quando a execução for autorizada.

**Interfaces:** Consome a aplicação completa e a revisão `a03e20261003`. Produz uma mudança revisável, com resultados de testes e limitações materiais documentadas. Não inclui deploy nem merge automático.

- [ ] **Passo 1 — Executar a suíte inteira:** `.venv/bin/python -m pytest -v --tb=short`. Esperar testes unitários, de migração, de concorrência e E2E aprovados; registrar nominalmente qualquer falha em vez de omiti-la.
- [ ] **Passo 2 — Verificar consistência:** executar `scripts/generate_json_schemas.py --check`, `alembic -c src/shared/database/alembic.ini check` no banco de teste atualizado e `git diff --check`; esperar ausência de divergências.
- [ ] **Passo 3 — Auditar referências ativas:** usar `rg` para procurar `src.modules.auth`, `get_current_user`, `get_current_profile_user`, `require_role`, `AuthenticatedUser`, `ProfileUser`, `external_id`, configurações de JWT e `auth_headers` nos arquivos ativos. Admitir referências somente no histórico Alembic, no bootstrap histórico de migrações, nos testes de remoção e nos documentos explicitamente históricos/de planejamento. A palavra genérica `token` em comentários do Alembic sobre interpolação não é um mecanismo de autenticação.
- [ ] **Passo 4 — Verificar exclusão no banco:** confirmar ausência de `auth` em `information_schema.schemata`, uma única linha anônima ativa, FKs válidas e snapshots de dados antigos preservados. Repetir a verificação após outra execução de `upgrade head`.
- [ ] **Passo 5 — Revisar a mudança completa:** verificar cobertura dos cinco pontos de Review Focus, assinaturas e callers, transações, erros de domínio e ausência de dependências que ficaram mascaradas pelo ambiente virtual antigo.
- [ ] **Passo 6 — Entregar para revisão:** apresentar os arquivos alterados, os comandos e resultados efetivamente observados, a necessidade de aplicar a nova migração e sua irreversibilidade. A implementação só poderá ser declarada concluída com essas evidências.

## Estado e próxima etapa

Plano consolidado em 2026-10-03, com base no código inspecionado e nas decisões do usuário. A implementação foi realizada na branch `feat/remove-auth`. A migração está pronta, mas ainda precisa ser executada e verificada contra PostgreSQL de teste antes da aplicação no banco real. A ausência de PostgreSQL e Poetry acessíveis neste ambiente impede a verificação de E2E e a regeneração do lockfile; o lock antigo foi removido porque continha dependências exclusivas de Auth e já estava obsoleto frente ao `pyproject.toml`.
