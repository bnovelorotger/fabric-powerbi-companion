from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import load_yaml


REQUIRED_KEYS = {
    "project_name": str,
    "business_goal": str,
    "domain": str,
    "grain": str,
    "source_domains": list,
    "required_kpis": list,
    "required_dimensions": list,
    "requested_pages": list,
    "constraints": list,
    "manual_visuals_by_user": bool,
}


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    for key, expected_type in REQUIRED_KEYS.items():
        if key not in payload:
            errors.append(f"Missing required key: {key}")
            continue
        if not isinstance(payload[key], expected_type):
            errors.append(
                f"Invalid type for {key}: expected {expected_type.__name__}, got {type(payload[key]).__name__}"
            )
    if payload.get("manual_visuals_by_user") is not True:
        errors.append("manual_visuals_by_user must be true for this workflow")
    for list_key in ("source_domains", "required_kpis", "required_dimensions", "requested_pages", "constraints"):
        values = payload.get(list_key, [])
        if isinstance(values, list) and not values:
            errors.append(f"{list_key} cannot be empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a model-factory brief.yaml file.")
    parser.add_argument("brief_path", type=Path)
    args = parser.parse_args()

    payload = load_yaml(args.brief_path)
    errors = validate(payload)
    if errors:
        for error in errors:
            print(f"[ERROR] {error}")
        return 1

    print("[OK] brief.yaml is valid")
    print(f"Project: {payload['project_name']}")
    print(f"Domain: {payload['domain']}")
    print(f"Source domains: {', '.join(payload['source_domains'])}")
    print(f"KPIs: {', '.join(payload['required_kpis'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
