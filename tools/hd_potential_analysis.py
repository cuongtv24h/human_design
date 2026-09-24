"""
Human Design Potential & Blind Spots Analysis Tool
Phân tích Tiềm năng & Điểm mù - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn - Lựa chọn hành vi cải thiện bản thân

Dựa trên ý kiến thực tế:
- Điểm mù bản thân, điểm yếu - điểm mạnh
- Quan sát mình dưới các góc nhìn khác nhau
- Lựa chọn hành vi phù hợp nhất để cải thiện bản thân

Tích hợp từ:
- 02_9_trung_tam.md: 9 Centers Defined/Undefined
- 03_36_kenh.md: 36 Channels - Tài năng cố định
- 01_mandala_64_cong.md: 64 Gates - Tiềm năng
- 04_5_loai_va_chien_luoc.md: Type Strategy
- 05_profile_cross_definition.md: Profile, Cross, Definition
- 09_tam_ly_so_hai_co_che_tri_oc.md: Fear Gates 19 cổng
- 12_tham_van_tong_quat_60_bien_the.md: Type deep dive
"""

from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER, CHANNEL_TO_CENTERS, CHANNELS, GATE_ORDER
from hd_consultation_general import TYPE_DEEP_DIVE, PROFILE_DEEP_DIVE
from hd_advanced_tools import analyze_fear_gates
from datetime import datetime

