"""Variables & PHS: 4 mũi tên từ Color/Tone/Base (đề xuất cũ B).

Nguồn luật suy: gethumandesign.com/docs/variable (+ determination, environment,
motivation, perspective, color-tone-base), đối chiếu Genetic Matrix Learn Hub
và HD ReDefined. Truy cập 2026-09-28.

- TL Determination (tiêu hóa): Design Sun — Color 1-6 + Tone → mũi tên.
- BL Environment (môi trường): Design Nodes — Color 1-6 + Tone → mũi tên.
- TR Motivation (động lực): Personality Sun — Color 1-6 + Tone → mũi tên.
- BR Perspective (góc nhìn): Personality Nodes — Color 1-6 + Tone → mũi tên.
- Cognition (giác quan tin cậy): DUY NHẤT từ Design Sun Tone.
- Mũi tên: Tone 1-3 = trái (chủ động), 4-6 = phải (thụ động).
- Transference (Motivation) và Distraction (Perspective): cặp đối diện,
  cách nhau 3 bước trên vòng 6 Color.

Yêu cầu GIỜ SINH CHÍNH XÁC: Tone đổi mỗi ~14 phút ở Sun, Node còn nhạy hơn.
"""

from __future__ import annotations

DETERMINATION = {
    1: {"en": "Appetite", "vi": "Thèm ăn", "L": ("Consecutive", "Từng món"),
        "R": ("Alternating", "Xen kẽ"),
        "tip": "Ăn theo cơn đói thật của cơ thể, không theo giờ giấc."},
    2: {"en": "Taste", "vi": "Vị giác", "L": ("Open", "Mở"),
        "R": ("Closed", "Kén chọn"),
        "tip": "Vị ngon thật sự lúc đó là la bàn; theo sức hút vị giác."},
    3: {"en": "Thirst", "vi": "Cơn khát", "L": ("Hot", "Nóng"),
        "R": ("Cold", "Lạnh"),
        "tip": "Nhiệt độ và nước là chìa khóa: nóng/ấm hoặc mát/lạnh."},
    4: {"en": "Touch", "vi": "Chạm", "L": ("Calm", "Tĩnh"),
        "R": ("Nervous", "Động"),
        "tip": "Mức náo động quanh bữa ăn quyết định tiêu hóa tốt hay không."},
    5: {"en": "Sound", "vi": "Âm thanh", "L": ("High", "Rộn ràng"),
        "R": ("Low", "Yên tĩnh"),
        "tip": "Môi trường âm thanh nuôi hoặc phá bữa ăn."},
    6: {"en": "Light", "vi": "Ánh sáng", "L": ("Direct", "Trực tiếp"),
        "R": ("Indirect", "Gián tiếp"),
        "tip": "Ăn ban ngày dưới sáng tự nhiên; tránh no trước khi ngủ."},
}

ENVIRONMENT = {
    1: {"en": "Caves", "vi": "Hang động", "L": ("Selective", "Chọn lọc"),
        "R": ("Blending", "Hòa trộn"),
        "tip": "Nơi kín, an toàn, một lối vào, tự kiểm soát ai bước vào."},
    2: {"en": "Markets", "vi": "Chợ", "L": ("Internal", "Hướng nội"),
        "R": ("External", "Hướng ngoại"),
        "tip": "Nơi đông đúc trao đổi, nhiều lựa chọn và chuyển động."},
    3: {"en": "Kitchens", "vi": "Nhà bếp", "L": ("Wet", "Ướt"),
        "R": ("Dry", "Khô"),
        "tip": "Nơi cùng làm cùng tạo ra thứ gì đó: bếp, xưởng, studio."},
    4: {"en": "Mountains", "vi": "Núi", "L": ("Active", "Chủ động"),
        "R": ("Passive", "Thụ động"),
        "tip": "Nơi cao thoáng nhìn bao quát, có khoảng lùi trước khi nhập cuộc."},
    5: {"en": "Valleys", "vi": "Thung lũng", "L": ("Narrow", "Hẹp"),
        "R": ("Wide", "Rộng"),
        "tip": "Nơi thấp vững để lắng nghe, quan sát và nối kết cộng đồng."},
    6: {"en": "Shores", "vi": "Bờ biển", "L": ("Natural", "Tự nhiên"),
        "R": ("Artificial", "Nhân tạo"),
        "tip": "Ranh giới hai môi trường gặp nhau: bờ nước, vùng chuyển tiếp."},
}

