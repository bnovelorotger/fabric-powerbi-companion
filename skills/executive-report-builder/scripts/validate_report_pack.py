from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import fitz

from report_common import (
    ReportError,
    comparable_stats,
    find_snapshot,
    format_value,
    load_json,
    load_yaml,
    query_map,
    resolve_value,
    write_text_new,
)


REQUIRED_BRIEF = (
    "scope",
    "period",
    "stakeholders",
    "primary_objective",
    "decisions_supported",
)
PII_PATTERN = re.compile(
    r"(^|[_\s])(students?|alumnos?|fullname|nombres?|emails?|mail|phones?|telefonos?|dni|documents?|contacts?)([_\s]|$)",
    re.IGNORECASE,
)
EXTERNAL_PATTERN = re.compile(r"(?:src|href)\s*=\s*[\"']https?://", re.IGNORECASE)


def add(checks: list[dict[str, Any]], name: str, status: str, detail: str) -> None:
    checks.append({"name": name, "status": status, "detail": detail})


def walk_sources(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if isinstance(value.get("source"), dict):
            found.append(value["source"])
        for child in value.values():
            found.extend(walk_sources(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(walk_sources(child))
    return found


def validate_pack(
    report_dir: Path,
    content_path: Path,
    html_path: Path | None,
    pdf_path: Path | None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    errors = 0
    warnings = 0

    brief = load_yaml(report_dir / "brief.yaml")
    spec = load_yaml(report_dir / "report_spec.yaml")
    content = load_yaml(content_path)
    snapshot_path = find_snapshot(report_dir, content)
    snapshot = load_json(snapshot_path)
    queries = query_map(snapshot)

    report_brief = brief.get("report") or {}
    missing = [key for key in REQUIRED_BRIEF if not report_brief.get(key)]
    if missing:
        errors += 1
        add(checks, "briefing obligatorio", "error", "Campos vacíos: " + ", ".join(missing))
    else:
        add(checks, "briefing obligatorio", "ok", "Alcance, periodo, stakeholders, objetivo y decisiones confirmados")

    access_mode = (spec.get("model") or {}).get("access_mode")
    if access_mode != "read_only":
        errors += 1
        add(checks, "modelo solo lectura", "error", f"access_mode={access_mode!r}")
    else:
        add(checks, "modelo solo lectura", "ok", "report_spec declara read_only")

    before, after = comparable_stats(snapshot)
    stat_aliases = (
        ("tables", "TableCount"),
        ("measures", "TotalMeasureCount"),
        ("relationships", "RelationshipCount"),
    )
    differences = []
    for short, native in stat_aliases:
        left = before.get(short, before.get(native))
        right = after.get(short, after.get(native))
        if left is None or right is None:
            differences.append(f"{short}: evidencia incompleta")
        elif left != right:
            differences.append(f"{short}: {left} -> {right}")
    if differences:
        errors += 1
        add(checks, "no mutación del modelo", "error", "; ".join(differences))
    else:
        add(checks, "no mutación del modelo", "ok", "Estadísticas antes/después sin cambios")

    missing_sources = []
    for source in walk_sources(content):
        try:
            query_id = str(source.get("query_id", ""))
            if query_id not in queries:
                raise ReportError(f"query {query_id} ausente")
            rows = queries[query_id].get("rows") or []
            row_index = int(source.get("row_index", 0))
            field = str(source.get("field", ""))
            if row_index >= len(rows) or field not in rows[row_index]:
                raise ReportError(f"{query_id}[{row_index}].{field} ausente")
        except (ReportError, TypeError, ValueError, IndexError) as exc:
            missing_sources.append(str(exc))
    if missing_sources:
        errors += 1
        add(checks, "trazabilidad de valores", "error", "; ".join(missing_sources))
    else:
        add(checks, "trazabilidad de valores", "ok", f"{len(walk_sources(content))} referencias resueltas")

    empty_queries = [query_id for query_id, query in queries.items() if not (query.get("rows") or [])]
    if empty_queries:
        warnings += 1
        add(checks, "resultados vacíos", "warning", ", ".join(empty_queries))
    else:
        add(checks, "resultados vacíos", "ok", "Todas las consultas contienen filas")

    quality_flags = snapshot.get("quality_flags") or []
    quality_errors = [flag for flag in quality_flags if flag.get("severity") == "error"]
    quality_warnings = [flag for flag in quality_flags if flag.get("severity") != "error"]
    if quality_errors:
        errors += 1
        add(
            checks,
            "calidad de datos",
            "error",
            "; ".join(f"{flag.get('code')}: {flag.get('message')}" for flag in quality_errors),
        )
    elif quality_warnings:
        warnings += 1
        add(
            checks,
            "calidad de datos",
            "warning",
            "; ".join(f"{flag.get('code')}: {flag.get('message')}" for flag in quality_warnings),
        )
    else:
        add(checks, "calidad de datos", "ok", "Sin flags de baja cobertura o contradicción")

    privacy_mode = str(report_brief.get("privacy_mode", "aggregate"))
    pii_columns = sorted(
        {
            str(column)
            for query in queries.values()
            for column in (query.get("columns") or [])
            if PII_PATTERN.search(str(column))
        }
    )
    if privacy_mode == "aggregate" and pii_columns:
        errors += 1
        add(checks, "privacidad agregada", "error", "Columnas potencialmente personales: " + ", ".join(pii_columns))
    else:
        add(checks, "privacidad agregada", "ok", f"Modo {privacy_mode}; sin PII detectada")

    spec_query_ids = {str(question.get("query_id")) for question in spec.get("questions", []) if question.get("query_id")}
    absent_spec_queries = sorted(spec_query_ids - set(queries))
    if absent_spec_queries:
        errors += 1
        add(checks, "cobertura de especificación", "error", "Sin snapshot: " + ", ".join(absent_spec_queries))
    else:
        add(checks, "cobertura de especificación", "ok", f"{len(spec_query_ids)} consultas especificadas disponibles")

    if spec.get("semantic_gaps"):
        warnings += 1
        add(checks, "gaps semánticos", "warning", f"{len(spec['semantic_gaps'])} gaps declarados")
    else:
        add(checks, "gaps semánticos", "ok", "Sin gaps declarados")

    if html_path:
        html_text = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
        if not html_text:
            errors += 1
            add(checks, "HTML", "error", f"No encontrado o vacío: {html_path}")
        elif EXTERNAL_PATTERN.search(html_text):
            errors += 1
            add(checks, "HTML autocontenido", "error", "Se detectaron recursos HTTP externos")
        else:
            title = str((content.get("report") or {}).get("title", ""))
            if title and title not in html_text:
                errors += 1
                add(checks, "HTML", "error", "El título del contenido no aparece en HTML")
            else:
                add(checks, "HTML autocontenido", "ok", "Sin recursos HTTP externos")

    if pdf_path:
        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            errors += 1
            add(checks, "PDF", "error", f"No encontrado o vacío: {pdf_path}")
        else:
            document = fitz.open(pdf_path)
            pdf_text = "\n".join(page.get_text() for page in document)
            if html_path and html_path.exists():
                html_text = html_path.read_text(encoding="utf-8")
                expected_pages = len(re.findall(r'class="sheet"', html_text))
            else:
                expected_pages = 1 + (
                    0
                    if (content.get("report") or {}).get("layout") == "one_pager"
                    else len(content.get("sections") or [])
                )
            if document.page_count != expected_pages:
                errors += 1
                add(checks, "paginación PDF", "error", f"Esperadas {expected_pages}; obtenidas {document.page_count}")
            else:
                add(checks, "paginación PDF", "ok", f"{document.page_count} páginas A4")
            title = str((content.get("report") or {}).get("title", ""))
            normalized_title = re.sub(r"\s+", " ", title).strip().lower()
            normalized_pdf = re.sub(r"\s+", " ", pdf_text).strip().lower()
            if normalized_title and normalized_title not in normalized_pdf:
                errors += 1
                add(checks, "contenido PDF", "error", "El título no aparece en el texto PDF")
            else:
                add(checks, "contenido PDF", "ok", "Título y texto extraíbles")
            document.close()

    status = "error" if errors else "warning" if warnings else "ok"
    return {
        "schema_version": "1.0",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "report_dir": str(report_dir),
        "content": str(content_path),
        "snapshot": str(snapshot_path),
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida un pack ejecutivo y su trazabilidad.")
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--write", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def resolve(report_dir: Path, value: Path | None) -> Path | None:
    if value is None:
        return None
    return value if value.is_absolute() else report_dir / value


def main() -> int:
    args = parse_args()
    report_dir = args.report_dir.resolve()
    content_path = resolve(report_dir, args.content)
    assert content_path is not None
    result = validate_pack(report_dir, content_path, resolve(report_dir, args.html), resolve(report_dir, args.pdf))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        output = resolve(report_dir, args.write)
        assert output is not None
        write_text_new(output, rendered, args.force)
        print(output)
    else:
        print(rendered)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReportError as exc:
        raise SystemExit(f"[ERROR] {exc}")
