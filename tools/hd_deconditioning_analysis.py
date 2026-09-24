#!/usr/bin/env python3
"""
Human Design Deconditioning Analysis - Giải điều kiện hóa & Not-Self (v3.0)
Nhu cầu thực tế: tìm điểm mù, lựa chọn hành vi phù hợp để cải thiện bản thân.
Not-Self theo Type + điều kiện hóa từng trung tâm mở + lộ trình 7 ngày/7 tháng/7 năm.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart
from hd_language import vn_authority, vn_strategy, vn_type

TYPE_NOTSELF = {
    "Generator": {"notself": "FRUSTRATION (Thất vọng/Bực bội)",
                  "signature": "SATISFACTION (Thỏa mãn)",
                  "focus": "Ngừng khởi xướng từ đầu óc. Quay về chờ đáp ứng. Frustration = đang làm việc sai/người sai.",
                  "mantra": "Tôi không cần phải khởi xướng - cơ hội sẽ đến và Sacral sẽ biết."},
    "Manifesting Generator": {"notself": "FRUSTRATION + ANGER (Thất vọng + Tức giận)",
                  "signature": "SATISFACTION + PEACE (Thỏa mãn + Bình yên)",
                  "focus": "Ngừng lao đi không thông báo. Đáp ứng trước, thông báo sau, rồi mới chạy.",
                  "mantra": "Tôi được phép nhanh - nhưng phải đáp ứng trước và thông báo sau."},
    "Projector": {"notself": "BITTERNESS (Đắng cay)",
                  "signature": "SUCCESS (Thành công)",
                  "focus": "Ngừng cố làm/giống Generator. Ngừng cho lời khuyên không được mời. Chờ công nhận + lời mời.",
                  "mantra": "Tôi không cần chứng minh năng lượng - giá trị của tôi là nhìn thấy và dẫn dắt."},
    "Manifestor": {"notself": "ANGER (Tức giận)",
                  "signature": "PEACE (Bình yên)",
                  "focus": "Ngừng hành động lén lút vì sợ bị cản. Inform trước để giảm kháng cự.",
                  "mantra": "Tôi được phép khởi xướng - và tôi sẽ thông báo để đường đi thông thoáng."},
    "Reflector": {"notself": "DISAPPOINTMENT (Thất vọng về cuộc đời)",
                  "signature": "SURPRISE (Ngạc nhiên thích thú)",
                  "focus": "Ngừng ép mình giống người khác. Chọn môi trường đúng, chờ hết chu kỳ trăng.",
                  "mantra": "Tôi khác biệt và đó là món quà - tôi cần thời gian và môi trường đúng."},
}

OPEN_CENTER_DECOND = {
    "Head": {"conditioning": "Bị ép phải trả lời mọi câu hỏi, ôm áp lực tinh thần của người khác.",
             "practice": "Mỗi tối liệt kê câu hỏi trong đầu, đánh dấu 'của mình/của người' - buông cái của người.",
             "mantra": "Tôi không cần trả lời mọi câu hỏi."},
    "Ajna": {"conditioning": "Bị ép phải chắc chắn, phải có quan điểm cố định, phải 'biết tuốt'.",
             "practice": "Tập nói 'Tôi chưa chắc, để tôi xem thêm' ít nhất 1 lần/ngày mà không xấu hổ.",
             "mantra": "Tôi không cần phải chắc chắn - không chắc cũng là trí tuệ."},
    "Throat": {"conditioning": "Bị ép phải nói/hành động để được chú ý, sợ im lặng.",
               "practice": "Trước khi nói: dừng 3 giây, hỏi 'có cần nói không, hay chỉ muốn được chú ý?'",
               "mantra": "Tôi không cần nói để được chú ý - im lặng cũng có giá trị."},
    "G": {"conditioning": "Bị ép phải cố định mình là ai, yêu ai, đi đâu - hoặc bị lôi theo hướng người khác.",
          "practice": "Thử vai trò mới mỗi tuần mà không cần 'đây là mình mãi mãi'.",
          "mantra": "Tôi được phép linh hoạt - hôm nay khác hôm qua cũng được."},
    "Heart": {"conditioning": "Bị ép chứng minh giá trị qua tiền/thành tích, hứa bừa để được yêu.",
              "practice": "Trước mỗi cam kết: chờ 24h. Hỏi 'mình muốn hay mình đang chứng minh?'",
              "mantra": "Tôi đã có giá trị - không cần chứng minh bằng tiền hay lời hứa."},
    "Spleen": {"conditioning": "Bám nỗi sợ và điều không tốt vì sợ thay đổi; lo âu sức khỏe mượn.",
               "practice": "Liệt kê 1 điều đang bám mà biết là hại - lên kế hoạch buông trong 7 ngày.",
               "mantra": "Buông điều hại mình là an toàn - nỗi sợ này có thể không phải của mình."},
    "Sacral": {"conditioning": "Bị ép làm việc như Generator, không biết khi nào đủ, kiệt sức.",
               "practice": "Đặt giờ dừng việc mỗi ngày + ngủ trưa. Nói không với việc rút năng lượng.",
               "mantra": "Tôi không cần làm nhiều như người có Sacral - nghỉ ngơi là làm việc."},
    "Solar Plexus": {"conditioning": "Hấp thụ cảm xúc người khác, sợ đối đầu nên nén, bùng nổ sau.",
                     "practice": "Khi cảm xúc dâng: hỏi 'cảm xúc này của ai?' - trả lại cái không phải của mình.",
                     "mantra": "Cảm xúc này có thể không phải của mình - tôi được phép bình tĩnh."},
    "Root": {"conditioning": "Bị ép vội vã, làm cho xong để xả áp lực, luôn trong trạng thái chạy.",
             "practice": "Khi thấy vội: dừng, hít sâu 3 lần, hỏi 'có thật sự gấp không?' - 90% là không.",
             "mantra": "Tôi không cần vội - áp lực này có thể không phải của mình."},
}

DEFINED_WARNINGS = {
    "Head": "Đừng ép người khác theo nhịp câu hỏi của bạn.",
    "Ajna": "Đừng ép người khác phải chắc chắn như bạn.",
    "Throat": "Lời bạn có trọng lượng - cẩn thận khi nói lúc giận.",
    "G": "Đừng ép người mở G phải 'chọn một hướng mãi mãi'.",
    "Heart": "Đừng ép người khác giữ cam kết kiểu bạn - họ không có ý chí cố định.",
    "Spleen": "Nỗi sợ thoáng qua của bạn có thể ám ảnh người mở Spleen cả ngày.",
    "Sacral": "Tiếng uh-huh của bạn vang - đừng ép người không có Sacral theo nhịp bạn.",
    "Solar Plexus": "Sóng cảm xúc của bạn tràn sang người khác - đừng quyết thay họ lúc bạn đang cao/trầm.",
    "Root": "Áp lực của bạn khiến người mở Root vội vã sai lầm - xả áp lực đúng chỗ.",
}


def analyze_deconditioning(birth_datetime, name=""):
    # Accept a precomputed chart when called from the report pipeline.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t = chart["type"]
    defined = set(chart["defined_centers"])
    order = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
    open_c = [c for c in order if c not in defined]

    ns = TYPE_NOTSELF[t]
    opens = [{"center": c, **OPEN_CENTER_DECOND[c]} for c in open_c]
    warns = [{"center": c, "warning": DEFINED_WARNINGS[c]} for c in order if c in defined]
    roadmap = {
        "7d": f"7 NGÀY: Thử nghiệm chiến lược sống ({vn_strategy(chart['strategy'], chart['type'])}) + quyền nội tại ({vn_authority(chart['authority'])}). Ghi nhật ký Not-Self mỗi tối: hôm nay mình {ns['notself'].split('(')[0].strip()} lúc nào? Vì sao?",
        "7m": f"7 THÁNG: Mỗi tháng làm việc với 1-2 trung tâm mở ({', '.join(open_c)}). Thực hành mantra + bài tập từng trung tâm. Quan sát quan hệ thay đổi.",
        "7y": ("7 NĂM: Chu kỳ thay tế bào hoàn toàn. Năm 1-2: nhận diện điều kiện hóa. Năm 3-5: sống Strategy+Authority thành bản năng. "
               "Năm 6-7: trí tuệ từ trung tâm mở chín - bạn thành người hướng dẫn người khác bằng chính trải nghiệm."),
    }
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": chart["profile"], "authority": chart["authority"],
        "definition": chart["definition"],
        "strategy": chart["strategy"],
        "defined_centers": sorted(defined), "open_centers": open_c,
        "deconditioning_analysis": {
            "notself_theme": ns["notself"], "signature": ns["signature"],
            "type_focus": ns["focus"], "type_mantra": ns["mantra"],
            "open_centers": opens, "count_open": len(open_c),
            "defined_warnings": warns, "count_defined": len(defined),
            "roadmap": roadmap,
            "summary": (f"{name or 'Bạn'} ({t}): Not-Self = {ns['notself']}, Chữ ký đúng = {ns['signature']}. "
                        f"Trọng tâm: {ns['focus']} Lộ trình: 7 ngày thử nghiệm -> 7 tháng đào sâu {len(open_c)} trung tâm mở -> 7 năm lột xác."),
        },
        "áp_dụng_cho": "100% dân số - 60 biến thể - Lộ trình 7 ngày/7 tháng/7 năm",
    }


def format_deconditioning_report(d):
    r = d["deconditioning_analysis"]
    L = [f"# BÁO CÁO GIẢI ĐIỀU KIỆN HÓA - {d['name']} - {d['type']} {d['profile']}",
         f"**Loại năng lượng:** {vn_type(d['type'], gloss=True)} | **Chiến lược sống:** {vn_strategy(d.get('strategy', ''), d['type'])} | **Quyền nội tại:** {vn_authority(d['authority'])}",
         "", "## 1. NOT-SELF vs CHỮ KÝ CỦA BẠN",
         f"**Not-Self (đèn đỏ):** {r['notself_theme']}",
         f"**Chữ ký (đèn xanh):** {r['signature']}",
         f"**Trọng tâm giải điều kiện:** {r['type_focus']}",
         f"**Mantra:** \"{r['type_mantra']}\"",
         "", f"## 2. GIẢI ĐIỀU KIỆN {r['count_open']} TRUNG TÂM MỞ"]
    for o in r["open_centers"]:
        L += [f"### {o['center']} (Mở)",
              f"- **Điều kiện hóa:** {o['conditioning']}",
              f"- **Bài tập:** {o['practice']}",
              f"- **Mantra:** \"{o['mantra']}\""]
    L += ["", f"## 3. CẢNH BÁO TỪ {r['count_defined']} TRUNG TÂM ĐỊNH NGHĨA (đừng điều kiện hóa người khác)"]
    for w in r["defined_warnings"]:
        L.append(f"- **{w['center']}:** {w['warning']}")
    L += ["", "## 4. LỘ TRÌNH 7 NGÀY / 7 THÁNG / 7 NĂM",
          f"- **7 ngày:** {r['roadmap']['7d']}",
          f"- **7 tháng:** {r['roadmap']['7m']}",
          f"- **7 năm:** {r['roadmap']['7y']}",
          "", "## 5. KẾT LUẬN", r["summary"], "",
          "> \"Deconditioning không phải sửa mình - mà là cởi bỏ cái không phải mình\"",
          "> \"7 năm - vì cơ thể cần đủ thời gian để tin bạn\""]
    return "\n".join(L)
