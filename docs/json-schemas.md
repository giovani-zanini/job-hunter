# JSON Schemas dos módulos profile e enterprise

Cada feature em `src/modules/profile/features/` e `src/modules/enterprise/features/`
possui um `schema.json` com todos os DTOs Pydantic definidos em seu `dtos.py`.
Os arquivos `src/modules/profile/schema.json` e `src/modules/enterprise/schema.json`
consolidam as respectivas features e os DTOs de `shared/dtos.py`.

Os arquivos seguem JSON Schema Draft 2020-12 e são autossuficientes: todas as
referências apontam para `$defs` no mesmo arquivo. `x-models` é um índice dos
contratos disponíveis, organizado por feature. Para validar um contrato
específico, use a referência indicada nesse índice. Por exemplo, no arquivo
`src/modules/profile/features/certificate/schema.json`,
`x-models.certificate.CertificateCreateRequest` aponta para
`#/$defs/CertificateCreateRequest`. O `anyOf` da raiz aceita qualquer um dos
DTOs listados no arquivo.

Requests e filtros usam o modo de validação do Pydantic; responses usam o modo
de serialização, refletindo o JSON devolvido pela API. Tipos usados por um DTO
de outra feature, como `SkillResponse` em `profile`, entram automaticamente no
`$defs` do arquivo da feature que os referencia.

Para atualizar os arquivos após modificar um DTO:

```bash
.venv/bin/python scripts/generate_json_schemas.py
```

Para verificar se os arquivos estão atualizados:

```bash
.venv/bin/python scripts/generate_json_schemas.py --check
```
