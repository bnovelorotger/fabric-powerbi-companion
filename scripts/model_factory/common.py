from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, allow_unicode=True, sort_keys=False)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def dump_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    output = []
    last_dash = False
    for char in value.lower().strip():
        if char.isalnum():
            output.append(char)
            last_dash = False
        elif not last_dash:
            output.append("-")
            last_dash = True
    return "".join(output).strip("-")
