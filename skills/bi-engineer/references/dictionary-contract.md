# Dictionary contract

Lee el diccionario antes de tocar el modelo.

## Minimum files to inspect

- `dictionary/tables.yml`
- `dictionary/columns.yml`
- `dictionary/measures.yml`
- `dictionary/relationships.yml`
- `dictionary/business_rules.yml`
- `dictionary/patterns.yml`
- `dictionary/validation_tests.yml`
- `dictionary/deprecated_objects.yml`
- `dictionary/changelog.md`

## Interpretation rules

- `catalog/` es evidencia tecnica extraida o preparada para el workflow.
- `dictionary/` es contexto gobernado y reusable.
- Si una definicion de negocio no esta en el diccionario, no la inventes sin marcarla en `Supuestos`.
- Si aparece un objeto tecnico nuevo, propon su registro para `BI_GOVERNANCE`.
