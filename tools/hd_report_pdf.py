#!/usr/bin/env python3
"""
Xuất báo cáo Human Design dạng PDF (A4, tiếng Việt):
bìa + BodyGraph minh họa + trung tâm + kênh + cổng + tiềm năng/điểm mù + tiền.

CLI:
    python3 hd_report_pdf.py --date 1984-11-02 --time 02:15 --tz +07:00 \\
        --name "Dương Thị Thu Huyền" --place "Lập Thạch, Vĩnh Phúc" \\
        --out Bao_cao_HD.pdf
"""

import sys
import os
import argparse
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))

from hd_calculator import (calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER)
from hd_analyzer import TYPE_ANALYSIS, CENTER_ANALYSIS, PROFILE_ANALYSIS
from hd_bodygraph import generate_bodygraph_svg, CHANNEL_NAMES, CENTERS
from hd_potential_analysis import analyze_potential_blindspots, format_potential_report, CENTER_BLINDSPOTS
from hd_money_analysis import analyze_money_map, format_money_report

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, PageBreak, HRFlowable,
                                KeepTogether)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", f"{FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", f"{FONT_DIR}/DejaVuSans-Bold.ttf"))

ACCENT = colors.HexColor("#6A1B9A")
ACCENT2 = colors.HexColor("#00838F")
DARK = colors.HexColor("#212121")
GRAY = colors.HexColor("#616161")

CENTER_VN = {
    "Head": "Đầu", "Ajna": "Ajna (Nhận thức)", "Throat": "Cổ họng",
    "G": "G — Bản ngã", "Heart": "Tim (Ego/Ý chí)",
    "Spleen": "Lách (Trực giác)", "Sacral": "Xương cùng (Sinh lực)",
    "Solar Plexus": "Đám rối mặt trời (Cảm xúc)", "Root": "Gốc (Áp lực)",
}
CENTER_ORDER = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen",
                "Sacral", "Solar Plexus", "Root"]

CHANNEL_VN = {
    (64, 47): "Trừu tượng hóa", (61, 24): "Nhận thức", (63, 4): "Logic",
    (17, 62): "Chấp nhận", (43, 23): "Cấu trúc hóa", (11, 56): "Tò mò",
    (35, 36): "Phù du", (12, 22): "Cởi mở", (16, 48): "Bước sóng",
    (20, 10): "Tỉnh thức", (20, 34): "Uy lực cá nhân", (20, 57): "Sóng não",
    (31, 7): "Dẫn đầu", (8, 1): "Cảm hứng", (33, 13): "Chứng nhân",
    (21, 45): "Dòng tiền", (2, 14): "Người giữ chìa khóa", (15, 5): "Nhịp điệu",
    (25, 51): "Khởi phát", (46, 29): "Khám phá", (26, 44): "Buông bỏ",
    (40, 37): "Cộng đồng", (18, 58): "Phán xét", (28, 38): "Đấu tranh",
    (32, 54): "Biến đổi", (50, 27): "Bảo tồn", (34, 10): "Niềm tin sắt đá",
    (34, 57): "Sức mạnh", (10, 57): "Hình mẫu hoàn hảo", (3, 60): "Đột biến",
    (9, 52): "Tập trung", (42, 53): "Trưởng thành", (59, 6): "Kết đôi",
    (30, 41): "Nhận diện", (49, 19): "Tổng hợp", (39, 55): "Sóng cảm xúc",
}

