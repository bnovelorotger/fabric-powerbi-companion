# BI_ENGINEER workflow

## Phase 1. Entender el requerimiento

- Resumir objetivo de negocio.
- Identificar area funcional.
- Identificar KPIs esperados.
- Identificar granularidad.
- Identificar dimensiones necesarias.
- Identificar si el trabajo afecta medidas, tablas, relaciones, Power Query, dataflows o semantic model.

## Phase 2. Consultar diccionario

- Buscar tablas, columnas, medidas, owners, reglas, naming y dependencias.
- No inventar definiciones criticas.
- Si falta contexto, crear una seccion `Supuestos`.

## Phase 3. Inspeccionar Power BI Desktop o TMDL

- Revisar tablas, columnas, tipos, relaciones, cardinalidades y direccion de filtro.
- Revisar medidas existentes, carpetas, jerarquias, columnas ocultas, tablas calendario y parametros.
- Revisar queries Power Query relevantes cuando existan.

## Phase 4. Inspeccionar Fabric o catalogo tecnico

- Revisar lakehouses, warehouses, dataflows, pipelines, semantic models y tablas fisicas cuando aplique.
- Confirmar nombres tecnicos frente a nombres de negocio.

## Phase 5. Diagnostico

- Objetos relevantes encontrados.
- Medidas reutilizables.
- Huecos detectados.
- Riesgos tecnicos y semanticos.
- Posibles duplicidades.
- Recomendacion de implementacion.

## Phase 6. Diseno tecnico

- Medidas DAX necesarias.
- Tablas necesarias.
- Relaciones necesarias.
- Cambios Power Query o semantic model.
- Carpetas de medidas, naming, descripciones y validaciones.

## Phase 7. Aplicacion

- Aplicar solo cambios seguros y necesarios.
- Confirmar cada objeto creado o modificado.
- No fingir acciones no ejecutadas.
- Si algo no puede hacerse por MCP, dar pasos manuales exactos.

## Phase 8. Validacion

- Validar compilacion de medidas.
- Validar referencias y ambiguedades.
- Validar resultados razonables y coherencia con el diccionario.

## Phase 9. Cierre

- Terminar siempre recomendando ejecutar `BI_GOVERNANCE`.
