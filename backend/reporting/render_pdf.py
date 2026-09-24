"""PDF from ``ReportDocument`` (plan P0-5) — ReportLab, DejaVu font, A4.

Layout: cover (subject + chart facts) → BodyGraph page → table of contents →
sections exactly as in the Markdown/web view. PDF outline (bookmarks) mirrors
the section list. ``tools/hd_report_pdf.build_pdf`` stays for the legacy CLI.
"""

from __future__ import annotations

import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, CondPageBreak, Flowable, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Preformatted, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from .contract import ReportDocument
from .mdblocks import Code, Heading, Inline, ListBlock, Paragraph as MdParagraph, Quote, Rule, Table as MdTable
from .mdblocks import parse_blocks
from .render_common import (
    Theme, bodygraph_png, breaks_between_sections, chart_facts, dejavu_paths, included_sections, mode_label,
    prepared_on, short_title, subject_lines,
)

PAGE_W, PAGE_H = A4
MARGIN_X = 20 * mm
MARGIN_TOP = 22 * mm
MARGIN_BOTTOM = 20 * mm
FRAME_W = PAGE_W - 2 * MARGIN_X

_FONTS_READY = False


def _register_fonts() -> None:
    global _FONTS_READY  # noqa: PLW0603
    if _FONTS_READY:
        return
    paths = dejavu_paths()
    for name, key in (("HD", "regular"), ("HD-Bold", "bold"), ("HD-Italic", "italic"),
                      ("HD-BoldItalic", "bold_italic"), ("HD-Mono", "mono")):
        pdfmetrics.registerFont(TTFont(name, paths[key]))
    pdfmetrics.registerFontFamily("HD", normal="HD", bold="HD-Bold", italic="HD-Italic", boldItalic="HD-BoldItalic")
    _FONTS_READY = True


def _styles(theme: Theme) -> dict[str, ParagraphStyle]:
    ink, muted = colors.HexColor(theme.ink), colors.HexColor(theme.muted)
    primary, dark = colors.HexColor(theme.primary), colors.HexColor(theme.primary_dark)
    base = dict(fontName="HD", textColor=ink)
    return {
        "brand": ParagraphStyle("brand", **{**base, "textColor": primary}, fontSize=10, leading=14),
        "cover_title": ParagraphStyle("cover_title", **{**base, "textColor": dark, "fontName": "HD-Bold"},
                                      fontSize=26, leading=33, spaceAfter=6),
        "cover_name": ParagraphStyle("cover_name", **{**base, "fontName": "HD-Bold"}, fontSize=17, leading=23),
        "cover_meta": ParagraphStyle("cover_meta", **{**base, "textColor": muted}, fontSize=10.5, leading=15),
        "section": ParagraphStyle("section", **{**base, "textColor": dark, "fontName": "HD-Bold"},
                                  fontSize=17, leading=23, spaceBefore=4, spaceAfter=10),
        "h1": ParagraphStyle("h1", **{**base, "textColor": dark, "fontName": "HD-Bold"}, fontSize=15, leading=20,
                             spaceBefore=12, spaceAfter=6),
        "h2": ParagraphStyle("h2", **{**base, "textColor": primary, "fontName": "HD-Bold"}, fontSize=13, leading=18,
                             spaceBefore=12, spaceAfter=5),
        "h3": ParagraphStyle("h3", **{**base, "fontName": "HD-Bold"}, fontSize=11.5, leading=16, spaceBefore=9,
                             spaceAfter=4),
        "body": ParagraphStyle("body", **base, fontSize=10.5, leading=16, spaceAfter=6, alignment=TA_LEFT),
        "quote": ParagraphStyle("quote", **base, fontSize=10.5, leading=16),
        "cell": ParagraphStyle("cell", **base, fontSize=9.5, leading=13),
        "cell_label": ParagraphStyle("cell_label", **{**base, "textColor": muted}, fontSize=9, leading=12.5),
        "cell_head": ParagraphStyle("cell_head", **{**base, "fontName": "HD-Bold"}, fontSize=9.5, leading=13),
        "code": ParagraphStyle("code", **{**base, "fontName": "HD-Mono"}, fontSize=8.5, leading=11.5),
        "caption": ParagraphStyle("caption", **{**base, "textColor": muted}, fontSize=9, leading=13,
                                  alignment=TA_CENTER),
        "toc_title": ParagraphStyle("toc_title", **{**base, "textColor": dark, "fontName": "HD-Bold"},
                                    fontSize=17, leading=23, spaceAfter=12),
        "toc0": ParagraphStyle("toc0", **base, fontSize=11, leading=16, leftIndent=0, firstLineIndent=0, rightIndent=14 * mm,
                               spaceBefore=3),
    }


