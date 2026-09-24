#!/usr/bin/env python3
"""
Human Design Relationship Analysis - Mối quan hệ & Thân mật chuyên sâu (v3.0)
Nhu cầu thực tế: cải thiện mối quan hệ (tình yêu, gia đình, bạn bè, đối tác).
Hỗ trợ: phân tích đơn (bạn mang gì vào mối quan hệ) + composite 2 người (điện từ, compromise, dominance).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER, CHANNELS

LOVE_GATES = {
    6: "Ma sát & Thân mật - ranh giới thân mật, cần đúng người mới mở.",
    59: "Tính dục & Cởi mở - năng lượng tình dục mạnh, phá vỡ rào cản thân mật.",
    27: "Chăm sóc & Nuôi dưỡng - cho đi sự quan tâm, cần được đáp lại.",
    10: "Yêu bản thân - yêu mình trước mới yêu người đúng cách.",
    15: "Cực đoan & Nhân văn - yêu con người qua mọi trạng thái, ghét khuôn mẫu.",
    46: "Yêu cơ thể - hiện diện trong cơ thể khi yêu, tình yêu thể xác thiêng liêng.",
    25: "Ngây thơ & Yêu phổ quát - yêu vô điều kiện, dễ tổn thương nếu đặt sai chỗ.",
    44: "Nhận diện mẫu hình - ngửi thấy pattern quan hệ từ quá khứ, cảnh giác bản năng.",
    40: "Cô đơn & Nghỉ ngơi - cần không gian riêng trong mối quan hệ, không phải hết yêu.",
    37: "Gia đình & Tình bạn - gắn kết qua chạm, ăn cùng, thuộc về một nhóm.",
    19: "Muốn & Nhạy cảm nhu cầu - cảm nhận điều người yêu cần trước khi họ nói.",
    49: "Nguyên tắc & Từ chối - có nguyên tắc trong yêu, sẵn sàng cắt khi vi phạm.",
    30: "Khao khát & Cảm xúc - đam mê mãnh liệt, cần đúng người đúng sóng.",
    41: "Mộng tưởng - tưởng tượng về tình yêu, cần thực tế hóa kỳ vọng.",
    55: "Tinh thần & Sóng - yêu qua cảm xúc dâng trào, lúc đầy lúc vơi.",
    39: "Khiêu khích - thử thách người yêu để khơi cảm xúc thật.",
    12: "Thận trọng - yêu qua lời nói đúng lúc, im lặng cũng là yêu.",
    22: "Cởi mở & Quyến rũ - thu hút bằng cảm xúc, cần tâm trạng đúng.",
    35: "Trải nghiệm & Thay đổi - yêu qua trải nghiệm mới, sợ nhàm chán.",
    36: "Khủng hoảng & Trải nghiệm - tình yêu qua sóng gió mới sâu.",
    5: "Nhịp điệu - cần nhịp chung (giờ giấc, thói quen) mới bền.",
    14: "Nguồn lực - mang tài nguyên vào quan hệ, hào phóng khi đúng người.",
    29: "Cam kết - nói CÓ là đi đến cùng, đừng hứa bừa.",
    9: "Tập trung - yêu sâu một người hơn yêu nhiều người hời hợt.",
    8: "Đóng góp - muốn người yêu tự hào về mình.",
    1: "Tự thể hiện - cần được yêu đúng con người thật, không phải vai diễn.",
}

AURA_DYNAMICS = {
    "Generator": "Aura BAO BỌC, hút người khác vào. Trong quan hệ: cần được hỏi/đáp ứng, đừng ép quyết định. Hợp khi đối phương tôn trọng tiếng uh-huh/uh-uh.",
    "Manifesting Generator": "Aura bao bọc nhưng NHANH - đối phương đôi khi không theo kịp. Cần thông báo hướng đi trong quan hệ để tránh kháng cự.",
    "Projector": "Aura XUYÊN THẤU, tập trung vào người khác - đối phương cảm thấy 'bị nhìn thấu'. Cần được CÔNG NHẬN và MỜI vào đời nhau, đừng tự xông vào.",
    "Manifestor": "Aura KHÉP, đẩy nhẹ - đối phương có thể thấy xa cách. Cần INFORM (thông báo) trong quan hệ: đi đâu, làm gì, cảm thấy sao - để người kia không lo.",
    "Reflector": "Aura LẤY MẪU - phản chiếu đối phương. Cần môi trường quan hệ lành mạnh và thời gian (chu kỳ mặt trăng) cho cam kết lớn.",
}

PROFILE_LOVE = {
    "1/3": "Tìm hiểu kỹ rồi thử sai trong yêu - cần đối phương kiên nhẫn với quá trình thử nghiệm.",
    "1/4": "Nền tảng vững + mạng lưới bạn bè ảnh hưởng lớn đến tình yêu.",
    "2/4": "Kín đáo, được 'gọi ra' trong tình yêu - cần đối phương chủ động nhưng tôn trọng không gian.",
    "2/5": "Tài năng ẩn + kỳ vọng cứu người - đối phương kỳ vọng cao, cần ranh giới.",
    "3/5": "Thử sai trong yêu đương, va chạm lớn - mỗi mối tình là bài học cứu người sau.",
    "3/6": "Thử sai rồi trưởng thành thành tấm gương - tình yêu ổn định dần theo tuổi.",
    "4/1": "Hiếm - tình yêu qua mạng lưới cố định, trung thành tuyệt đối khi đã chọn.",
    "4/6": "Bạn bè thành người yêu - quan hệ bền qua giai đoạn tấm gương.",
    "5/1": "Bị kỳ vọng là giải pháp - đối phương chiếu hình mẫu lên bạn, cần làm rõ con người thật.",
    "5/2": "Kỳ vọng + kín đáo - cần không gian riêng song song với vai trò người hùng.",
    "6/2": "3 giai đoạn: thử sai (trước 30) - quan sát (30-50) - tấm gương (sau 50). Tình yêu chín muộn.",
    "6/3": "Tấm gương qua thử sai liên tục - mối quan hệ là hành trình trưởng thành không ngừng.",
}


def _gate_sets(chart):
    p = {d["gate"] for d in chart["personality_gates"].values()}
    dth = {d["gate"] for d in chart["design_gates"].values()}
    return p | dth


def _hanging(chart):
    allg = _gate_sets(chart)
    in_ch = set()
    for g1, g2 in chart["defined_channels"]:
        in_ch.add(g1)
        in_ch.add(g2)
    return sorted(allg - in_ch)


def analyze_relationship(birth_datetime, name="", partner_datetime=None, partner_name=""):
    # The primary chart may be supplied by the report orchestrator.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t, p = chart["type"], chart["profile"]
    allg = _gate_sets(chart)
    hanging = _hanging(chart)

    love_active = [{"gate": g, "center": GATE_TO_CENTER.get(g, ""), "love": LOVE_GATES[g]}
                   for g in sorted(allg) if g in LOVE_GATES]
    seek = [{"gate": g, "center": GATE_TO_CENTER.get(g, ""),
             "looking_for": [f"cổng {b}" for (a, b) in CHANNELS if a == g] + [f"cổng {a}" for (a, b) in CHANNELS if b == g]}
            for g in hanging]

    emotional = "Solar Plexus" in chart["defined_centers"]
    emotional_dynamics = ("Bạn có sóng cảm xúc riêng - đừng quyết chuyện tình cảm trong khoảnh khắc. "
                          "Đối phương sẽ cảm nhận sóng của bạn." if emotional else
                          "Bạn hấp thụ cảm xúc đối phương - học phân biệt cảm xúc nào là của mình, của ai.")

    composite = None
    if partner_datetime is not None:
        pchart = calculate_hd_chart(partner_datetime)
        pg = _gate_sets(pchart)
        electromagnetics, compromises, dominances = [], [], []
        for g1, g2 in CHANNELS:
            a1, a2 = g1 in allg, g2 in allg
            b1, b2 = g1 in pg, g2 in pg
            a_full = a1 and a2
            b_full = b1 and b2
            if (a1 and not a2 and b2 and not b1) or (a2 and not a1 and b1 and not b2):
                electromagnetics.append(f"{g1}-{g2}")
            if a_full and (b1 != b2):
                dominances.append(f"Bạn trội kênh {g1}-{g2}")
            if b_full and (a1 != a2):
                dominances.append(f"{partner_name or 'Đối phương'} trội kênh {g1}-{g2}")
        for g in sorted(allg & pg):
            compromises.append(f"cổng {g} ({GATE_MEANINGS.get(g, '')})")
        composite = {
            "partner_type": pchart["type"], "partner_profile": pchart["profile"],
            "partner_authority": pchart["authority"],
            "electromagnetics": electromagnetics, "count_electro": len(electromagnetics),
            "compromises": compromises, "count_compromise": len(compromises),
            "dominances": dominances, "count_dominance": len(dominances),
            "summary": (f"Hai bạn tạo {len(electromagnetics)} kết nối điện từ (hút nhau mạnh), "
                        f"{len(compromises)} điểm compromise (cùng cổng - cần thỏa hiệp), "
                        f"{len(dominances)} điểm dominance (một người trội). Điện từ nhiều = hấp dẫn mạnh nhưng cũng xung đột mạnh."),
        }

    advice = [
        f"Aura {t}: {AURA_DYNAMICS[t]}",
        f"Profile {p} trong yêu: {PROFILE_LOVE.get(p, '')}",
        emotional_dynamics,
        f"Bạn tìm ở đối phương {len(hanging)} mảnh ghép (cổng treo) - nhưng đừng biến đối phương thành 'nửa còn lại' duy nhất.",
        "Quy tắc vàng: Strategy + Authority áp dụng cho CẢ việc chọn người yêu và quyết định trong quan hệ.",
    ]
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": p, "authority": chart["authority"],
        "definition": chart["definition"],
        "defined_centers": sorted(chart["defined_centers"]),
        "relationship_analysis": {
            "love_gates_active": love_active, "count_love_gates": len(love_active),
            "aura_style": AURA_DYNAMICS[t],
            "profile_style": PROFILE_LOVE.get(p, ""),
            "what_you_seek": seek, "count_hanging": len(hanging),
            "emotional_dynamics": emotional_dynamics,
            "composite": composite,
            "advice": advice,
            "summary": (f"{name or 'Bạn'} ({t} {p}) mang {len(love_active)} cổng tình yêu vào quan hệ, "
                        f"tìm kiếm {len(hanging)} mảnh ghép từ đối phương. Chìa khóa: {AURA_DYNAMICS[t][:80]}..."),
        },
        "áp_dụng_cho": "100% dân số - 60 biến thể - Đơn hoặc Composite 2 người",
    }


def format_relationship_report(d):
    r = d["relationship_analysis"]
    L = [f"# BÁO CÁO MỐI QUAN HỆ & THÂN MẬT - {d['name']} - {d['type']} {d['profile']}",
         f"**Type:** {d['type']} | **Profile:** {d['profile']} | **Authority:** {d['authority']} | **Cổng tình yêu:** {r['count_love_gates']}",
         "", "## 1. PHONG CÁCH YÊU CỦA BẠN",
         f"**Aura {d['type']}:** {r['aura_style']}",
         f"**Profile {d['profile']}:** {r['profile_style']}",
         f"**Cảm xúc trong quan hệ:** {r['emotional_dynamics']}",
         "", f"## 2. CỔNG TÌNH YÊU KÍCH HOẠT ({r['count_love_gates']})"]
    for lg in r["love_gates_active"]:
        L.append(f"- **Cổng {lg['gate']}** ({lg['center']}): {lg['love']}")
    L += ["", f"## 3. BẠN TÌM GÌ Ở ĐỐI PHƯƠNG ({r['count_hanging']} mảnh ghép)"]
    for s in r["what_you_seek"][:15]:
        L.append(f"- **Cổng treo {s['gate']}** ({s['center']}): tìm {', '.join(s['looking_for'])}")
    if r["composite"]:
        c = r["composite"]
        L += ["", "## 4. COMPOSITE 2 NGƯỜI",
              f"**Đối phương:** {c['partner_type']} {c['partner_profile']} | {c['partner_authority']}",
              f"**Kết nối điện từ ({c['count_electro']}):** {', '.join(c['electromagnetics']) if c['electromagnetics'] else 'không có - ít hút nhau kiểu điện từ'}",
              f"**Compromise ({c['count_compromise']}):** {'; '.join(c['compromises'][:8]) if c['compromises'] else 'không có'}",
              f"**Dominance ({c['count_dominance']}):** {'; '.join(c['dominances'][:8]) if c['dominances'] else 'không có'}",
              c["summary"]]
    L += ["", "## 5. LỜI KHUYÊN", *[f"{i}. {a}" for i, a in enumerate(r["advice"], 1)],
          "", "## 6. KẾT LUẬN", r["summary"], "",
          "> \"Đừng tìm nửa còn lại - hãy là một người trọn vẹn rồi gặp nhau\"",
          "> \"Strategy + Authority cũng dùng để chọn người yêu\""]
    return "\n".join(L)
