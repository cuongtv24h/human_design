"""One place that turns a stored report into a downloadable file.

Used by the authenticated export routes, the 5-minute signed links (P0-10) and the
client share page (P3). Every format is built from the same ``ReportDocument``.
"""

from __future__ import annotations

import unicodedata
from urllib.parse import quote

from fastapi import HTTPException, Response
from sqlalchemy.orm import Session

from backend.reporting.export import _slug, bodygraph_svg
from backend.reporting.infographic import render_infographic_html
from backend.reporting.render_common import MissingFontError

from .models import Report
from .services import ARTIFACT_FORMATS, load_document, render_artifact, report_theme

INFOGRAPHIC_CSP = "default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:"

# format -> (media type, filename suffix, download by default)
FILE_FORMATS: dict[str, tuple[str, str, bool]] = {
    "pdf": (ARTIFACT_FORMATS["pdf"][0], ARTIFACT_FORMATS["pdf"][1], True),
    "docx": (ARTIFACT_FORMATS["docx"][0], ARTIFACT_FORMATS["docx"][1], True),
    "markdown": ("text/markdown; charset=utf-8", ".md", True),
    "infographic": ("text/html; charset=utf-8", "_infographic.html", False),
    "bodygraph_svg": ("image/svg+xml", "_bodygraph.svg", False),
}
FORMAT_LABELS = {"pdf": "PDF", "docx": "Word (DOCX)", "markdown": "Markdown", "infographic": "Infographic",
                 "bodygraph_svg": "BodyGraph SVG"}


def ascii_filename(value: str) -> str:
    """"Nguyễn Văn Đức" → "Nguyen Van Duc" for the legacy filename= parameter."""
    value = value.replace("đ", "d").replace("Đ", "D")
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()


def render_file(db: Session, artifact_dir: str, report: Report, fmt: str) -> bytes | str:
    if fmt not in FILE_FORMATS:
        raise HTTPException(status_code=404, detail="Định dạng không được hỗ trợ.")
    if not report.document:
        raise HTTPException(status_code=409, detail="Báo cáo chưa có nội dung.")
    if fmt in ARTIFACT_FORMATS:
        try:
            return render_artifact(artifact_dir, report, fmt, report_theme(db, report))
        except MissingFontError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    document = load_document(report)
    if fmt == "markdown":
        return document.to_markdown()
    if fmt == "infographic":
        return render_infographic_html(document)
    return bodygraph_svg(document)


def file_response(db: Session, artifact_dir: str, report: Report, fmt: str, download: bool | None = None,
                  extra_headers: dict[str, str] | None = None) -> Response:
    body = render_file(db, artifact_dir, report, fmt)
    media_type, suffix, default_download = FILE_FORMATS[fmt]
    headers = {"Cache-Control": "private, no-store", **(extra_headers or {})}
    if download if download is not None else default_download:
        name = f"{_slug(report.client.full_name)}_{report.id[:8]}{suffix}"
        legacy = ascii_filename(name) or f"bao-cao{suffix}"
        headers["Content-Disposition"] = f"attachment; filename=\"{legacy}\"; filename*=UTF-8''{quote(name)}"
    if fmt == "infographic":
        headers["Content-Security-Policy"] = INFOGRAPHIC_CSP
    return Response(content=body, media_type=media_type, headers=headers)
