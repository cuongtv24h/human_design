"""
Human Design Deep Analyzer - Phân tích chuyên sâu
Sử dụng kết quả từ hd_calculator để tạo báo cáo phân tích chi tiết bằng tiếng Việt
"""

from hd_calculator import (
    calculate_hd_chart, format_chart_text,
    GATE_MEANINGS, GATE_TO_CENTER, CHANNEL_TO_CENTERS, GATE_ORDER
)
from hd_language import vn_authority, vn_center, vn_definition, vn_strategy, vn_type
from datetime import datetime
import json

# Ý nghĩa chi tiết các trung tâm mở/định nghĩa
CENTER_ANALYSIS = {
    "Head": {
        "defined": "Bạn có áp lực tinh thần cố định. Luôn có câu hỏi, cảm hứng trong đầu. Bạn truyền cảm hứng cho người khác nhưng cần học cách phân biệt câu hỏi nào là của mình.",
        "undefined": "Bạn cởi mở với cảm hứng và câu hỏi. Bạn dễ bị áp lực bởi câu hỏi của người khác. Bài học: Không cần trả lời mọi câu hỏi. Trí tuệ: Biết câu hỏi nào đáng giá để theo đuổi."
    },
    "Ajna": {
        "defined": "Cách suy nghĩ cố định, đáng tin cậy. Bạn có quan điểm riêng. Thách thức: Cố chứng minh mình chắc chắn.",
        "undefined": "Tư duy linh hoạt, cởi mở nhiều quan điểm. Không cần phải chắc chắn. Trí tuệ: Thấy được nhiều góc nhìn, khôn ngoan về tư duy."
    },
    "Throat": {
        "defined": "Có cách biểu hiện cố định, dễ thu hút sự chú ý. Lời nói/hành động có trọng lượng.",
        "undefined": "Áp lực phải nói, thu hút chú ý. Bài học: Nói khi được công nhận, đúng thời điểm. Trí tuệ: Biết khi nào nên nói."
    },
    "G": {
        "defined": "Bản sắc, tình yêu, phương hướng cố định. Bạn biết mình là ai, yêu ai, đi đâu.",
        "undefined": "Linh hoạt về bản sắc, tìm kiếm tình yêu và phương hướng. Dễ cảm thấy lạc lối. Trí tuệ: Biết nơi nào, ai là đúng. Khôn ngoan về bản sắc."
    },
    "Heart": {
        "defined": "Ý chí mạnh, có thể giữ lời hứa, động lực vật chất. Cần sử dụng ý chí đúng cách.",
        "undefined": "Không có ý chí cố định, không nên hứa bừa, không cố chứng minh giá trị. Trí tuệ: Khôn ngoan về tiền bạc, giá trị, cam kết."
    },
    "Spleen": {
        "defined": "Trực giác tức thì, hệ miễn dịch mạnh, nỗi sợ cố định. Trực giác nói 1 lần, khẽ.",
        "undefined": "Nhạy cảm với nỗi sợ, dễ bám víu. Trí tuệ: Khôn ngoan về sức khỏe, trực giác, nỗi sợ."
    },
    "Sacral": {
        "defined": "Có năng lượng sống bền bỉ. Cần đáp ứng đúng, nếu không sẽ thất vọng. Năng lượng tình dục mạnh.",
        "undefined": "Không có năng lượng bền bỉ, không biết khi nào đủ. Dễ kiệt sức nếu cố làm như Generator. Trí tuệ: Biết ai có năng lượng tốt, khôn ngoan về công việc."
    },
    "Solar Plexus": {
        "defined": "Sóng cảm xúc cố định. Không có sự thật trong khoảnh khắc. Cần chờ sự rõ ràng theo thời gian. Trí tuệ cảm xúc.",
        "undefined": "Tránh đối đầu, né tránh sự thật, hấp thụ cảm xúc người khác. Trí tuệ: Thấu cảm cực mạnh, khôn ngoan về cảm xúc."
    },
    "Root": {
        "defined": "Xử lý áp lực cố định, có thể chịu stress.",
        "undefined": "Bị áp lực phải làm nhanh cho xong, vội vã. Trí tuệ: Khôn ngoan về áp lực, thời gian."
    }
}

