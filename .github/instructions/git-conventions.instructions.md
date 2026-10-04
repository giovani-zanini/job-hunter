---
applyTo: "**"
---

# Conventional Commits

Siga [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
Mensagens de commit (descrição, corpo e rodapés) são escritas em inglês;
documentação e revisões de código e segurança são escritas em português brasileiro.

Formato: `<type>[optional scope][!]: <description>`.
Use tipos consistentes em minúsculas: `feat`, `fix`, `docs`, `style`, `refactor`,
`perf`, `test`, `build`, `ci`, `chore`, `revert`.
Escopo é opcional; sugestões: `profile`, `enterprise`, `shared`, `database`,
`codex`, `deps`, `tests`, `profile/skill`, `enterprise/vacancy`.

```text
chore(codex): configure repository agent guidance
fix(profile): preserve profile associations
feat(enterprise)!: change vacancy response contract

BREAKING CHANGE: vacancy responses now use the new contract.
```

Indique quebras com `!` ou `BREAKING CHANGE:`. Tipos adicionais não implicam
incremento automático de versão pela especificação. Não reescreva commits antigos
para adequá-los ao padrão; o CI verifica os novos commits do PR.

Mantenha commits focados e descrições claras. Agrupe modelos, migrações e testes
correspondentes; atualize os JSON Schemas quando mudar DTOs. Não edite migrações
históricas. Confira os refs reais antes de escolher uma branch de base.

Commitizen valida o formato via hook `commit-msg`. Consulte
[a configuração do Codex](../../docs/codex.md) e [AGENTS.md](../../AGENTS.md).