# 9 Centers Not-Self vs Wisdom - Điểm mù vs Trí tuệ
CENTER_BLINDSPOTS = {
    "Head": {
        "defined": {"strength": "Áp lực tinh thần cố định, luôn có câu hỏi, cảm hứng trong đầu. Bạn truyền cảm hứng cho người khác.", "blindspot": "Cố gắng trả lời mọi câu hỏi, áp lực phải có câu trả lời, truyền cảm hứng không đúng lúc."},
        "undefined": {"strength": "Trí tuệ: Biết câu hỏi nào đáng giá để theo đuổi. Cởi mở với cảm hứng và câu hỏi đa dạng.", "blindspot": "Điểm mù: Bị áp lực bởi câu hỏi của người khác, cảm thấy phải trả lời mọi câu hỏi, áp lực tinh thần không phải của mình. Not-Self: Cố gắng trả lời mọi câu hỏi để giảm áp lực."}
    },
    "Ajna": {
        "defined": {"strength": "Cách suy nghĩ cố định, đáng tin cậy. Có quan điểm riêng, chắc chắn.", "blindspot": "Cố chứng minh mình chắc chắn, cố thuyết phục người khác, không linh hoạt quan điểm."},
        "undefined": {"strength": "Trí tuệ: Thấy được nhiều góc nhìn, khôn ngoan về tư duy, linh hoạt quan điểm.", "blindspot": "Điểm mù: Không cần phải chắc chắn nhưng cố gắng chắc chắn để được công nhận, bị điều kiện hóa phải có quan điểm cố định. Not-Self: Cố chứng minh mình chắc chắn, sợ không chắc chắn."}
    },
    "Throat": {
        "defined": {"strength": "Có cách biểu hiện cố định, dễ thu hút sự chú ý. Lời nói/hành động có trọng lượng.", "blindspot": "Nói quá nhiều, thu hút chú ý không đúng lúc, lời nói có trọng lượng nên cần cẩn thận."},
        "undefined": {"strength": "Trí tuệ: Biết khi nào nên nói, khôn ngoan về biểu hiện, thu hút chú ý đúng lúc.", "blindspot": "Điểm mù: Áp lực phải nói, thu hút chú ý, nói để được công nhận, nói không đúng lúc. Not-Self: Cố gắng nói, thu hút chú ý để được công nhận."}
    },
    "G": {
        "defined": {"strength": "Bản sắc, tình yêu, phương hướng cố định. Bạn biết mình là ai, yêu ai, đi đâu.", "blindspot": "Cố định về bản sắc, tình yêu, phương hướng, khó linh hoạt."},
        "undefined": {"strength": "Trí tuệ: Biết nơi nào, ai là đúng. Khôn ngoan về bản sắc, tình yêu, phương hướng. Linh hoạt về bản sắc.", "blindspot": "Điểm mù: Linh hoạt về bản sắc nhưng cảm thấy lạc lối, tìm kiếm tình yêu và phương hướng, dễ cảm thấy không biết mình là ai. Not-Self: Tìm kiếm tình yêu và phương hướng từ người khác, cảm thấy lạc lối."}
    },
    "Heart": {
        "defined": {"strength": "Ý chí mạnh, có thể giữ lời hứa, động lực vật chất, có thể cam kết.", "blindspot": "Ép ý chí quá mức, hứa hẹn quá mức, vấn đề tim mạch, dạ dày nếu ép ý chí."},
        "undefined": {"strength": "Trí tuệ: Khôn ngoan về tiền bạc, giá trị, cam kết. Biết ai có ý chí tốt, linh hoạt về giá trị.", "blindspot": "Điểm mù lớn nhất cho 65% dân số: Không có ý chí cố định nhưng cố chứng minh giá trị qua tiền, hứa hẹn bừa bãi để chứng minh, làm việc quá sức để chứng minh giá trị, dễ bị lợi dụng về tiền. Not-Self: Cố chứng minh giá trị, hứa bừa, làm việc quá sức để chứng minh."}
    },
    "Spleen": {
        "defined": {"strength": "Trực giác tức thì, hệ miễn dịch mạnh, nỗi sợ cố định. Trực giác nói 1 lần, khẽ.", "blindspot": "Bỏ qua trực giác tức thì, nỗi sợ cố định, trực giác nói khẽ nên dễ bỏ qua."},
        "undefined": {"strength": "Trí tuệ: Khôn ngoan về sức khỏe, trực giác, nỗi sợ. Nhạy cảm với nỗi sợ, thấu cảm.", "blindspot": "Điểm mù: Nhạy cảm với nỗi sợ, dễ bám víu vào nỗi sợ, bám víu vào điều không tốt cho sức khỏe, sợ hãi không phải của mình. Not-Self: Bám víu vào nỗi sợ, bám víu vào điều không tốt cho sức khỏe."}
    },
    "Sacral": {
        "defined": {"strength": "Có năng lượng sống bền bỉ, năng lượng tình dục mạnh, có thể làm việc bền bỉ nếu làm việc yêu thích.", "blindspot": "Không biết khi nào đủ, làm việc quá sức, kiệt sức Sacral nếu làm việc không yêu thích, Frustration."},
        "undefined": {"strength": "Trí tuệ: Biết ai có năng lượng tốt, khôn ngoan về công việc, năng lượng. Không có năng lượng bền bỉ là trí tuệ.", "blindspot": "Điểm mù: Không có năng lượng bền bỉ nhưng cố làm việc như Generator 8h, không biết khi nào đủ, dễ kiệt sức nếu cố làm như Generator. Not-Self: Cố làm việc như Generator, không biết khi nào đủ, kiệt sức."}
    },
    "Solar Plexus": {
        "defined": {"strength": "Sóng cảm xúc cố định, trí tuệ cảm xúc, không có sự thật trong khoảnh khắc, cần chờ sự rõ ràng theo thời gian.", "blindspot": "Cảm xúc chi phối, không có sự thật trong khoảnh khắc nhưng cố quyết định trong khoảnh khắc, sóng cảm xúc ảnh hưởng người khác."},
        "undefined": {"strength": "Trí tuệ: Thấu cảm cực mạnh, khôn ngoan về cảm xúc, cảm nhận cảm xúc người khác sâu sắc.", "blindspot": "Điểm mù: Tránh đối đầu, né tránh sự thật, hấp thụ cảm xúc người khác, cảm xúc không phải của mình, sợ đối đầu. Not-Self: Tránh đối đầu, né tránh sự thật, hấp thụ cảm xúc người khác."}
    },
    "Root": {
        "defined": {"strength": "Xử lý áp lực cố định, có thể chịu stress, áp lực, adrenaline.", "blindspot": "Áp lực cố định, có thể chịu stress nhưng cũng tạo áp lực cho người khác."},
        "undefined": {"strength": "Trí tuệ: Khôn ngoan về áp lực, thời gian, biết áp lực nào đáng giá.", "blindspot": "Điểm mù: Bị áp lực phải làm nhanh cho xong, vội vã, áp lực không phải của mình, làm nhanh để giảm áp lực. Not-Self: Vội vã, làm nhanh cho xong để giảm áp lực."}
    }
}

