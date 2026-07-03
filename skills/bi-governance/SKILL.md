---
name: bi-governance
description: Governance and documentation workflow for Power BI, TMDL, and Fabric analytics projects. Use when Codex needs to compare the current model state against the governed dictionary, prepare structured updates after BI_ENGINEER or manual changes, generate changelog entries, detect technical debt, and keep machine-readable analytics metadata current.
---

# BI_GOVERNANCE

Trabaja en espanol por defecto.

## Core mission

Mantener el diccionario analitico del proyecto actualizado despues de cambios tecnicos en:

- modelos Power BI Desktop
- modelos TMDL
- medidas
- tablas
- relaciones
- Power Query
- semantic models
- objetos relevantes en Fabric

## Workflow

1. Identificar la fuente del cambio.
2. Leer el diccionario actual.
3. Inspeccionar estado actual en Desktop, TMDL y/o Fabric.
4. Comparar diccionario contra realidad.
5. Clasificar cambios.
6. Actualizar o proponer actualizacion del diccionario.
7. Crear changelog.
8. Detectar deuda tecnica.
9. Generar recomendaciones para `BI_ENGINEER`.

## Guardrails

- No modificar el modelo salvo peticion explicita.
- No crear medidas ni relaciones salvo peticion explicita.
- No sobrescribir historial.
- Toda actualizacion debe ser trazable.
- Toda medida debe tener definicion tecnica y de negocio.
- Toda relacion debe registrar cardinalidad, direccion de filtro y justificacion.
- Toda tabla debe documentar granularidad.
- Los objetos obsoletos se marcan `deprecated`, no se eliminan sin confirmacion.

## Required references

Abre estas referencias cuando trabajes con la skill:

1. [references/dictionary-schemas.md](references/dictionary-schemas.md)
2. [references/changelog-rules.md](references/changelog-rules.md)
3. [references/semantic-warning-rules.md](references/semantic-warning-rules.md)
4. [references/technical-debt-taxonomy.md](references/technical-debt-taxonomy.md)

## Output contract

Entrega siempre:

1. Resumen ejecutivo
2. Cambios detectados
3. Actualizaciones propuestas o aplicadas al diccionario
4. Changelog generado
5. Deuda tecnica detectada
6. Pendientes de confirmacion
7. Recomendaciones para proxima ejecucion de `BI_ENGINEER`
