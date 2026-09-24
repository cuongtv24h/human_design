#!/usr/bin/env python3
"""
Human Design Team Analysis - Xây hệ thống đúng người đúng việc (v3.0)
Nhu cầu thực tế: xây hệ thống đúng mắt xích, đúng chức năng.
Vai trò Type trong team + phong cách lãnh đạo + bản đồ ghế ngồi + tuyển dụng + quản lý.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart, GATE_TO_CENTER
from hd_language import vn_type

TYPE_TEAM_ROLE = {
    "Generator": {"share": "37%", "role": "LỰC LƯỢNG XÂY DỰNG (Workforce)",
        "strength": "Làm bền bỉ, chất lượng ổn định khi làm việc yêu thích - xương sống mọi tổ chức.",
        "manage": "Đừng giao việc rồi ép deadline khô - hãy HỎI để Sacral đáp ứng. Giao việc đúng sở trường thì không cần giám sát.",
        "seat": "Vận hành, sản xuất, thực thi, chuyên môn sâu."},
    "Manifesting Generator": {"share": "33%", "role": "XÂY NHANH + TỐI ƯU (Fast Builder)",
        "strength": "Đa nhiệm, tìm đường tắt, triển khai nhanh - hợp startup, dự án gấp.",
        "manage": "Cho tự do đổi cách làm, chỉ chốt kết quả. Yêu cầu THÔNG BÁO khi đổi hướng để team không loạn.",
        "seat": "Triển khai, growth, đa dự án, tối ưu quy trình."},
    "Projector": {"share": "20%", "role": "NGƯỜI DẪN DẮT (Guide/Manager)",
        "strength": "Nhìn thấy năng lực người khác, phân việc đúng người, quản lý hệ thống.",
        "manage": "Đừng bắt làm 8 tiếng như Generator - trả lương theo GIÁ TRỊ NHÌN THẤY, không theo giờ. Mời vào vai trò, công nhận công khai.",
        "seat": "Quản lý, cố vấn, HR, điều phối, chiến lược."},
    "Manifestor": {"share": "9%", "role": "NGƯỜI KHỞI XƯỚNG (Initiator)",
        "strength": "Mở đường, tạo ảnh hưởng, khởi động cái mới - founder, rainmaker.",
        "manage": "Đừng kiểm soát chi tiết - giao MỤC TIÊU, để tự do cách làm. Yêu cầu INFORM team trước hành động lớn.",
        "seat": "Founder, BD, đối ngoại, khởi động dự án mới."},
    "Reflector": {"share": "1%", "role": "NGƯỜI ĐÁNH GIÁ (Evaluator)",
        "strength": "Gương soi sức khỏe tổ chức - cảm nhận môi trường, phát hiện sớm vấn đề văn hóa.",
        "manage": "Đừng ép quyết nhanh - cho thời gian chu kỳ. Đặt ở vị trí quan sát, đánh giá, văn hóa.",
        "seat": "QA văn hóa, cố vấn độc lập, đánh giá, cộng đồng."},
}

PROFILE_LEADERSHIP = {
    "1/3": "Lãnh đạo bằng chuyên môn sâu + thực nghiệm - nhân viên tin vì sếp giỏi nghề.",
    "1/4": "Lãnh đạo qua nền tảng + quan hệ thân - xây team như gia đình.",
    "2/4": "Lãnh đạo kín đáo - tỏa sáng khi được mời, dẫn qua mạng lưới tin cậy.",
    "2/5": "Lãnh đạo tài năng ẩn - được gọi ra cứu nguy, cần không gian riêng.",
    "3/5": "Lãnh đạo qua trải nghiệm - nhân viên nể vì sếp đã 'đổ máu' thật.",
    "3/6": "Lãnh đạo trưởng thành dần - càng lâu càng thành tấm gương.",
    "4/1": "Lãnh đạo mạng lưới cố định - giữ người bằng trung thành và nền tảng.",
    "4/6": "Lãnh đạo quan hệ bền - team gắn bó lâu dài.",
    "5/1": "Lãnh đạo giải pháp - nhân viên kỳ vọng sếp giải quyết mọi thứ, cần ranh giới.",
    "5/2": "Lãnh đạo người hùng kín đáo - xuất hiện khi cần, rút lui khi xong.",
    "6/2": "Lãnh đạo tấm gương - dẫn bằng cách sống, đỉnh cao sau 50.",
    "6/3": "Lãnh đạo trưởng thành liên tục - team cùng lớn với sếp.",
}

SEAT_MAP = [
    {"seat": "Tài chính / Deal lớn", "look_for": "Kênh 21-45 (Dòng tiền), Heart định nghĩa, cổng 14 (nguồn lực), cổng 44 (nhận diện)."},
    {"seat": "Sales / Marketing", "look_for": "Kênh 26-44 (Buông bỏ/truyền bá), Throat định nghĩa, cổng 35 (trải nghiệm), MG/Generator năng lượng cao."},
    {"seat": "Vận hành / Thực thi", "look_for": "Sacral định nghĩa (Generator/MG), kênh 9-52 (tập trung), kênh 42-53 (hoàn thành)."},
    {"seat": "Quản lý / Điều phối", "look_for": "Projector + G định nghĩa + kênh 7-31 (Alpha) hoặc 13-33 (lắng nghe)."},
    {"seat": "Chiến lược / Cố vấn", "look_for": "Projector/Manifestor + Ajna liên quan (11-56 tò mò, 43-23 insight, 17-62 logic)."},
    {"seat": "Chăm sóc khách hàng / Cộng đồng", "look_for": "Kênh 19-49 (nhạy cảm nhu cầu), 37-40 (cộng đồng), 27-50 (chăm sóc)."},
    {"seat": "Sáng tạo / Nội dung", "look_for": "Kênh 1-8 (cảm hứng), 11-56 (kể chuyện), 35-36 (trải nghiệm), 30-41 (khát vọng)."},
    {"seat": "Kỹ thuật / Chuyên môn sâu", "look_for": "Kênh 16-48 (bậc thầy), 9-52 (tập trung), 48-16 chiều sâu tài năng."},
    {"seat": "Nhân sự / Văn hóa", "look_for": "Reflector/Projector + Solar mở (gương cảm xúc) + kênh 13-33 (lắng nghe chứng nhân)."},
    {"seat": "Khởi động dự án mới", "look_for": "Manifestor + kênh 25-51 (khởi phát) hoặc MG 20-34 (hành động nhanh)."},
]

MANAGE_BY_TYPE = {
    "Generator": "Hỏi để đáp ứng - đừng ra lệnh khô. Khen khi làm tốt, đổi việc khi Frustration.",
    "Manifesting Generator": "Chốt kết quả, thả cách làm. Bắt buộc thông báo khi đổi hướng.",
    "Projector": "Mời + công nhận công khai. Trả theo giá trị, không theo giờ. Cho nghỉ đủ.",
    "Manifestor": "Giao mục tiêu, đừng soi cách làm. Yêu cầu inform trước việc lớn.",
    "Reflector": "Cho thời gian + môi trường tốt. Đừng ép quyết nhanh. Lắng nghe cảm nhận của họ về team.",
}


def analyze_team(birth_datetime, name=""):
    # Accept a precomputed chart when called from the report pipeline.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t, p = chart["type"], chart["profile"]
    role = TYPE_TEAM_ROLE[t]
    defined = set(chart["defined_centers"])

    env = []
    env.append("Cần được HỎI và đáp ứng - môi trường ra lệnh khô làm bạn kiệt sức." if t in ("Generator", "Manifesting Generator")
               else "Cần CÔNG NHẬN + LỜI MỜI - môi trường phớt lờ làm bạn đắng cay." if t == "Projector"
               else "Cần TỰ DO + được INFORM ngược - môi trường kiểm soát giết chết bạn." if t == "Manifestor"
               else "Cần MÔI TRƯỜNG LÀNH MẠNH + thời gian - môi trường độc hại làm bạn bệnh.")
    if "Throat" in defined:
        env.append("Throat định nghĩa: bạn cần vai trò được NÓI/đại diện - đừng nhốt sau hậu trường mãi.")
    if "Heart" not in defined:
        env.append("Heart mở: đừng nhận lương/kpi kiểu 'chứng minh giá trị' - đàm phán theo giá trị thực.")
    if "Solar Plexus" in defined:
        env.append("Solar định nghĩa: cần môi trường tôn trọng nhịp cảm xúc - tránh nơi ép quyết ngay.")

    collab = [f"Với {k}: {v}" for k, v in MANAGE_BY_TYPE.items() if k != t]
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": p, "authority": chart["authority"],
        "definition": chart["definition"],
        "defined_centers": sorted(defined),
        "team_analysis": {
            "your_role": role, "leadership_style": PROFILE_LEADERSHIP.get(p, ""),
            "ideal_environment": env, "seat_map": SEAT_MAP,
            "manage_others": [{"type": k, "tip": v} for k, v in MANAGE_BY_TYPE.items()],
            "collaboration": collab,
            "summary": (f"{name or 'Bạn'} ({t} {p}): vai trò team = {role['role']} ({role['share']} dân số). "
                        f"Ghế hợp: {role['seat']} Lãnh đạo kiểu: {PROFILE_LEADERSHIP.get(p, '')}"),
        },
        "áp_dụng_cho": "100% dân số - Tuyển dụng, quản lý, xây hệ thống",
    }


def format_team_report(d):
    r = d["team_analysis"]
    role = r["your_role"]
    L = [f"# BÁO CÁO TEAM & HỆ THỐNG - {d['name']} - {d['type']} {d['profile']}",
         f"**Loại năng lượng:** {vn_type(d['type'], gloss=True)} ({role['share']}) | **Vai trò:** {role['role']}",
         "", "## 1. VAI TRÒ CỦA BẠN TRONG HỆ THỐNG",
         f"**{role['role']}**", f"**Điểm mạnh:** {role['strength']}",
         f"**Cách quản lý bạn hiệu quả:** {role['manage']}", f"**Ghế ngồi hợp:** {role['seat']}",
         "", "## 2. PHONG CÁCH LÃNH ĐẠO",
         f"**Profile {d['profile']}:** {r['leadership_style']}",
         "", "## 3. MÔI TRƯỜNG LÀM VIỆC LÝ TƯỞNG"]
    L += [f"- {e}" for e in r["ideal_environment"]]
    L += ["", "## 4. BẢN ĐỒ GHẾ NGỒI - TUYỂN ĐÚNG NGƯỜI ĐÚNG VIỆC"]
    for s in r["seat_map"]:
        L.append(f"- **{s['seat']}:** tìm {s['look_for']}")
    L += ["", "## 5. QUẢN LÝ TỪNG TYPE"]
    for m in r["manage_others"]:
        L.append(f"- **{m['type']}:** {m['tip']}")
    L += ["", "## 6. KẾT LUẬN", r["summary"], "",
          "> \"Đúng người đúng việc - sai ghế, thiên tài cũng thành gánh nặng\"",
          "> \"70% Generator/MG xây - 20% Projector dẫn - 9% Manifestor mở đường - 1% Reflector soi\""]
    return "\n".join(L)