MOTIVATION = {
    1: {"en": "Fear", "vi": "Sợ hãi",
        "tip": "Đối mặt điều chưa biết để biến mơ hồ thành sáng tỏ.",
        "transference": 4},
    2: {"en": "Hope", "vi": "Hy vọng",
        "tip": "Tin mọi sự đúng lúc; hướng về điều khả dĩ đáng chờ.",
        "transference": 5},
    3: {"en": "Desire", "vi": "Ham muốn",
        "tip": "Muốn trực tiếp nhúng tay thay đổi thế giới vật chất.",
        "transference": 6},
    4: {"en": "Need", "vi": "Nhu cầu",
        "tip": "Lọc nhiễu, chỉ giữ điều thật sự cần thiết.",
        "transference": 1},
    5: {"en": "Guilt", "vi": "Tội lỗi",
        "tip": "Thấy chỗ hỏng và sửa: trách nhiệm và hàn gắn, không tự trách.",
        "transference": 2},
    6: {"en": "Innocence", "vi": "Ngây thơ",
        "tip": "Không chương trình ngầm; gặp mỗi khoảnh khắc như mới tinh.",
        "transference": 3},
}

PERSPECTIVE = {
    1: {"en": "Survival", "vi": "Sống còn",
        "tip": "Nhìn điều thực tế giữ cuộc sống vận hành mỗi ngày.",
        "distraction": 4},
    2: {"en": "Possibility", "vi": "Khả năng",
        "tip": "Thấy trước khe cửa, tiềm năng chưa thành hình.",
        "distraction": 5},
    3: {"en": "Power", "vi": "Quyền lực",
        "tip": "Đọc ảnh hưởng và dòng năng lượng chảy qua tình huống.",
        "distraction": 6},
    4: {"en": "Wanting", "vi": "Khao khát",
        "tip": "Cảm điều đang thiếu, điều muốn được lấp đầy.",
        "distraction": 1},
    5: {"en": "Probability", "vi": "Xác suất",
        "tip": "Cân xác suất xảy ra và quy luật ẩn sau mẫu hình.",
        "distraction": 2},
    6: {"en": "Personal", "vi": "Cá nhân",
        "tip": "Thấy qua trải nghiệm sống trực tiếp của chính mình.",
        "distraction": 3},
}

COGNITION = {
    1: {"en": "Smell", "vi": "Khứu giác",
        "tip": "Ngửi là biết an toàn và đúng hay không, trước cả lời nói."},
    2: {"en": "Taste", "vi": "Vị giác",
        "tip": "Phải nếm thử mới biết hợp hay không."},
    3: {"en": "Outer Vision", "vi": "Nhìn ngoài",
        "tip": "Định hướng qua điều mắt thấy: hình mẫu trước mặt."},
    4: {"en": "Inner Vision", "vi": "Nhìn trong",
        "tip": "Tin điều hình dung được bên trong; cần không gian tưởng tượng."},
    5: {"en": "Feeling", "vi": "Cảm nhận",
        "tip": "Đọc tần số cảm xúc và bầu không khí của sự việc."},
    6: {"en": "Touch", "vi": "Chạm",
        "tip": "Phải chạm tay, đi vào không gian mới hiểu thật."},
}

ARROW_MEANING = {
    "determination": {"L": "Não chủ động: tiêu hóa tốt khi tập trung, có cấu trúc.",
                      "R": "Não thụ động: tiêu hóa tốt khi thả lỏng, không gò ép."},
    "environment": {"L": "Chủ động tìm và dựng không gian đúng cho mình.",
                    "R": "Để không gian đúng tự tìm đến; hợp di chuyển đổi chỗ."},
    "motivation": {"L": "Trí chiến lược: học để dùng vào mục tiêu cụ thể.",
                   "R": "Trí thụ động: thư viện sống, thu nhận rồi tỏa khi được khơi."},
    "perspective": {"L": "Nhìn hội tụ: phóng to chi tiết điều tra kỹ.",
                    "R": "Nhìn ngoại vi: bao quát toàn cảnh trong một ánh nhìn."},
}


def _clamp(v: int, lo: int = 1, hi: int = 6) -> int:
    return max(lo, min(hi, int(v)))


def arrow_of(tone: int) -> str:
    """Tone 1-3 = trái (L), 4-6 = phải (R)."""
    return "L" if _clamp(tone) <= 3 else "R"