CHANNEL_DESC = {
    (1, 8): ("Kênh của Cảm hứng Sáng tạo: bạn được thiết kế để thể hiện bản thân "
             "một cách độc đáo và đóng góp mẫu hình mới cho tập thể. Sáng tạo của bạn "
             "không phải để làm hài lòng ai — nó là tiếng nói chân thật từ bản ngã (G)."),
    (10, 20): ("Kênh của Tỉnh thức: sống trọn trong hiện tại, hành xử đúng với chính mình "
               "ngay lúc này. Bạn không cần trở thành ai khác — sức mạnh nằm ở sự chân thật "
               "và hiện diện trong từng khoảnh khắc."),
    (10, 34): ("Kênh của Niềm tin Sắt đá: sức mạnh sinh lực (Sacral) phục vụ cho việc sống "
               "đúng với chính mình. Khi bạn làm điều mình yêu và tin, năng lượng gần như "
               "vô tận; khi làm trái mình, cơ thể sẽ phản đối."),
    (19, 49): ("Kênh của Tổng hợp: nhạy cảm sâu sắc với nhu cầu của người khác (cổng 19) "
               "kết hợp nguyên tắc và sự từ chối (cổng 49). Bạn cảm nhận được cộng đồng cần gì, "
               "nhưng chỉ đáp ứng khi đúng nguyên tắc — sẵn sàng 'cách mạng' khi cần."),
    (20, 34): ("Kênh của Uy lực Cá nhân: sức mạnh hành động ngay trong hiện tại. Với tư cách "
               "Manifesting Generator, đây là động cơ giúp bạn vừa đáp ứng nhanh vừa triển khai "
               "mạnh — miễn là đã lắng nghe Sacral trước khi lao đi."),
}

PLANETS = ["Sun", "Earth", "Moon", "North Node", "South Node", "Mercury",
           "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
PLANET_VN = {"Sun": "Mặt Trời", "Earth": "Trái Đất", "Moon": "Mặt Trăng",
             "North Node": "La Hầu", "South Node": "Kế Đô", "Mercury": "Thủy",
             "Venus": "Kim", "Mars": "Hỏa", "Jupiter": "Mộc", "Saturn": "Thổ",
             "Uranus": "Thiên Vương", "Neptune": "Hải Vương", "Pluto": "Diêm Vương"}


def _styles():
    return {
        "title": ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=26,
                                leading=32, alignment=TA_CENTER, textColor=ACCENT),
        "subtitle": ParagraphStyle("subtitle", fontName="DejaVu-Bold", fontSize=18,
                                   leading=24, alignment=TA_CENTER, textColor=DARK),
        "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=16, leading=20,
                             textColor=ACCENT, spaceBefore=6, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=12.5, leading=16,
                             textColor=ACCENT2, spaceBefore=8, spaceAfter=5),
        "body": ParagraphStyle("body", fontName="DejaVu", fontSize=10.5, leading=15.5,
                               alignment=TA_JUSTIFY, textColor=DARK, spaceAfter=5),
        "bullet": ParagraphStyle("bullet", fontName="DejaVu", fontSize=10.5, leading=15,
                                 leftIndent=14, bulletIndent=4, spaceAfter=3, textColor=DARK),
        "small": ParagraphStyle("small", fontName="DejaVu", fontSize=9.5, leading=13.5,
                                textColor=GRAY, alignment=TA_CENTER),
        "cell": ParagraphStyle("cell", fontName="DejaVu", fontSize=9.5, leading=13, textColor=DARK),
        "cell_b": ParagraphStyle("cell_b", fontName="DejaVu-Bold", fontSize=9.5, leading=13, textColor=DARK),
        "cell_h": ParagraphStyle("cell_h", fontName="DejaVu-Bold", fontSize=10, leading=13,
                                 textColor=colors.white),
        "center": ParagraphStyle("center", fontName="DejaVu", fontSize=11, leading=15,
                                 alignment=TA_CENTER, textColor=DARK),
        "quote": ParagraphStyle("quote", fontName="DejaVu-Oblique", fontSize=10.5, leading=15,
                                alignment=TA_CENTER, textColor=GRAY, spaceBefore=6),
        "h3": ParagraphStyle("h3", fontName="DejaVu-Bold", fontSize=11, leading=14,
                             textColor=DARK, spaceBefore=6, spaceAfter=4),
    }


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(A4[0] / 2, 12 * mm,
                             f"Hệ thống Human Design v3.0  •  Trang {doc.page}")
    canvas.restoreState()


