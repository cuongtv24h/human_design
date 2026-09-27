#!/usr/bin/env python3
"""
Human Design Career Analysis - Sự nghiệp & mô hình kinh doanh theo thiết kế (v1.0)
Nhu cầu thực tế: chọn mô hình làm việc/kinh doanh đúng Type, đường sự nghiệp
đúng Profile, kênh nghề nghiệp nổi bật, Money Lines (mạch tiền Ego) và quyết
định kinh doanh đúng Authority. Tham chiếu hệ BG5 (Base Group) của Ra Uru Hu.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart
from hd_language import vn_type

# BG5: 5 Loại sự nghiệp tương ứng 5 Type.
BG5_TYPE = {
    "Generator": {
        "bg5": "Classic Builder (Người Xây Dựng Cổ Điển)", "share": "37%",
        "model": "Chuyên môn sâu + làm việc yêu thích + giá trị bền vững. Làm thuê chuyên sâu, freelancer đặt lịch kín, hoặc chủ nhỏ làm nghề yêu.",
        "leadership": "Lãnh đạo bằng năng lượng bền bỉ và tay nghề - nhân viên nể vì sếp làm giỏi và làm gương.",
        "team_role": "Xương sống thực thi (70% cùng MG) - vận hành, sản xuất, chuyên môn.",
        "business_tip": "Đừng nhận mọi việc - chỉ nhận việc Sacral uh-huh. Định giá theo giá trị đầu ra, không bán giờ rẻ.",
    },
    "Manifesting Generator": {
        "bg5": "Express Builder (Người Xây Dựng Tốc Hành)", "share": "33%",
        "model": "Đa dòng tiền + đa dự án + tối ưu đường tắt. Hợp startup, growth, portfolio career, kinh doanh nhiều nhánh.",
        "leadership": "Lãnh đạo đa năng - dẫn nhiều mặt trận cùng lúc, tìm lối tắt cho cả team.",
        "team_role": "Triển khai nhanh + tối ưu (70% cùng Generator) - growth, đa dự án, cải tiến quy trình.",
        "business_tip": "Cho phép mình bẻ lái - portfolio nhiều nhánh thắng một con đường duy nhất. Nhớ thông báo khi đổi hướng.",
    },
    "Projector": {
        "bg5": "Advisor (Cố Vấn)", "share": "20%",
        "model": "Consulting / coaching / advisory / quản lý / chuyên gia được mời. Giá cao theo GIÁ TRỊ NHÌN THẤY, không bán 8 tiếng/ngày.",
        "leadership": "Bậc thầy quản lý năng lượng - đặt đúng người đúng việc, nhìn thấy điều team không thấy.",
        "team_role": "Người dẫn dắt (20%) - quản lý, HR, điều phối, chiến lược.",
        "business_tip": "Xây uy tín để được MỜI - content, case study, quan hệ. Từ chối việc không được công nhận.",
    },
    "Manifestor": {
        "bg5": "Initiator (Người Khởi Xướng)", "share": "9%",
        "model": "Founder / high-ticket / sản phẩm đột phá / tự chủ cao. Mở đường, tạo ảnh hưởng, khởi động cái mới.",
        "leadership": "Lãnh đạo khởi xướng - tạo tầm nhìn và động lực, không hợp quản lý chi tiết hàng ngày.",
        "team_role": "Người mở đường (9%) - founder, BD, đối ngoại, khởi động dự án.",
        "business_tip": "Inform trước hành động lớn để giảm kháng cự. Thuê Generator/Projector lo vận hành thay vì tự ôm.",
    },
    "Reflector": {
        "bg5": "Evaluator (Người Đánh Giá)", "share": "1%",
        "model": "Community / đánh giá / trung gian / cố vấn môi trường / vai trò linh hoạt. Thu nhập từ góc nhìn độc nhất về sức khỏe hệ thống.",
        "leadership": "Lãnh đạo phản chiếu - soi sức khỏe tổ chức, cảnh báo sớm vấn đề văn hóa.",
        "team_role": "Gương soi tổ chức (1%) - QA văn hóa, cố vấn độc lập, cộng đồng.",
        "business_tip": "Chọn môi trường/tổ chức lành mạnh - thu nhập của bạn gắn với nơi bạn đứng. Đừng ký deal khi bị hối thúc.",
    },
}

PROFILE_CAREER = {
    "1/3": "Nghiên cứu + thực nghiệm: chuyên gia kỹ thuật, R&D, kiểm định. Cần nền tảng vững rồi mới bung.",
    "1/4": "Chuyên gia của cộng đồng: đào tạo, cố vấn cho khách hàng thân thiết. Mạng lưới ấm là kênh bán hàng.",
    "2/4": "Tài năng được gọi ra qua quan hệ: nghệ nhân, chuyên gia thầm lặng, nghề từ lời giới thiệu.",
    "2/5": "Chuyên gia cứu nguy kín đáo: freelance cao cấp, cố vấn theo vụ, cần ranh giới rõ.",
    "3/5": "Thử sai để cứu người: cứu nguy dự án, turnaround, review sản phẩm, nghề cần kinh nghiệm xương máu.",
    "3/6": "Trưởng thành dần thành tấm gương: càng lâu năm càng có giá - hợp nghề tích lũy uy tín.",
    "4/1": "Một con đường duy nhất cho người thân: nghề cố định phục vụ cộng đồng trung thành, đừng nhảy lung tung.",
    "4/6": "Quan hệ bền thành thương hiệu: chăm sóc khách hàng dài hạn, cộng đồng, đối ngoại.",
    "5/1": "Giải pháp thực tế cho số đông: lãnh đạo sản phẩm, cố vấn chiến lược. Coi chừng quá tải kỳ vọng.",
    "5/2": "Người hùng kín đáo: xuất hiện khi cần, rút khi xong - hợp vai trò chuyên gia độc lập, cố vấn cấp cao.",
    "6/2": "Tấm gương sau giai đoạn ủ: mentor, người truyền cảm hứng - đỉnh cao giá trị sau 50.",
    "6/3": "Trưởng thành liên tục cùng nghề: nghề cho phép vừa làm vừa học cả đời.",
}

# Kênh nghề nghiệp nổi bật: (g1, g2) -> ý nghĩa sự nghiệp.
CAREER_CHANNELS = {
    (21, 45): "MONEY LINE - Dòng tiền & quản trị vật chất: đàm phán deal, quản lý tài nguyên, vị trí kiểm soát dòng tiền.",
    (26, 44): "MONEY LINE - Truyền bá & nhận diện: sales, marketing, truyền thông - biến ý tưởng thành doanh số.",
    (2, 14): "Giữ chìa khóa nguồn lực: quản lý tài sản, phân bổ nguồn lực đúng chỗ - 'thủ kho' của tổ chức.",
    (1, 8): "Cảm hứng & hình mẫu: sáng tạo định hướng, KOL chuyên môn, vai trò truyền cảm hứng.",
    (7, 31): "Alpha lãnh đạo: dẫn dắt tập thể bằng tầm nhìn - quản lý, thủ lĩnh cộng đồng.",
    (10, 20): "Thức tỉnh & sống đúng mình: nghề cần sự chân thật hiện diện - coach, healer, người dẫn đường.",
    (13, 33): "Lắng nghe & chứng nhân: HR, tư vấn, nghiên cứu người dùng - nghề nghe để hiểu.",
    (43, 23): "Insight đột phá: chiến lược, R&D, cố vấn - biến hiểu biết thành lời giải thích rõ ràng.",
    (11, 56): "Tò mò & kể chuyện: content, đào tạo, truyền thông - nghề kể và dạy.",
    (35, 36): "Trải nghiệm & khủng hoảng: nghề nhiều biến động - khởi nghiệp, cứu nguy, du lịch trải nghiệm.",
    (16, 48): "Bậc thầy kỹ năng: chuyên gia sâu một nghề - kỹ thuật, thủ công, học thuật.",
    (9, 52): "Tập trung & tĩnh lặng: nghề cần đào sâu - nghiên cứu, phân tích, lập trình.",
    (34, 10): "Khám phá & hành động: MG - triển khai nhanh, kinh doanh đa nhánh.",
    (5, 15): "Nhịp điệu & cực đoan: nghề theo nhịp - nông nghiệp nhịp mùa, wellness, nghệ thuật biểu diễn.",
    (27, 50): "Chăm sóc & bảo tồn: y tế, giáo dục mầm non, chăm sóc khách hàng, bảo vệ giá trị.",
    (19, 49): "Nhạy cảm nhu cầu & nguyên tắc: nghề phục vụ cộng đồng, đàm phán nguyên tắc, nhân sự.",
    (37, 40): "Cộng đồng & ý chí: xây cộng đồng, hội nhóm, kinh doanh dựa trên giao ước rõ ràng.",
    (30, 41): "Khát vọng & khởi đầu cảm xúc: sáng tạo nội dung cảm xúc, marketing khơi gợi, nghệ thuật.",
    (25, 51): "Khởi phát & cạnh tranh: Manifestor - mở đường, BD, thể thao đỉnh cao, sales săn deal.",
    (20, 34): "Hành động ngay (Charisma bận rộn): MG - triển khai thần tốc, đa nhiệm cường độ cao.",
}

# Cổng liên quan tiền/nghề trong mạch Ego và lân cận.
MONEY_GATES = {
    14: "Cổng 14 Nguồn lực: biết biến kỹ năng thành thịnh vượng - chìa khóa monetize tài năng.",
    21: "Cổng 21 Kiểm soát: quản trị vật chất - hợp vị trí cầm dòng tiền, đàm phán.",
    26: "Cổng 26 Buông bỏ (Ego): bán hàng/truyền bá - biến giá trị thành doanh số.",
    44: "Cổng 44 Nhận diện: ngửi thấy cơ hội và nhân tài - hợp tuyển dụng, đầu tư, môi giới.",
    45: "Cổng 45 Tập hợp: phân phối nguồn lực cộng đồng - hợp lãnh đạo tổ chức, quản lý quỹ.",
}


def _scan_channels(defined_channels):
    found = []
    for ch in defined_channels:
        if not isinstance(ch, (list, tuple)) or len(ch) < 2:
            continue
        g1, g2 = ch[0], ch[1]
        if (g1, g2) in CAREER_CHANNELS:
            found.append({"channel": f"{g1}-{g2}", "meaning": CAREER_CHANNELS[(g1, g2)]})
        elif (g2, g1) in CAREER_CHANNELS:
            found.append({"channel": f"{g2}-{g1}", "meaning": CAREER_CHANNELS[(g2, g1)]})
    return found


def analyze_career(birth_datetime, name=""):
    # Accept a precomputed chart when called from the report pipeline.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t, p = chart["type"], chart["profile"]
    bg5 = BG5_TYPE[t]
    career_channels = _scan_channels(chart.get("defined_channels", []))
    gates = set(chart.get("all_activated_gates", []))
    money_gates = [{"gate": g, "meaning": m} for g, m in MONEY_GATES.items() if g in gates]
    money_lines = [c for c in career_channels if c["meaning"].startswith("MONEY LINE")]
    cross = chart.get("incarnation_cross", "")
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": p, "authority": chart.get("authority", ""),
        "definition": chart.get("definition", ""),
        "defined_centers": sorted(set(chart.get("defined_centers", []))),
        "career_analysis": {
            "bg5": bg5,
            "profile_career": PROFILE_CAREER.get(p, ""),
            "career_channels": career_channels,
            "money_lines": money_lines,
            "money_gates": money_gates,
            "cross_career": (f"Thập giá {cross}: không phải 'nghề cụ thể phải làm', mà là trạng thái năng lượng "
                              "tự động mở ra đúng cơ hội nghề nghiệp khi bạn sống đúng Chiến lược & Thẩm quyền."),
            "decision_tip": (f"Quyết định kinh doanh theo Thẩm quyền {chart.get('authority', '')} - "
                              "đặc biệt với deal lớn: không để trí (mind) ép chốt khi cơ thể chưa rõ."),
            "summary": (f"{name or 'Bạn'} ({t} {p}) - BG5 {bg5['bg5']}: {bg5['model']}"),
        },
        "áp_dụng_cho": "100% dân số - Hướng nghiệp, mô hình kinh doanh, vai trò trong tổ chức",
    }


def format_career_report(d):
    r = d["career_analysis"]
    b = r["bg5"]
    L = [f"# BÁO CÁO SỰ NGHIỆP & KINH DOANH - {d['name']} - {d['type']} {d['profile']}",
         f"**Loại năng lượng:** {vn_type(d['type'], gloss=True)} ({b['share']}) | **BG5:** {b['bg5']}",
         "", "## 1. MÔ HÌNH LÀM VIỆC/KINH DOANH THEO TYPE",
         f"**{b['bg5']}**", f"**Mô hình phù hợp:** {b['model']}",
         f"**Phong cách lãnh đạo:** {b['leadership']}", f"**Vai trò trong tổ chức:** {b['team_role']}",
         f"**Mẹo kinh doanh:** {b['business_tip']}",
         "", f"## 2. ĐƯỜNG SỰ NGHIỆP THEO PROFILE {d['profile']}",
         r["profile_career"],
         "", "## 3. KÊNH NGHỀ NGHIỆP NỔI BẬT"]
    if r["career_channels"]:
        for c in r["career_channels"]:
            L.append(f"- **Kênh {c['channel']}:** {c['meaning']}")
    else:
        L.append("- Không có kênh nghề nghiệp đặc trưng - sức mạnh của bạn nằm ở Type/Profile và các kênh khác trong đồ thị.")
    L += ["", "## 4. MONEY LINES - MẠCH TIỀN CỦA BẠN"]
    if r["money_lines"]:
        for c in r["money_lines"]:
            L.append(f"- **Kênh {c['channel']}:** {c['meaning']}")
    else:
        L.append("- Không có Money Line trực tiếp - dòng tiền của bạn chảy qua chuyên môn và mô hình đúng Type (xem mục 1).")
    if r["money_gates"]:
        for g in r["money_gates"]:
            L.append(f"- **{g['meaning']}")
    L += ["", "## 5. SỨ MỆNH ỨNG DỤNG VÀO NGHỀ", r["cross_career"],
          "", "## 6. QUYẾT ĐỊNH KINH DOANH ĐÚNG", r["decision_tip"],
          "", "## 7. KẾT LUẬN", r["summary"], "",
          "> \"BG5 không hỏi Bạn là ai - mà hỏi Bạn nên làm việc thế nào\"",
          "> \"Đừng hỏi nghề nào hot - hỏi mô hình nào đúng thiết kế của mình\""]
    return "\n".join(L)
