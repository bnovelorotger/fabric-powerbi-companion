# Technical debt taxonomy

Usa esta taxonomia al revisar el modelo y el diccionario:

```yaml
technical_debt:
  - undocumented_measures
  - duplicated_measures
  - measures_without_folder
  - measures_without_description
  - ambiguous_relationships
  - many_to_many_relationships
  - unused_columns
  - hidden_business_columns
  - inconsistent_naming
  - missing_grain_definition
  - missing_owner
  - missing_validation
  - deprecated_objects_still_used
```

## Severity guidance

- `high`: riesgo semantico o ejecutivo directo
- `medium`: complica mantenimiento o reutilizacion
- `low`: gap documental menor
