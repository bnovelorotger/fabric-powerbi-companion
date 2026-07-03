from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from common import repo_root, slugify


def bootstrap(project_name: str, output_slug: str | None = None) -> Path:
    root = repo_root()
    projects_dir = root / "projects"
    template_dir = projects_dir / "_template"
    slug = output_slug or slugify(project_name)
    project_dir = projects_dir / slug

    if project_dir.exists():
        raise FileExistsError(f"Project directory already exists: {project_dir}")

    project_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy2(template_dir / "brief.yaml", project_dir / "brief.yaml")
    shutil.copy2(template_dir / "semantic_spec.yaml", project_dir / "semantic_spec.yaml")
    (project_dir / "artifacts").mkdir()
    (project_dir / "logs").mkdir()

    brief_path = project_dir / "brief.yaml"
    brief_text = brief_path.read_text(encoding="utf-8")
    brief_text = brief_text.replace("TODO project name", project_name)
    brief_path.write_text(brief_text, encoding="utf-8")
    return project_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a new model-factory project from the template.")
    parser.add_argument("project_name")
    parser.add_argument("--slug", default=None)
    args = parser.parse_args()

    project_dir = bootstrap(args.project_name, args.slug)
    print("[OK] Project bootstrapped")
    print(f"Path: {project_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
