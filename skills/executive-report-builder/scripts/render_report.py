from __future__ import annotations

import argparse
import base64
import copy
import html
import json
import re
from pathlib import Path
from typing import Any

from report_common import (
    ReportError,
    content_version,
    find_snapshot,
    format_value,
    load_json,
    load_yaml,
    query_map,
    resolve_value,
    write_text_new,
)


COLORS = ["#0b0d0e", "#f52236", "#8f8f8f", "#328b3a", "#d97706"]
TABLE_ROWS_PER_PAGE = 24
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_kpis(kpis: list[dict[str, Any]], queries: dict[str, dict[str, Any]]) -> str:
    cards = []
    for item in kpis:
        value = resolve_value(item, queries)
        display = item.get("display") or format_value(
            value, str(item.get("format", "text")), int(item.get("decimals", 1))
        )
        status = str(item.get("status", "neutral"))
        cards.append(
            '<article class="kpi">'
            f'<div class="kpi-label">{esc(item.get("label"))}</div>'
            f'<div class="kpi-value {esc(status)}">{esc(display)}</div>'
            f'<div class="kpi-delta {esc(status)}">{esc(item.get("delta", ""))}</div>'
            f'<div class="kpi-note">{esc(item.get("note", ""))}</div>'
            "</article>"
        )
    return '<section class="kpi-grid">' + "".join(cards) + "</section>" if cards else ""


def render_bar(visual: dict[str, Any], queries: dict[str, dict[str, Any]]) -> str:
    items = visual.get("items") or []
    values = []
    for item in items:
        try:
            values.append(float(resolve_value(item, queries)))
        except (TypeError, ValueError):
            values.append(0.0)
    maximum = max([abs(value) for value in values] or [1.0]) or 1.0
    rows = []
    for item, number in zip(items, values):
        width = min(100.0, abs(number) / maximum * 100.0)
        display = item.get("display") or format_value(
            number, str(item.get("format", "decimal")), int(item.get("decimals", 1))
        )
        status = str(item.get("status", "neutral"))
        rows.append(
            '<div class="bar-row">'
            f'<span>{esc(item.get("label"))}</span>'
            f'<div class="bar-track"><div class="bar-fill {esc(status)}" style="width:{width:.2f}%"></div></div>'
            f'<span class="bar-value {esc(status)}">{esc(display)}</span>'
            "</div>"
        )
    return "".join(rows)


def render_distribution(visual: dict[str, Any], queries: dict[str, dict[str, Any]]) -> str:
    parts = visual.get("items") or []
    values = []
    for item in parts:
        try:
            values.append(max(0.0, float(resolve_value(item, queries))))
        except (TypeError, ValueError):
            values.append(0.0)
    total = sum(values) or 1.0
    spans = []
    legend = []
    for index, (item, value) in enumerate(zip(parts, values)):
        pct = value / total * 100.0
        color = str(item.get("color") or COLORS[index % len(COLORS)])
        spans.append(f'<span style="width:{pct:.2f}%;background:{esc(color)}">{pct:.0f}%</span>')
        legend.append(f'<span><i class="legend-dot" style="background:{esc(color)}"></i>{esc(item.get("label"))}</span>')
    return '<div class="distribution">' + "".join(spans) + '</div><div class="trend-legend">' + "".join(legend) + "</div>"


def render_trend(visual: dict[str, Any], queries: dict[str, dict[str, Any]]) -> str:
    series = visual.get("series") or []
    all_values: list[float] = []
    normalized: list[tuple[dict[str, Any], list[float]]] = []
    for item in series:
        values = [float(value) for value in item.get("values", [])]
        all_values.extend(values)
        normalized.append((item, values))
    if not all_values:
        return '<div class="callout caution">Sin datos para la tendencia.</div>'
    minimum, maximum = min(all_values), max(all_values)
    span = maximum - minimum or 1.0
    width, height, pad = 600, 180, 25
    polylines = []
    legend = []
    for index, (item, values) in enumerate(normalized):
        color = str(item.get("color") or COLORS[index % len(COLORS)])
        denominator = max(1, len(values) - 1)
        points = []
        circles = []
        for point_index, value in enumerate(values):
            x = pad + point_index * (width - 2 * pad) / denominator
            y = height - pad - (value - minimum) / span * (height - 2 * pad)
            points.append(f"{x:.1f},{y:.1f}")
            circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{esc(color)}"/>')
        polylines.append(
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{esc(color)}" stroke-width="3"/>'
            + "".join(circles)
        )
        legend.append(f'<span><i class="legend-dot" style="background:{esc(color)}"></i>{esc(item.get("label"))}</span>')
    svg = (
        f'<svg class="trend-svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(visual.get("title"))}">'
        f'<line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" stroke="#aaa"/>'
        + "".join(polylines)
        + "</svg>"
    )
    return svg + '<div class="trend-legend">' + "".join(legend) + "</div>"