def _cover_footer(canvas, doc):
    if doc.page == 1:
        canvas.saveState()
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(GRAY)
        canvas.drawCentredString(A4[0] / 2, 12 * mm,
                                 "Hệ thống Human Design v3.0 • Tính bằng Swiss Ephemeris")
        canvas.restoreState()
    else:
        _footer(canvas, doc)


def _chan_name(g1, g2):
    en = CHANNEL_NAMES.get((g1, g2)) or CHANNEL_NAMES.get((g2, g1), "")
    vn = CHANNEL_VN.get((g1, g2)) or CHANNEL_VN.get((g2, g1), "")
    return en, vn


def _append_markdown(story, text, st):
    import re
    from xml.sax.saxutils import escape
    NL = chr(10)
    for raw in text.split(NL):
        s = raw.strip()
        if not s:
            story.append(Spacer(1, 2 * mm))
            continue
        kind = "body"
        if s.startswith("### "):
            kind, s = "h3", s[4:]
        elif s.startswith("## "):
            kind, s = "h2", s[3:]
        elif s.startswith("# "):
            kind, s = "h1", s[2:]
        elif s.startswith("> "):
            kind, s = "quote", s[2:]
        elif s.startswith("- ") or s.startswith("* "):
            kind, s = "bullet", s[2:]
        elif re.match(r"^" + chr(92) + "d+" + chr(92) + ". ", s):
            kind = "bullet"
            s = re.sub(r"^" + chr(92) + "d+" + chr(92) + ". ", "", s, count=1)
        s = escape(s)
        s = re.sub(chr(92) + "*" + chr(92) + "*(.+?)" + chr(92) + "*" + chr(92) + "*", r"<b>" + chr(92) + "1</b>", s)
        if kind == "bullet":
            story.append(Paragraph(s, st["bullet"], bulletText=chr(8226)))
        else:
            story.append(Paragraph(s, st[kind]))


