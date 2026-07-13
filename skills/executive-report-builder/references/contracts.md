# Contratos del pack ejecutivo

## Estructura

```text
executive_reports/<report_slug>/
  brief.yaml
  report_spec.yaml
  data/snapshot_<timestamp>.json
  content/report_content_vN.yaml
  output/report_vN.html
  output/report_vN.pdf
  qa/report_validation_vN.json
```

## `brief.yaml`

Campos obligatorios no vacíos:

```yaml
schema_version: "1.0"
report:
  slug: student-lifecycle
  title: Evolución del ciclo del estudiante
  scope: Matrícula, inicio, finalización y continuidad
  period: 2026-Q1
  stakeholders:
    - Decanato
  detail_level: executive
  primary_objective: Detectar pérdidas del ciclo y programas prioritarios
  decisions_supported:
    - Priorizar intervenciones por programa
```

Campos recomendados: `comparator`, `length` (`one_pager` o `multipage`), `priority_dimensions`, `success_criteria`, `confidentiality`, `privacy_mode` (`aggregate` por defecto), `approved_at` y `approved_by`.

## `report_spec.yaml`

```yaml
schema_version: "1.0"
model:
  expected_name: executive_model
  access_mode: read_only
questions:
  - id: lifecycle-conversion
    executive_question: ¿Dónde se pierde volumen del ciclo?
    measures:
      - Measures[Enrolled]
      - Measures[Started]
    dimensions:
      - v_atn_programs[prg_mshied_name]
    filters: []
    comparator: previous_academic_period
    query_id: lifecycle_summary
    visual: funnel
    minimum_base: 30
    caveats: []
semantic_gaps: []
```

Cada pregunta debe tener `id`, `executive_question`, `measures`, `query_id` y `visual`. Registrar medidas ausentes en `semantic_gaps`; no inventar su resultado.

## Snapshot JSON

```json
{
  "schema_version": "1.0",
  "model": {
    "connection_name": "PBIDesktop-model-12345",
    "database_name": "guid",
    "model_name": "Model",
    "stats_before": {"tables": 27, "measures": 379, "relationships": 29},
    "stats_after": {"tables": 27, "measures": 379, "relationships": 29}
  },
  "extracted_at": "2026-07-13T10:00:00+02:00",
  "filters": [{"field": "Period", "values": ["2026-Q1"]}],
  "quality_flags": [
    {"code": "low_coverage", "severity": "warning", "message": "Tasa de respuesta inferior al umbral"}
  ],
  "queries": [
    {
      "id": "executive_kpis",
      "dax": "EVALUATE ROW(...) ",
      "columns": ["Matriculados", "Tasa"],
      "rows": [{"Matriculados": 2322, "Tasa": 0.216}],
      "warnings": []
    }
  ]
}
```

Conservar el DAX literal. `stats_before` y `stats_after` deben coincidir en tablas, medidas y relaciones.
Registrar baja cobertura como `warning` y contradicciones no resueltas como `error` dentro de `quality_flags`.


## `report_content_vN.yaml`

```yaml
schema_version: "1.0"
report:
  version: 1
  title: Resumen y comentarios
  subtitle: Encuestas Asignatura-Profesor
  organization: Analytics Team
  period: 2026-Q1
  date: 2026-07-13
  source_label: Power BI · executive_model
  logo_path: assets/organization-logo.png
  brand:
    primary: "#d82032"
    ink: "#0b0d0e"
    panel: "#f0f0f0"
  confidentiality: Uso interno
  layout: one_pager
  executive_summary:
    - type: fact
      text: La satisfacción se mantiene en niveles positivos.
    - type: caution
      text: La participación obliga a interpretar los resultados como señales.
kpis:
  - label: Matriculados
    source: {query_id: executive_kpis, field: Matriculados, row_index: 0}
    format: integer
    status: neutral
    note: Base del corte
sections:
  - title: Lectura por segmento
    intro: Comparación dentro del alcance aprobado.
    visuals:
      - type: bar
        title: Satisfacción por segmento
        items:
          - {label: Global, value: 4.41, display: "4,41", status: positive}
footnotes:
  - Los resultados proceden del snapshot trazable adjunto.
```

Tipos de visual soportados: `bar`, `trend`, `distribution`, `table`, `callout` y `text`. Un valor puede ser literal o resolverse mediante `source`. Formatos: `integer`, `decimal`, `percent` y `text`.
En modo multipágina, las tablas de más de 24 filas se dividen automáticamente en páginas de anexo; en one-pager, cualquier desbordamiento bloquea la exportación.

## Versionado

- Crear `v1` para la primera versión.
- Incrementar la versión si cambia briefing, especificación, snapshot o narrativa.
- No sobrescribir HTML, PDF, contenido ni QA existentes sin `--force` y autorización explícita.
