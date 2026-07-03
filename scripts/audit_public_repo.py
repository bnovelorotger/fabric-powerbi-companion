from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".csv",
    ".ps1",
    ".py",
    ".tmdl",
    ".cmd",
    ".gitignore",
}

SKIP_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

DISALLOWED_FILE_NAMES = {
    ".env",
    "auth.json",
    "cache.bin",
}

PATTERNS = {
    "windows_user_path": re.compile(r"C:\\\\Users\\\\", re.IGNORECASE),
    "unix_user_path": re.compile(r"/Users/"),
    "email_address": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "password_literal": re.compile(r"(password|pass|pwd)\s*[:=]\s*.+", re.IGNORECASE),
    "secret_literal": re.compile(r"(client_secret|api[_-]?key|access_token|refresh_token)\s*[:=]\s*.+", re.IGNORECASE),
    "auth_header": re.compile(r"Authorization\s*[:=]\s*Bearer\s+", re.IGNORECASE),
    "fabric_endpoint": re.compile(r"[A-Za-z0-9-]+\.fabric\.microsoft\.com", re.IGNORECASE),
}


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        yield path


def scan_text_file(path: Path) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in TEXT_EXTENSIONS:
        return findings
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return findings
    for rule_name, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            if path.name == "audit_public_repo.py" and rule_name in {"windows_user_path", "unix_user_path"}:
                continue
            line_number = text[: match.start()].count("\n") + 1
            findings.append(
                {
                    "rule": rule_name,
                    "path": str(path),
                    "line": line_number,
                    "snippet": match.group(0)[:160],
                }
            )
    return findings


def audit_repo(root: Path, max_file_mb: int) -> dict:
    findings: list[dict[str, str | int]] = []
    oversized: list[dict[str, str | int]] = []
    for path in iter_files(root):
        if path.name in DISALLOWED_FILE_NAMES:
            findings.append({"rule": "disallowed_file_name", "path": str(path), "line": 0, "snippet": path.name})
        for part in path.parts:
            lowered = part.lower()
            if lowered.startswith("tmp_") or lowered.startswith("_tmp_") or lowered == ".codex_tmp":
                findings.append({"rule": "temporary_folder_present", "path": str(path), "line": 0, "snippet": part})
                break
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > max_file_mb:
            oversized.append({"path": str(path), "size_mb": round(size_mb, 2)})
        findings.extend(scan_text_file(path))
    return {
        "root": str(root),
        "finding_count": len(findings),
        "oversized_file_count": len(oversized),
        "findings": findings,
        "oversized_files": oversized,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a candidate public repository for secrets and publication risks.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--max-file-mb", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = audit_repo(args.root, args.max_file_mb)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Root: {result['root']}")
        print(f"Findings: {result['finding_count']}")
        print(f"Oversized files: {result['oversized_file_count']}")
        for finding in result["findings"]:
            print(f"[{finding['rule']}] {finding['path']}:{finding['line']} -> {finding['snippet']}")
        for item in result["oversized_files"]:
            print(f"[oversized_file] {item['path']} -> {item['size_mb']} MB")
    return 1 if result["finding_count"] or result["oversized_file_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
