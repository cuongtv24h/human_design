#!/usr/bin/env python3
"""
Human Design Health Analysis - Sức khỏe Thân-Tâm-Trí (v3.0)
Nhu cầu thực tế: quy luật vận hành con người để cải thiện sức khỏe thân-tâm-trí.
Framework: Type + Centers (Defined/Open) + Channels + Not-Self signals + Sleep/Rest.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER

TYPE_HEALTH = {
    "Generator": {
        "pattern": "Sinh lực Sacral bền bỉ nhưng HỮU HẠN theo từng ngày - cần xả hết năng lượng mỗi ngày qua việc yêu thích.",
        "risk": "Kiệt sức Sacral (burnout): làm việc không yêu thích -> Frustration tích tụ -> cơ thể kiệt quệ, mất ngủ, suy nhược.",
        "sleep": "Đi ngủ khi đã xả hết năng lượng (nằm xuống trước khi ngủ ~1h để xả). Ngủ đủ, dậy khi tỉnh táo tự nhiên.",
        "exercise": "Vận động đổ mồ hôi mỗi ngày để xả Sacral. Thiếu vận động = bứt rứt, khó ngủ.",
        "recovery": "Frustration là tín hiệu sớm nhất - khi thấy bực bội vô cớ, dừng lại, đổi việc, nghỉ ngơi.",
    },
    "Manifesting Generator": {
        "pattern": "Năng lượng nhanh + đa nhiệm - cơ thể chạy nhanh hơn người thường, dễ bỏ qua tín hiệu mệt.",
        "risk": "Chấn thương do vội (bỏ bước), căng cơ, kiệt sức vì ôm nhiều việc; tức giận tích tụ gây cao huyết áp, tim mạch.",
        "sleep": "Khó 'tắt máy' vì đầu vẫn chạy nhiều dự án - cần nghi thức xả năng lượng trước ngủ (viết ra, vận động nhẹ).",
        "exercise": "Thể thao tốc độ, đa dạng, đổi món thường xuyên. Không hợp routine đơn điệu.",
        "recovery": "Anger + Frustration = đèn đỏ. Thông báo + giảm tải + ngủ bù.",
    },
    "Projector": {
        "pattern": "Không có Sacral - năng lượng KHÔNG bền bỉ. Thiết kế để làm việc theo nhịp: tập trung sâu rồi nghỉ sâu.",
        "risk": "Burnout là chủ đề cả đời: cố làm như Generator -> suy nhược, mất ngủ kinh niên, suy giảm miễn dịch.",
        "sleep": "Cần ngủ NHIỀU hơn người khác + ngủ trưa (nap) là bắt buộc, không phải lười. Nên ngủ riêng để xả năng lượng mượn.",
        "exercise": "Nhẹ nhàng, đều đặn (đi bộ, yoga, bơi chậm). Tránh gắng sức kéo dài.",
        "recovery": "Bitterness (đắng cay vì không được công nhận) là tín hiệu lệch - cần nghỉ + chờ lời mời đúng.",
    },
    "Manifestor": {
        "pattern": "Năng lượng dồn cục: bùng nổ hành động rồi cần nghỉ hoàn toàn. Cơ thể chịu tác động mạnh của cơn giận.",
        "risk": "Giận dữ tích tụ -> tim mạch, huyết áp, dạ dày. Bị kiểm soát/cản trở kéo dài -> suy nhược thần kinh.",
        "sleep": "Cần ngủ riêng (aura khép). Xả hết cơn giận trong ngày, đừng mang vào giấc ngủ.",
        "exercise": "Môn xả lực mạnh ngắn (võ, chạy nước rút, gym nặng) rồi nghỉ dài.",
        "recovery": "Anger là la bàn - khi giận, kiểm tra: mình đã Inform chưa? Có ai đang kiểm soát mình không?",
    },
    "Reflector": {
        "pattern": "Nhạy cảm nhất với MÔI TRƯỜNG - sức khỏe phản ánh chất lượng môi trường sống và cộng đồng xung quanh.",
        "risk": "Môi trường độc hại (người, nơi chốn, thông tin) -> bệnh không rõ nguyên nhân, rối loạn chu kỳ, trầm cảm.",
        "sleep": "Cần không gian ngủ riêng, sạch năng lượng. Sức khỏe dao động theo chu kỳ Mặt Trăng 28 ngày.",
        "exercise": "Theo chu kỳ: có ngày sung sức, có ngày cần nghỉ tuyệt đối - tôn trọng nhịp, đừng ép.",
        "recovery": "Disappointment (thất vọng về cuộc đời) = ở sai môi trường. Đổi môi trường trước khi chữa bệnh.",
    },
}

CENTER_HEALTH = {
    "Head": {
        "defined": {"strength": "Áp lực tinh thần ổn định, cảm hứng đều đặn.",
                     "blindspot": "Căng đầu kinh niên nếu ôm quá nhiều câu hỏi - đau đầu, mất ngủ do nghĩ nhiều."},
        "open": {"wisdom": "Biết câu hỏi nào đáng theo, đầu óc thoáng khi ở đúng môi trường.",
                 "vulnerable": "Hấp thụ áp lực tinh thần của người khác -> đau đầu, rối loạn, mất ngủ không phải của mình."},
    },
    "Ajna": {
        "defined": {"strength": "Tư duy khái niệm nhất quán, ít bị lung lay.",
                     "blindspot": "Cứng đầu gây stress khi thực tế khác niềm tin - căng thẳng vùng trán, xoang."},
        "open": {"wisdom": "Linh hoạt góc nhìn, đầu óc mở.",
                 "vulnerable": "Cố tỏ ra chắc chắn để được công nhận -> đau đầu, áp lực phải 'biết tuốt'."},
    },
    "Throat": {
        "defined": {"strength": "Biểu hiện mạnh, giọng nói có lực.",
                     "blindspot": "Nói/hành động quá độ -> viêm họng, tuyến giáp, khản tiếng; áp lực phải luôn 'thể hiện'."},
        "open": {"wisdom": "Linh hoạt cách biểu hiện theo hoàn cảnh.",
                 "vulnerable": "Áp lực phải nói để được chú ý -> nói quá nhiều rồi kiệt giọng, rối loạn tuyến giáp."},
    },
    "G": {
        "defined": {"strength": "Bản sắc ổn định - ít stress vì 'mình là ai'.",
                     "blindspot": "Cố chấp hướng đi sai -> stress kéo dài, ảnh hưởng gan (ức chế cảm xúc)."},
        "open": {"wisdom": "Linh hoạt vai trò, thấu hiểu nhiều kiểu người.",
                 "vulnerable": "Lạc lối, không biết mình là ai -> lo âu, trầm cảm, tìm kiếm bản thân qua người khác."},
    },
    "Heart": {
        "defined": {"strength": "Ý chí mạnh, chịu được cam kết lớn.",
                     "blindspot": "Ép ý chí quá sức -> TIM MẠCH, dạ dày, kiệt sức vì không biết dừng."},
        "open": {"wisdom": "Khôn ngoan về giá trị và cam kết - biết đủ.",
                 "vulnerable": "Cố chứng minh giá trị -> hứa bừa, làm quá sức -> BỆNH TIM, huyết áp (điểm mù sức khỏe lớn nhất của 65% dân số)."},
    },
    "Spleen": {
        "defined": {"strength": "Miễn dịch tốt, trực giác cơ thể nhanh, biết ngay cái gì hại mình.",
                     "blindspot": "Chủ quan sức khỏe vì 'cơ thể mình khỏe' - bỏ qua kiểm tra định kỳ."},
        "open": {"wisdom": "Nhạy cảm, thấu cảm nỗi sợ và bệnh tật của người khác.",
                 "vulnerable": "Bám víu điều không tốt (thuốc lá, quan hệ độc hại, việc hại sức khỏe) vì sợ thay đổi; lo âu sức khỏe không phải của mình."},
    },
    "Sacral": {
        "defined": {"strength": "Sinh lực dồi dào, sức bền tốt, tình dục khỏe.",
                     "blindspot": "Không biết khi nào đủ -> làm quá sức -> kiệt sức Sacral, rối loạn tình dục, Frustration kinh niên."},
        "open": {"wisdom": "Biết khi nào đủ, khôn ngoan về năng lượng làm việc.",
                 "vulnerable": "Không có năng lượng bền bỉ - cố đua với Generator -> suy nhược, kiệt sức, mất ngủ."},
    },
    "Solar Plexus": {
        "defined": {"strength": "Trí tuệ cảm xúc sâu, sóng cảm xúc là hệ thống định hướng.",
                     "blindspot": "Ăn theo cảm xúc, rối loạn thần kinh khi nén cảm xúc; quyết định vội trong sóng -> stress hậu quả."},
        "open": {"wisdom": "Gương cảm xúc trong - thấu cảm mà không chìm.",
                 "vulnerable": "Hấp thụ cảm xúc người khác -> lo âu, trầm cảm 'không phải của mình'; sợ đối đầu nên nén bệnh."},
    },
    "Root": {
        "defined": {"strength": "Chịu áp lực và deadline tốt, adrenaline ổn định.",
                     "blindspot": "Nghiện áp lực -> tuyến thượng thận kiệt, lúc nào cũng căng như dây đàn; tạo áp lực cho người xung quanh."},
        "open": {"wisdom": "Biết nhịp nào là đúng, không cần vội.",
                 "vulnerable": "Vội vã cho xong để xả áp lực -> sai sót, tai nạn, kiệt sức thượng thận vì luôn trong trạng thái 'chạy'."},
    },
}

HEALTH_CHANNELS = {
    (10, 20): "Tỉnh thức trong hiện tại - cơ thể khỏe khi bạn sống đúng mình, bệnh khi sống trái mình.",
    (10, 34): "Sinh lực phục vụ lẽ sống - làm điều mình tin thì khỏe, làm trái thì cơ thể phản đối ngay.",
    (10, 57): "Hình mẫu hoàn hảo - trực giác sinh tồn nhạy, cơ thể tự biết cách giữ mình (lắng nghe nó).",
    (34, 57): "Sức mạnh sinh tồn - năng lượng dồi dào cho việc sống còn, cần xả qua vận động.",
    (27, 50): "Bảo tồn & Chăm sóc - chú ý dinh dưỡng, chăm người khác nhưng đừng quên chăm mình.",
    (28, 38): "Đấu tranh - sinh lực đến từ thử thách; thiếu mục đích thì uể oải, có mục đích thì khỏe.",
    (28, 32): None, (32, 54): "Biến đổi - stress từ tham vọng leo thang; thành công cần đi cùng nghỉ ngơi.",
    (18, 58): "Phán xét & Hoàn thiện - áp lực 'chưa đủ tốt' gây stress kinh niên; học cách đủ.",
    (3, 60): "Đột biến - năng lượng thất thường (lúc bùng nổ lúc tụt); tôn trọng nhịp, đừng ép đều.",
    (39, 55): "Sóng cảm xúc mạnh - cảm xúc ảnh hưởng trực tiếp cơ thể; cần xả cảm xúc lành mạnh.",
    (19, 49): "Nhạy cảm nhu cầu - dễ ôm nhu cầu người khác thành bệnh của mình; giữ ranh giới.",
    (6, 59): "Kết đôi & Ma sát - sức khỏe tình dục và ranh giới thân mật ảnh hưởng lớn đến toàn thân.",
}

BODY_SIGNALS = [
    "Frustration (bực bội) kéo dài = Sacral đang làm việc sai -> đổi việc hoặc nghỉ.",
    "Anger (giận) bùng phát = ranh giới bị xâm phạm hoặc thiếu Inform -> xả + thiết lập lại.",
    "Bitterness (đắng cay) = cho đi không được công nhận -> dừng cho, chờ lời mời.",
    "Mất ngủ không rõ lý do = kiểm tra Head/Ajna mở (áp lực mượn) hoặc Sacral chưa xả.",
    "Đau đầu kinh niên = غالبا áp lực tinh thần mượn (Head/Ajna mở) hoặc cố chứng minh (Heart mở).",
    "Tim đập nhanh/huyết áp = Heart (chứng minh quá sức) hoặc giận nén (Manifestor/Solar).",
    "Kiệt sức dù ngủ đủ = làm trái thiết kế (việc sai, người sai, môi trường sai).",
]


def analyze_health(birth_datetime, name=""):
    # Accept a precomputed chart from the report orchestrator to avoid duplicate calculation.
    chart = birth_datetime if isinstance(birth_datetime, dict) else calculate_hd_chart(birth_datetime)
    t = chart["type"]
    defined = set(chart["defined_centers"])
    order = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
    open_c = [c for c in order if c not in defined]

    centers_health = {}
    for c in order:
        key = "defined" if c in defined else "open"
        info = CENTER_HEALTH[c][key]
        centers_health[c] = {"status": "DEFINED" if c in defined else "OPEN", **info}

    channels_health = []
    for g1, g2 in chart["defined_channels"]:
        key = (g1, g2) if (g1, g2) in HEALTH_CHANNELS else (g2, g1)
        desc = HEALTH_CHANNELS.get(key)
        if desc:
            channels_health.append({"channel": f"{g1}-{g2}", "health": desc})
        else:
            channels_health.append({"channel": f"{g1}-{g2}",
                                    "health": f"{GATE_MEANINGS.get(g1, '')} + {GATE_MEANINGS.get(g2, '')} - năng lượng ổn định, ít rủi ro sức khỏe trực tiếp."})

    type_h = TYPE_HEALTH[t]
    vuln = [f"{c}: {centers_health[c].get('vulnerable', centers_health[c].get('blindspot', ''))}" for c in open_c]
    practice_7d = [
        f"Ngày 1-2: Ghi nhật ký năng lượng - khi nào sung mãn, khi nào tụt? (theo dõi {t}).",
        "Ngày 3-4: Thử nghiệm giấc ngủ đúng thiết kế: " + type_h["sleep"],
        "Ngày 5: Vận động xả đúng kiểu: " + type_h["exercise"],
        "Ngày 6: Quan sát 1 tín hiệu cơ thể trong BODY_SIGNALS và truy nguyên nhân.",
        "Ngày 7: Tổng kết - điều gì cho năng lượng, điều gì rút năng lượng? Lên kế hoạch tuần mới.",
    ]
    summary = (f"{name or 'Bạn'} là {t}: {type_h['pattern']} Rủi ro lớn nhất: {type_h['risk']} "
               f"Trung tâm cần chăm nhất: {', '.join(open_c)} (mở - dễ hấp thụ) + chú ý điểm mù của {len(defined)} trung tâm định nghĩa.")

    return {
        "name": name, "birth_datetime": str(chart["birth_datetime"]),
        "type": t, "profile": chart["profile"], "authority": chart["authority"],
        "definition": chart["definition"],
        "defined_centers": sorted(defined), "open_centers": open_c,
        "health_analysis": {
            "type_health": type_h,
            "centers_health": centers_health,
            "channels_health": channels_health,
            "vulnerabilities": vuln,
            "body_signals": BODY_SIGNALS,
            "practice_7d": practice_7d,
            "summary": summary,
        },
        "áp_dụng_cho": "100% dân số - 60 biến thể (5 Types x 12 Profiles)",
    }


def format_health_report(d):
    h = d["health_analysis"]
    L = [f"# BÁO CÁO SỨC KHỎE THÂN-TÂM-TRÍ - {d['name']} - {d['type']} {d['profile']}",
         f"**Type:** {d['type']} | **Profile:** {d['profile']} | **Authority:** {d['authority']}",
         f"**Trung tâm mở (cần chăm):** {', '.join(h['open_centers'] if 'open_centers' in h else d['open_centers'])}",
         "",
         "## 1. QUY LUẬT SỨC KHỎE THEO TYPE",
         f"**Quy luật:** {h['type_health']['pattern']}",
         f"**Rủi ro lớn nhất:** {h['type_health']['risk']}",
         f"**Giấc ngủ:** {h['type_health']['sleep']}",
         f"**Vận động:** {h['type_health']['exercise']}",
         f"**Phục hồi:** {h['type_health']['recovery']}",
         "",
         "## 2. SỨC KHỎE 9 TRUNG TÂM",
         "### Định nghĩa - Điểm mạnh & điểm mù sức khỏe:"]
    for c, info in h["centers_health"].items():
        if info["status"] == "DEFINED":
            L.append(f"- **{c} (Defined):** Mạnh: {info['strength']} | Điểm mù: {info['blindspot']}")
    L.append("### Mở - Trí tuệ & vùng dễ tổn thương:")
    for c, info in h["centers_health"].items():
        if info["status"] == "OPEN":
            L.append(f"- **{c} (Open):** Trí tuệ: {info['wisdom']} | Dễ tổn thương: {info['vulnerable']}")
    L += ["", "## 3. KÊNH & SỨC KHỎE"]
    for ch in h["channels_health"]:
        L.append(f"- **Kênh {ch['channel']}:** {ch['health']}")
    L += ["", "## 4. 7 TÍN HIỆU CƠ THỂ CẦN NGHE"]
    for s in h["body_signals"]:
        L.append(f"- {s}")
    L += ["", "## 5. THỰC HÀNH 7 NGÀY"]
    for i, p in enumerate(h["practice_7d"], 1):
        L.append(f"{i}. {p}")
    L += ["", "## 6. KẾT LUẬN", h["summary"], "",
          "> \"Cơ thể không bao giờ nói dối - Mind mới là kẻ nói dối\"",
          "> \"Kiệt sức là tín hiệu lệch thiết kế, không phải huy chương\""]
    return "\n".join(L)