# Channels as talents - Điểm mạnh tài năng cố định
# Using existing CHANNELS but with talent description

# Profile as perspective - Góc nhìn
PROFILE_PERSPECTIVES = {
    "1/3": {"perspective": "Investigator/Martyr - Góc nhìn nghiên cứu thử sai", "strength": "Nghiên cứu sâu, nền tảng vững chắc, học qua thử và sai, thích nghi, hài hước, an toàn từ kiến thức", "blindspot": "Sợ không đủ kiến thức, trì hoãn, thử sai có thể va chạm, cần an toàn"},
    "1/4": {"perspective": "Investigator/Opportunist - Góc nhìn nghiên cứu cơ hội", "strength": "Nền tảng vững chắc + mạng lưới bạn bè, ảnh hưởng qua người quen, bạn bè là chìa khóa", "blindspot": "Cần cân bằng giữa nghiên cứu và mạng lưới, có thể phụ thuộc bạn bè"},
    "2/4": {"perspective": "Hermit/Opportunist - Góc nhìn ẩn sĩ cơ hội", "strength": "Tài năng tự nhiên, cần ở một mình để phát triển, được gọi ra qua mạng lưới, cân bằng ẩn dật và kết nối", "blindspot": "Không biết mình có tài năng, cần người khác gọi ra, ngại kết nối"},
    "2/5": {"perspective": "Hermit/Heretic - Góc nhìn ẩn sĩ dị giáo", "strength": "Tài năng tự nhiên + giải pháp thực tế, cần ở một mình", "blindspot": "Bị chiếu rọi kỳ vọng lớn, cần biên giới với kỳ vọng"},
    "3/5": {"perspective": "Martyr/Heretic - Góc nhìn tử vì đạo dị giáo", "strength": "Thử và sai, va chạm lớn, mang giải pháp thực tế cứu người, học qua thất bại", "blindspot": "Va chạm lớn, thử sai có thể mất mát, bị kỳ vọng cứu người"},
    "3/6": {"perspective": "Martyr/Role Model - Góc nhìn tử vì đạo hình mẫu", "strength": "3 giai đoạn cuộc đời: 0-30 thử sai, 30-50 quan sát trên mái nhà, 50+ hình mẫu", "blindspot": "Giai đoạn đầu thử sai nhiều, cần thời gian để trở thành hình mẫu"},
    "4/6": {"perspective": "Opportunist/Role Model - Góc nhìn cơ hội hình mẫu", "strength": "Mạng lưới bạn bè + quan sát để trở thành hình mẫu", "blindspot": "Cần cân bằng giữa mạng lưới và quan sát"},
    "4/1": {"perspective": "Opportunist/Investigator - Góc nhìn cơ hội điều tra - Hiếm 2% - Định mệnh cố định", "strength": "Định mệnh cố định, không thể bị ảnh hưởng, một con đường duy nhất, cần nền tảng vững chắc để ảnh hưởng người khác", "blindspot": "Định mệnh cố định, không linh hoạt, có thể cô đơn về đường đi"},
    "5/1": {"perspective": "Heretic/Investigator - Góc nhìn dị giáo điều tra", "strength": "Giải pháp thực tế có nền tảng, bị kỳ vọng lớn, cứu người", "blindspot": "Bị kỳ vọng lớn, chiếu rọi, cần nền tảng vững chắc để đáp ứng kỳ vọng"},
    "5/2": {"perspective": "Heretic/Hermit - Góc nhìn dị giáo ẩn sĩ", "strength": "Giải pháp thực tế + tài năng tự nhiên, cần ở một mình", "blindspot": "Cần cân bằng giữa giải pháp thực tế và ở một mình, bị kỳ vọng"},
    "6/2": {"perspective": "Role Model/Hermit - Góc nhìn hình mẫu ẩn sĩ", "strength": "3 giai đoạn, tài năng tự nhiên, quan sát rồi hình mẫu sau 50, cần ở một mình", "blindspot": "Giai đoạn đầu thử sai, cần ở một mình, tỏa sáng sau 50"},
    "6/3": {"perspective": "Role Model/Martyr - Góc nhìn hình mẫu tử vì đạo", "strength": "3 giai đoạn, thử sai để trở thành hình mẫu, quan sát và thử nghiệm", "blindspot": "Thử sai để trở thành hình mẫu, cần thời gian"}
}

