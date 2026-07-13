from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent


def run(*args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
        capture_output=True,
        check=False,
    )
    if result.returncode != expect:
        raise AssertionError(
            f"Código {result.returncode}, esperado {expect}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def create_pack(root: Path, slug: str, layout: str, version: int, sections: int) -> Path:
    project = root / "projects" / "fixture"
    run(
        str(SCRIPT_DIR / "bootstrap_report_pack.py"),
        "--project-dir",
        str(project),
        "--report-slug",
        slug,
        "--title",
        "Resumen ejecutivo de prueba",
    )
    pack = project / "executive_reports" / slug
    brief = yaml.safe_load((pack / "brief.yaml").read_text(encoding="utf-8"))
    brief["report"].update(
        {
            "scope": "Encuestas y experiencia académica",
            "period": "2026-Q1",
            "stakeholders": ["Decanato"],
            "primary_objective": "Priorizar focos de mejora",
            "decisions_supported": ["Revisar programas con baja participación"],
            "length": layout,
        }
    )
    write_yaml(pack / "brief.yaml", brief)
    spec = {
        "schema_version": "1.0",
        "model": {"expected_name": "fixture", "access_mode": "read_only"},
        "questions": [
            {
                "id": "summary",
                "executive_question": "¿Cómo evoluciona el resultado?",
                "measures": ["Measures[Score]"],
                "query_id": "kpis",
                "visual": "trend",
            }
        ],
        "semantic_gaps": [],
    }
    write_yaml(pack / "report_spec.yaml", spec)
    snapshot = {
        "schema_version": "1.0",
        "model": {
            "connection_name": "PBIDesktop-fixture-1234",
            "database_name": "fixture",
            "model_name": "fixture",
            "stats_before": {"tables": 27, "measures": 379, "relationships": 29},
            "stats_after": {"tables": 27, "measures": 379, "relationships": 29},
        },
        "extracted_at": "2026-07-13T10:00:00+02:00",
        "filters": [{"field": "Period", "values": ["2026-Q1"]}],
        "quality_flags": [
            {"code": "low_coverage", "severity": "warning", "message": "Cobertura inferior al 30%"}
        ],
        "queries": [
            {
                "id": "kpis",
                "dax": "EVALUATE ROW(\"Satisfaccion\", 4.26, \"Respuestas\", 1088)",
                "columns": ["Satisfaccion", "Respuestas"],
                "rows": [{"Satisfaccion": 4.26, "Respuestas": 1088}],
                "warnings": [],
            },
            {"id": "optional_empty", "dax": "EVALUATE FILTER(...) ", "columns": [], "rows": [], "warnings": []},
        ],
    }
    snapshot_name = "snapshot_20260713T100000.json"
    (pack / "data" / snapshot_name).write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    visual_sets = []
    for index in range(sections):
        visuals = [
            {
                "type": "bar",
                "title": "Resultado por segmento",
                "items": [
                    {"label": "Global", "value": 4.41, "display": "4,41", "status": "positive"},
                    {"label": "Oficial", "value": 4.18, "display": "4,18", "status": "caution"},
                ],
            },
            {
                "type": "trend",
                "title": "Evolución",
                "series": [{"label": "Satisfacción", "values": [4.18, 4.14, 4.20, 4.26]}],
            },
        ]
        if layout == "multipage" and index == sections - 1:
            visuals.append(
                {
                    "type": "table",
                    "title": "Anexo de programas",
                    "columns": ["Programa", "Periodo", "Valor"],
                    "rows": [[f"Programa {row:02d}", "2026-Q1", f"{4 + row / 100:.2f}"] for row in range(52)],
                }
            )
        visual_sets.append(
            {
            "title": f"Lectura {index + 1}",
            "intro": "Comparación ejecutiva dentro del alcance aprobado.",
            "visuals": visuals,
            }
        )
    content = {
        "schema_version": "1.0",
        "snapshot": f"data/{snapshot_name}",
        "report": {
            "version": version,
            "title": "Resumen ejecutivo de prueba",
            "subtitle": "Encuestas Asignatura-Profesor",
            "organization": "Analytics Team",
            "period": "2026-Q1",
            "date": "2026-07-13",
            "source_label": "Power BI · fixture",
            "confidentiality": "Uso interno",
            "layout": layout,
            "executive_summary": [
                {"type": "fact", "text": "La satisfacción se mantiene positiva."},
                {"type": "caution", "text": "La cobertura exige cautela."},
            ],
        },
        "kpis": [
            {
                "label": "Satisfacción media",
                "source": {"query_id": "kpis", "field": "Satisfaccion", "row_index": 0},
                "format": "decimal",
                "decimals": 2,
                "status": "positive",
                "note": "Escala 1-5",
            },
            {
                "label": "Respuestas",
                "source": {"query_id": "kpis", "field": "Respuestas", "row_index": 0},
                "format": "integer",
                "status": "neutral",
            },
        ],
        "sections": visual_sets,
        "footnotes": ["Datos agregados y trazables al snapshot."],
    }
    content_path = pack / "content" / f"report_content_v{version}.yaml"
    if content_path.exists():
        content_path.unlink()
    write_yaml(content_path, content)
    return pack


def exercise(pack: Path, version: int, expected_status: str = "warning") -> None:
    content = f"content/report_content_v{version}.yaml"
    html = pack / "output" / f"report_v{version}.html"
    pdf = pack / "output" / f"report_v{version}.pdf"
    qa = pack / "qa" / f"report_validation_v{version}.json"
    run(str(SCRIPT_DIR / "render_report.py"), "--report-dir", str(pack), "--content", content)
    run(str(SCRIPT_DIR / "export_pdf.py"), "--html", str(html), "--pdf", str(pdf))
    run(
        str(SCRIPT_DIR / "validate_report_pack.py"),
        "--report-dir",
        str(pack),
        "--content",
        content,
        "--html",
        str(html),
        "--pdf",
        str(pdf),
        "--write",
        str(qa),
    )
    result = json.loads(qa.read_text(encoding="utf-8"))
    assert result["status"] == expected_status, result
    assert html.stat().st_size > 5_000
    assert pdf.stat().st_size > 10_000
    overwrite = run(
        str(SCRIPT_DIR / "render_report.py"),
        "--report-dir",
        str(pack),
        "--content",
        content,
        expect=1,
    )
    assert "sobrescribir" in overwrite.stderr.lower()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="executive-report-builder-") as temp:
        root = Path(temp)
        one_pager = create_pack(root, "one-pager", "one_pager", 1, 1)
        exercise(one_pager, 1)
        multipage = create_pack(root, "evolution", "multipage", 1, 2)
        exercise(multipage, 1)

        content_v1 = yaml.safe_load((multipage / "content" / "report_content_v1.yaml").read_text(encoding="utf-8"))
        content_v1["report"]["version"] = 2
        content_v1["report"]["subtitle"] = "Iteración para Rectorado"
        write_yaml(multipage / "content" / "report_content_v2.yaml", content_v1)
        exercise(multipage, 2)

        broken = yaml.safe_load((one_pager / "brief.yaml").read_text(encoding="utf-8"))
        broken["report"]["stakeholders"] = []
        write_yaml(one_pager / "brief.yaml", broken)
        result = run(
            str(SCRIPT_DIR / "validate_report_pack.py"),
            "--report-dir",
            str(one_pager),
            "--content",
            "content/report_content_v1.yaml",
            expect=1,
        )
        assert "briefing obligatorio" in result.stdout

        broken["report"]["stakeholders"] = ["Decanato"]
        write_yaml(one_pager / "brief.yaml", broken)
        snapshot_path = one_pager / "data" / "snapshot_20260713T100000.json"
        contradictory = json.loads(snapshot_path.read_text(encoding="utf-8"))
        contradictory["quality_flags"].append(
            {
                "code": "contradictory_totals",
                "severity": "error",
                "message": "El total no coincide con el desglose",
            }
        )
        snapshot_path.write_text(json.dumps(contradictory, ensure_ascii=False, indent=2), encoding="utf-8")
        result = run(
            str(SCRIPT_DIR / "validate_report_pack.py"),
            "--report-dir",
            str(one_pager),
            "--content",
            "content/report_content_v1.yaml",
            expect=1,
        )
        assert "calidad de datos" in result.stdout and "contradictory_totals" in result.stdout

    print("[OK] one-pager, multipágina, versionado, PDF, QA y errores de contrato")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
