---
name: executive-report-builder
description: Crear, regenerar y validar informes ejecutivos independientes en HTML y PDF A4 a partir de medidas y consultas DAX de un Power BI Desktop abierto. Usar cuando Codex deba recoger alcance, stakeholders y objetivo, inspeccionar un PBIX en solo lectura, interpretar datos gobernados, aplicar una estética ejecutiva configurable, conservar trazabilidad y permitir iteraciones versionadas fuera de Power BI.
---

# EXECUTIVE_REPORT_BUILDER

Trabajar en español por defecto.

## Guardrails obligatorios

- Operar sobre Power BI Desktop exclusivamente en solo lectura.
- Usar solo operaciones MCP de conexión, inspección, listado, exportación de TMDL y ejecución o validación DAX.
- No usar operaciones `Create`, `Update`, `Delete`, `Rename`, `Move`, `Refresh`, transacciones ni cambios de metadatos.
- Reutilizar medidas gobernadas y sus descripciones. No reconstruir KPIs desde columnas si existe una medida válida.
- Tratar la ausencia de una métrica como `semantic_gap`; proponer resolverla mediante `BI_ENGINEER` en otro flujo.
- Trabajar con agregados. No extraer PII o detalle individual salvo autorización explícita y justificación en el brief.
- Separar siempre hechos, inferencias y cautelas. No afirmar causalidad a partir de correlación.
- No sobrescribir versiones aprobadas.

## Flujo

1. Localizar el proyecto bajo `projects/<proyecto>/` y leer su brief, semantic spec, diccionario y gobierno relevantes.
2. Recoger el briefing antes de consultar datos. Confirmar como mínimo:
   - alcance y periodo;
   - stakeholders y nivel de detalle;
   - objetivo principal y decisiones que debe apoyar.
3. Completar comparador, longitud, confidencialidad, dimensiones prioritarias y criterios de éxito cuando afecten al diseño. Leer [references/contracts.md](references/contracts.md).
4. Crear el pack con `scripts/bootstrap_report_pack.py`. Detenerse si el briefing obligatorio sigue incompleto.
5. Detectar instancias locales de Power BI Desktop. Conectar automáticamente si hay una; si hay varias, pedir al usuario que elija. Si no hay ninguna, explicar cómo abrir el PBIX y detener la extracción.
6. Capturar estadísticas iniciales del modelo. Inspeccionar tablas, relaciones, medidas, descripciones, carpetas y señales de frescura siguiendo [references/powerbi-readonly-workflow.md](references/powerbi-readonly-workflow.md).
7. Construir `report_spec.yaml`: vincular cada pregunta ejecutiva con medidas, dimensiones, filtros, comparador, consulta, visual, cobertura mínima y cautelas.
8. Validar todas las consultas DAX antes de ejecutarlas. Ejecutar solo las aprobadas y guardar un snapshot conforme al contrato.
9. Redactar `report_content_vN.yaml`. Priorizar la decisión del stakeholder, mostrar denominadores y advertir muestras o coberturas débiles.
10. Renderizar HTML con `scripts/render_report.py` y exportar PDF con `scripts/export_pdf.py`. Aplicar [references/executive-visual-system.md](references/executive-visual-system.md).
11. Ejecutar `scripts/validate_report_pack.py` y revisar el JSON de QA. Corregir errores antes de entregar.
12. Volver a capturar estadísticas del modelo y confirmar que tablas, medidas y relaciones no cambiaron.

## Comandos

```powershell
python scripts/bootstrap_report_pack.py --project-dir <project> --report-slug <slug>
python scripts/preflight.py
python scripts/render_report.py --report-dir <pack> --content content/report_content_v1.yaml
python scripts/export_pdf.py --html <pack>/output/report_v1.html --pdf <pack>/output/report_v1.pdf
python scripts/validate_report_pack.py --report-dir <pack> --content content/report_content_v1.yaml --html output/report_v1.html --pdf output/report_v1.pdf --write qa/report_validation_v1.json
```

Resolver rutas relativas desde el directorio del pack. No usar `--force` salvo que el usuario confirme que la versión no está aprobada.

## Entrega

Entregar HTML y PDF, indicar versión, periodo, modelo fuente, filtros, fecha de extracción, warnings y ruta del QA. Si existe un `semantic_gap`, incluirlo sin ocultarlo y no presentar el KPI como disponible.