def _markup(inline: Inline) -> str:
    out = []
    for span in inline:
        text = escape(span.text)
        if span.code:
            text = f'<font face="HD-Mono">{text}</font>'
        if span.italic:
            text = f"<i>{text}</i>"
        if span.bold:
            text = f"<b>{text}</b>"
        out.append(text)
    return "".join(out)


def _lines(lines: list[Inline]) -> str:
    return "<br/>".join(_markup(line) for line in lines)


class _SectionAnchor(Flowable):
    """Zero-size marker: bookmark + TOC entry for a section title."""

    def __init__(self, key: str, title: str) -> None:
        super().__init__()
        self.key, self.title = key, title
        self.width = self.height = 0

    def draw(self) -> None:
        canvas = self.canv
        canvas.bookmarkPage(self.key)
        canvas.addOutlineEntry(self.title, self.key, level=0, closed=False)


class _ReportDoc(BaseDocTemplate):
    def afterFlowable(self, flowable) -> None:  # noqa: N802 - ReportLab API
        if isinstance(flowable, _SectionAnchor):
            self.notify("TOCEntry", (0, short_title(flowable.title), self.page, flowable.key))


def _blocks_to_flowables(markdown: str, st: dict[str, ParagraphStyle], theme: Theme) -> list:
    story: list = []
    line_color = colors.HexColor(theme.line)
    for block in parse_blocks(markdown):
        if isinstance(block, Heading):
            style = st["h1"] if block.level <= 1 else st["h2"] if block.level == 2 else st["h3"]
            story.append(Paragraph(_markup(block.text), style))
        elif isinstance(block, MdParagraph):
            story.append(Paragraph(_lines(block.lines), st["body"]))
        elif isinstance(block, ListBlock):
            for item in block.items:
                indent = 12 + item.level * 14
                bullet = f"{item.number}." if item.number is not None else ("•" if item.level == 0 else "◦")
                style = ParagraphStyle(f"li{item.level}", parent=st["body"], leftIndent=indent + 4,
                                       bulletIndent=indent - 10, spaceAfter=3)
                story.append(Paragraph(_lines(item.lines), style, bulletText=bullet))
            story.append(Spacer(1, 3))
        elif isinstance(block, Quote):
            para = Paragraph(_lines(block.lines), st["quote"])
            box = Table([[para]], colWidths=[FRAME_W])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6ECD9")),
                ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(theme.accent)),
                ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]))
            story += [box, Spacer(1, 7)]
        elif isinstance(block, MdTable):
            cols = max(1, len(block.header))
            data = [[Paragraph(_markup(c), st["cell_head"]) for c in block.header]]
            data += [[Paragraph(_markup(c), st["cell"]) for c in row] for row in block.rows]
            table = Table(data, colWidths=[FRAME_W / cols] * cols, repeatRows=1)
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, line_color),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF3FA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story += [table, Spacer(1, 8)]
        elif isinstance(block, Rule):
            rule = Table([[""]], colWidths=[FRAME_W], rowHeights=[1])
            rule.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 0.6, line_color)]))
            story += [Spacer(1, 6), rule, Spacer(1, 6)]
        elif isinstance(block, Code):
            story += [Preformatted(block.text, st["code"]), Spacer(1, 6)]
    return story


