from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from report_common import ReportError, write_text_new


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inicializa un pack de informe ejecutivo trazable.")
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--report-slug", required=True)
    parser.add_argument("--title", default="Informe ejecutivo")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_dir = args.project_dir.resolve() / "executive_reports" / args.report_slug
    if report_dir.exists():
        raise ReportError(f"El pack ya existe: {report_dir}")

    for relative in ("data", "content", "output", "qa"):
        (report_dir / relative).mkdir(parents=True, exist_ok=False)

    brief = {
        "schema_version": "1.0",
        "report": {
            "slug": args.report_slug,
            "title": args.title,
            "scope": None,
            "period": None,
            "stakeholders": [],
            "detail_level": "executive",
            "primary_objective": None,
            "decisions_supported": [],
            "comparator": None,
            "length": "multipage",
            "priority_dimensions": [],
            "success_criteria": [],
            "confidentiality": "Uso interno",
            "privacy_mode": "aggregate",
        },
    }
    spec = {
        "schema_version": "1.0",
        "model": {"expected_name": None, "access_mode": "read_only"},
        "questions": [],
        "semantic_gaps": [],
    }
    content = {
        "schema_version": "1.0",
        "snapshot": "data/snapshot_PENDING.json",
        "report": {
            "version": 1,
            "title": args.title,
            "subtitle": None,
            "organization": "Analytics Team",
            "period": None,
            "date": None,
            "source_label": "Power BI Desktop",
            "confidentiality": "Uso interno",
            "layout": "multipage",
            "logo_path": None,
            "brand": {"primary": "#d82032", "ink": "#0b0d0e", "panel": "#f0f0f0"},
            "executive_summary": [],
        },
        "kpis": [],
        "sections": [],
        "footnotes": [],
    }

    write_text_new(report_dir / "brief.yaml", yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
    write_text_new(report_dir / "report_spec.yaml", yaml.safe_dump(spec, allow_unicode=True, sort_keys=False))
    write_text_new(
        report_dir / "content" / "report_content_v1.yaml",
        yaml.safe_dump(content, allow_unicode=True, sort_keys=False),
    )
    print(report_dir)
    print("Completa alcance, periodo, stakeholders, objetivo y decisiones antes de consultar el PBIX.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