# Ý nghĩa 12 Profile chi tiết
PROFILE_ANALYSIS = {
    "1/3": "Investigator/Martyr - Người nghiên cứu thử sai. Bạn cần nền tảng vững chắc, nghiên cứu sâu trước khi hành động. Cuộc đời là thử và sai để tìm ra sự thật. Bạn học qua va chạm. An toàn đến từ kiến thức.",
    "1/4": "Investigator/Opportunist - Nghiên cứu cơ hội. Cần nền tảng vững chắc để chia sẻ với mạng lưới bạn bè. Ảnh hưởng qua người quen. Bạn bè là chìa khóa.",
    "2/4": "Hermit/Opportunist - Ẩn sĩ cơ hội. Bạn có tài năng tự nhiên, cần ở một mình để phát triển, rồi được gọi ra qua mạng lưới. Cân bằng giữa ẩn dật và kết nối.",
    "2/5": "Hermit/Heretic - Ẩn sĩ dị giáo. Tài năng tự nhiên nhưng bị người khác chiếu rọi kỳ vọng. Cần ở một mình, cẩn thận với sự chiếu rọi.",
    "3/5": "Martyr/Heretic - Tử vì đạo dị giáo. Cuộc đời thử và sai, va chạm lớn, nhưng để cứu người, mang giải pháp thực tế. Bạn học qua thất bại.",
    "3/6": "Martyr/Role Model - Tử vì đạo hình mẫu. 3 giai đoạn cuộc đời: 0-30 thử sai, 30-50 quan sát trên mái nhà, 50+ làm hình mẫu. Cuộc đời là hành trình trở thành hình mẫu qua thử sai.",
    "4/6": "Opportunist/Role Model - Cơ hội hình mẫu. Ảnh hưởng qua mạng lưới bạn bè, cần quan sát để trở thành hình mẫu. Bạn bè và quan sát.",
    "4/1": "Opportunist/Investigator - Cơ hội điều tra. Profile hiếm, định mệnh cố định (Juxtaposition). Bạn không thể bị ảnh hưởng, cần nền tảng vững chắc để ảnh hưởng người khác. Một con đường duy nhất.",
    "5/1": "Heretic/Investigator - Dị giáo điều tra. Người mang giải pháp thực tế có nền tảng. Bị kỳ vọng lớn, chiếu rọi. Cần nền tảng vững chắc để đáp ứng kỳ vọng.",
    "5/2": "Heretic/Hermit - Dị giáo ẩn sĩ. Giải pháp thực tế + tài năng tự nhiên. Cần ở một mình, cẩn thận với kỳ vọng của người khác.",
    "6/2": "Role Model/Hermit - Hình mẫu ẩn sĩ. 3 giai đoạn, tài năng tự nhiên, quan sát rồi trở thành hình mẫu. Cần ở một mình.",
    "6/3": "Role Model/Martyr - Hình mẫu tử vì đạo. 3 giai đoạn, thử sai để trở thành hình mẫu. Cuộc đời là hành trình quan sát và thử nghiệm."
}

