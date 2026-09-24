"""PDF / DOCX renderers built from ReportDocument (plan P0-5, P0-6) + Markdown block parser."""

from __future__ import annotations

import io
import pathlib
import sys
import zipfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
for path in (ROOT, ROOT / "tools", ROOT / "mcp"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.reporting import export_report  # noqa: E402
from backend.reporting.contract import ReportRequest  # noqa: E402
from backend.reporting.mdblocks import (  # noqa: E402
    Code, Heading, ListBlock, Paragraph, Quote, Rule, Table, parse_blocks, parse_inline,
)
from backend.reporting.orchestrator import ReportOrchestrator  # noqa: E402
from backend.reporting import render_common  # noqa: E402
from backend.reporting.render_common import Theme, included_sections  # noqa: E402
from backend.reporting.render_docx import render_docx  # noqa: E402
from backend.reporting.render_pdf import render_pdf  # noqa: E402

SUBJECT = {"name": "Nguyễn Văn A", "birth_date": "1990-05-15", "birth_time": "08:30", "birth_location": "Hòa Bình"}
EXTRA_MD = (
    "\n\n> Trích dẫn **đậm**\n\n| Cột A | Cột B |\n|---|---|\n| 1 | *nghiêng* |\n\n---\n\n"
    "```\nmã\n```\n\n1. một\n2. hai\n   - con\n"
)


def _document(template: str = "operating_manual", tier: str = "deep_core"):
    request = ReportRequest.model_validate({"subject": SUBJECT, "tier": tier, "template": template})
    return ReportOrchestrator().run(request)


# --- markdown parser ----------------------------------------------------------

def test_inline_styles_and_literals():
    spans = parse_inline("**đậm** và *nghiêng* _cũng nghiêng_ `mã` [liên kết](https://x.vn)")
    assert [(s.text, s.bold, s.italic, s.code) for s in spans] == [
        ("đậm", True, False, False), (" và ", False, False, False), ("nghiêng", False, True, False),
        (" ", False, False, False), ("cũng nghiêng", False, True, False), (" ", False, False, False),
        ("mã", False, False, True), (" liên kết", False, False, False),
    ]
    assert parse_inline("2 * 3 = 6")[0].text == "2 * 3 = 6"
    assert parse_inline("snake_case_name")[0].text == "snake_case_name"
    assert parse_inline("**chưa đóng")[0].text == "**chưa đóng"
    assert parse_inline("<script>x</script>")[0].text == "<script>x</script>"


def test_block_parser_covers_report_dialect():
    blocks = parse_blocks("# Tiêu đề\n\ndòng 1\ndòng 2\n\n- a\n  - b\n    tiếp\n" + EXTRA_MD)
    kinds = [type(b) for b in blocks]
    assert kinds == [Heading, Paragraph, ListBlock, Quote, Table, Rule, Code, ListBlock]
    assert len(blocks[1].lines) == 2
    assert [(i.level, len(i.lines)) for i in blocks[2].items] == [(0, 1), (1, 2)]
    assert blocks[4].rows[0][1][0].italic
    assert [(i.number, i.level) for i in blocks[7].items] == [(1, 0), (2, 0), (None, 1)]


# --- PDF ----------------------------------------------------------------------

def test_pdf_contains_subject_bodygraph_and_all_sections():
    pypdf = pytest.importorskip("pypdf")
    document = _document()
    pdf = render_pdf(document)
    assert pdf.startswith(b"%PDF")
    reader = pypdf.PdfReader(io.BytesIO(pdf))
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert "Nguyễn Văn A" in text
    assert "15/05/1990 08:30 (giờ Việt Nam)" in text
    assert "UTC" not in text
    assert "Người định hướng (Projector)" in text
    for section in included_sections(document):
        assert section.title.split(":")[0] in text
    assert [item.title for item in reader.outline] == [s.title for s in included_sections(document)]
    assert any("/Image" in str(page.get("/Resources", {}).get("/XObject", {})) or page.images
               for page in reader.pages[:3])


def test_pdf_hides_internal_warnings_and_renders_extra_markdown():
    pypdf = pytest.importorskip("pypdf")
    document = _document("sections", "free_basic")
    document.warnings.append("Chế độ LLM không khả dụng, dùng nội dung template: test")
    document.sections[0].content_markdown += EXTRA_MD
    text = "\n".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(render_pdf(document))).pages)
    assert "Chế độ LLM không khả dụng" not in text
    assert "Cột A" in text and "nghiêng" in text


def test_pdf_without_rasterizer_prints_note(monkeypatch):
    pypdf = pytest.importorskip("pypdf")
    monkeypatch.setattr(render_common, "_rasterize", lambda svg, zoom: None)
    monkeypatch.setattr(render_common, "_PNG_CACHE", {})
    import backend.reporting.render_pdf as module

    monkeypatch.setattr(module, "bodygraph_png", render_common.bodygraph_png)
    text = pypdf.PdfReader(io.BytesIO(render_pdf(_document("sections", "free_basic")))).pages[1].extract_text()
    assert "xem file SVG" in text


# --- DOCX ---------------------------------------------------------------------

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid",
             "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
             "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr", "pPrChange"]
TCPR_ORDER = ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar",
              "textDirection", "tcFitText", "vAlign", "hideMark"]


def _ooxml_order_violations(data: bytes) -> list[str]:
    from lxml import etree

    bad = []
    archive = zipfile.ZipFile(io.BytesIO(data))
    root = etree.fromstring(archive.read("word/document.xml"))
    for tag, order in (("pPr", PPR_ORDER), ("tcPr", TCPR_ORDER)):
        for element in root.iter(W + tag):
            names = [child.tag.replace(W, "") for child in element]
            index = [order.index(n) for n in names if n in order]
            if index != sorted(index):
                bad.append(f"{tag}: {names}")
    return bad


def test_docx_structure_image_and_valid_element_order():
    docx = pytest.importorskip("docx")
    document = _document("sections", "deep_core")
    document.sections[0].content_markdown += EXTRA_MD
    data = render_docx(document, Theme(brand_name="Studio Thử"))
    word = docx.Document(io.BytesIO(data))
    text = "\n".join(p.text for p in word.paragraphs)
    cells = "\n".join(c.text for t in word.tables for row in t.rows for c in row.cells)
    assert "Nguyễn Văn A" in cells and "15/05/1990 08:30 (giờ Việt Nam)" in cells
    assert "UTC" not in text + cells
    headings = [p.text for p in word.paragraphs if p.style.name == "Heading 1"]
    assert headings[1:] == [s.title for s in included_sections(document)]
    assert len(word.inline_shapes) == 1
    assert "STUDIO THỬ" in text
    assert word.core_properties.title == document.title
    assert _ooxml_order_violations(data) == []


def test_export_report_writes_pdf_and_docx(tmp_path):
    paths = export_report(_document("sections", "free_basic"), tmp_path, include_pdf=True, include_docx=True)
    assert paths["pdf"].read_bytes().startswith(b"%PDF")
    assert paths["docx"].read_bytes()[:2] == b"PK"
    assert "pdf" not in export_report(_document("sections", "free_basic"), tmp_path / "plain")
