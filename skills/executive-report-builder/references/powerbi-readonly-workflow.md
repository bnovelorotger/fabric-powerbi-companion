# Flujo Power BI en solo lectura

## Operaciones permitidas

1. `connection_operations`: `ListLocalInstances`, `Connect`, `ListConnections`, `GetConnection` y `Disconnect`.
2. `model_operations`: `Get`, `GetStats` y `ExportTMDL`.
3. Operaciones de tablas, columnas, medidas y relaciones: `List`, `Get`, `GetSchema` y `ExportTMDL`.
4. `dax_query_operations`: `Validate` y `Execute`.

No usar ninguna operación que cree, actualice, borre, renombre, mueva, refresque o abra una transacción.

## Selección de instancia

- Cero instancias: pedir abrir el PBIX correcto y detener la extracción.
- Una instancia: conectar automáticamente y comunicar el título de ventana.
- Varias instancias: presentar título de ventana y puerto; pedir al usuario una selección explícita.

## Inspección mínima

- Leer el diccionario gobernado del proyecto antes del modelo vivo.
- Capturar nombre, base de datos, estadísticas, tablas, relaciones y medidas.
- Priorizar medidas con descripción, carpeta ejecutiva y formato definido.
- Localizar medidas de contexto o frescura y ejecutarlas cuando existan.
- Revisar filtros y granularidad antes de escribir DAX.
- Validar cada consulta antes de ejecutarla.
- Limitar filas y evitar columnas con PII en modo `aggregate`.

## Evidencia de no mutación

Capturar `GetStats` antes y después. Comparar al menos `TableCount`, `TotalMeasureCount` y `RelationshipCount`. Para una revisión reforzada, exportar TMDL antes y después y comparar su hash normalizado.

## Gaps

Registrar un gap cuando no exista una medida gobernada, la semántica sea ambigua o falte cobertura. Incluir medida deseada, pregunta ejecutiva afectada, evidencia revisada y recomendación para `BI_ENGINEER`. Continuar solo con las secciones que sigan siendo defendibles.

