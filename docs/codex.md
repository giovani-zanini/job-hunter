# Codex: instalação, configuração e revisão

O Job Hunter usa Superpowers para o método de desenvolvimento e checks executáveis para validar código, contratos e commits. Commits são escritos em inglês; documentação, respostas e revisões, em português brasileiro.

## Arquivos e responsabilidades

| Arquivo | Responsabilidade |
| --- | --- |
| `AGENTS.md` | Arquitetura, decisões estáveis, comandos e instruções de review do Codex. |
| `SECURITY.md` na raiz | Escopo, propriedades e critérios para análise do Codex Security. |
| `.codex/config.toml` | Sandbox, aprovações e suporte a múltiplos agentes no projeto confiável. |
| `.pre-commit-config.yaml` | Ruff, contratos JSON e validação de mensagens de commit. |
| `.github/workflows/quality.yml` | Verificações de código, commits novos do PR, testes com PostgreSQL e auditoria de dependências. |
| `pyproject.toml` | Ferramentas de desenvolvimento com versões explícitas e configuração do Ruff/Commitizen. |

O nome reconhecido pelo Codex é `AGENTS.md`. Evite cópias em `agent.md` ou outros nomes que possam divergir. `SECURITY.md` é contexto de política, não autorização para executar comandos.

## Codex e Superpowers no computador local

