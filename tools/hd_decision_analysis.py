#!/usr/bin/env python3
"""
Human Design Decision Analysis - Ra quyết định theo Authority (v3.0)
Nhu cầu thực tế: lựa chọn hành vi phù hợp, quyết định đúng để cải thiện bản thân.
7 Authorities + quy trình từng bước + thời gian + câu hỏi + bẫy.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart
from hd_language import vn_authority, vn_type

AUTHORITY_GUIDE = {
    "Emotional": {
        "full": "Emotional - Solar Plexus (Cảm xúc)",
        "how": "KHÔNG có sự thật trong khoảnh khắc. Sóng cảm xúc lên-xuống; sự rõ ràng chỉ đến khi sóng lắng.",
        "process": ["Nhận tín hiệu/cơ hội -> ghi nhận cảm xúc đầu tiên NHƯNG chưa quyết.",
                    "Chờ ít nhất 1 đêm (việc lớn: vài ngày đến 1 tuần) - ngủ với nó.",
                    "Quan sát sóng: lúc cao có còn muốn? lúc thấp có còn muốn?",
                    "Khi cảm giác NHẤT QUÁN qua cả đỉnh và đáy -> đó là câu trả lời.",
                    "Quyết xong thì đi - đừng xem lại khi sóng đổi."],
        "timing": "Việc nhỏ: vài giờ. Việc vừa: 1-3 ngày. Việc lớn (nghề, nhà, hôn nhân): 1-4 tuần.",
        "questions": ["Cảm giác này có còn khi mình bình tĩnh không?", "Mình có quyết khác đi nếu đợi thêm 3 ngày?", "Đây là sóng cao, sóng thấp, hay sự rõ ràng?"],
        "traps": ["Quyết trong hứng khởi -> hối hận khi tụt.", "Quyết trong tuyệt vọng -> bỏ lỡ cơ hội.", "Để người khác ép quyết ngay."],
    },
    "Sacral": {
        "full": "Sacral (Phản ứng Xương cùng)",
        "how": "Sự thật đến NGAY TRONG KHOẢNH KHẮC qua âm thanh cơ thể: uh-huh (mở, đi lên) = CÓ; uh-uh (đóng, đi xuống) = KHÔNG.",
        "process": ["Đặt câu hỏi ĐÚNG/SAI, cụ thể, trong hiện tại (đừng hỏi mở).",
                    "Lắng nghe âm thanh ĐẦU TIÊN của cơ thể - trước khi đầu óc phân tích.",
                    "uh-huh -> đi ngay. uh-uh -> dừng ngay, không cần lý do.",
                    "Không có tiếng rõ -> chưa phải lúc, chờ tín hiệu rõ hơn.",
                    "Tin cơ thể hơn lý trí - Sacral không biết nói dối."],
        "timing": "Ngay lập tức - Sacral trả lời trong hiện tại. Càng chờ đầu óc càng nhiễu.",
        "questions": ["Cơ thể mình nói uh-huh hay uh-uh?", "Mình có đang dùng lý do để lấn át tiếng cơ thể?", "Câu hỏi đã đủ cụ thể chưa?"],
        "traps": ["Hỏi ý kiến quá nhiều người -> nhiễu.", "Dùng logic để ép uh-uh thành uh-huh.", "Quyết cho tương lai xa thay vì hiện tại."],
    },
    "Splenic": {
        "full": "Splenic (Trực giác Lách)",
        "how": "Trực giác đến TỨC THÌ, NHẸ NHÀNG, chỉ nói MỘT LẦN rồi im. Không ồn ào như cảm xúc, không lặp lại.",
        "process": ["Chú ý cú 'biết' đầu tiên, thoáng qua - thường kèm cảm giác cơ thể nhẹ.",
                    "Đừng đòi lý do - trực giác không giải thích.",
                    "Hành động ngay theo cú hit đầu tiên.",
                    "Nếu đã bỏ lỡ (đầu óc xen vào) -> chờ cơ hội/tín hiệu mới, đừng cố gợi lại.",
                    "Ghi nhật ký trực giác để tăng độ tin cậy theo thời gian."],
        "timing": "Tức thì - trong vài giây đầu. Càng phân tích càng mất.",
        "questions": ["Cú cảm đầu tiên (trước khi nghĩ) là gì?", "Cơ thể mình nhẹ đi hay nặng lại?", "Mình có đang sợ nên mới do dự?"],
        "traps": ["Đòi trực giác lặp lại/lớn tiếng hơn.", "Nhầm nỗi sợ (to, ồn) với trực giác (nhẹ, quiet).", "Hỏi người khác để xác nhận trực giác."],
    },
    "Heart": {
        "full": "Heart/Ego (Ý chí)",
        "how": "Quyết bằng Ý CHÍ: 'Tôi MUỐN điều này, tôi cam kết'. Đúng khi có cái gì đó đáng giá (tiền, địa vị, thử thách) đặt cược.",
        "process": ["Hỏi thẳng: 'Tôi có THỰC SỰ muốn không - đủ để đặt cược không?'",
                    "Kiểm tra động cơ: vì mình muốn hay vì chứng minh với ai?",
                    "Nếu ý chí rõ và có phần thưởng xứng đáng -> cam kết 100%.",
                    "Nói ra cam kết - lời hứa của Heart Defined có trọng lượng.",
                    "Giữ lời - mỗi lần giữ lời, ý chí mạnh thêm."],
        "timing": "Khi ý chí rõ - có thể nhanh. Đừng quyết khi kiệt sức ý chí.",
        "questions": ["Mình muốn hay mình 'nên'?", "Phần thưởng có xứng đáng không?", "Mình có giữ được lời này?"],
        "traps": ["Hứa bừa để chứng minh (đặc biệt khi Heart mở mà tưởng mình có ý chí).", "Cam kết khi kiệt sức.", "Quyết vì sĩ diện thay vì ý chí thật."],
    },
    "Self": {
        "full": "Self/G (Bản ngã - Hướng đi)",
        "how": "Quyết bằng CẢM GIÁC ĐÚNG HƯỚNG: 'đây có phải là mình, có đưa mình đúng đường không?' Cần nói ra để nghe.",
        "process": ["Nói với người đáng tin (sounding board) - không cần lời khuyên, cần được nghe.",
                    "Lắng nghe CHÍNH MÌNH nói - câu nào nghe 'đúng mình' nhất?",
                    "Kiểm tra: quyết này có đúng với con người mình không?",
                    "Đi theo hướng khiến mình cảm thấy 'là mình' nhất.",
                    "Tránh môi trường/ người khiến mình mất cảm giác về mình khi quyết."],
        "timing": "Qua vài lần nói ra - khi tiếng nói trong rõ dần. Đừng quyết trong môi trường sai.",
        "questions": ["Điều này có 'là mình' không?", "Mình đang nói từ bản ngã hay từ nỗi sợ?", "Ở đây (môi trường này) mình có thấy mình không?"],
        "traps": ["Quyết trong môi trường sai/người sai.", "Nghe lời khuyên thay vì nghe chính mình.", "Nhầm kỳ vọng người khác với hướng của mình."],
    },
    "Mental": {
        "full": "Mental (Môi trường - Không có Authority nội tại)",
        "how": "KHÔNG có tiếng nói nội tại đáng tin để quyết. Sự rõ ràng đến qua NÓI RA + MÔI TRƯỜNG ĐÚNG + thời gian.",
        "process": ["Tìm 2-3 sounding boards (người nghe tốt, không áp đặt).",
                    "Nói ra mọi góc nhìn - nghe mình nói để thấy rõ.",
                    "Chỉ quyết khi ở môi trường khiến mình thấy sáng, nhẹ, đúng.",
                    "Cho thời gian - đừng ép deadline quyết định.",
                    "Quyết xong, kiểm tra lại ở môi trường khác để chắc."],
        "timing": "Chậm mà chắc - ngày đến tuần. Đừng bao giờ quyết vội.",
        "questions": ["Mình đã nói ra hết chưa?", "Môi trường này có đúng cho mình?", "Mình có đang bị ép quyết nhanh?"],
        "traps": ["Ép mình phải 'chắc chắn' như người khác.", "Quyết một mình trong đầu.", "Quyết ở môi trường sai vì tiện."],
    },
    "Lunar": {
        "full": "Lunar (Chu kỳ Mặt Trăng 28 ngày - Reflector)",
        "how": "Sự thật lộ dần qua CHU KỲ MẶT TRĂNG - nếm trải đủ 64 cổng qua 28 ngày. Không quyết vội bao giờ.",
        "process": ["Nhận cơ hội -> ghi lại, đừng quyết.",
                    "Theo dõi cảm nhận qua các tuần trăng (mỗi tuần nhìn khác nhau là bình thường).",
                    "Nói chuyện với vòng tròn tin cậy qua chu kỳ.",
                    "Hết 28 ngày: điều gì CÒN ĐÚNG qua mọi pha trăng -> đó là câu trả lời.",
                    "Việc nhỏ hàng ngày: theo Strategy (chờ surprise) + cảm nhận hiện tại."],
        "timing": "Việc lớn: đủ 28 ngày. Việc nhỏ: trong ngày nhưng đừng ép.",
        "questions": ["Mình đã đi hết chu kỳ chưa?", "Điều này có đúng ở mọi pha trăng?", "Ai đang ép mình quyết nhanh?"],
        "traps": ["Quyết nhanh vì sợ mất cơ hội.", "Quyết theo cảm xúc của người xung quanh (hấp thụ).", "Ở sai môi trường mà quyết."],
    },
}

STRATEGY_FLOW = {
    "Generator": "Chờ tín hiệu -> Sacral đáp ứng -> kiểm tra Authority -> hành động bền bỉ.",
    "Manifesting Generator": "Chờ tín hiệu -> Sacral đáp ứng -> INFORM người liên quan -> kiểm tra Authority -> hành động nhanh.",
    "Projector": "Chờ CÔNG NHẬN + LỜI MỜI đúng -> kiểm tra Authority -> nhận lời -> dẫn dắt.",
    "Manifestor": "Cảm xung động khởi xướng -> INFORM người bị ảnh hưởng -> kiểm tra Authority -> hành động.",
    "Reflector": "Chờ điều BẤT NGỜ (surprise) -> nếm qua chu kỳ trăng -> kiểm tra với vòng tròn tin cậy -> quyết.",
}


def _match_authority(auth_str):
    s = (auth_str or "").lower()
    if "solar" in s or "emotion" in s:
        return "Emotional"
    if "sacral" in s:
        return "Sacral"
    if "spleen" in s or "splenic" in s:
        return "Heart" if "heart" in s or "ego" in s else "Splenic"
    if "heart" in s or "ego" in s:
        return "Heart"
    if "self" in s or "identity" in s or "\ng\n" in s or s.strip() == "g":
        return "Self"
    if "lunar" in s or "moon" in s or "none" in s or "reflector" in s:
        return "Lunar"
    if "mental" in s or "ajna" in s or "throat" in s or "head" in s:
        return "Mental"
    return "Emotional"


def analyze_decision(birth_datetime, name=""):
    # Accept a precomputed chart when called from the report pipeline.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t = chart["type"]
    key = _match_authority(chart["authority"])
    g = AUTHORITY_GUIDE[key]
    mind_traps = [
        "Mind (đầu óc) để ĐO LƯỜNG và so sánh - KHÔNG BAO GIỜ để ra quyết định.",
        "Dấu hiệu Mind đang lái: phân tích quá mức, hỏi 10 người, liệt kê pros/cons mãi không xong.",
        "Câu thần chú: 'Đầu óc là hành khách, Authority mới là tài xế'.",
    ]
    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": chart["profile"], "authority": chart["authority"],
        "definition": chart["definition"],
        "decision_analysis": {
            "authority_key": key, "authority_full": g["full"],
            "how_it_works": g["how"], "process": g["process"],
            "timing": g["timing"], "questions": g["questions"], "traps": g["traps"],
            "strategy_flow": STRATEGY_FLOW[t],
            "mind_traps": mind_traps,
            "big_vs_small": ("Việc LỚN (nghề, nhà, hôn nhân, đầu tư lớn): đi đủ quy trình + đủ thời gian. "
                             "Việc NHỎ hàng ngày: rút gọn - Strategy nhanh + 1 câu hỏi Authority."),
            "summary": (f"{name or 'Bạn'} quyết đúng bằng {vn_authority(g['full'])}. Quy trình: {' -> '.join(g['process'][:3])}... "
                        f"Thời gian: {g['timing']} Kết hợp Strategy {t}: {STRATEGY_FLOW[t]}"),
        },
        "áp_dụng_cho": "100% dân số - 7 Authorities - 60 biến thể",
    }


def format_decision_report(d):
    r = d["decision_analysis"]
    L = [f"# BÁO CÁO RA QUYẾT ĐỊNH - {d['name']} - {d['type']} {d['profile']}",
         f"**Quyền nội tại:** {vn_authority(r['authority_full'])} | **Loại năng lượng:** {vn_type(d['type'], gloss=True)}",
         "", "## 1. AUTHORITY CỦA BẠN HOẠT ĐỘNG THẾ NÀO", r["how_it_works"],
         "", "## 2. QUY TRÌNH QUYẾT ĐỊNH TỪNG BƯỚC"]
    L += [f"{i}. {s}" for i, s in enumerate(r["process"], 1)]
    L += ["", "## 3. THỜI GIAN QUYẾT ĐỊNH", r["timing"],
          "", "## 4. CÂU HỎI PHẢI TỰ HỎI"]
    L += [f"- {q}" for q in r["questions"]]
    L += ["", "## 5. BẪY CẦN TRÁNH"]
    L += [f"- {x}" for x in r["traps"]]
    L += ["", "## 6. LUỒNG STRATEGY + AUTHORITY", r["strategy_flow"],
          "", "## 7. BẪY ĐẦU ÓC (MIND KHÔNG PHẢI AUTHORITY)"]
    L += [f"- {x}" for x in r["mind_traps"]]
    L += ["", "## 8. VIỆC LỚN vs VIỆC NHỎ", r["big_vs_small"],
          "", "## 9. KẾT LUẬN", r["summary"], "",
          "> \"Đừng tin đầu óc - hãy tin cơ thể bạn\"",
          "> \"Quyết định đúng = Strategy + Authority, không phải pros/cons\""]
    return "\n".join(L)
