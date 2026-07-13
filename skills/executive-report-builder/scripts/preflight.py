from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    checks.append(("Python >= 3.10", sys.version_info >= (3, 10), sys.version.split()[0]))
    for distribution in ("PyYAML", "playwright", "PyMuPDF"):
        try:
            version = importlib.metadata.version(distribution)
            checks.append((distribution, True, version))
        except importlib.metadata.PackageNotFoundError:
            checks.append((distribution, False, "no instalado"))
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            executable = Path(playwright.chromium.executable_path)
            checks.append(("Chromium Playwright", executable.exists(), str(executable)))
    except Exception as exc:  # pragma: no cover - diagnóstico de entorno
        checks.append(("Chromium Playwright", False, str(exc)))

    failed = False
    for name, ok, detail in checks:
        print(f"[{'OK' if ok else 'ERROR'}] {name}: {detail}")
        failed = failed or not ok
    if failed:
        print("Ejecuta: pip install -r requirements.txt")
        print("Después: python -m playwright install chromium")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

