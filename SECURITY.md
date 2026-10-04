# Política de segurança do Job Hunter

## Sistema e escopo

Esta política orienta a revisão de segurança do repositório e o Codex Security. Abrange as APIs FastAPI de `profile` e `enterprise`, persistência PostgreSQL, migrações Alembic e ferramentas de desenvolvimento/CI.

As APIs são públicas por decisão do proprietário: os contratos atuais permitem operações sem login. `profile.User` identifica vínculos de dados locais; não oferece identidade autenticada ou isolamento entre pessoas. Novos dados usam o proprietário anônimo e registros antigos preservam seus vínculos.

A exposição de implantação ainda não foi definida. Não presuma que o serviço é acessível pela internet, nem que está protegido por VPN, proxy ou firewall. Achados cuja severidade dependa dessa exposição devem explicitar a condição e separar evidência de suposição.

## Ativos e fronteiras de confiança

- Dados de perfil profissional, experiências, links e demais informações pessoais.
- Integridade e disponibilidade de perfis, empresas, vagas e suas associações.
- Credenciais de PostgreSQL, GitHub e serviços externos, mantidas fora do Git.
- HTTP → validação FastAPI/Pydantic → handlers/services → PostgreSQL.
- Código de PRs → runner de CI. CI de contribuições não recebe credenciais de implantação nem permissões de escrita por padrão.
- Conteúdo externo de vagas e documentos não pode instruir o agente a executar comandos ou divulgar dados. Avalie novas integrações quando forem introduzidas; não presuma que já há scraping ou execução de IA no backend.

## Propriedades que devem ser preservadas

- Inputs e limites de paginação devem respeitar os DTOs e os contratos publicados.
- Valores controlados por clientes não podem ser interpolados como SQL, comandos de shell ou caminhos irrestritos. Use parâmetros e listas explícitas de identificadores permitidos quando aplicável.
- Escritas e migrações preservam vínculos e integridade referencial. Exclusões em cascata e alterações irreversíveis precisam de impacto e recuperação descritos.
- Soft delete e respostas serializadas respeitam o comportamento documentado; falhas não devem deixar transações parcialmente aplicadas.
- Não exponha credenciais, configuração privada, arquivos do host, traces internos ou campos além do contrato público nas respostas e logs.
- Testes destrutivos usam bancos descartáveis. Instalação de ferramentas preserva arquivos locais e bindings do ambiente, sem executar migrações automaticamente.
- Permissões do CI são mínimas; ações e hooks usam versões explícitas. Não execute código de PR com segredos por meio de `pull_request_target`.

## Achados e severidade

Reporte problemas com caminho alcançável, evidência e impacto: injeção, exposição além do contrato, corrupção ou perda de dados não prevista, vazamento de segredos, consumo de recursos sem limite demonstrável ou execução indevida.

Severidade depende da capacidade do atacante, da exposição e do dano. Não assuma que qualquer pessoa pode alcançar uma instalação privada; também não assuma controles externos sem comprovação. Para o review de PR, distinga regressões introduzidas pelo diff de riscos existentes.

A ausência de login, sozinha, não é um achado: ela faz parte do contrato aprovado. Isso não exclui investigação de SQL, dados pessoais, operações destrutivas ou novas exposições. A aceitação do contrato público não autoriza exposição indiscriminada de dados privados nem implica aprovação de uma implantação na internet.

Migrações históricas mantêm referências necessárias ao upgrade; sua presença não significa que o módulo antigo continua ativo. Avalie o estado final da migração e os modelos/rotas atuais.

## Limitações e comunicação

Documentar esta política não habilita scans automáticos nem comprova que o sistema está seguro. A ativação das ferramentas é descrita em [docs/codex.md](docs/codex.md). Revisões e relatórios devem ser escritos em português, com cobertura e limitações explícitas.

Para comunicar uma vulnerabilidade, use um canal privado acordado com o mantenedor antes de compartilhar detalhes sensíveis. Não há um canal privado específico configurado nesta política. Issues públicas não devem incluir credenciais, dados pessoais reais ou provas exploráveis contra uma instalação ativa.