def build_pdf(chart, name, birth_local_str, utc_str, place_str, out_path):
    # CairoSVG needs the native libcairo library. Keep text/report generation
    # usable when that optional system dependency is unavailable.
    try:
        import cairosvg
    except (ImportError, OSError):
        cairosvg = None

    st = _styles()
    story = []
    defined = set(chart["defined_centers"])
    p_gates = {d["gate"] for d in chart["personality_gates"].values()}
    d_gates = {d["gate"] for d in chart["design_gates"].values()}

    # ================= BÌA =================
    story.append(Spacer(1, 28 * mm))
    story.append(Paragraph("BÁO CÁO HUMAN DESIGN", st["title"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("Bản đồ năng lượng & Thiết kế cuộc đời", st["center"]))
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(name, st["subtitle"]))
    story.append(Spacer(1, 4 * mm))
    info = f"Ngày sinh: {birth_local_str}"
    if place_str:
        info += f"  •  Nơi sinh: {place_str}"
    story.append(Paragraph(info, st["center"]))
    story.append(Paragraph(f"Giờ UTC tính toán: {utc_str}", st["center"]))
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="80%", color=ACCENT, thickness=1.2,
                            hAlign="CENTER", spaceAfter=8))

    facts = [
        ("Type (Loại năng lượng)", f"{chart['type']}<br/>{chart['strategy']}"),
        ("Authority (Thẩm quyền)", str(chart["authority"])),
        ("Profile (Vai trò)", f"{chart['profile']}"),
        ("Definition (Cấu trúc)", str(chart["definition"])),
        ("Incarnation Cross (Sứ mệnh)", str(chart["incarnation_cross"])),
        ("Trung tâm", f"Định nghĩa {len(defined)}: {', '.join(sorted(defined))}<br/>"
                      f"Mở {9 - len(defined)}: {', '.join(sorted(set(CENTER_ORDER) - defined))}"),
        ("Kênh & Cổng", f"{len(chart['defined_channels'])} kênh định nghĩa  •  "
                        f"{len(chart['all_activated_gates'])} cổng kích hoạt"),
    ]
    rows = [[Paragraph(f"<b>{k}</b>", st["cell"]),
             Paragraph(v, st["cell"])] for k, v in facts]
    t = Table(rows, colWidths=[62 * mm, 100 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3E5F5")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#FAFAFA")),
        ("BOX", (0, 0), (-1, -1), 0.8, ACCENT),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CE93D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph("“Không có chart xấu — mỗi thiết kế đều có mục đích.<br/>"
                           "Đừng tin, hãy thử nghiệm.” — Ra Uru Hu", st["quote"]))
    story.append(PageBreak())

    # ================= BODYGRAPH FULL =================
    story.append(Paragraph("Bản đồ BodyGraph — Toàn cảnh 9 trung tâm, 36 kênh, 64 cổng", st["h1"]))
    story.append(Paragraph("Trung tâm <b>có màu</b> = Định nghĩa (năng lượng cố định, điểm mạnh). "
                           "Trung tâm <b>trắng</b> = Mở (nơi học trí tuệ, dễ bị điều kiện hóa). "
                           "Kênh <b>có màu</b> = Định nghĩa (tài năng cố định). "
                           "<b>Đen</b> = Personality/Ý thức, <b>Đỏ</b> = Design/Vô thức.",
                           st["body"]))
    if cairosvg is not None:
        tmpdir = tempfile.mkdtemp()
        full_png = os.path.join(tmpdir, "bg_full.png")
        focus_png = os.path.join(tmpdir, "bg_focus.png")
        svg_full = generate_bodygraph_svg(chart, name=name, birth_local_str=birth_local_str,
                                          utc_str=utc_str, place_str=place_str, mode="full")
        svg_focus = generate_bodygraph_svg(chart, name=name, birth_local_str=birth_local_str,
                                           utc_str=utc_str, place_str=place_str, mode="focus")
        cairosvg.svg2png(bytestring=svg_full.encode("utf-8"), write_to=full_png,
                         scale=2, background_color="white")
        cairosvg.svg2png(bytestring=svg_focus.encode("utf-8"), write_to=focus_png,
                         scale=2, background_color="white")
        story.append(Image(full_png, width=152 * mm, height=210.3 * mm))
        story.append(PageBreak())
    else:
        story.append(Paragraph(
            "BodyGraph chưa được nhúng vì thiếu thư viện native Cairo. "
            "Cài <b>libcairo2</b> rồi chạy lại để có hình minh họa; phần báo cáo chữ vẫn được xuất.",
            st["body"]))
        story.append(PageBreak())

    # ================= SỐNG ĐÚNG THIẾT KẾ =================
    story.append(Paragraph("1. Sống đúng thiết kế của bạn", st["h1"]))
    story.append(Paragraph(f"<b>Type: {chart['type']}</b>", st["h2"]))
    for line in str(TYPE_ANALYSIS.get(chart["type"], "")).strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            story.append(Paragraph(line[1:].strip(), st["bullet"], bulletText="•"))
        else:
            story.append(Paragraph(line, st["body"]))
    story.append(Paragraph(f"<b>Strategy (Chiến lược): {chart['strategy']}</b>", st["h2"]))
    story.append(Paragraph("Strategy là cách bạn tương tác đúng với cuộc đời để giảm kháng cự "
                           "và nhận về đúng cơ hội. Với Manifesting Generator: <b>Chờ tín hiệu để "
                           "Đáp Ứng từ Sacral (uh-huh/uh-uh), rồi Thông Báo</b> cho những người bị "
                           "ảnh hưởng trước khi hành động.", st["body"]))
    story.append(Paragraph(f"<b>Authority (Thẩm quyền ra quyết định): {chart['authority']}</b>", st["h2"]))
    story.append(Paragraph("Bạn là người cảm xúc: <b>không có sự thật trong khoảnh khắc</b>. Sóng cảm xúc "
                           "cần thời gian để lắng xuống và cho bạn sự rõ ràng. Với quyết định lớn, hãy chờ "
                           "ít nhất một đêm (tốt hơn là vài ngày), và đừng quyết khi đang ở đỉnh cao hứng khởi "
                           "hay đáy sâu tuyệt vọng.", st["body"]))
    story.append(Paragraph(f"<b>Profile (Vai trò): {chart['profile']}</b>", st["h2"]))
    story.append(Paragraph(str(PROFILE_ANALYSIS.get(chart["profile"], "")), st["body"]))
    story.append(Paragraph(f"<b>Definition: {chart['definition']}</b>", st["h2"]))
    story.append(Paragraph("Bạn có 2 cụm năng lượng tách rời — chủ đề cuộc đời là tìm kiếm sự kết nối "
                           "(qua người khác hoặc dòng chảy hành tinh). Đừng phụ thuộc vào cầu nối; "
                           "hãy kiên nhẫn với sự tách rời.", st["body"]))
    story.append(Paragraph(f"<b>Incarnation Cross: {chart['incarnation_cross']}</b>", st["h2"]))
    story.append(Paragraph("Thập tự Luân hồi là mục đích sống tổng quát — bối cảnh lớn mà cuộc đời bạn "
                           "diễn ra. Đây là Right Angle Cross (góc phải): hành trình mang tính cá nhân, "
                           "tự trải nghiệm và chiêm nghiệm.", st["body"]))

    # ================= 9 TRUNG TÂM =================
    story.append(Paragraph("2. Chín trung tâm năng lượng", st["h1"]))
    story.append(Paragraph("Trung tâm <b>Định nghĩa</b> (có màu): năng lượng nhất quán, là điểm mạnh cố định "
                           "nhưng cũng có 'điểm mù của điểm mạnh'. Trung tâm <b>Mở</b> (trắng): nơi bạn hấp thụ "
                           "và học trí tuệ — không phải nơi để ra quyết định.", st["body"]))
    chead = [Paragraph("<b>Trung tâm</b>", st["cell_h"]),
             Paragraph("<b>Trạng thái</b>", st["cell_h"]),
             Paragraph("<b>Ý nghĩa với bạn</b>", st["cell_h"])]
    crows = [chead]
    for c in CENTER_ORDER:
        is_def = c in defined
        key = "defined" if is_def else "undefined"
        txt = CENTER_ANALYSIS.get(c, {}).get(key, "")
        blind = CENTER_BLINDSPOTS.get(c, {}).get(key, {})
        extra = ""
        if isinstance(blind, dict):
            extra = blind.get("blindspot", "") or blind.get("not-self", "") or ""
        cell_txt = txt + (f"<br/><i>Lưu ý: {extra}</i>" if extra else "")
        crows.append([
            Paragraph(f"<b>{c}</b><br/>{CENTER_VN.get(c, '')}", st["cell"]),
            Paragraph('<font color="#2E7D32"><b>ĐỊNH NGHĨA</b></font>' if is_def
                      else '<font color="#757575"><b>MỞ</b></font>', st["cell"]),
            Paragraph(cell_txt, st["cell"]),
        ])
    tc = Table(crows, colWidths=[34 * mm, 24 * mm, 104 * mm], repeatRows=1)
    tc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9F6FF")]),
        ("BOX", (0, 0), (-1, -1), 0.8, ACCENT),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CE93D8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(tc)

    # ================= KÊNH ĐỊNH NGHĨA =================
    story.append(Paragraph("3. Kênh định nghĩa — Tài năng cố định", st["h1"]))
    story.append(Paragraph("Kênh định nghĩa là nơi <b>cả 2 cổng ở 2 đầu đều kích hoạt</b> — tạo thành dòng "
                           "năng lượng ổn định, là tài năng bẩm sinh nhất quán của bạn.", st["body"]))
    for g1, g2 in sorted(chart["defined_channels"], key=lambda x: (min(x), max(x))):
        en, vn = _chan_name(g1, g2)
        desc = CHANNEL_DESC.get((g1, g2)) or CHANNEL_DESC.get((g2, g1))
        if not desc:
            desc = (f"{GATE_MEANINGS.get(g1, '')} + {GATE_MEANINGS.get(g2, '')}.")
        c1, c2 = GATE_TO_CENTER.get(g1, ""), GATE_TO_CENTER.get(g2, "")
        story.append(KeepTogether([
            Paragraph(f"<b>Kênh {g1}-{g2}</b> — {en} • {vn} &nbsp;({c1} ↔ {c2})", st["h2"]),
            Paragraph(f"Cổng {g1}: {GATE_MEANINGS.get(g1, '')} — Cổng {g2}: "
                      f"{GATE_MEANINGS.get(g2, '')}.", st["body"]),
            Paragraph(desc, st["body"]),
        ]))
    story.append(PageBreak())
    story.append(Paragraph("Bản đồ BodyGraph — Chế độ nổi bật kênh định nghĩa", st["h1"]))
    story.append(Paragraph("Cùng một bản đồ nhưng làm mờ các kênh mở, giúp bạn tập trung vào "
                           "luồng năng lượng cố định (tài năng bẩm sinh) của mình.", st["body"]))
    if cairosvg is not None:
        story.append(Image(focus_png, width=152 * mm, height=210.3 * mm))
    else:
        story.append(Paragraph(
            "Chế độ BodyGraph nổi bật không được nhúng vì thiếu thư viện native Cairo.",
            st["body"]))
    story.append(PageBreak())

    # ================= CỔNG KÍCH HOẠT =================
    story.append(Paragraph("4. Cổng kích hoạt — Personality & Design", st["h1"]))
    story.append(Paragraph("<b>Personality (Đen/Ý thức)</b>: những gì bạn biết về mình — tính cách, "
                           "tư duy. <b>Design (Đỏ/Vô thức)</b>: những gì người khác cảm nhận ở bạn — "
                           "cơ thể, bản năng.", st["body"]))

    def gate_table(title, gdict, color):
        story.append(Paragraph(title, st["h2"]))
        head = [Paragraph("<b>Hành tinh</b>", st["cell_h"]),
                Paragraph("<b>Cổng.Hào</b>", st["cell_h"]),
                Paragraph("<b>Ý nghĩa cổng</b>", st["cell_h"]),
                Paragraph("<b>Trung tâm</b>", st["cell_h"])]
        rows = [head]
        for p in PLANETS:
            d = gdict.get(p)
            if not d:
                continue
            g, ln = d["gate"], d["line"]
            rows.append([
                Paragraph(f"{p}<br/>{PLANET_VN.get(p, '')}", st["cell"]),
                Paragraph(f"<b>{g}.{ln}</b>", st["cell"]),
                Paragraph(str(GATE_MEANINGS.get(g, "")), st["cell"]),
                Paragraph(str(GATE_TO_CENTER.get(g, "")), st["cell"]),
            ])
        t = Table(rows, colWidths=[42 * mm, 22 * mm, 62 * mm, 36 * mm], repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), color),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
            ("BOX", (0, 0), (-1, -1), 0.8, color),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDBDBD")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)

    gate_table("Personality — 13 cổng ý thức (Đen)", chart["personality_gates"],
               colors.HexColor("#424242"))
    gate_table("Design — 13 cổng vô thức (Đỏ)", chart["design_gates"],
               colors.HexColor("#C62828"))

    # ================= TIỀM NĂNG & ĐIỂM MÙ =================
    story.append(Paragraph("5. Tiềm năng & Điểm mù — Đa góc nhìn", st["h1"]))
    pot = analyze_potential_blindspots(
        datetime.strptime(utc_str, "%d/%m/%Y %H:%M"), name=name)["potential_analysis"]
    story.append(Paragraph("<b>Điểm mạnh cố định</b>", st["h2"]))
    story.append(Paragraph(str(pot["strengths"].get("summary", "")), st["body"]))
    story.append(Paragraph("<b>Điểm mù & Trí tuệ từ trung tâm mở</b>", st["h2"]))
    story.append(Paragraph(str(pot["blindspots"].get("summary", "")), st["body"]))
    hg = pot["blindspots"].get("hanging_gates", [])
    if hg:
        if isinstance(hg[0], dict):
            hg_txt = "; ".join(str(x.get("gate", x)) for x in hg[:14])
        else:
            hg_txt = "; ".join(str(x) for x in hg[:14])
        story.append(Paragraph(f"<b>Cổng treo (tiềm năng chờ kết nối):</b> {hg_txt}", st["body"]))
    story.append(Paragraph("<b>11 góc nhìn về bản thân</b>", st["h2"]))
    story.append(Paragraph(str(pot["perspectives"].get("summary", "")), st["body"]))
    story.append(Paragraph("<b>Hành vi phù hợp để cải thiện</b>", st["h2"]))
    beh = pot.get("appropriate_behavior", {})
    strat = beh.get("strategy", {})
    if isinstance(strat, dict):
        story.append(Paragraph(f"<b>Strategy:</b> {strat.get('name', '')} — "
                               f"{strat.get('description', '')}<br/><i>Thực hành:</i> "
                               f"{strat.get('practice', '')}", st["body"]))
    else:
        story.append(Paragraph(f"<b>Strategy:</b> {strat}", st["body"]))
    story.append(Paragraph(f"<b>Authority:</b> {beh.get('authority', '')}", st["body"]))
    story.append(Paragraph(f"<b>Bẫy tâm trí:</b> {beh.get('not_self_mind', '')}", st["body"]))
    decond = beh.get("deconditioning", {})
    if isinstance(decond, dict):
        for k in ("7d", "7m", "7y"):
            if decond.get(k):
                story.append(Paragraph(f"<b>{k}:</b> {decond[k]}", st["bullet"], bulletText="•"))

    # ================= PHỤ LỤC A: TIỀM NĂNG & ĐIỂM MÙ ĐẦY ĐỦ =================
    story.append(PageBreak())
    story.append(Paragraph("Phụ lục A. Báo cáo Tiềm năng & Điểm mù — đầy đủ", st["h1"]))
    story.append(Paragraph("Phân tích chi tiết từng trung tâm, kênh, cổng treo, cổng sợ hãi, "
                           "11 góc nhìn đa chiều và lộ trình hành vi phù hợp.", st["body"]))
    _pot_full = analyze_potential_blindspots(datetime.strptime(utc_str, "%d/%m/%Y %H:%M"), name=name)
    _append_markdown(story, format_potential_report(_pot_full), st)

    # ================= TIỀN BẠC =================
    story.append(Paragraph("6. Bản đồ tiền bạc", st["h1"]))
    mon = analyze_money_map(datetime.strptime(utc_str, "%d/%m/%Y %H:%M"),
                            name=name)["money_analysis"]
    tms = mon.get("type_money_strategy", {})
    story.append(Paragraph("<b>Cách thu hút tiền theo Type</b>", st["h2"]))
    story.append(Paragraph(str(tms.get("money_aura", "")), st["body"]))
    how = tms.get("how_to_attract", "")
    if isinstance(how, list):
        for h in how:
            story.append(Paragraph(str(h), st["bullet"], bulletText="•"))
    elif how:
        story.append(Paragraph(str(how), st["body"]))
    story.append(Paragraph(f"<b>Định giá:</b> {tms.get('pricing', '')}", st["body"]))
    story.append(Paragraph(f"<b>Mô hình phù hợp:</b> {tms.get('business_model', '')}", st["body"]))
    story.append(Paragraph("<b>Trung tâm Tim & tiền bạc</b>", st["h2"]))
    story.append(Paragraph(str(mon.get("heart_center_money", {}).get("analysis", "")), st["body"]))
    mg = mon.get("money_gates", {})
    story.append(Paragraph(f"<b>Cổng tiền kích hoạt ({mg.get('count', 0)}):</b> "
                           f"{mg.get('summary', '')}", st["body"]))
    story.append(Paragraph(f"<b>Quyết định tiền theo Authority:</b> {mon.get('authority_money', '')}",
                           st["body"]))

    # ================= PHỤ LỤC B: BẢN ĐỒ TIỀN ĐẦY ĐỦ =================
    story.append(PageBreak())
    story.append(Paragraph("Phụ lục B. Bản đồ Tiền bạc — đầy đủ", st["h1"]))
    story.append(Paragraph("Chiến lược tiền theo Type, trung tâm Tim, phong cách tiền theo Profile, "
                           "kênh & cổng tiền, và cách ra quyết định tiền theo Authority.", st["body"]))
    _mon_full = analyze_money_map(datetime.strptime(utc_str, "%d/%m/%Y %H:%M"), name=name)
    _append_markdown(story, format_money_report(_mon_full), st)

    # ================= THỰC HÀNH =================
    story.append(Paragraph("7. Thực hành 7 ngày", st["h1"]))
    practices = [
        "Mỗi sáng: nhắc mình Strategy — <b>Chờ để Đáp Ứng, rồi Thông Báo</b>. Đừng khởi xướng từ đầu óc.",
        "Trước mỗi quyết định lớn: hỏi Sacral (uh-huh/uh-uh), rồi <b>chờ qua đêm</b> cho sóng cảm xúc lắng xuống.",
        "Quan sát 4 trung tâm mở (Head, Ajna, Heart, Spleen): đây là nơi học trí tuệ, không phải nơi ra quyết định.",
        "Để ý dấu hiệu Not-Self: <b>Thất vọng + Tức giận</b> = đang đi lệch thiết kế. Chữ ký đúng: <b>Thỏa mãn + Bình yên</b>.",
        "Ghi nhật ký mỗi tối: hôm nay mình đáp ứng hay khởi xướng? Quyết định từ Authority hay từ đầu óc?",
    ]
    for pr in practices:
        story.append(Paragraph(pr, st["bullet"], bulletText="✦"))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("“Hiểu mình — Sống là mình.”<br/>Chúc bạn hành trình thử nghiệm đầy thú vị!",
                           st["quote"]))

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=16 * mm,
                            title=f"Báo cáo Human Design - {name}",
                            author="Hệ thống Human Design v3.0")
    doc.build(story, onFirstPage=_cover_footer, onLaterPages=_cover_footer)
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Xuất báo cáo Human Design PDF")
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--tz", default="+07:00")
    ap.add_argument("--name", default="")
    ap.add_argument("--place", default="")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dt_naive = datetime.strptime(f"{args.date} {args.time}", "%Y-%m-%d %H:%M")
    sign = 1 if args.tz[0] == "+" else -1
    off = timedelta(hours=sign * int(args.tz[1:3]),
                    minutes=sign * int(args.tz[4:6]) if len(args.tz) > 3 else 0)
    dt_utc = (dt_naive.replace(tzinfo=timezone(off))).astimezone(timezone.utc).replace(tzinfo=None)

    chart = calculate_hd_chart(dt_utc)
    birth_local = f"{dt_naive.strftime('%d/%m/%Y %H:%M')} ({args.tz})"
    utc_s = dt_utc.strftime("%d/%m/%Y %H:%M")
    build_pdf(chart, args.name or "Human Design Chart", birth_local, utc_s,
              args.place, args.out)
    print(f"OK - {args.out}")


if __name__ == "__main__":
    main()