def analyze_variables(chart: dict) -> dict:
    """Suy 4 mũi tên + chi tiết từ chart đã tính (cần Sun và North Node P/D)."""
    pg, dg = chart["personality_gates"], chart["design_gates"]
    d_sun, d_node = dg["Sun"], dg["North Node"]
    p_sun, p_node = pg["Sun"], pg["North Node"]

    det_c, det_t = _clamp(d_sun["color"]), _clamp(d_sun["tone"])
    env_c, env_t = _clamp(d_node["color"]), _clamp(d_node["tone"])
    mot_c, mot_t = _clamp(p_sun["color"]), _clamp(p_sun["tone"])
    per_c, per_t = _clamp(p_node["color"]), _clamp(p_node["tone"])
    det_a, env_a, mot_a, per_a = (arrow_of(det_t), arrow_of(env_t),
                                  arrow_of(mot_t), arrow_of(per_t))

    det, env = DETERMINATION[det_c], ENVIRONMENT[env_c]
    mot, per = MOTIVATION[mot_c], PERSPECTIVE[per_c]
    cog = COGNITION[det_t]
    return {
        "code": f"D{det_a}{env_a}-P{mot_a}{per_a}",
        "determination": {
            "arrow": det_a, "color": det_c, "tone": det_t,
            "name_en": det["en"], "name_vi": det["vi"],
            "variant_en": det[det_a][0], "variant_vi": det[det_a][1],
            "meaning": ARROW_MEANING["determination"][det_a], "tip": det["tip"],
        },
        "environment": {
            "arrow": env_a, "color": env_c, "tone": env_t,
            "name_en": env["en"], "name_vi": env["vi"],
            "variant_en": env[env_a][0], "variant_vi": env[env_a][1],
            "meaning": ARROW_MEANING["environment"][env_a], "tip": env["tip"],
        },
        "motivation": {
            "arrow": mot_a, "color": mot_c, "tone": mot_t,
            "name_en": mot["en"], "name_vi": mot["vi"],
            "meaning": ARROW_MEANING["motivation"][mot_a], "tip": mot["tip"],
            "transference_en": MOTIVATION[mot["transference"]]["en"],
            "transference_vi": MOTIVATION[mot["transference"]]["vi"],
        },
        "perspective": {
            "arrow": per_a, "color": per_c, "tone": per_t,
            "name_en": per["en"], "name_vi": per["vi"],
            "meaning": ARROW_MEANING["perspective"][per_a], "tip": per["tip"],
            "distraction_en": PERSPECTIVE[per["distraction"]]["en"],
            "distraction_vi": PERSPECTIVE[per["distraction"]]["vi"],
        },
        "cognition": {
            "tone": det_t, "name_en": cog["en"], "name_vi": cog["vi"],
            "tip": cog["tip"],
        },
        "note": ("Tầng thực nghiệm, cần giờ sinh chính xác đến phút. "
                 "Chỉ luận sau khi thân chủ đã sống đúng Strategy + Authority."),
    }


def format_variables_report(v: dict) -> str:
    """Tóm tắt Variables/PHS tiếng Việt cho báo cáo."""
    d, e, m, p, c = (v["determination"], v["environment"], v["motivation"],
                     v["perspective"], v["cognition"])
    arrow = {"L": "trái ◀", "R": "phải ▶"}
    return "\n".join([
        f"Variables {v['code']} (trái = chủ động, phải = thụ động):",
        f"- Tiêu hóa ({d['name_en']} {d['variant_en']} — {d['name_vi']} {d['variant_vi']}, mũi tên {arrow[d['arrow']]}): {d['tip']} {d['meaning']}",
        f"- Môi trường ({e['name_en']} {e['variant_en']} — {e['name_vi']} {e['variant_vi']}, mũi tên {arrow[e['arrow']]}): {e['tip']} {e['meaning']}",
        f"- Động lực ({m['name_en']} — {m['name_vi']}, mũi tên {arrow[m['arrow']]}): {m['tip']} Khi lệch, tâm trí trượt sang {m['transference_en']} ({m['transference_vi']}).",
        f"- Góc nhìn ({p['name_en']} — {p['name_vi']}, mũi tên {arrow[p['arrow']]}): {p['tip']} Khi lệch, mắt nhìn trượt sang {p['distraction_en']} ({p['distraction_vi']}).",
        f"- Giác quan tin cậy ({c['name_en']} — {c['name_vi']}): {c['tip']}",
        f"Lưu ý: {v['note']}",
    ])
