from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

from report_common import ReportError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exporta un HTML ejecutivo a PDF A4.")
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    html_path = args.html.resolve()
    pdf_path = args.pdf.resolve()
    if not html_path.exists():
        raise ReportError(f"HTML no encontrado: {html_path}")
    if pdf_path.exists() and not args.force:
        raise ReportError(f"Se rechaza sobrescribir una versión existente: {pdf_path}")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1240, "height": 1754})
        page.goto(html_path.as_uri(), wait_until="networkidle")
        page.emulate_media(media="print")
        overflow = page.locator(".sheet").evaluate_all(
            "els => els.map((el, i) => ({page: i + 1, overflow: el.scrollHeight - el.clientHeight}))"
        )
        clipped = [item for item in overflow if item["overflow"] > 2]
        if clipped:
            browser.close()
            raise ReportError(f"Contenido desbordado en páginas: {clipped}")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        )
        browser.close()
    print(pdf_path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReportError as exc:
        raise SystemExit(f"[ERROR] {exc}")