# Ý nghĩa Type
TYPE_ANALYSIS = {
    "Generator": """
GENERATOR - NGƯỜI KIẾN TẠO (37% dân số)
Bạn là nguồn năng lượng sống của hành tinh. Bạn ở đây để làm công việc bạn yêu thích và tìm thấy sự thỏa mãn.

Chiến lược: Chờ để Đáp Ứng. Đừng khởi xướng. Hãy để cuộc sống mang đến câu hỏi, cơ hội. Lắng nghe tiếng Sacral: uh-huh (mở, cao) là có, uh-uh (đóng, thấp) là không.

Not-Self: Thất vọng (Frustration) - Khi bạn làm việc không đúng, ép bản thân khởi xướng, hoặc không lắng nghe Sacral.

Chữ ký: Thỏa mãn (Satisfaction) - Khi làm đúng việc, đúng cách.

Thực hành:
- Hỏi câu hỏi có/không thay vì mở
- Đừng quyết định bằng đầu óc
- Làm việc bạn yêu, bạn sẽ có năng lượng vô tận
- Kiên nhẫn chờ đợi
""",
    "Manifesting Generator": """
MANIFESTING GENERATOR - NGƯỜI KIẾN TẠO ĐA NĂNG (33%)
Bạn là Generator nhưng nhanh hơn, đa nhiệm, có khả năng bỏ qua bước. Bạn ở đây để tìm ra con đường hiệu quả nhất.

Chiến lược: Chờ để Đáp Ứng, rồi Thông Báo. Đáp ứng như Generator, nhưng sau khi đáp ứng, hãy thông báo cho những người bị ảnh hưởng trước khi hành động để giảm kháng cự.

Not-Self: Thất vọng + Tức giận
Chữ ký: Thỏa mãn + Bình yên

Đặc điểm:
- Nhanh, có thể làm tắt
- Đa đam mê, được phép thay đổi hướng
- Cần thử và sai
- Học cách thông báo
""",
    "Projector": """
PROJECTOR - NGƯỜI CỐ VẤN (20%)
Bạn không ở đây để làm việc như Generator. Bạn ở đây để hướng dẫn, quản lý, nhìn thấy người khác. Bạn là nhà lãnh đạo mới.

Chiến lược: Chờ Lời Mời. Đặc biệt cho 4 việc lớn: Tình yêu, Công việc, Nơi ở, Mối quan hệ quan trọng. Khi được công nhận đúng và được mời, bạn sẽ thành công. Khi cố gắng ép buộc, bạn sẽ cay đắng.

Not-Self: Cay đắng (Bitterness) - Khi không được công nhận, cố gắng như Generator.

Chữ ký: Thành công (Success)

Thực hành:
- Đừng làm việc 8 tiếng
- Nghỉ ngơi nhiều, ngủ một mình để giải phóng năng lượng người khác
- Tập trung vào việc học hệ thống, hiểu người khác
- Chờ lời mời đúng - nó sẽ thay đổi cuộc đời bạn
- Bạn cần được công nhận trước khi được mời
""",
    "Manifestor": """
MANIFESTOR - NGƯỜI KHỞI XƯỚNG (9%)
Bạn là người duy nhất được thiết kế để khởi xướng. Bạn ở đây để tạo ra tác động, bắt đầu mọi thứ. Aura của bạn đóng và đẩy, khiến người khác hơi e dè nhưng tôn trọng.

Chiến lược: Thông Báo (Inform) trước khi hành động. Không phải xin phép, mà là thông báo: "Tôi sẽ làm...". Điều này giảm kháng cự và giận dữ.

Not-Self: Tức giận (Anger) - Khi bị kiểm soát, không được tự do, gặp kháng cự.

Chữ ký: Bình yên (Peace)

Thực hành:
- Tìm sự bình yên, không phải ai cũng hiểu bạn
- Bạn cần tự chủ, ghét bị kiểm soát
- Thông báo để được tự do
- Bạn ở đây để tác động, không phải để làm việc bền bỉ
""",
    "Reflector": """
REFLECTOR - NGƯỜI PHẢN CHIẾU (1% - Hiếm nhất)
Bạn là trung tâm của cộng đồng, là người đánh giá sức khỏe cộng đồng. Bạn phản chiếu môi trường xung quanh. Bạn là tắc kè hoa, thay đổi theo Mặt Trăng.

Chiến lược: Chờ 28-29 ngày - Một chu kỳ Mặt Trăng. Đừng quyết định vội. Nói chuyện với nhiều người, ở nhiều môi trường khác nhau, cảm nhận sự nhất quán.

Thẩm quyền: Lunar - Mặt Trăng. Không có thẩm quyền nội tại.

Not-Self: Thất vọng (Disappointment) - Khi môi trường không đúng, thất vọng về thế giới.

Chữ ký: Ngạc nhiên (Surprise) - Khi cuộc sống kỳ diệu.

Thực hành:
- Môi trường là TẤT CẢ
- Ngủ, sống, làm việc ở nơi đúng
- Bạn thấy những gì người khác không thấy
- Bạn cần thời gian
- Bạn là món quà hiếm cho nhân loại
"""
}

