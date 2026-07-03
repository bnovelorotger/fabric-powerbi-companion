from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import dump_yaml, load_json, load_yaml


def compare(dictionary_dir: Path, snapshot_path: Path) -> dict:
    tables_yaml = load_yaml(dictionary_dir / "tables.yml").get("tables", [])
    measures_yaml = load_yaml(dictionary_dir / "measures.yml").get("measures", [])
    relationships_yaml = load_yaml(dictionary_dir / "relationships.yml").get("relationships", [])
    snapshot = load_json(snapshot_path)

    dict_tables = {item["name"] for item in tables_yaml}
    dict_measures = {item["name"] for item in measures_yaml}
    dict_relationships = {
        (item["from_table"], item["from_column"], item["to_table"], item["to_column"])
        for item in relationships_yaml
    }

    snapshot_tables = {item["name"] for item in snapshot.get("tables", [])}
    snapshot_measures = {item["name"] for item in snapshot.get("measures", [])}
    snapshot_relationships = {
        (item["from_table"], item["from_column"], item["to_table"], item["to_column"])
        for item in snapshot.get("relationships", [])
        if {"from_table", "from_column", "to_table", "to_column"} <= set(item)
    }

    return {
        "changes": {
            "new_tables": sorted(snapshot_tables - dict_tables),
            "missing_tables": sorted(dict_tables - snapshot_tables),
            "new_measures": sorted(snapshot_measures - dict_measures),
            "missing_measures": sorted(dict_measures - snapshot_measures),
            "new_relationships": [
                {
                    "from_table": row[0],
                    "from_column": row[1],
                    "to_table": row[2],
                    "to_column": row[3],
                }
                for row in sorted(snapshot_relationships - dict_relationships)
            ],
            "missing_relationships": [
                {
                    "from_table": row[0],
                    "from_column": row[1],
                    "to_table": row[2],
                    "to_column": row[3],
                }
                for row in sorted(dict_relationships - snapshot_relationships)
            ],
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare governed dictionary objects against a model snapshot.")
    parser.add_argument("dictionary_dir", type=Path)
    parser.add_argument("snapshot_path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = compare(args.dictionary_dir, args.snapshot_path)
    if args.output:
        dump_yaml(args.output, result)

    changes = result["changes"]
    print("[OK] Dictionary comparison generated")
    print(f"New tables: {len(changes['new_tables'])}")
    print(f"New measures: {len(changes['new_measures'])}")
    print(f"New relationships: {len(changes['new_relationships'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
