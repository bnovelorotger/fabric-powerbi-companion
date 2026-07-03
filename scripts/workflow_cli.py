from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
MODEL_FACTORY = ROOT / "scripts" / "model_factory"
if str(MODEL_FACTORY) not in sys.path:
    sys.path.insert(0, str(MODEL_FACTORY))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from audit_public_repo import audit_repo
from detect_local_pbi import find_local_instances
from bootstrap_project import bootstrap
from build_semantic_spec import build_spec
from compare_dictionary_to_model import compare
from export_pbi_snapshot import build_snapshot
from generate_changelog import render_entry
from sync_dictionary_from_snapshot import sync
from validate_brief import validate
from common import dump_yaml, load_yaml


def validate_environment() -> dict:
    fabric_cli_available = importlib.util.find_spec("fabric_cli") is not None
    report = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "pyyaml_available": True,
        "fabric_cli_available": fabric_cli_available,
        "local_pbi_instance_count": len(find_local_instances()),
        "skills_folder_present": (ROOT / "skills").exists(),
    }
    return report


def connect_fabric(config_path: Path) -> dict:
    config = load_yaml(config_path)
    fabric = config.get("fabric", {})
    required = ["tenant_name", "workspace_name", "semantic_model_name"]
    missing = [key for key in required if not str(fabric.get(key, "")).strip()]
    if missing:
        raise ValueError(f"Missing fabric config keys: {', '.join(missing)}")
    payload = {
        "tenant_name": fabric["tenant_name"],
        "workspace_name": fabric["workspace_name"],
        "semantic_model_name": fabric["semantic_model_name"],
        "preferred_item_name": fabric.get("preferred_item_name", ""),
        "recommended_codex_mcp_request": {
            "request": {
                "operation": "ConnectFabric",
                "tenantName": fabric["tenant_name"],
                "workspaceName": fabric["workspace_name"],
                "semanticModelName": fabric["semantic_model_name"],
            }
        },
        "fallback_connection_string_shape": (
            f"Data Source=powerbi://api.powerbi.com/v1.0/{fabric['tenant_name']}/{fabric['workspace_name']};"
            f"Initial Catalog={fabric['semantic_model_name']};"
        ),
        "note": "This command validates config and prepares the live connection payload. The actual live connection is expected to be performed by Codex MCP tooling.",
    }
    return payload


def append_changelog(changes_path: Path, changelog_path: Path, source: str, changed_by: str, summary: str) -> None:
    payload = load_yaml(changes_path)
    if summary:
        payload["summary"] = summary
    entry = render_entry(source, changed_by, payload)
    with changelog_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)
        handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Public workflow CLI for Analytics AI Core.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-environment")
    subparsers.add_parser("detect-pbi")

    connect_fabric_parser = subparsers.add_parser("connect-fabric")
    connect_fabric_parser.add_argument("--config", type=Path, default=ROOT / "config" / "workflow.example.yaml")

    bootstrap_parser = subparsers.add_parser("bootstrap-project")
    bootstrap_parser.add_argument("project_name")
    bootstrap_parser.add_argument("--slug", default=None)

    validate_brief_parser = subparsers.add_parser("validate-brief")
    validate_brief_parser.add_argument("brief_path", type=Path)

    build_spec_parser = subparsers.add_parser("build-semantic-spec")
    build_spec_parser.add_argument("brief_path", type=Path)
    build_spec_parser.add_argument("output_path", type=Path)

    snapshot_parser = subparsers.add_parser("snapshot-from-tmdl")
    snapshot_parser.add_argument("tmdl_folder", type=Path)
    snapshot_parser.add_argument("output_path", type=Path)

    compare_parser = subparsers.add_parser("compare-dictionary")
    compare_parser.add_argument("dictionary_dir", type=Path)
    compare_parser.add_argument("snapshot_path", type=Path)
    compare_parser.add_argument("--output", type=Path)

    sync_parser = subparsers.add_parser("sync-dictionary")
    sync_parser.add_argument("snapshot_path", type=Path)
    sync_parser.add_argument("dictionary_dir", type=Path)
    sync_parser.add_argument("model_name")
    sync_parser.add_argument("--domain", default="Starter")
    sync_parser.add_argument("--owner", default="analytics_ai_core")
    sync_parser.add_argument("--changes-output", type=Path)

    changelog_parser = subparsers.add_parser("generate-changelog")
    changelog_parser.add_argument("changes_path", type=Path)
    changelog_parser.add_argument("changelog_path", type=Path)
    changelog_parser.add_argument("--source", default="workflow_cli")
    changelog_parser.add_argument("--changed-by", default="Codex")
    changelog_parser.add_argument("--summary", default="")

    audit_parser = subparsers.add_parser("audit-public-repo")
    audit_parser.add_argument("--root", type=Path, default=ROOT)
    audit_parser.add_argument("--max-file-mb", type=int, default=5)
    audit_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "validate-environment":
        print(json.dumps(validate_environment(), indent=2))
        return 0

    if args.command == "detect-pbi":
        print(json.dumps({"instances": find_local_instances()}, indent=2))
        return 0

    if args.command == "connect-fabric":
        print(json.dumps(connect_fabric(args.config), indent=2))
        return 0

    if args.command == "bootstrap-project":
        project_dir = bootstrap(args.project_name, args.slug)
        print(f"[OK] Project bootstrapped: {project_dir}")
        return 0

    if args.command == "validate-brief":
        payload = load_yaml(args.brief_path)
        errors = validate(payload)
        if errors:
            for error in errors:
                print(f"[ERROR] {error}")
            return 1
        print("[OK] brief.yaml is valid")
        return 0

    if args.command == "build-semantic-spec":
        spec = build_spec(args.brief_path, args.output_path)
        print(json.dumps({"sources": len(spec["sources"]), "tables": len(spec["tables"]), "relationships": len(spec["relationships"])}, indent=2))
        return 0

    if args.command == "snapshot-from-tmdl":
        snapshot = build_snapshot(args.tmdl_folder)
        output_path = args.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
        print(json.dumps({"tables": len(snapshot["tables"]), "measures": len(snapshot["measures"]), "relationships": len(snapshot["relationships"])}, indent=2))
        return 0

    if args.command == "compare-dictionary":
        result = compare(args.dictionary_dir, args.snapshot_path)
        if args.output:
            dump_yaml(args.output, result)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "sync-dictionary":
        result = sync(args.snapshot_path, args.dictionary_dir, args.model_name, args.domain, args.owner)
        if args.changes_output:
            dump_yaml(args.changes_output, result)
        print(json.dumps({"summary": result["summary"], "changes": len(result["changes"])}, indent=2))
        return 0

    if args.command == "generate-changelog":
        append_changelog(args.changes_path, args.changelog_path, args.source, args.changed_by, args.summary)
        print("[OK] Changelog entry appended")
        return 0

    if args.command == "audit-public-repo":
        result = audit_repo(args.root, args.max_file_mb)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Root: {result['root']}")
            print(f"Findings: {result['finding_count']}")
            print(f"Oversized files: {result['oversized_file_count']}")
        return 1 if result["finding_count"] or result["oversized_file_count"] else 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
