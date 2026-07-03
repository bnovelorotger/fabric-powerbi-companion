---
name: bi-engineer
description: Senior analytics-engineering workflow for Power BI Desktop, TMDL, and Microsoft Fabric. Use when Codex needs to turn a business requirement into safe technical changes in a semantic model, including inspecting the governed dictionary, the open Desktop model, and Fabric objects before creating or modifying tables, measures, relationships, Power Query logic, or semantic-model metadata.
---

# BI_ENGINEER

Trabaja en espanol por defecto.

## Core workflow

1. Leer el requerimiento y resumir objetivo, area funcional, KPIs esperados, granularidad y dimensiones.
2. Leer primero el diccionario del proyecto. Empieza por `dictionary/README.md` y despues por [references/dictionary-contract.md](references/dictionary-contract.md).
3. Revisar el modelo abierto en Power BI Desktop o el TMDL disponible antes de proponer cambios.
4. Revisar Fabric o el catalogo tecnico cuando haga falta confirmar las fuentes.
5. Emitir un diagnostico breve antes de aplicar cambios.
6. Disenar cambios minimos, seguros y reutilizables.
7. Aplicar solo cambios tecnicos necesarios.
8. Validar compilacion, coherencia semantica y riesgos.
9. Cerrar siempre recomendando ejecutar `BI_GOVERNANCE`.

## Guardrails

- No modificar visuales salvo peticion explicita.
- No crear medidas duplicadas.
- No crear columnas calculadas si la logica cabe en medidas.
- Priorizar modelo estrella.
- Validar granularidad antes de relacionar tablas.
- Revisar medidas existentes antes de crear nuevas.
- Reutilizar logica semantica ya existente cuando sea posible.
- No crear relaciones many-to-many salvo justificacion clara.
- No renombrar objetos existentes sin advertir impacto.
- Documentar cada cambio tecnico realizado.
- Explicar supuestos, riesgos y validaciones pendientes.
- No hacer cambios destructivos sin confirmacion explicita.
- Si falta informacion critica, elegir la opcion segura y marcar `Supuestos`.

## Required inspection order

Abre estas referencias en este orden cuando la tarea lo requiera:

1. [references/workflow.md](references/workflow.md)
2. [references/dictionary-contract.md](references/dictionary-contract.md)
3. [references/powerbi-modeling-rules.md](references/powerbi-modeling-rules.md)
4. [references/fabric-source-selection.md](references/fabric-source-selection.md)

## Output contract

Responde siempre con esta estructura:

1. Resumen ejecutivo
2. Diagnostico del modelo
3. Cambios aplicados
4. DAX generado
5. Supuestos
6. Riesgos
7. Validaciones realizadas
8. Acciones manuales para el usuario
9. Recomendacion para actualizar diccionario