def _facts_table(rows: list[tuple[str, str]], st: dict[str, ParagraphStyle], theme: Theme) -> Table:
    data = [[Paragraph(escape(label), st["cell_label"]), Paragraph(escape(value or "—"), st["cell"])]
            for label, value in rows]
    table = Table(data, colWidths=[62 * mm, FRAME_W - 62 * mm])
    table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor(theme.line)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def render_pdf(document: ReportDocument, theme: Theme | None = None) -> bytes:
    """Render ``document`` to PDF bytes."""
    _register_fonts()
    theme = theme or Theme()
    st = _styles(theme)
    name = document.subject.name or "Báo cáo"
    buffer = io.BytesIO()

    def cover_page(canvas, _doc) -> None:
        canvas.saveState()
        canvas.setFillColor(colors.HexColor(theme.paper))
        canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor(theme.primary))
        canvas.rect(0, PAGE_H - 9 * mm, PAGE_W, 9 * mm, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor(theme.accent))
        canvas.rect(0, PAGE_H - 10.5 * mm, PAGE_W, 1.5 * mm, stroke=0, fill=1)
        canvas.setFont("HD", 8)
        canvas.setFillColor(colors.HexColor(theme.muted))
        canvas.drawCentredString(PAGE_W / 2, 12 * mm, f"{theme.brand_name} · Tính bằng Swiss Ephemeris")
        canvas.restoreState()

    def content_page(canvas, doc) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor(theme.line))
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN_X, PAGE_H - 14 * mm, PAGE_W - MARGIN_X, PAGE_H - 14 * mm)
        canvas.setFont("HD", 8)
        canvas.setFillColor(colors.HexColor(theme.muted))
        canvas.drawString(MARGIN_X, PAGE_H - 12 * mm, f"{document.title}"[:95])
        canvas.drawString(MARGIN_X, 12 * mm, theme.brand_name)
        canvas.drawRightString(PAGE_W - MARGIN_X, 12 * mm, f"Trang {doc.page}")
        canvas.restoreState()

    doc = _ReportDoc(buffer, pagesize=A4, title=document.title, author=theme.brand_name,
                     subject=f"Human Design — {name}", creator=theme.brand_name)
    frame = Frame(MARGIN_X, MARGIN_BOTTOM, FRAME_W, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame], onPage=cover_page),
        PageTemplate(id="content", frames=[frame], onPage=content_page),
    ])

    story: list = [Spacer(1, 18 * mm), Paragraph(escape(theme.brand_name.upper()), st["brand"]), Spacer(1, 4 * mm),
                   Paragraph(escape(document.title), st["cover_title"]), Spacer(1, 10 * mm),
                   Paragraph("Thông tin người được phân tích", st["h2"]),
                   _facts_table(subject_lines(document), st, theme), Spacer(1, 8 * mm),
                   Paragraph("Bản thiết kế tóm tắt", st["h2"]),
                   _facts_table(chart_facts(document), st, theme), Spacer(1, 10 * mm),
                   Paragraph(escape(f"Chuẩn bị ngày {prepared_on(document)} · {mode_label(document)}"),
                             st["cover_meta"]),
                   Paragraph("Giờ sinh hiển thị đúng như đã khai báo (giờ Việt Nam).", st["cover_meta"]),
                   NextPageTemplate("content"), PageBreak()]

    png = bodygraph_png(document)
    story.append(Paragraph("BodyGraph — Bản đồ năng lượng của bạn", st["section"]))
    if png:
        image = Image(io.BytesIO(png))
        max_w, max_h = FRAME_W, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM - 30 * mm
        ratio = min(max_w / image.imageWidth, max_h / image.imageHeight)
        image.drawWidth, image.drawHeight = image.imageWidth * ratio, image.imageHeight * ratio
        story += [image, Spacer(1, 3 * mm),
                  Paragraph("Trung tâm có màu = năng lượng ổn định, tài năng bẩm sinh · Trung tâm trắng = nơi dễ bị "
                            "ảnh hưởng, cũng là nơi học được trí tuệ · Đen = Personality (ý thức) · Đỏ = Design "
                            "(vô thức).", st["caption"])]
    else:
        story.append(Paragraph("Không dựng được hình BodyGraph trên máy chủ này — xem file SVG đi kèm báo cáo.",
                               st["body"]))
    story.append(PageBreak())

    sections = included_sections(document)
    toc = TableOfContents(levelStyles=[st["toc0"]], dotsMinLevel=0)
    story += [Paragraph("Mục lục", st["toc_title"]), toc, PageBreak()]

    new_page = breaks_between_sections(document)
    for index, section in enumerate(sections):
        if index and new_page:
            story.append(PageBreak())
        elif index:
            story += [Spacer(1, 6 * mm), CondPageBreak(60 * mm)]
        key = f"s{index}"
        body = _blocks_to_flowables(section.content_markdown, st, theme)
        # Keep the title with the first block so a heading never sits alone at a page bottom.
        story.append(KeepTogether([_SectionAnchor(key, section.title),
                                   Paragraph(escape(section.title), st["section"]), *body[:1]]))
        story += body[1:]

    doc.multiBuild(story)
    return buffer.getvalue()


__all__ = ["render_pdf"]
