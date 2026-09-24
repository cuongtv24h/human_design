"""Shared pieces for the PDF / DOCX renderers (plan P0-5, P0-6).

Every renderer consumes the same ``ReportDocument`` — subject info + the
auto-generated BodyGraph + sections written in the chosen ``content_mode`` —
so PDF, DOCX, Markdown and the web view always carry identical content.
Internal ``warnings`` (e.g. "LLM fell back to template") are for coaches and
are intentionally *not* printed in client-facing files.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import timedelta, timezone
from pathlib import Path

from .contract import ContentMode, ReportDocument, ReportSection
from .export import bodygraph_svg
from .language_vn import TYPE_VN, vn_authority, vn_definition, vn_strategy

from hd_time import display_birth  # noqa: E402  (tools/ added to sys.path by .contract)

VN_TZ = timezone(timedelta(hours=7))


@dataclass(frozen=True)
class Theme:
    """D10: auto-generated sample theme; organisations can override later."""

    brand_name: str = "Human Design Studio"
    primary: str = "#3565A8"
    primary_dark: str = "#234474"
    accent: str = "#C8963E"
    paper: str = "#FBF8F1"
    ink: str = "#232227"
    muted: str = "#6B675E"
    line: str = "#E7E1D4"

    @classmethod
    def from_mapping(cls, data: dict | None) -> "Theme":
        if not data:
            return cls()
        known = {k: str(v) for k, v in data.items() if k in cls.__dataclass_fields__ and v}
        return cls(**known)


# --- fonts ------------------------------------------------------------------

FONT_DIRS = (
    os.environ.get("HD_FONT_DIR", ""),
    str(Path(__file__).resolve().parents[2] / "assets" / "fonts"),
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/dejavu",
    "/usr/share/fonts/TTF",
    "/usr/local/share/fonts",
    "/Library/Fonts",
    "C:/Windows/Fonts",
)


def find_font(filename: str) -> str | None:
    for directory in FONT_DIRS:
        if directory:
            candidate = Path(directory) / filename
            if candidate.is_file():
                return str(candidate)
    return None


class MissingFontError(RuntimeError):
    pass


def dejavu_paths() -> dict[str, str]:
    """Paths of the DejaVu Sans family (full Vietnamese coverage)."""
    regular = find_font("DejaVuSans.ttf")
    if regular is None:
        raise MissingFontError(
            "Không tìm thấy font DejaVuSans.ttf (cần để in tiếng Việt). "
            "Cài gói fonts-dejavu-core (apt) hoặc đặt HD_FONT_DIR tới thư mục chứa font."
        )
    bold = find_font("DejaVuSans-Bold.ttf") or regular
    return {
        "regular": regular,
        "bold": bold,
        "italic": find_font("DejaVuSans-Oblique.ttf") or regular,
        "bold_italic": find_font("DejaVuSans-BoldOblique.ttf") or bold,
        "mono": find_font("DejaVuSansMono.ttf") or regular,
    }


# --- BodyGraph image --------------------------------------------------------


_PNG_CACHE: dict[str, bytes] = {}
_PNG_CACHE_MAX = 32


def bodygraph_png(document: ReportDocument, zoom: float = 1.4) -> bytes | None:
    """Rasterize the BodyGraph SVG to PNG (zoom 1.4 ≈ 185 dpi at A4 print width).

    Rasterizing takes ~1–2 s, so results are memoized by SVG content: the chart
    of a report never changes, only its text does.

    Uses resvg (self-contained wheel, no system libraries); falls back to
    CairoSVG when libcairo is installed. Returns ``None`` if neither works so the
    caller can print a note instead of failing the whole export.
    """
    svg = bodygraph_svg(document)
    key = hashlib.sha256(f"{zoom}|{svg}".encode("utf-8")).hexdigest()
    if key in _PNG_CACHE:
        return _PNG_CACHE[key]
    png = _rasterize(svg, zoom)
    if png is not None:
        if len(_PNG_CACHE) >= _PNG_CACHE_MAX:
            _PNG_CACHE.pop(next(iter(_PNG_CACHE)))
        _PNG_CACHE[key] = png
    return png


def _rasterize(svg: str, zoom: float) -> bytes | None:
    try:
        import resvg_py  # noqa: PLC0415

        font_dirs = [d for d in FONT_DIRS if d and Path(d).is_dir()]
        return bytes(resvg_py.svg_to_bytes(svg_string=svg, background="#ffffff", zoom=zoom,
                                           font_dirs=font_dirs or None))
    except Exception:  # noqa: BLE001 - optional dependency / render failure
        pass
    try:
        import cairosvg  # noqa: PLC0415

        return cairosvg.svg2png(bytestring=svg.encode("utf-8"), scale=zoom, background_color="white")
    except Exception:  # noqa: BLE001
        return None


# --- facts shown on the cover ----------------------------------------------

MODE_LABEL = {
    ContentMode.TEMPLATE: "Nội dung chuẩn",
    ContentMode.LLM: "Biên tập bởi chuyên gia AI",
}


def subject_lines(document: ReportDocument) -> list[tuple[str, str]]:
    subject = document.subject
    rows = [("Họ và tên", subject.name or "—"),
            ("Ngày · giờ sinh", display_birth(subject.birth_date, subject.birth_time, subject.timezone))]
    if subject.birth_location:
        rows.append(("Nơi sinh", subject.birth_location))
    return rows


def chart_facts(document: ReportDocument) -> list[tuple[str, str]]:
    """Key chart facts, bilingual per the shared terminology (tools/hd_language.py)."""
    chart = document.chart
    chart_type = str(chart.get("type", ""))
    type_value = f"{TYPE_VN[chart_type]} ({chart_type})" if chart_type in TYPE_VN else chart_type
    return [
        ("Loại năng lượng · Type", type_value),
        ("Chiến lược sống · Strategy", vn_strategy(str(chart.get("strategy", "")), chart_type)),
        ("Quyền nội tại · Authority", vn_authority(str(chart.get("authority", "")))),
        ("Nhân cách · Profile", str(chart.get("profile", ""))),
        ("Định nghĩa · Definition", vn_definition(str(chart.get("definition", "")))),
        ("Chữ thập hóa thân · Incarnation Cross", str(chart.get("incarnation_cross", ""))),
    ]


def prepared_on(document: ReportDocument) -> str:
    return document.provenance.generated_at.astimezone(VN_TZ).strftime("%d/%m/%Y")


def mode_label(document: ReportDocument) -> str:
    return MODE_LABEL.get(document.content_mode, str(document.content_mode))


def included_sections(document: ReportDocument) -> list[ReportSection]:
    return [s for s in sorted(document.sections, key=lambda item: item.order) if s.status == "included"]


def breaks_between_sections(document: ReportDocument) -> bool:
    """Long narrative parts start on a new page; short technical sections flow on."""
    if document.plan.definition_key == "operating_manual":
        return True
    sections = included_sections(document)
    if not sections:
        return False
    average = sum(len(s.content_markdown) for s in sections) / len(sections)
    return average > 2500


def short_title(title: str) -> str:
    """TOC label: "Phần 3 — Tháo gỡ gánh nặng: Những điều…" → "Phần 3 — Tháo gỡ gánh nặng"."""
    head = title.split(":", 1)[0].strip()
    return head if len(head) >= 8 else title
