from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import load_yaml, now_utc_iso


def render_entry(source: str, changed_by: str, payload: dict) -> str:
    version = now_utc_iso().replace(":", "").replace("-", "")
    summary = payload.get("summary", "Generated change log entry")
    lines = [
        "",
        f"## {now_utc_iso()}",
        "",
        f"- version: `{version}`",
        f"- changed_by: `{changed_by}`",
        f"- source: `{source}`",
        f"- summary: `{summary}`",
        "- changes:",
    ]
    for change in payload.get("changes", []):
        lines.append(
            f"  - `{change['object_type']}` `{change['object_name']}` `{change['change_type']}` - {change['description']} ({change['validation_status']})"
        )
    lines.append("- pending_actions:")
    pending = payload.get("pending_actions", ["review pending confirmations"])
    for item in pending:
        lines.append(f"  - {item}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a markdown changelog entry from a structured change file.")
    parser.add_argument("changes_path", type=Path)
    parser.add_argument("changelog_path", type=Path)
    parser.add_argument("--source", default="model_factory")
    parser.add_argument("--changed-by", default="Codex")
    parser.add_argument("--summary", default="")
    args = parser.parse_args()

    if not args.changes_path.exists():
        print(f"[ERROR] Changes file not found: {args.changes_path}")
        return 1

    payload = load_yaml(args.changes_path)
    if not payload or not payload.get("changes"):
        print("[ERROR] Changes payload is empty or has no changes")
        return 1

    if args.summary:
        payload["summary"] = args.summary

    entry = render_entry(args.source, args.changed_by, payload)
    with args.changelog_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
        handle.write("\n")

    print("[OK] Changelog entry appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