def analyze_chart(chart):
    """Tạo báo cáo phân tích chuyên sâu"""
    report = []
    report.append(f"# PHÂN TÍCH HUMAN DESIGN CHUYÊN SÂU")
    report.append(f"Ngày sinh: {chart['birth_datetime']} UTC")
    report.append(f"Ngày Design (88° trước): {chart['design_datetime']} UTC")
    report.append("")
    
    # Type
    report.append(f"## 1. LOẠI NĂNG LƯỢNG: {vn_type(chart['type'], gloss=True)}")
    report.append(TYPE_ANALYSIS.get(chart['type'], ""))
    report.append(f"**Chiến lược sống**: {vn_strategy(chart['strategy'], chart['type'])}")
    report.append(f"**Quyền nội tại**: {vn_authority(chart['authority'])}")
    report.append("")
    
    # Authority chi tiết
    report.append(f"## 2. QUYỀN NỘI TẠI: {vn_authority(chart['authority'])}")
    if "Emotional" in chart['authority']:
        report.append("""
Bạn có Solar Plexus định nghĩa. Bạn là người cảm xúc. KHÔNG BAO GIỜ quyết định trong khoảnh khắc.
Sóng cảm xúc của bạn cần thời gian để đạt đến sự rõ ràng. Hãy chờ ít nhất một đêm, tốt hơn là vài ngày.
Hỏi bản thân: Cảm xúc này có nhất quán theo thời gian không?
Đừng quyết định khi đang ở đỉnh cao hứng khởi hay đáy sâu tuyệt vọng.
Sự rõ ràng đến theo thời gian.
""")
    elif "Sacral" in chart['authority']:
        report.append("""
Bạn có Sacral Authority. Quyết định ngay lập tức qua tiếng bụng.
Âm thanh uh-huh (mở, cao, cơ thể hướng về phía trước) là CÓ.
Âm thanh uh-uh (đóng, thấp, cơ thể co lại) là KHÔNG.
Đừng quyết định bằng đầu óc. Tin vào cơ thể.
""")
    elif "Splenic" in chart['authority']:
        report.append("""
Bạn có Splenic Authority. Trực giác tức thì, chỉ nói một lần, rất khẽ, trong hiện tại.
Nó liên quan đến sức khỏe, an toàn, sống sót.
Không lặp lại. Nếu bạn bỏ lỡ, nó biến mất.
Học cách tin ngay lập tức.
""")
    elif "Ego" in chart['authority']:
        report.append("""
Bạn có Ego/Heart Authority. Quyết định dựa trên ý chí và những gì bạn sẵn sàng cam kết.
Hỏi: "Tôi có thực sự muốn cam kết ý chí của mình cho điều này không? Tôi có muốn hứa không?"
Liên quan đến vật chất, tiền bạc, lòng tự trọng.
""")
    elif "Self-Projected" in chart['authority']:
        report.append("""
Bạn có Self-Projected Authority (G-Center). Bạn cần nói ra thành tiếng với người bạn tin cậy để nghe sự thật của mình.
Không tìm lời khuyên, tìm sự lắng nghe.
Sự thật đến qua giọng nói của chính bạn: "Tôi biết..." "Tôi là..."
Cần người lắng nghe đáng tin cậy, không phải cố vấn.
""")
    elif "Mental" in chart['authority'] or "Environment" in chart['authority']:
        report.append("""
Bạn là Mental Projector. Không có thẩm quyền nội tại dưới Throat.
Bạn cần sounding board - nói chuyện với nhiều người tin cậy ở môi trường đúng.
Không tìm lời khuyên, mà tìm sự phản chiếu qua việc nói ra.
Môi trường đúng là chìa khóa. Bạn cần ở nơi đúng để có sự rõ ràng.
""")
    else:
        report.append("""
Bạn là Reflector - Lunar Authority. Bạn cần chờ 1 chu kỳ Mặt Trăng (28-29 ngày).
Nói chuyện với nhiều người khác nhau, ở nhiều môi trường khác nhau.
Cảm nhận sự nhất quán theo thời gian và không gian.
""")
    
    # Profile
    report.append(f"## 3. PROFILE: {chart['profile']}")
    report.append(PROFILE_ANALYSIS.get(chart['profile'], f"Profile {chart['profile']} - Cần tra cứu thêm"))
    report.append("")
    
    # Definition
    report.append(f"## 4. ĐỊNH NGHĨA: {vn_definition(chart['definition'])}")
    if "Single" in chart['definition']:
        report.append("Tất cả trung tâm định nghĩa của bạn nối liền nhau. Bạn có năng lượng nhất quán, cảm giác toàn vẹn. Bạn tự xử lý, không cần người khác để cầu nối. Bạn có thể tự mình hoàn thành mọi việc.")
    elif "Split" in chart['definition']:
        report.append(f"Bạn có {chart['definition_groups']} nhóm năng lượng tách rời. Bạn cần người khác hoặc transit hành tinh để cầu nối. Chủ đề cuộc đời: Tìm kiếm sự kết nối. Bạn có thể cảm thấy thiếu gì đó. Học cách không phụ thuộc vào cầu nối, kiên nhẫn với sự tách rời.")
    else:
        report.append("Không định nghĩa (Reflector) — bạn cởi mở hoàn toàn, lấy mẫu môi trường.")
    report.append("")
    
    # Centers
    report.append(f"## 5. 9 TRUNG TÂM - {len(chart['defined_centers'])} Định nghĩa, {9-len(chart['defined_centers'])} Mở")
    all_centers = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
    for center in all_centers:
        if center in chart['defined_centers']:
            report.append(f"**{vn_center(center)}: ĐỊNH NGHĨA (Có màu)** - {CENTER_ANALYSIS[center]['defined']}")
        else:
            report.append(f"**{vn_center(center)}: MỞ (Trắng)** - {CENTER_ANALYSIS[center]['undefined']}")
    report.append("")
    
    # Channels
    report.append(f"## 6. KÊNH ĐỊNH NGHĨA - {len(chart['defined_channels'])} kênh")
    report.append("Đây là tài năng cố định, năng lượng nhất quán của bạn.")
    for g1, g2 in chart['defined_channels']:
        centers = CHANNEL_TO_CENTERS.get((g1,g2)) or CHANNEL_TO_CENTERS.get((g2,g1))
        report.append(f"- **{g1}-{g2}** ({centers[0]} - {centers[1]}): {GATE_MEANINGS.get(g1)} + {GATE_MEANINGS.get(g2)}")
    report.append("")
    
    # Gates
    report.append(f"## 7. CỔNG KÍCH HOẠT - {len(chart['all_activated_gates'])} cổng")
    report.append("### Personality (Ý thức - Đen) - Những gì bạn biết về mình:")
    for planet in ["Sun", "Earth", "Moon", "North Node", "South Node", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
        data = chart['personality_gates'][planet]
        report.append(f"- {planet}: Gate {data['gate']}.{data['line']} - {GATE_MEANINGS.get(data['gate'])} - Center: {GATE_TO_CENTER.get(data['gate'])}")
    
    report.append("")
    report.append("### Design (Vô thức - Đỏ) - Những gì người khác thấy ở bạn, cơ thể bạn:")
    for planet in ["Sun", "Earth", "Moon", "North Node", "South Node", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
        data = chart['design_gates'][planet]
        report.append(f"- {planet}: Gate {data['gate']}.{data['line']} - {GATE_MEANINGS.get(data['gate'])} - Center: {GATE_TO_CENTER.get(data['gate'])}")
    
    report.append("")
    
    # Incarnation Cross
    report.append(f"## 8. INCARNATION CROSS: {chart['incarnation_cross']}")
    report.append(f"Type: {chart['cross_type']}")
    report.append(f"- Personality Sun: Gate {chart['p_sun_gate']} - {GATE_MEANINGS.get(chart['p_sun_gate'])} - Quarter: {chart['quarters']['p_sun']}")
    report.append(f"- Personality Earth: Gate {chart['p_earth_gate']} - {GATE_MEANINGS.get(chart['p_earth_gate'])} - Quarter: {chart['quarters']['p_earth']}")
    report.append(f"- Design Sun: Gate {chart['d_sun_gate']} - {GATE_MEANINGS.get(chart['d_sun_gate'])} - Quarter: {chart['quarters']['d_sun']}")
    report.append(f"- Design Earth: Gate {chart['d_earth_gate']} - {GATE_MEANINGS.get(chart['d_earth_gate'])} - Quarter: {chart['quarters']['d_earth']}")
    report.append("")
    report.append("Incarnation Cross là mục đích sống tổng quát. Để biết tên chính xác (ví dụ Right Angle Cross of the Sphinx), cần tra cứu bảng 192 Cross với 4 cổng này.")
    report.append("")
    
    # Tổng kết thực hành
    report.append("## 9. THỰC HÀNH - SỐNG ĐÚNG THIẾT KẾ")
    report.append(f"""
1. **Sống đúng chiến lược sống**: {vn_strategy(chart['strategy'], chart['type'])}
2. **Ra quyết định bằng quyền nội tại**: {vn_authority(chart['authority'])} - Không bằng đầu óc
3. **Tôn trọng loại năng lượng**: {vn_type(chart['type'], gloss=True)} - {TYPE_ANALYSIS.get(chart['type'],'')[:100]}...
4. **Hiểu Profile {chart['profile']}**: Vai trò của bạn trong vở kịch cuộc đời
5. **Chăm sóc trung tâm mở**: Đây là nơi bạn học trí tuệ, không phải nơi ra quyết định
6. **Deconditioning**: Quá trình 7 năm để giải điều kiện hóa. Kiên nhẫn.
""")
    
    return "\n".join(report)

def analyze_from_datetime(dt):
    chart = calculate_hd_chart(dt)
    text = format_chart_text(chart)
    deep = analyze_chart(chart)
    return chart, text, deep

if __name__ == "__main__":
    dt = datetime(1990, 5, 15, 8, 30, 0)
    chart, text, deep = analyze_from_datetime(dt)
    print(text)
    print("\n\n")
    print(deep)