def analyze_potential_blindspots(birth_datetime, name=""):
    """Phân tích Tiềm năng & Điểm mù - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn"""
    chart = calculate_hd_chart(birth_datetime) if isinstance(birth_datetime, datetime) else birth_datetime
    
    hd_type = chart["type"]
    profile = chart["profile"]
    authority = chart["authority"]
    defined_centers = chart["defined_centers"]
    defined_channels = chart["defined_channels"]
    all_gates = chart["all_activated_gates"]
    definition = chart["definition"]
    incarnation_cross = chart["incarnation_cross"]
    
    # All centers
    all_centers = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
    undefined_centers = [c for c in all_centers if c not in defined_centers]
    
    # Strengths - Defined centers
    strengths_centers = []
    for center in defined_centers:
        info = CENTER_BLINDSPOTS.get(center, {})
        defined_info = info.get("defined", {})
        strengths_centers.append({
            "center": center,
            "strength": defined_info.get("strength", ""),
            "blindspot": defined_info.get("blindspot", ""),
            "type": "Defined - Điểm mạnh cố định"
        })
    
    # Blind spots - Undefined centers
    blindspots_centers = []
    for center in undefined_centers:
        info = CENTER_BLINDSPOTS.get(center, {})
        undefined_info = info.get("undefined", {})
        blindspots_centers.append({
            "center": center,
            "strength": undefined_info.get("strength", ""),  # Wisdom
            "blindspot": undefined_info.get("blindspot", ""),
            "type": "Undefined/Open - Điểm mù + Trí tuệ"
        })
    
    # Strengths - Defined channels (talents)
    strengths_channels = []
    for ch in defined_channels:
        if isinstance(ch, (list, tuple)):
            g1, g2 = ch[0], ch[1]
            centers = CHANNEL_TO_CENTERS.get((g1,g2)) or CHANNEL_TO_CENTERS.get((g2,g1)) or "Unknown"
            strengths_channels.append({
                "channel": f"{g1}-{g2}",
                "gates": [g1,g2],
                "centers": centers,
                "talent": f"Tài năng cố định: {GATE_MEANINGS.get(g1,'')} + {GATE_MEANINGS.get(g2,'')} = Kênh {g1}-{g2}",
                "type": "Defined Channel - Tài năng cố định"
            })
    
    # Potential - Hanging gates (gates not in defined channels)
    defined_gates = set()
    for ch in defined_channels:
        if isinstance(ch, (list, tuple)):
            defined_gates.add(ch[0])
            defined_gates.add(ch[1])
    
    hanging_gates = [g for g in all_gates if g not in defined_gates]
    potential_gates = []
    for gate in hanging_gates:
        potential_gates.append({
            "gate": gate,
            "meaning": GATE_MEANINGS.get(gate, ""),
            "center": GATE_TO_CENTER.get(gate, ""),
            "potential": f"Tiềm năng treo: {GATE_MEANINGS.get(gate,'')} tại {GATE_TO_CENTER.get(gate,'')} - Cần người có cổng đối diện để tạo thành kênh tài năng",
            "type": "Hanging Gate - Tiềm năng chưa kết nối"
        })
    
    # Fear gates - Blind spots from fears
    try:
        fear_data = analyze_fear_gates(birth_datetime)
        fear_gates = fear_data.get("fear_gates", [])
        fear_summary = fear_data.get("summary", "")
    except:
        fear_gates = []
        fear_summary = "Không có data fear"
    
    # Profile perspective
    profile_perspective = PROFILE_PERSPECTIVES.get(profile, {})
    
    # Type perspective
    type_perspective = TYPE_DEEP_DIVE.get(hd_type, {})
    
    # Multiple perspectives - 9 centers + Type + Profile as different angles
    perspectives = []
    perspectives.append({"angle": f"Type {hd_type}", "description": f"Góc nhìn năng lượng: {type_perspective.get('aura','')[:150]}", "type": "Type Perspective"})
    perspectives.append({"angle": f"Profile {profile}", "description": profile_perspective.get("perspective","") + " - " + profile_perspective.get("strength","")[:150], "type": "Profile Perspective"})
    for center in all_centers:
        is_defined = center in defined_centers
        info = CENTER_BLINDSPOTS.get(center, {})
        perspective_info = info.get("defined" if is_defined else "undefined", {})
        perspectives.append({
            "angle": f"Center {center} ({'Defined' if is_defined else 'Open'})",
            "description": perspective_info.get("strength","")[:150] + " | Blindspot: " + perspective_info.get("blindspot","")[:100],
            "type": f"Center Perspective - {'Điểm mạnh' if is_defined else 'Điểm mù + Trí tuệ'}"
        })
    
    # Appropriate behavior - Strategy + Authority
    type_strategy = type_perspective.get("strategy", {})
    appropriate_behavior = {
        "strategy": {
            "name": type_strategy.get("name",""),
            "description": type_strategy.get("description",""),
            "practice": type_strategy.get("practice",""),
            "type": f"Strategy cho {hd_type}"
        },
        "authority": {
            "name": authority,
            "description": f"Authority {authority} - Cách ra quyết định đúng cho bạn",
            "type": "Authority - Ra quyết định"
        },
        "not_self_mind": "Tâm trí (Mind) KHÔNG BAO GIỜ là Authority - Mind để đo lường, không phải ra quyết định - Bẫy lớn nhất là để Mind ra quyết định thay vì Authority",
        "deconditioning": {
            "7_days": f"Thử nghiệm 7 ngày với Strategy: {chart['strategy']} + Authority: {authority}",
            "7_months": f"Quan sát {len(undefined_centers)} Open Centers - Nơi bạn học trí tuệ, không phải ra quyết định: {', '.join(undefined_centers)}",
            "7_years": "Deconditioning 7 năm - Giải điều kiện hóa, tế bào thay mới hoàn toàn (chu kỳ Uranus)"
        }
    }
    
    result = {
        "name": name,
        "birth_datetime": str(chart["birth_datetime"]),
        "type": hd_type,
        "profile": profile,
        "authority": authority,
        "definition": definition,
        "incarnation_cross": incarnation_cross,
        "defined_centers": defined_centers,
        "undefined_centers": undefined_centers,
        "potential_analysis": {
            "strengths": {
                "centers": strengths_centers,
                "channels": strengths_channels,
                "count_centers": len(strengths_centers),
                "count_channels": len(strengths_channels),
                "summary": f"Bạn có {len(strengths_centers)} trung tâm định nghĩa (điểm mạnh cố định) và {len(strengths_channels)} kênh định nghĩa (tài năng cố định)"
            },
            "blindspots": {
                "centers": blindspots_centers,
                "hanging_gates": potential_gates,
                "fear_gates": fear_gates,
                "fear_summary": fear_summary,
                "count_centers": len(blindspots_centers),
                "count_hanging_gates": len(potential_gates),
                "summary": f"Bạn có {len(blindspots_centers)} trung tâm mở (điểm mù + trí tuệ) và {len(potential_gates)} cổng treo (tiềm năng chưa kết nối) và {len(fear_gates) if isinstance(fear_gates, list) else 0} cổng sợ hãi (điểm mù sợ hãi)"
            },
            "perspectives": {
                "list": perspectives,
                "count": len(perspectives),
                "summary": f"Bạn có {len(perspectives)} góc nhìn khác nhau về bản thân: 1 Type + 1 Profile + 9 Centers = 11 góc nhìn"
            },
            "profile_perspective": profile_perspective,
            "type_perspective": {"aura": type_perspective.get("aura",""), "psychology": type_perspective.get("psychology",[])},
            "appropriate_behavior": appropriate_behavior
        },
        "áp_dụng_cho": "100% dân số - Phân tích Tiềm năng & Điểm mù - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn - Lựa chọn hành vi phù hợp"
    }
    
    return result

