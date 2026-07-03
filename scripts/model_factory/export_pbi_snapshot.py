from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import dump_json, now_utc_iso


TABLE_RE = re.compile(r"^table\s+(.+)$")
COLUMN_RE = re.compile(r"^\s+column\s+(.+)$")
MEASURE_EXPR_RE = re.compile(r"^\s+measure\s+'?([^'=]+?)'?\s*=\s*(.+)$")
REL_NAME_RE = re.compile(r"^relationship\s+(.+)$")
FROM_RE = re.compile(r"^\s+fromColumn:\s+([^.]+)\.(.+)$")
TO_RE = re.compile(r"^\s+toColumn:\s+([^.]+)\.(.+)$")
COMMENT_RE = re.compile(r"^\s*///\s*(.+)$")
DISPLAY_FOLDER_RE = re.compile(r"^\s+displayFolder:\s+(.+)$")
FORMAT_STRING_RE = re.compile(r"^\s+formatString:\s+(.+)$")


def parse_table_file(path: Path) -> dict:
    table_name = path.stem
    columns: list[str] = []
    measures: list[dict] = []
    current_measure: dict | None = None
    pending_comment: str | None = None
    table_description = ""

    def finalize_measure() -> None:
        nonlocal current_measure
        if current_measure:
            measures.append(current_measure)
            current_measure = None

    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if match := COMMENT_RE.match(line):
                pending_comment = match.group(1).strip()
                continue
            if match := TABLE_RE.match(line):
                finalize_measure()
                table_name = match.group(1).strip().strip("'")
                if pending_comment:
                    table_description = pending_comment
                    pending_comment = None
            elif match := COLUMN_RE.match(line):
                finalize_measure()
                columns.append(match.group(1).strip().strip("'"))
            elif match := MEASURE_EXPR_RE.match(line):
                finalize_measure()
                current_measure = {
                    "name": match.group(1).strip(),
                    "expression": match.group(2).strip(),
                    "description": pending_comment or "",
                    "display_folder": "",
                    "format_string": "",
                }
                pending_comment = None
            elif current_measure and (match := DISPLAY_FOLDER_RE.match(line)):
                current_measure["display_folder"] = match.group(1).strip()
            elif current_measure and (match := FORMAT_STRING_RE.match(line)):
                current_measure["format_string"] = match.group(1).strip()
        finalize_measure()
    return {"name": table_name, "description": table_description, "columns": columns, "measures": measures}


def parse_relationships(path: Path) -> list[dict]:
    if not path.exists():
        return []
    relationships = []
    current: dict | None = None
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if match := REL_NAME_RE.match(line):
                if current:
                    relationships.append(current)
                current = {"name": match.group(1).strip()}
            elif current and (match := FROM_RE.match(line)):
                current["from_table"] = match.group(1).strip()
                current["from_column"] = match.group(2).strip()
            elif current and (match := TO_RE.match(line)):
                current["to_table"] = match.group(1).strip()
                current["to_column"] = match.group(2).strip()
        if current:
            relationships.append(current)
    return relationships


def build_snapshot(tmdl_folder: Path) -> dict:
    definition_dir = tmdl_folder / "definition" if (tmdl_folder / "definition").exists() else tmdl_folder
    tables_dir = definition_dir / "tables"
    relationship_file = definition_dir / "relationships.tmdl"

    tables = []
    measures = []
    for path in sorted(tables_dir.glob("*.tmdl")):
        table = parse_table_file(path)
        tables.append(table)
        for measure in table["measures"]:
            measures.append(
                {
                    "name": measure["name"],
                    "table": table["name"],
                    "expression": measure["expression"],
                    "description": measure["description"],
                    "display_folder": measure["display_folder"],
                    "format_string": measure["format_string"],
                }
            )

    return {
        "generated_at_utc": now_utc_iso(),
        "tmdl_folder": str(tmdl_folder),
        "tables": tables,
        "measures": measures,
        "relationships": parse_relationships(relationship_file),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize a TMDL export into a compact model snapshot JSON.")
    parser.add_argument("tmdl_folder", type=Path)
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()

    snapshot = build_snapshot(args.tmdl_folder)
    dump_json(args.output_path, snapshot)
    print("[OK] Snapshot exported")
    print(f"Tables: {len(snapshot['tables'])}")
    print(f"Measures: {len(snapshot['measures'])}")
    print(f"Relationships: {len(snapshot['relationships'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
