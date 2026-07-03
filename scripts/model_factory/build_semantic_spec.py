from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from common import dump_yaml, load_yaml, read_csv, repo_root


DEFAULT_VALIDATION_RULES = [
    "Validate dimension uniqueness before creating many-to-one relationships",
    "Avoid many-to-many relationships unless an override reason is documented",
    "Prefer explicit measures over implicit aggregations",
    "Review date table requirements before creating time-intelligence measures",
]


FOLDER_MAP = {
    "Admissions": ["Admissions", "Executive"],
    "Enrollment": ["Enrollment", "Executive"],
    "Academic Progress": ["Academic", "Executive"],
    "Retention": ["Academic", "Executive"],
    "Finance": ["Finance", "Executive"],
    "Satisfaction": ["Quality", "Executive"],
    "Operations": ["Operations", "Executive"],
}


def build_spec(brief_path: Path, output_path: Path) -> dict:
    brief = load_yaml(brief_path)
    root = repo_root()
    catalog_dir = root / "catalog"

    lakehouse_tables = read_csv(catalog_dir / "lakehouse_tables.csv")
    table_columns = read_csv(catalog_dir / "table_columns.csv")
    relationships = read_csv(catalog_dir / "relationships.csv")
    sources_lineage = read_csv(catalog_dir / "sources_lineage.csv")

    source_domains = set(brief["source_domains"])
    candidate_tables = [row for row in lakehouse_tables if row.get("schema_name") in source_domains]
    column_counts = Counter(
        f"{row['schema_name']}.{row['table_name']}" for row in table_columns if row.get("schema_name") in source_domains
    )

    source_entries = []
    for domain in brief["source_domains"]:
        lineage_matches = [row for row in sources_lineage if domain in row.get("curated_layer", "")]
        source_entries.append(
            {
                "domain": domain,
                "usage_mode": "import",
                "priority": "canonical_curated_domain",
                "lineage_hints": [
                    {
                        "source_system": row["source_system"],
                        "curated_layer": row["curated_layer"],
                        "downstream_item": row["downstream_item"],
                    }
                    for row in lineage_matches
                ],
            }
        )

    table_entries = []
    for row in candidate_tables:
        full_name = f"{row['schema_name']}.{row['table_name']}"
        table_entries.append(
            {
                "name": full_name,
                "source_item": row["storage_item_name"],
                "source_type": row["storage_item_type"],
                "column_count": column_counts.get(full_name, 0),
                "documentation_status": row["documentation_status"],
                "selection_reason": "matches requested canonical domain",
            }
        )

    relationship_entries = []
    for row in relationships:
        if row.get("source_schema") in source_domains or row.get("target_schema") in source_domains:
            relationship_entries.append(
                {
                    "from_table": f"{row['source_schema']}.{row['source_table']}",
                    "from_column": row["fk_column"],
                    "to_table": f"{row['target_schema']}.{row['target_table']}",
                    "to_column": row["candidate_pk_column"],
                    "status": row["relationship_status"],
                    "confidence": row["confidence"],
                }
            )

    measure_entries = []
    for kpi in brief["required_kpis"]:
        measure_entries.append(
            {
                "name": kpi,
                "status": "to_design",
                "reuse_first": True,
                "notes": "Check dictionary and open model before creating",
            }
        )

    spec = {
        "sources": source_entries,
        "tables": table_entries,
        "relationships": relationship_entries,
        "measures": measure_entries,
        "column_visibility_policy": {
            "hide_technical_keys": True,
            "keep_business_columns_visible": True,
            "hide_provider_rate_columns_when_explicit_measures_exist": True,
        },
        "measure_folders": FOLDER_MAP.get(brief["domain"], [brief["domain"], "Executive"]),
        "validation_rules": DEFAULT_VALIDATION_RULES,
        "assumptions": [
            "The PBIX starts from a blank Desktop model.",
            "Import mode is the default for new sandbox builds.",
            "Visuals will be created manually by the user.",
        ],
        "risks": [
            "Live Fabric may diverge from the local catalog and require a reconciliation pass.",
            "Some documented relationships are planned or inferred rather than fully validated in a new model.",
        ],
        "pending_manual_actions": [
            "Review final KPI definitions with business stakeholders.",
            "Build report visuals manually once the technical model is validated.",
        ],
    }

    dump_yaml(output_path, spec)
    return spec


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an initial semantic_spec.yaml from a brief.")
    parser.add_argument("brief_path", type=Path)
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()

    spec = build_spec(args.brief_path, args.output_path)
    print("[OK] semantic_spec.yaml generated")
    print(f"Sources: {len(spec['sources'])}")
    print(f"Candidate tables: {len(spec['tables'])}")
    print(f"Relationship hints: {len(spec['relationships'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
