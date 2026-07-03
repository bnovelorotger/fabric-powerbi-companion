from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import dump_yaml, load_json, load_yaml, now_utc_iso


def upsert_by_name(items: list[dict], key: str, payload: dict) -> tuple[list[dict], str]:
    for index, item in enumerate(items):
        if item.get(key) == payload.get(key):
            if item == payload:
                return items, "unchanged"
            items[index] = payload
            return items, "updated"
    items.append(payload)
    return items, "created"


def sync(snapshot_path: Path, dictionary_dir: Path, model_name: str, domain: str, owner: str) -> dict:
    snapshot = load_json(snapshot_path)

    tables_doc = load_yaml(dictionary_dir / "tables.yml")
    measures_doc = load_yaml(dictionary_dir / "measures.yml")
    relationships_doc = load_yaml(dictionary_dir / "relationships.yml")
    semantic_models_doc = load_yaml(dictionary_dir / "semantic_models.yml")

    created_tables = []
    updated_tables = []
    created_measures = []
    updated_measures = []
    created_relationships = []
    updated_relationships = []

    for table in snapshot.get("tables", []):
        table_entry = {
            "name": table["name"],
            "display_name": table["name"],
            "domain": domain,
            "source_system": "Power BI Desktop Local",
            "source_object": table["name"],
            "grain": "pending_confirmation",
            "primary_key": "",
            "date_column": "",
            "owner": owner,
            "refresh_frequency": "manual_local_model",
            "used_for": ["sandbox_validation"],
            "status": "draft",
            "description": table.get("description") or f"Local semantic-model table captured from {model_name}.",
            "columns": table.get("columns", []),
            "relationships": [],
            "last_reviewed": now_utc_iso(),
        }
        tables_doc["tables"], status = upsert_by_name(tables_doc.get("tables", []), "name", table_entry)
        if status == "created":
            created_tables.append(table["name"])
        elif status == "updated":
            updated_tables.append(table["name"])

    for measure in snapshot.get("measures", []):
        measure_entry = {
            "name": measure["name"],
            "table": measure["table"],
            "folder": measure.get("display_folder") or domain,
            "domain": domain,
            "business_definition": "pending_confirmation",
            "technical_definition": measure.get("description") or f"Local measure captured from {model_name}.",
            "dax": measure.get("expression", "pending_export_or_manual_capture"),
            "dependencies": [measure["table"]],
            "used_for": ["sandbox_validation"],
            "filters_assumptions": "pending_confirmation",
            "owner": owner,
            "status": "draft",
            "created_by": "sync_dictionary_from_snapshot.py",
            "last_modified": now_utc_iso(),
            "validation_status": "pending_confirmation",
        }
        measures_doc["measures"], status = upsert_by_name(measures_doc.get("measures", []), "name", measure_entry)
        if status == "created":
            created_measures.append(measure["name"])
        elif status == "updated":
            updated_measures.append(measure["name"])

    relationship_index = {
        (
            item["from_table"],
            item["from_column"],
            item["to_table"],
            item["to_column"],
        ): item
        for item in relationships_doc.get("relationships", [])
    }
    for relationship in snapshot.get("relationships", []):
        key = (
            relationship["from_table"],
            relationship["from_column"],
            relationship["to_table"],
            relationship["to_column"],
        )
        is_new_relationship = key not in relationship_index
        relationship_payload = {
            "from_table": relationship["from_table"],
            "from_column": relationship["from_column"],
            "to_table": relationship["to_table"],
            "to_column": relationship["to_column"],
            "cardinality": "pending_confirmation",
            "filter_direction": "pending_confirmation",
            "active": True,
            "business_reason": f"Relationship captured from {model_name}.",
            "grain_validation": "pending_confirmation",
            "risk_level": "pending_confirmation",
            "status": "draft",
        }
        if is_new_relationship:
            relationship_index[key] = relationship_payload
            created_relationships.append(
                f"{relationship['from_table']}.{relationship['from_column']}->{relationship['to_table']}.{relationship['to_column']}"
            )
        else:
            if relationship_index[key] != relationship_payload:
                updated_relationships.append(
                    f"{relationship['from_table']}.{relationship['from_column']}->{relationship['to_table']}.{relationship['to_column']}"
                )
            relationship_index[key] = relationship_payload
    relationships_doc["relationships"] = list(relationship_index.values())

    model_entry = {
        "name": model_name,
        "workspace": "Power BI Desktop Local",
        "domain": domain,
        "fact_tables": [table["name"] for table in snapshot.get("tables", []) if table["name"].startswith("fact_")],
        "dimension_tables": [table["name"] for table in snapshot.get("tables", []) if table["name"].startswith("dim_")],
        "key_measures": [measure["name"] for measure in snapshot.get("measures", [])],
        "reports_using_it": [],
        "refresh_schedule": "manual_local_model",
        "owner": owner,
        "certification_status": "draft",
        "description": "Local semantic model registered from a TMDL or Desktop validation flow.",
        "status": "draft",
    }
    semantic_models_doc["semantic_models"], _ = upsert_by_name(
        semantic_models_doc.get("semantic_models", []),
        "name",
        model_entry,
    )

    dump_yaml(dictionary_dir / "tables.yml", tables_doc)
    dump_yaml(dictionary_dir / "measures.yml", measures_doc)
    dump_yaml(dictionary_dir / "relationships.yml", relationships_doc)
    dump_yaml(dictionary_dir / "semantic_models.yml", semantic_models_doc)

    changes = (
        [
            {
                "object_type": "table",
                "object_name": name,
                "change_type": "new_object",
                "description": "Local table added to the governed dictionary.",
                "impact": "available_for_future_reuse",
                "validation_status": "pending_confirmation",
            }
            for name in created_tables
        ]
        + [
            {
                "object_type": "table",
                "object_name": name,
                "change_type": "modified_object",
                "description": "Local table metadata refreshed in the governed dictionary.",
                "impact": "dictionary_enrichment",
                "validation_status": "pending_confirmation",
            }
            for name in updated_tables
        ]
        + [
            {
                "object_type": "measure",
                "object_name": name,
                "change_type": "new_object",
                "description": "Local measure added to the governed dictionary.",
                "impact": "available_for_future_reuse",
                "validation_status": "pending_confirmation",
            }
            for name in created_measures
        ]
        + [
            {
                "object_type": "measure",
                "object_name": name,
                "change_type": "modified_object",
                "description": "Local measure metadata refreshed in the governed dictionary.",
                "impact": "dictionary_enrichment",
                "validation_status": "pending_confirmation",
            }
            for name in updated_measures
        ]
        + [
            {
                "object_type": "relationship",
                "object_name": name,
                "change_type": "new_object",
                "description": "Local relationship added to the governed dictionary.",
                "impact": "available_for_future_reuse",
                "validation_status": "pending_confirmation",
            }
            for name in created_relationships
        ]
        + [
            {
                "object_type": "relationship",
                "object_name": name,
                "change_type": "modified_object",
                "description": "Local relationship metadata refreshed in the governed dictionary.",
                "impact": "dictionary_enrichment",
                "validation_status": "pending_confirmation",
            }
            for name in updated_relationships
        ]
    )
    return {
        "summary": f"Synchronized local snapshot for {model_name} into the governed dictionary.",
        "changes": changes,
        "pending_actions": [
            "Confirm business definitions for draft measures before broader reuse.",
            "Review cardinality and filter direction metadata for draft relationships.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync a model snapshot into the governed dictionary.")
    parser.add_argument("snapshot_path", type=Path)
    parser.add_argument("dictionary_dir", type=Path)
    parser.add_argument("model_name")
    parser.add_argument("--domain", default="Starter")
    parser.add_argument("--owner", default="analytics_ai_core")
    parser.add_argument("--changes-output", type=Path)
    args = parser.parse_args()

    result = sync(args.snapshot_path, args.dictionary_dir, args.model_name, args.domain, args.owner)
    if args.changes_output:
        dump_yaml(args.changes_output, result)

    print("[OK] Dictionary synchronized from snapshot")
    print(f"Change rows: {len(result['changes'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
