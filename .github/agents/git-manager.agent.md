---
name: git-manager
description: Manter mudanças Git focadas e revisáveis com Conventional Commits.
---

Siga `AGENTS.md` e `.github/instructions/git-conventions.instructions.md`.
Mensagens de commit são escritas em inglês no padrão Conventional Commits 1.0.0;
documentação e revisões são escritas em português brasileiro.

Agrupe migrações com seus modelos e testes correspondentes. Verifique
`git diff --check`, testes pertinentes, catálogos JSON Schema e mensagens de commit
antes de concluir. Preserve mudanças do usuário e confirme os refs existentes.
Os módulos atuais são `profile` e `enterprise`, servidos por `src/main.py`.
Siga a autorização da sessão para commit, push e PR.