def render_table(visual: dict[str, Any]) -> str:
    columns = visual.get("columns") or []
    rows = visual.get("rows") or []
    head = "".join(f"<th>{esc(column)}</th>" for column in columns)
    body = []
    for row in rows:
        if isinstance(row, dict):
            values = [row.get(column, "") for column in columns]
        else:
            values = row
        body.append("<tr>" + "".join(f"<td>{esc(value)}</td>" for value in values) + "</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def render_visual(visual: dict[str, Any], queries: dict[str, dict[str, Any]]) -> str:
    kind = str(visual.get("type", "text"))
    if kind == "bar":
        body = render_bar(visual, queries)
    elif kind == "distribution":
        body = render_distribution(visual, queries)
    elif kind == "trend":
        body = render_trend(visual, queries)
    elif kind == "table":
        body = render_table(visual)
    elif kind == "callout":
        body = f'<div class="callout {esc(visual.get("status", ""))}">{esc(visual.get("text"))}</div>'
    else:
        body = f'<p>{esc(visual.get("text", ""))}</p>'
    return f'<article class="visual"><h3>{esc(visual.get("title", ""))}</h3>{body}</article>'


def render_section(section: dict[str, Any], queries: dict[str, dict[str, Any]]) -> str:
    visuals = section.get("visuals") or []
    grid_class = "visual-grid single" if len(visuals) == 1 else "visual-grid"
    return (
        '<section class="section">'
        f'<h2>{esc(section.get("title"))}</h2>'
        f'<p class="section-intro">{esc(section.get("intro", ""))}</p>'
        f'<div class="{grid_class}">{"".join(render_visual(item, queries) for item in visuals)}</div>'
        "</section>"
    )


def expand_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for section in sections:
        visuals = section.get("visuals") or []
        long_tables = [
            visual
            for visual in visuals
            if visual.get("type") == "table" and len(visual.get("rows") or []) > TABLE_ROWS_PER_PAGE
        ]
        if not long_tables:
            expanded.append(section)
            continue
        regular = [visual for visual in visuals if visual not in long_tables]
        if regular:
            regular_section = copy.deepcopy(section)
            regular_section["visuals"] = regular
            expanded.append(regular_section)
        for table in long_tables:
            rows = table.get("rows") or []
            chunks = [rows[index : index + TABLE_ROWS_PER_PAGE] for index in range(0, len(rows), TABLE_ROWS_PER_PAGE)]
            for index, chunk in enumerate(chunks, start=1):
                table_section = copy.deepcopy(section)
                table_section["title"] = f"{section.get('title', '')} · tabla {index}/{len(chunks)}"
                table_copy = copy.deepcopy(table)
                table_copy["rows"] = chunk
                table_section["visuals"] = [table_copy]
                expanded.append(table_section)
    return expanded


def render_summary(items: list[dict[str, Any]]) -> str:
    if not items:
        return ""
    lines = []
    for item in items:
        kind = str(item.get("type", "fact"))
        lines.append(f'<li class="{esc(kind)}">{esc(item.get("text"))}</li>')
    return '<section class="summary"><h2>Conclusión ejecutiva</h2><ul>' + "".join(lines) + "</ul></section>"


def footer(report: dict[str, Any], page: int) -> str:
    return (
        '<footer class="footer">'
        f'<span>{esc(report.get("organization", ""))} · {esc(report.get("confidentiality", ""))}</span>'
        f'<span>{esc(report.get("date", ""))} · <span class="page-number" data-page="{page:02d}"></span></span>'
        "</footer>"
    )


def masthead(report: dict[str, Any], logo_uri: str, compact: bool = False) -> str:
    title = report.get("title", "Informe ejecutivo")
    period = report.get("period", "")
    return (
        '<header class="masthead"><div>'
        f'<div class="brand-kicker">{esc(report.get("organization", "Analytics Team"))}</div>'
        f'<h1 class="title">{esc(title)}<br><span class="period">{esc(period)}</span></h1>'
        f'<p class="subtitle">{esc(report.get("subtitle", ""))}</p>'
        '<div class="meta-row">'
        f'<span class="chip">Fuente: {esc(report.get("source_label", ""))}</span>'
        f'<span class="chip">Versión {esc(report.get("version", ""))}</span>'
        "</div></div>"
        + (
            f'<img class="logo" alt="{esc(report.get("organization", "Organization"))} logo" src="{logo_uri}">'
            if logo_uri
            else ""
        )
        + "</header>"
    )


def brand_css(report: dict[str, Any]) -> str:
    brand = report.get("brand") or {}
    mapping = {"primary": "--red", "ink": "--black", "panel": "--panel"}
    declarations = []
    for key, css_variable in mapping.items():
        value = brand.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not HEX_COLOR.fullmatch(value):
            raise ReportError(f"Color de marca inválido en report.brand.{key}: {value!r}")
        declarations.append(f"{css_variable}:{value}")
    return ":root{" + ";".join(declarations) + "}" if declarations else ""


def build_html(content: dict[str, Any], snapshot: dict[str, Any], css: str, logo_uri: str) -> str:
    report = content.get("report") or {}
    queries = query_map(snapshot)
    sections = content.get("sections") or []
    layout = report.get("layout", "multipage")
    pages: list[str] = []
    first_body = masthead(report, logo_uri) + render_kpis(content.get("kpis") or [], queries)
    if layout == "one_pager":
        first_body += "".join(render_section(section, queries) for section in sections)
    first_body += render_summary(report.get("executive_summary") or [])
    footnotes = content.get("footnotes") or []
    if footnotes:
        first_body += '<div class="footnotes">' + "<br>".join(esc(note) for note in footnotes) + "</div>"
    pages.append(f'<main class="sheet">{first_body}{footer(report, 1)}</main>')

    if layout != "one_pager":
        for index, section in enumerate(expand_sections(sections), start=2):
            body = masthead({**report, "title": section.get("title"), "subtitle": section.get("intro")}, logo_uri, True)
            body += render_section({**section, "title": "", "intro": ""}, queries)
            pages.append(f'<main class="sheet">{body}{footer(report, index)}</main>')

    manifest = {
        "schema_version": content.get("schema_version"),
        "report_version": report.get("version"),
        "snapshot_model": snapshot.get("model", {}).get("model_name"),
        "extracted_at": snapshot.get("extracted_at"),
        "query_ids": sorted(queries),
    }
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{esc(report.get("title"))}</title><style>{css}{brand_css(report)}</style></head><body>'
        + "".join(pages)
        + '<script id="report-manifest" type="application/json">'
        + json.dumps(manifest, ensure_ascii=False).replace("</", "<\\/")
        + "</script>"
        + "</body></html>"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Renderiza un informe ejecutivo autocontenido.")
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--content", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_dir = args.report_dir.resolve()
    content_path = args.content if args.content.is_absolute() else report_dir / args.content
    content = load_yaml(content_path)
    snapshot_path = find_snapshot(report_dir, content)
    snapshot = load_json(snapshot_path)
    version = content_version(content_path, content)
    output = args.output or report_dir / "output" / f"report_v{version}.html"
    if not output.is_absolute():
        output = report_dir / output
    skill_root = Path(__file__).resolve().parents[1]
    css = (skill_root / "assets" / "report.css").read_text(encoding="utf-8")
    logo_uri = ""
    logo_path = (content.get("report") or {}).get("logo_path")
    if logo_path:
        candidate = (report_dir / str(logo_path)).resolve()
        try:
            candidate.relative_to(report_dir)
        except ValueError as exc:
            raise ReportError("report.logo_path debe permanecer dentro del pack") from exc
        logo_uri = data_uri(candidate)
    rendered = build_html(content, snapshot, css, logo_uri)
    write_text_new(output, rendered, args.force)
    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReportError as exc:
        raise SystemExit(f"[ERROR] {exc}")
