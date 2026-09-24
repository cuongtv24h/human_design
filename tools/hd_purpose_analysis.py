#!/usr/bin/env python3
"""
Human Design Purpose Analysis - Mục đích & Sứ mệnh ứng dụng thực tế (v3.0)
Nhu cầu thực tế: tìm mục đích sống, sứ mệnh, xây cuộc đời đúng hướng.
Incarnation Cross (192) + Quarter + Angle + Sun/Earth + Profile + Type + kênh nghề nghiệp.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER
from hd_language import vn_authority, vn_strategy

QUARTERS = {
    "Initiation": {"vn": "Khởi xướng (Tâm trí)", "purpose": "Mục đích qua TÂM TRÍ - học hỏi, đặt câu hỏi, tìm hiểu, khởi đầu. Bạn ở đây để tâm trí dẫn đường cho hành trình."},
    "Civilization": {"vn": "Văn minh (Hình thức)", "purpose": "Mục đích qua HÌNH THỨC - xây dựng, tổ chức, vật chất hóa, tạo ra cái sờ được. Bạn ở đây để xây."},
    "Duality": {"vn": "Nhị nguyên (Gắn kết)", "purpose": "Mục đích qua GẮN KẾT - quan hệ, hợp tác, yêu thương, kết nối người với người. Bạn ở đây để gắn kết."},
    "Mutation": {"vn": "Đột biến (Biến đổi)", "purpose": "Mục đích qua BIẾN ĐỔI - thay đổi, tiến hóa, phá cũ lập mới. Bạn ở đây để biến đổi mình và đời."},
}

ANGLES = {
    "Right Angle": "GÓC PHẢI (cá nhân): hành trình TỰ TRẢI NGHIỆM - học qua đời mình, chiêm nghiệm, số phận cá nhân. ~64% dân số.",
    "Left Angle": "GÓC TRÁI (liên cá nhân): hành trình QUA NGƯỜI KHÁC - dạy, dẫn, chữa, kết nối. Sứ mệnh gắn với tha nhân. ~33% dân số.",
    "Juxtaposition": "ĐỐI ĐỈNH (cố định): hành trình CỐ ĐỊNH, đi đường hẹp - làm đúng một việc, không cần linh hoạt. Hiếm ~3%.",
}

TYPE_CONTRIBUTION = {
    "Generator": "Đóng góp: XÂY DỰNG bền bỉ - làm ra của cải vật chất/tinh thần cho đời qua công việc yêu thích.",
    "Manifesting Generator": "Đóng góp: XÂY NHANH + TỐI ƯU - tìm đường tắt, đa dòng, lan tỏa hiệu quả.",
    "Projector": "Đóng góp: DẪN DẮT + NHÌN THẤY - quản lý năng lượng người khác, cố vấn, tổ chức hệ thống.",
    "Manifestor": "Đóng góp: KHỞI XƯỚNG - mở đường, tạo phong trào, gây ảnh hưởng lớn.",
    "Reflector": "Đóng góp: PHẢN CHIẾU - gương soi sức khỏe cộng đồng, đánh giá, bảo vệ môi trường sống.",
}

PROFILE_ROLE_PURPOSE = {
    "1/3": "Nhà nghiên cứu + thực nghiệm - sứ mệnh qua nền tảng sâu và trải nghiệm thật.",
    "1/4": "Nền tảng + lan tỏa qua mạng lưới - sứ mệnh qua bạn bè và cộng đồng thân.",
    "2/4": "Tài năng thiên bẩm + mạng lưới - được gọi ra để tỏa sáng cho người quen.",
    "2/5": "Tài năng ẩn + giải pháp phổ quát - được gọi ra để cứu đám đông.",
    "3/5": "Thử sai + giải pháp thực tế - sứ mệnh qua va chạm và bài học xương máu.",
    "3/6": "Thử sai thành tấm gương - sứ mệnh chín dần, càng già càng sáng.",
    "4/1": "Mạng lưới + nền tảng cố định - sứ mệnh hiếm: giữ lửa cho cộng đồng định mệnh.",
    "4/6": "Bạn bè thành tấm gương - sứ mệnh qua quan hệ bền và trưởng thành.",
    "5/1": "Giải pháp phổ quát + nền tảng - sứ mệnh cứu người bằng hệ thống chắc.",
    "5/2": "Người hùng + ẩn sĩ - sứ mệnh khi được gọi, nghỉ khi xong việc.",
    "6/2": "Tấm gương + ẩn sĩ - sứ mệnh 3 giai đoạn, đỉnh cao sau 50 tuổi.",
    "6/3": "Tấm gương qua thử sai - sứ mệnh trưởng thành không ngừng nghỉ.",
}

VOCATION_CHANNELS = {
    (1, 8): "Nghệ thuật, sáng tạo, thiết kế, personal branding.",
    (2, 14): "Quản lý tài nguyên, tài chính, định hướng nguồn lực.",
    (3, 60): "Đổi mới, R&D, khởi nghiệp đột phá.",
    (4, 63): "Nghiên cứu, phân tích logic, kiểm chứng.",
    (5, 15): "Nhịp điệu, nông nghiệp, wellness, công việc theo chu kỳ.",
    (6, 59): "Tư vấn quan hệ, gia đình, thân mật, sức khỏe sinh sản.",
    (7, 31): "Lãnh đạo, quản lý, dẫn dắt tổ chức.",
    (9, 52): "Chuyên gia sâu, học thuật, kỹ thuật chi tiết.",
    (10, 20): "Coaching hiện diện, mindfulness, truyền cảm hứng sống thật.",
    (10, 34): "Nghề theo lẽ sống, personal mission-driven work.",
    (10, 57): "Y tế trực giác, chẩn đoán, nghề sinh tồn.",
    (11, 56): "Giáo dục, kể chuyện, truyền thông, du lịch trải nghiệm.",
    (12, 22): "Nghệ thuật biểu diễn, diễn thuyết truyền cảm.",
    (13, 33): "Lịch sử, chứng nhân, lưu trữ tri thức, mentor.",
    (16, 48): "Chuyên môn sâu, bậc thầy nghề, đào tạo kỹ năng.",
    (17, 62): "Quản trị hệ thống, tổ chức, logic vận hành.",
    (18, 58): "QA/QC, biên tập, hoàn thiện sản phẩm.",
    (19, 49): "Cộng đồng, chăm sóc, hoạt động xã hội, F&B nhu cầu.",
    (20, 34): "Kinh doanh tốc độ, sales hành động, startup execution.",
    (20, 57): "Trực giác tức thì: trading, cấp cứu, nghề quyết nhanh.",
    (21, 45): "Tài chính, deal lớn, quản lý tiền tập thể.",
    (23, 43): "Insight, tư vấn chiến lược, phát minh khái niệm.",
    (24, 61): "Triết học, tư duy sâu, nghiên cứu nội tâm.",
    (25, 51): "Khởi xướng mạo hiểm, shockseven, nghề thiêng liêng.",
    (26, 44): "Sales, marketing, đàm phán, truyền bá.",
    (27, 50): "Chăm sóc sức khỏe, dinh dưỡng, bảo tồn, mẹ/cha.",
    (28, 38): "Nghề có ý nghĩa sinh tử, vượt khó, truyền cảm hứng nghị lực.",
    (29, 46): "Cam kết dài hạn: xây dựng, thể thao bền, dự án lớn.",
    (30, 41): "Sáng tạo cảm xúc: phim, nhạc, văn - nghề khát vọng.",
    (32, 54): "Tham vọng leo thang: corporate ladder, scale business.",
    (35, 36): "Trải nghiệm: du lịch, ẩm thực, nghề nhiều biến động.",
    (37, 40): "Gia đình, nhà hàng, cộng đồng, deal công bằng.",
    (39, 55): "Cảm xúc dâng trào: nghệ thuật, chữa lành cảm xúc.",
    (42, 53): "Hoàn thành chu kỳ: quản lý dự án đến cùng.",
    (47, 64): "Trừu tượng hóa quá khứ: viết lách, tổng kết, review.",
}


def analyze_purpose(birth_datetime, name=""):
    # Accept a precomputed chart when called from the report pipeline.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t, p = chart["type"], chart["profile"]
    qs = chart.get("quarters", {})
    pq = qs.get("personality_sun_quarter", "") if isinstance(qs, dict) else ""
    qinfo = QUARTERS.get(pq, {"vn": pq, "purpose": ""})

    sun_work = {"gate": chart["p_sun_gate"], "meaning": GATE_MEANINGS.get(chart["p_sun_gate"], ""),
                "center": GATE_TO_CENTER.get(chart["p_sun_gate"], ""),
                "role": "Life's Work (70% sứ mệnh) - việc đời bạn sinh ra để làm."}
    earth_ground = {"gate": chart["p_earth_gate"], "meaning": GATE_MEANINGS.get(chart["p_earth_gate"], ""),
                    "center": GATE_TO_CENTER.get(chart["p_earth_gate"], ""),
                    "role": "Grounding - nền đất giữ bạn vững khi làm việc đời."}
    d_sun = {"gate": chart["d_sun_gate"], "meaning": GATE_MEANINGS.get(chart["d_sun_gate"], ""),
             "center": GATE_TO_CENTER.get(chart["d_sun_gate"], ""),
             "role": "Evolution (vô thức) - điều cơ thể bạn tiến hóa về."}
    d_earth = {"gate": chart["d_earth_gate"], "meaning": GATE_MEANINGS.get(chart["d_earth_gate"], ""),
               "center": GATE_TO_CENTER.get(chart["d_earth_gate"], ""),
               "role": "Vô thức grounding - nền tảng ẩn bạn đứng lên."}

    vocations = []
    for g1, g2 in chart["defined_channels"]:
        key = (g1, g2) if (g1, g2) in VOCATION_CHANNELS else (g2, g1)
        v = VOCATION_CHANNELS.get(key, "")
        if v:
            vocations.append({"channel": f"{g1}-{g2}", "vocations": v})

    steps = [
        f"Bước 1: Sống đúng chiến lược sống ({vn_strategy(chart['strategy'], chart['type'])}) + quyền nội tại ({vn_authority(chart['authority'])}) - sứ mệnh chỉ lộ khi đi đúng đường.",
        f"Bước 2: Đào sâu cổng {sun_work['gate']} ({sun_work['meaning']}) - 70% sứ mệnh nằm ở đây.",
        f"Bước 3: Sống vai trò Profile {p}: {PROFILE_ROLE_PURPOSE.get(p, '')}",
        f"Bước 4: Đóng góp theo {t}: {TYPE_CONTRIBUTION[t]}",
        "Bước 5: Kiên nhẫn - sứ mệnh là HÀNH TRÌNH sống mỗi ngày, không phải đích đến một lần.",
    ]
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": p, "authority": chart["authority"],
        "definition": chart["definition"],
        "incarnation_cross": chart["incarnation_cross"], "cross_type": chart["cross_type"],
        "purpose_analysis": {
            "cross": chart["incarnation_cross"],
            "angle": chart["cross_type"],
            "angle_meaning": ANGLES.get(chart["cross_type"], ""),
            "quarter": qinfo["vn"], "quarter_purpose": qinfo["purpose"],
            "sun_work": sun_work, "earth_ground": earth_ground,
            "design_sun": d_sun, "design_earth": d_earth,
            "profile_role": PROFILE_ROLE_PURPOSE.get(p, ""),
            "type_contribution": TYPE_CONTRIBUTION[t],
            "vocations": vocations,
            "practical_steps": steps,
            "summary": (f"{name or 'Bạn'} ({t} {p}): Sứ mệnh {chart['incarnation_cross']} - {ANGLES.get(chart['cross_type'], '')[:60]}... "
                        f"Việc đời (70%): cổng {sun_work['gate']} {sun_work['meaning']}. Vai trò: {PROFILE_ROLE_PURPOSE.get(p, '')}"),
        },
        "áp_dụng_cho": "100% dân số - 192 Crosses - 60 biến thể",
    }


def format_purpose_report(d):
    r = d["purpose_analysis"]
    L = [f"# BÁO CÁO SỨ MỆNH & MỤC ĐÍCH - {d['name']} - {d['type']} {d['profile']}",
         f"**Cross:** {r['cross']} | **Angle:** {r['angle']} | **Quarter:** {r['quarter']}",
         "", "## 1. INCARNATION CROSS - BỐI CẢNH SỨ MỆNH",
         f"**{r['cross']}**", f"**{r['angle']}:** {r['angle_meaning']}",
         f"**Quarter {r['quarter']}:** {r['quarter_purpose']}",
         "", "## 2. 4 TRỤ SỨ MỆNH (MẶT TRỜI/TRÁI ĐẤT)"]
    for k in ("sun_work", "earth_ground", "design_sun", "design_earth"):
        x = r[k]
        L.append(f"- **Cổng {x['gate']}** ({x['center']}): {x['meaning']} - *{x['role']}*")
    L += ["", "## 3. VAI TRÒ & ĐÓNG GÓP",
          f"**Profile {d['profile']}:** {r['profile_role']}",
          f"**Type {d['type']}:** {r['type_contribution']}",
          "", "## 4. HƯỚNG NGHỀ TỪ KÊNH ĐỊNH NGHĨA"]
    for v in r["vocations"]:
        L.append(f"- **Kênh {v['channel']}:** {v['vocations']}")
    if not r["vocations"]:
        L.append("- Không có kênh định nghĩa (Reflector) - nghề nghiệp linh hoạt theo môi trường và chu kỳ.")
    L += ["", "## 5. 5 BƯỚC SỐNG ĐÚNG SỨ MỆNH"]
    L += [f"{i}. {s}" for i, s in enumerate(r["practical_steps"], 1)]
    L += ["", "## 6. KẾT LUẬN", r["summary"], "",
          "> \"Sứ mệnh không phải tìm - mà là sống ra mỗi ngày\"",
          "> \"Strategy + Authority trước, sứ mệnh tự lộ sau\""]
    return "\n".join(L)
