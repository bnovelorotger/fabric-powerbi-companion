# Changelog rules

Cada entrada debe registrar:

```yaml
version:
date:
changed_by:
source:
summary:
changes:
  - object_type:
    object_name:
    change_type:
    description:
    impact:
    validation_status:
pending_actions:
```

## Rules

- No sobrescribir entradas historicas.
- Registrar si el cambio viene de `BI_ENGINEER`, Fabric, Desktop, TMDL o usuario.
- Incluir impacto y validacion pendiente cuando aplique.
