from __future__ import annotations

import json
import os
from pathlib import Path


def _candidate_roots() -> list[Path]:
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if not local_app_data:
        return []
    base = Path(local_app_data) / "Microsoft"
    return [
        base / "Power BI Desktop",
        base / "Power BI Desktop Store App",
    ]


def find_local_instances() -> list[dict[str, str]]:
    instances: list[dict[str, str]] = []
    for root in _candidate_roots():
        if not root.exists():
            continue
        for port_file in root.rglob("msmdsrv.port.txt"):
            try:
                port = port_file.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if not port.isdigit():
                continue
            workspace_dir = port_file.parent
            instances.append(
                {
                    "workspace_dir": str(workspace_dir),
                    "port": port,
                    "connection_string": f"Provider=MSOLAP;Data Source=localhost:{port}",
                }
            )
    deduped = {(item["port"], item["workspace_dir"]): item for item in instances}
    return sorted(deduped.values(), key=lambda item: int(item["port"]))


def main() -> int:
    payload = {
        "count": 0,
        "instances": [],
    }
    payload["instances"] = find_local_instances()
    payload["count"] = len(payload["instances"])
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