def format_potential_report(potential_data):
    """Format báo cáo Tiềm năng & Điểm mù"""
    lines = []
    lines.append(f"# TIỀM NĂNG & ĐIỂM MÙ - BẢN ĐỒ ĐA GÓC NHÌN - {potential_data.get('name','')} - {potential_data['type']} {potential_data['profile']}")
    lines.append(f"**Type:** {potential_data['type']} | **Profile:** {potential_data['profile']} | **Authority:** {potential_data['authority']} | **Definition:** {potential_data['definition']}")
    lines.append(f"**Defined Centers:** {len(potential_data['defined_centers'])} | **Open Centers:** {len(potential_data['undefined_centers'])} | **Cross:** {potential_data['incarnation_cross']}")
    lines.append("")
    
    # Strengths
    pa = potential_data["potential_analysis"]
    lines.append(f"## 1. ĐIỂM MẠNH - TÀI NĂNG CỐ ĐỊNH - STRENGTHS")
    lines.append(f"{pa['strengths']['summary']}")
    lines.append("")
    lines.append(f"### Trung tâm định nghĩa - Điểm mạnh cố định ({pa['strengths']['count_centers']}):")
    for center in pa["strengths"]["centers"]:
        lines.append(f"- **{center['center']} (Defined):** {center['strength']}")
        lines.append(f"  - Blindspot của điểm mạnh: {center['blindspot']}")
    lines.append("")
    lines.append(f"### Kênh định nghĩa - Tài năng cố định ({pa['strengths']['count_channels']}):")
    for ch in pa["strengths"]["channels"]:
        lines.append(f"- **Kênh {ch['channel']} ({ch['centers']}):** {ch['talent']}")
    lines.append("")
    
    # Blindspots
    lines.append(f"## 2. ĐIỂM MÙ & TIỀM NĂNG - BLIND SPOTS & POTENTIAL")
    lines.append(f"{pa['blindspots']['summary']}")
    lines.append("")
    lines.append(f"### Trung tâm mở - Điểm mù + Trí tuệ ({pa['blindspots']['count_centers']}):")
    for center in pa["blindspots"]["centers"]:
        lines.append(f"- **{center['center']} (Open):**")
        lines.append(f"  - **Trí tuệ (Wisdom):** {center['strength']}")
        lines.append(f"  - **Điểm mù (Blindspot/Not-Self):** {center['blindspot']}")
    lines.append("")
    lines.append(f"### Cổng treo - Tiềm năng chưa kết nối ({pa['blindspots']['count_hanging_gates']}):")
    for gate in pa["blindspots"]["hanging_gates"][:10]:  # Show first 10
        lines.append(f"- **Gate {gate['gate']} ({gate['center']}):** {gate['meaning']} - {gate['potential'][:100]}")
    if len(pa["blindspots"]["hanging_gates"]) > 10:
        lines.append(f"- ... và {len(pa['blindspots']['hanging_gates'])-10} cổng treo khác")
    lines.append("")
    lines.append(f"### Cổng sợ hãi - Điểm mù sợ hãi:")
    lines.append(f"{pa['blindspots']['fear_summary']}")
    lines.append("")
    
    # Perspectives
    lines.append(f"## 3. QUAN SÁT ĐA GÓC NHÌN - MULTIPLE PERSPECTIVES ({pa['perspectives']['count']} góc nhìn)")
    lines.append(f"{pa['perspectives']['summary']}")
    lines.append("")
    lines.append(f"Bạn có thể quan sát mình dưới {pa['perspectives']['count']} góc nhìn khác nhau:")
    for pers in pa["perspectives"]["list"]:
        lines.append(f"- **{pers['angle']} ({pers['type']}):** {pers['description'][:150]}")
    lines.append("")
    lines.append(f"### Góc nhìn Profile - {potential_data['profile']}:")
    pp = pa["profile_perspective"]
    lines.append(f"- **Perspective:** {pp.get('perspective','')}")
    lines.append(f"- **Strength:** {pp.get('strength','')}")
    lines.append(f"- **Blindspot:** {pp.get('blindspot','')}")
    lines.append("")
    lines.append(f"### Góc nhìn Type - {potential_data['type']}:")
    tp = pa["type_perspective"]
    lines.append(f"- **Aura:** {tp.get('aura','')}")
    lines.append(f"- **Psychology:**")
    for psy in tp.get("psychology", [])[:3]:
        lines.append(f"  - {psy}")
    lines.append("")
    
    # Appropriate behavior
    lines.append(f"## 4. LỰA CHỌN HÀNH VI PHÙ HỢP - APPROPRIATE BEHAVIOR - Cải thiện bản thân")
    ab = pa["appropriate_behavior"]
    lines.append(f"### Strategy - {ab['strategy']['name']} (cho {potential_data['type']}):")
    lines.append(f"- **Mô tả:** {ab['strategy']['description']}")
    lines.append(f"- **Thực hành:** {ab['strategy']['practice']}")
    lines.append("")
    lines.append(f"### Authority - {ab['authority']['name']}:")
    lines.append(f"- {ab['authority']['description']}")
    lines.append("")
    lines.append(f"### Not-Self Mind - Bẫy lớn nhất:")
    lines.append(f"{ab['not_self_mind']}")
    lines.append("")
    lines.append(f"### Lộ trình thực hành:")
    lines.append(f"- **7 ngày:** {ab['deconditioning']['7_days']}")
    lines.append(f"- **7 tháng:** {ab['deconditioning']['7_months']}")
    lines.append(f"- **7 năm:** {ab['deconditioning']['7_years']}")
    lines.append("")
    
    lines.append(f"## 5. KẾT LUẬN - Hiểu mình qua đa góc nhìn để cải thiện")
    lines.append(f"Bạn là {potential_data['type']} {potential_data['profile']} - Có {pa['strengths']['count_centers']} điểm mạnh cố định (Defined Centers) + {pa['strengths']['count_channels']} tài năng cố định (Defined Channels) + {pa['blindspots']['count_centers']} điểm mù + trí tuệ (Open Centers) + {pa['blindspots']['count_hanging_gates']} tiềm năng treo")
    lines.append(f"Bạn có {pa['perspectives']['count']} góc nhìn khác nhau về bản thân - Hãy quan sát mình dưới các góc nhìn này")
    lines.append(f"Hành vi phù hợp nhất để cải thiện bản thân là sống đúng Strategy: {potential_data['type']} - {ab['strategy']['name']} và Authority: {ab['authority']['name']}")
    lines.append(f"Hãy thử nghiệm 7 ngày và quan sát")
    lines.append("")
    lines.append(f"> \"Hiểu mình - Sống là mình\"")
    lines.append(f"> \"Không có chart xấu - mỗi thiết kế có mục đích\"")
    lines.append(f"> \"Điểm mù không phải điểm yếu - Open Centers là nơi bạn học trí tuệ\"")
    lines.append(f"> \"Đừng tin, hãy thử nghiệm\" - Ra Uru Hu")
    
    return "\n".join(lines)

# Test
if __name__ == "__main__":
    dt = datetime(1990, 5, 15, 1, 30)
    data = analyze_potential_blindspots(dt, name="Test User")
    print(format_potential_report(data)[:8000])
