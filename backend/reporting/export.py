"""Xuất báo cáo thành file: Markdown + BodyGraph SVG tự sinh.

Chuẩn báo cáo: thông tin người được phân tích + BodyGraph tự sinh qua công cụ
(``tools/hd_bodygraph.py``) + nội dung theo ``content_mode``. Module này đóng
gói bước cuối: từ ``ReportDocument`` ra cặp file ``.md`` + ``_bodygraph.svg``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

from .contract import ReportDocument

_TOOLS_DIR = str(Path(__file__).resolve().parents[2] / "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)


def bodygraph_svg(document: ReportDocument) -> str:
    """Generate the BodyGraph SVG for a document's calculated chart."""
    from hd_bodygraph import generate_bodygraph_svg  # noqa: PLC0415
    from hd_time import display_birth  # noqa: PLC0415

    subject = document.subject
    return generate_bodygraph_svg(
        document.chart,
        name=subject.name,
        # Hiển thị đúng giờ khai báo, không kèm giờ UTC (tools/hd_time.py).
        birth_local_str=f"Sinh {display_birth(subject.birth_date, subject.birth_time, subject.timezone)}",
        place_str=subject.birth_location,
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^0-9A-Za-zÀ-ỹà-ỹ]+", "-", value).strip("-").lower()
    return slug or "bao-cao"


def export_report(
    document: ReportDocument,
    out_dir: str | Path,
    include_bodygraph: bool = True,
    include_infographic: bool = False,
    include_pdf: bool = False,
    include_docx: bool = False,
) -> dict[str, Path]:
    """Write the report markdown (and BodyGraph SVG / infographic) into ``out_dir``.

    Returns the written paths keyed by ``markdown``, ``bodygraph_svg``,
    ``infographic_html``, ``pdf`` and ``docx`` (all but markdown only when requested).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slug = _slug(document.title or document.subject.name)
    paths: dict[str, Path] = {}
    bodygraph_ref: str | None = None
    if include_bodygraph:
        svg_path = out / f"{slug}_bodygraph.svg"
        svg_path.write_text(bodygraph_svg(document), encoding="utf-8")
        paths["bodygraph_svg"] = svg_path
        bodygraph_ref = svg_path.name
    if include_infographic:
        from .infographic import render_infographic_html  # noqa: PLC0415

        html_path = out / f"{slug}_infographic.html"
        html_path.write_text(
            render_infographic_html(document, include_bodygraph=include_bodygraph), encoding="utf-8"
        )
        paths["infographic_html"] = html_path
    if include_pdf:
        from .render_pdf import render_pdf  # noqa: PLC0415

        pdf_path = out / f"{slug}.pdf"
        pdf_path.write_bytes(render_pdf(document))
        paths["pdf"] = pdf_path
    if include_docx:
        from .render_docx import render_docx  # noqa: PLC0415

        docx_path = out / f"{slug}.docx"
        docx_path.write_bytes(render_docx(document))
        paths["docx"] = docx_path
    md_path = out / f"{slug}.md"
    md_path.write_text(document.to_markdown(bodygraph_path=bodygraph_ref), encoding="utf-8")
    paths["markdown"] = md_path
    return paths


__all__ = ["bodygraph_svg", "export_report"]
