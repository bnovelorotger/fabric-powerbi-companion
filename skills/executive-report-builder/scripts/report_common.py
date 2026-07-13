from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


class ReportError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ReportError(f"No existe el archivo requerido: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ReportError(f"Se esperaba un objeto YAML en {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ReportError(f"No existe el archivo requerido: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ReportError(f"Se esperaba un objeto JSON en {path}")
    return data


def write_text_new(path: Path, text: str, force: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not force:
        raise ReportError(f"Se rechaza sobrescribir una versión existente: {path}")
    path.write_text(text, encoding="utf-8")


def content_version(content_path: Path, content: dict[str, Any]) -> int:
    value = content.get("report", {}).get("version")
    if isinstance(value, int) and value > 0:
        return value
    match = re.search(r"_v(\d+)$", content_path.stem)
    if match:
        return int(match.group(1))
    raise ReportError("No se pudo determinar la versión del contenido")


def find_snapshot(report_dir: Path, content: dict[str, Any]) -> Path:
    configured = content.get("snapshot")
    if configured:
        path = report_dir / str(configured)
        if not path.exists():
            raise ReportError(f"Snapshot configurado no encontrado: {path}")
        return path
    candidates = sorted((report_dir / "data").glob("snapshot_*.json"))
    if not candidates:
        raise ReportError("No hay snapshots en data/")
    return candidates[-1]


def query_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for query in snapshot.get("queries", []):
        if isinstance(query, dict) and query.get("id"):
            result[str(query["id"])] = query
    return result


def resolve_source(source: dict[str, Any], queries: dict[str, dict[str, Any]]) -> Any:
    query_id = str(source.get("query_id", ""))
    field = str(source.get("field", ""))
    row_index = int(source.get("row_index", 0))
    if query_id not in queries:
        raise ReportError(f"Query no encontrada en snapshot: {query_id}")
    rows = queries[query_id].get("rows") or []
    if row_index < 0 or row_index >= len(rows):
        raise ReportError(f"Fila {row_index} no disponible en query {query_id}")
    row = rows[row_index]
    if not isinstance(row, dict) or field not in row:
        raise ReportError(f"Campo {field} no disponible en query {query_id}")
    return row[field]


def resolve_value(item: dict[str, Any], queries: dict[str, dict[str, Any]]) -> Any:
    source = item.get("source")
    if isinstance(source, dict):
        return resolve_source(source, queries)
    return item.get("value", "")


def format_value(value: Any, format_name: str = "text", decimals: int = 1) -> str:
    if value is None:
        return "—"
    if format_name == "text":
        return str(value)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if format_name == "integer":
        return f"{number:,.0f}".replace(",", ".")
    if format_name == "percent":
        return f"{number * 100:.{decimals}f}%".replace(".", ",")
    if format_name == "decimal":
        return f"{number:.{decimals}f}".replace(".", ",")
    return str(value)


def comparable_stats(snapshot: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    model = snapshot.get("model", {})
    before = model.get("stats_before") or {}
    after = model.get("stats_after") or {}
    return before, after