Instale o Codex CLI seguindo [a documentação oficial](https://developers.openai.com/codex/cli). Para a distribuição npm, com Node.js instalado:

```bash
npm install -g @openai/codex
codex --version
codex login
cd /caminho/para/job-hunter
codex
```

No CLI, abra `/plugins`, procure Superpowers e instale pelo marketplace oficial. No Codex App, abra Plugins, selecione Superpowers e siga a instalação. Inicie uma nova sessão após instalar. Não copie as skills do plugin para o repositório nem mantenha uma segunda instalação manual delas.

Confira as skills disponíveis no cliente e invoque `$using-superpowers` em uma nova sessão. O agente deve identificar a skill e seguir o fluxo aplicável. A disponibilidade do plugin nesta conversa não comprova sua instalação no CLI ou em outro computador.

Referência: [instalação atual do Superpowers para Codex App/CLI](https://github.com/obra/superpowers#codex-app).

## Confiança, permissões e configuração pessoal

A configuração de projeto só é carregada quando o cliente confia no checkout. Use o fluxo de confiança do Codex para este repositório específico. No CLI, a confiança fica na configuração pessoal; o exemplo abaixo usa um caminho absoluto que deve ser adaptado:

```toml
[projects."/caminho/absoluto/job-hunter"]
trust_level = "trusted"
```

O projeto usa `workspace-write`, aprovações `on-request` e rede desabilitada no sandbox por padrão. Instalações e ferramentas remotas podem exigir acesso de rede conforme a política do cliente. Não desative o sandbox ou a verificação TLS para contornar um bloqueio.

Modelo, esforço de raciocínio, conta, chaves, plugins e preferências de memória pertencem à configuração pessoal. `multi_agent = true` disponibiliza ferramentas quando suportadas; não exige delegação em toda tarefa nem define um modelo caro para os subagentes. Confira as opções compatíveis com a versão instalada antes de personalizar esses valores.

Referências: [configuração](https://developers.openai.com/codex/config-basic), [referência completa](https://developers.openai.com/codex/config-reference) e [descoberta de AGENTS.md](https://developers.openai.com/codex/guides/agents-md).

## Dependências e hooks locais

O setup de Poetry também pode ser usado em Linux/macOS a partir de qualquer checkout, com o cache fora do projeto:

```bash
JOB_HUNTER_CLOUD_SETUP_DIR=/tmp/job-hunter-setup bash scripts/cloud-install.sh
.venv/bin/pre-commit install
.venv/bin/pre-commit run --all-files
```

`pre-commit install` ativa `pre-commit` e `commit-msg`, declarados em `default_install_hook_types`. Preserve hooks existentes; o framework pode mantê-los como hooks legados. Não use opções para sobrescrevê-los sem conferir seu conteúdo.

Em ambientes cloud com diretório pessoal somente para leitura, execute `export PRE_COMMIT_HOME=/tmp/job-hunter-pre-commit-cache` antes de executar o pre-commit ou `git commit`. No computador local, o cache padrão pode ser mantido.

Os hooks remotos precisam de rede na primeira instalação. O hook de contratos usa o Python da `.venv` do checkout e os DTOs atuais. O setup funciona sem lockfile versionado, cria a resolução externa e a reutiliza enquanto os inputs forem iguais. Nesse caso a resolução inicial pode variar entre computadores; um futuro lockfile versionado é uma decisão separada.

Ruff começa com `E9`, `F63`, `F7` e `F82`, incluindo nomes não definidos. Não há supressão global para os modelos. A formatação pode ser usada em arquivos modificados com `.venv/bin/ruff format <arquivos>`; ela não provoca uma reformatação geral via hook.

```bash
.venv/bin/cz check --message 'feat(profile): add public profile filtering'
.venv/bin/ruff check src scripts tests
.venv/bin/python -m pytest tests/unit -q
.venv/bin/python scripts/generate_json_schemas.py --check
```

## Conventional Commits

A fonte é [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/). O formato é:

```text
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

Descrição, corpo e rodapés em inglês. Use tipos consistentes em minúsculas: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. Escopos são opcionais; prefira os módulos ou a feature afetada.

```text
chore(codex): configure repository agent guidance
fix(profile): preserve links when restoring a profile
feat(enterprise)!: change vacancy response contract

BREAKING CHANGE: vacancy responses now use the new contract.
```

`feat` e `fix` têm os significados definidos pela especificação. Outros tipos não implicam automaticamente incremento de versão. Não há release automática configurada nesta mudança.

Commitizen valida sintaxe; ele não verifica se o inglês está correto nem se a descrição é fiel à mudança. O CI valida commits do intervalo do PR e aceita mensagens especiais de merge/fixup previstas pelo Commitizen. O histórico anterior não é reescrito. Na integração por squash, mantenha também a mensagem final no padrão.

## Revisão de código no GitHub

No cliente/conta que administra o Codex, conecte o repositório e habilite a revisão automática para ele nas configurações de Code review. Confira também como tratar PRs em draft. Essas preferências são da conta e não são ativadas por `.codex/config.toml` ou pelo workflow de qualidade.

As instruções ficam na seção `Review guidelines` de `AGENTS.md`. Para solicitar uma revisão manual em um PR conectado, use `@codex review`, conforme a integração disponível. Confira se a resposta está em português e se considera as APIs públicas atuais.

No CLI:

```bash
codex review --uncommitted
# Para uma branch de trabalho que parte de development:
codex review --base development
```

Referência: [Codex no GitHub](https://developers.openai.com/codex/integrations/github).

## Revisão de segurança

Instale Codex Security no marketplace do cliente em que pretende executar scans. As skills atuais incluem:

- `define-security-policy`: manter a política aplicável em `SECURITY.md`.
- `security-diff-scan`: investigar vulnerabilidades em um PR, commit ou diff.
- `threat-model`: mapear ativos, fronteiras e ameaças concretas quando solicitado ou durante um scan.
- `security-scan`: analisar o repositório ou um escopo específico.

Use a política deste projeto, incluindo a decisão de acesso público e a exposição de implantação ainda indefinida. O plugin deve verificar suas capacidades e indicar limites antes do scan. Não trate a instalação como prova de execução ou como ativação automática em todo PR.

O CI configura automaticamente `pip-audit` para vulnerabilidades conhecidas das dependências; isso não substitui a revisão do código pelo Codex Security. Scans recorrentes ou de PR no serviço Codex Security exigem a configuração disponível nessa conta/serviço. Habilite-os ali, confira o alvo e execute um scan para verificar o funcionamento. Este repositório não contém credenciais ou um workflow que tente chamar uma API de segurança não documentada.

A auditoria usa `pip freeze --all --exclude-editable` para consultar as versões já instaladas, sem uma segunda resolução. Exclui o pacote local editável; as dependências dele continuam incluídas. O modo estrito interrompe o job se a coleta das dependências auditadas falhar, e nenhum identificador de vulnerabilidade é ignorado.

Referências: [Codex Security](https://developers.openai.com/codex/security), [plugin atual](https://github.com/openai/plugins/tree/main/plugins/codex-security) e [resolução da política](https://github.com/openai/plugins/blob/main/plugins/codex-security/references/security-guidance.md).

## Complementos pesquisados

| Recurso | Uso e limite |
| --- | --- |
| [Context7](https://github.com/upstash/context7) | Documentação de bibliotecas por versão. Instale uma integração no cliente escolhido; use apenas quando a consulta técnica acrescentar informação. |
| [GitHub](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md) | Contexto de PRs, issues e CI. A configuração MCP do VS Code não é descoberta automaticamente pelo Codex. Use o plugin ou um MCP pessoal, sem duplicar ambos no mesmo cliente. |
| [Commitizen](https://commitizen-tools.github.io/commitizen/tutorials/auto_check/) | Hook `commit-msg` e verificação do intervalo de commits no CI. |
| [Ruff](https://github.com/astral-sh/ruff-pre-commit) | Checks determinísticos de Python, complementares à revisão humana/agêntica. |
| [pip-audit](https://github.com/pypa/pip-audit) | Auditoria das dependências resolvidas, sem correção automática ou exclusões de vulnerabilidades. |

Para MCP do GitHub, prefira configuração pessoal baseada em `bearer_token_env_var`, conforme a documentação do GitHub. Nunca coloque o valor do token no TOML versionado. Tokens e autenticação de outros clientes não são transferidos automaticamente.

OpenAI Developers passa a ser útil quando houver integração efetiva com APIs/SDKs da OpenAI. Playwright e Figma dependem de uma interface visual que não faz parte do backend atual. Skills genéricas extras de planejamento, TDD e revisão sobreporiam Superpowers. O antigo catálogo `openai/skills` está descontinuado; prefira [plugins atuais](https://github.com/openai/plugins) e documentação dos mantenedores.

## Memória e hooks de sessão

`AGENTS.md` e a documentação pertinente mantêm as decisões compartilhadas. Memória nativa, se disponível, é uma preferência pessoal e precisa ser conferida contra a branch atual. Ela não substitui os arquivos versionados. Não compartilhe dados de currículos, tokens ou resultados sensíveis como memória.

Não há servidor externo de memória nem hook personalizado de `SessionStart`, `Stop` ou `PostToolUse`. Um hook que execute testes indiscriminadamente poderia atingir banco indevido ou repetir trabalho. Hooks de Git e CI fornecem verificações explícitas e reproduzíveis sem alterar o fluxo do Superpowers.

Os resultados medidos desta configuração estão em [codex-validation.md](codex-validation.md), incluindo as falhas existentes da suíte E2E.
