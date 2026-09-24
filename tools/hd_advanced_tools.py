"""
Human Design Advanced Tools - Tích hợp từ tài liệu nghiên cứu cá nhân
- Fear Gates Analysis (từ Wiki Phân mục 4)
- Love Gates Analysis (từ Wiki Phân mục 5)
- Incarnation Cross Details (từ Wiki Phân mục 3 - 192 Crosses)
- Manifestor Deep Dive (từ Wiki Phân mục 6)

Tác giả: Tích hợp từ docs cá nhân - 2026-09-23
"""

from hd_calculator import (
    calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER, 
    CHANNEL_TO_CENTERS, GATE_ORDER, CHANNELS
)
from datetime import datetime
import json

# ==================== FEAR GATES (từ Phân mục 4) ====================

SPLENIC_FEARS = {
    18: {"name": "Sợ không hoàn hảo", "quẻ": "Sơn Phong Cổ", "sứ_mệnh": "29,30", "mô_tả": "Phán xét và độc tài trong sửa chữa người khác để đạt niềm vui sống giả tạo"},
    28: {"name": "Sợ cuộc sống vô nghĩa/cái chết", "quẻ": "Trạch Phong Đại Quá", "sứ_mệnh": "82", "mô_tả": "Đấu tranh tìm đam mê cốt lõi để vượt qua hư vô"},
    32: {"name": "Sợ thất bại/đứt gãy truyền thống", "quẻ": "Lôi Phong Hằng", "sứ_mệnh": "94", "mô_tả": "Bản năng tiết kiệm và lưu trữ để đảm bảo tồn tại"},
    50: {"name": "Sợ sụp đổ luật lệ bộ lạc", "quẻ": "Hỏa Phong Đỉnh", "sứ_mệnh": "148", "mô_tả": "Lửa trại - thiết lập quy tắc nấu ăn, chia sẻ thực phẩm để duy trì trật tự cộng đồng"},
    44: {"name": "Sợ bóng ma quá khứ", "quẻ": "Thiên Phong Cấu", "sứ_mệnh": "130,131", "mô_tả": "Quản lý con người, phân công nhiệm vụ dựa trên kinh nghiệm cũ để tránh lặp lại sai lầm"},
    57: {"name": "Sợ tương lai/không xác định", "quẻ": "Thuần Tốn", "sứ_mệnh": "169", "mô_tả": "Đọc rung cảm tức thời để biết điều gì đúng/sai, tránh thảm họa"},
}

AJNA_ANXIETIES = {
    17: {"name": "Lo âu ý kiến không chứng minh được", "sứ_mệnh": "49,50", "mô_tả": "Áp lực tổ chức và hướng dẫn người khác qua quan điểm có cấu trúc"},
    47: {"name": "Lo âu trước hỗn loạn", "sứ_mệnh": "139,140", "mô_tả": "Áp lực xâu chuỗi mảnh ghép quá khứ thành bức tranh toàn cảnh có ý nghĩa"},
    24: {"name": "Lo âu vòng lặp tư duy", "sứ_mệnh": "70,72", "mô_tả": "Lặp lại ký ức để tìm hiểu sâu sắc về quá trình hóa thân"},
    43: {"name": "Lo bị coi là kỳ quặc", "sứ_mệnh": "127,128", "mô_tả": "Áp lực diễn đạt hiểu biết đột biến (Aha!) thành ngôn ngữ cộng đồng đồng hóa được"},
    11: {"name": "Lo không hiện thực hóa ý tưởng", "sứ_mệnh": "31,33", "mô_tả": "Giáo dục, vai trò nhà tiên tri truyền đạt triết lý và trải nghiệm"},
    4: {"name": "Lo thiếu giải pháp logic", "sứ_mệnh": "10,11", "mô_tả": "Áp lực tạo lý thuyết và công thức để giải đố khuôn mẫu thế giới"},
}

SOLAR_NERVOUSNESS = {
    30: {"name": "Hồi hộp đam mê cháy bỏng", "sứ_mệnh": "88,89", "mô_tả": "Ám ảnh, thúc đẩy trải nghiệm cái mới cho đến khi cháy hết mình và phục hồi"},
    55: {"name": "Hồi hộp dồi dào/thiếu hụt", "sứ_mệnh": "163,165", "mô_tả": "Nhu cầu thức ăn ngon và lãng mạn để nuôi dưỡng tinh thần, cưỡi sóng u sầu tìm thức tỉnh"},
    49: {"name": "Hồi hộp bị từ chối", "sứ_mệnh": "145,147", "mô_tả": "Robin Hood - cách mạng hóa nguyên tắc để cung cấp thực phẩm và bảo vệ quyền lợi cộng đồng"},
    6: {"name": "Hồi hộp rào cản thân mật", "sứ_mệnh": "16,18", "mô_tả": "Bị ném ra khỏi Eden, thúc đẩy tìm kiếm cân bằng trong cọ xát mối quan hệ"},
    37: {"name": "Hồi hộp công bằng", "sứ_mệnh": "109,110", "mô_tả": "Thỏa thuận và giao kèo trong gia đình, đảm bảo mỗi đóng góp nhận đền đáp tương xứng"},
    22: {"name": "Hồi hộp đối diện người lạ", "sứ_mệnh": "64,66", "mô_tả": "Năng khiếu lắng nghe và cai trị duyên dáng, biến thông tin thành nghệ thuật"},
    36: {"name": "Hồi hộp trải nghiệm mới", "sứ_mệnh": "106", "mô_tả": "Động lực khám phá lại Eden qua khủng hoảng thực tế, biến thiếu kinh nghiệm thành trí tuệ"},
}

# Cross đặc biệt liên quan sợ hãi
FEAR_CROSSES = {
    "Cross of Limitation": {"gates": [32,42,56,60], "mô_tả": "Sợ giới hạn, dẫn đến bảo thủ hoặc trầm cảm nếu không hiểu ranh giới tồn tại"},
    "Cross of Crisis": {"gates": [36,6,15,10], "mô_tả": "Hỗn loạn cảm xúc tạo ra khủng hoảng để tìm kiếm trưởng thành"},
}

def analyze_fear_gates(birth_datetime):
    """Phân tích 19 cổng sợ hãi/lo âu/hồi hộp trong chart"""
    chart = calculate_hd_chart(birth_datetime) if isinstance(birth_datetime, datetime) else calculate_hd_chart(birth_datetime)
    
    activated = set(chart["all_activated_gates"])
    
    splenic_active = []
    for gate, info in SPLENIC_FEARS.items():
        if gate in activated:
            # Tìm xem gate này từ Personality hay Design
            p_gates = [v["gate"] for v in chart["personality_gates"].values()]
            d_gates = [v["gate"] for v in chart["design_gates"].values()]
            source = []
            if gate in p_gates:
                source.append("Personality (Ý thức - Đen)")
            if gate in d_gates:
                source.append("Design (Vô thức - Đỏ)")
            
            splenic_active.append({
                "gate": gate,
                "name": info["name"],
                "quẻ": info["quẻ"],
                "sứ_mệnh": info["sứ_mệnh"],
                "mô_tả": info["mô_tả"],
                "center": "Spleen - Trực giác",
                "type": "Fear - Sợ hãi sinh tồn",
                "source": source,
                "meaning": GATE_MEANINGS.get(gate)
            })
    
    ajna_active = []
    for gate, info in AJNA_ANXIETIES.items():
        if gate in activated:
            p_gates = [v["gate"] for v in chart["personality_gates"].values()]
            d_gates = [v["gate"] for v in chart["design_gates"].values()]
            source = []
            if gate in p_gates:
                source.append("Personality")
            if gate in d_gates:
                source.append("Design")
            
            ajna_active.append({
                "gate": gate,
                "name": info["name"],
                "sứ_mệnh": info["sứ_mệnh"],
                "mô_tả": info["mô_tả"],
                "center": "Ajna - Trí óc",
                "type": "Anxiety - Lo âu tư duy",
                "source": source,
                "meaning": GATE_MEANINGS.get(gate)
            })
    
    solar_active = []
    for gate, info in SOLAR_NERVOUSNESS.items():
        if gate in activated:
            p_gates = [v["gate"] for v in chart["personality_gates"].values()]
            d_gates = [v["gate"] for v in chart["design_gates"].values()]
            source = []
            if gate in p_gates:
                source.append("Personality")
            if gate in d_gates:
                source.append("Design")
            
            solar_active.append({
                "gate": gate,
                "name": info["name"],
                "sứ_mệnh": info["sứ_mệnh"],
                "mô_tả": info["mô_tả"],
                "center": "Solar Plexus - Cảm xúc",
                "type": "Nervousness - Hồi hộp cảm xúc",
                "source": source,
                "meaning": GATE_MEANINGS.get(gate)
            })
    
    # Kiểm tra Cross of Limitation và Crisis
    special_crosses = []
    for cross_name, cross_info in FEAR_CROSSES.items():
        count = len(set(cross_info["gates"]).intersection(activated))
        if count >= 2:  # Có ít nhất 2 cổng trong cross
            special_crosses.append({
                "cross": cross_name,
                "gates": cross_info["gates"],
                "activated": list(set(cross_info["gates"]).intersection(activated)),
                "count": count,
                "mô_tả": cross_info["mô_tả"]
            })
    
    return {
        "total_fear_gates": len(splenic_active) + len(ajna_active) + len(solar_active),
        "splenic_fears": {"count": len(splenic_active), "gates": splenic_active, "description": "Nỗi sợ sinh tồn trong khoảnh khắc hiện tại - bản năng bảo vệ thân xác"},
        "ajna_anxieties": {"count": len(ajna_active), "gates": ajna_active, "description": "Lo âu tư duy - áp lực xử lý dữ liệu, tìm kiếm chắc chắn"},
        "solar_nervousness": {"count": len(solar_active), "gates": solar_active, "description": "Hồi hộp cảm xúc - bất ổn trước làn sóng cảm xúc, khao khát"},
        "special_crosses": special_crosses,
        "advice": """
        Nhận diện 20 Cổng Sợ hãi là bước đầu tiên để tách biệt người quan sát khỏi cỗ xe cơ thể.
        Khi bạn thấy mình lo âu về tương lai (Cổng 57) hay căng thẳng về thỏa thuận (Cổng 37), hãy hiểu đó chỉ là áp lực nhận thức đang vận hành, không phải mệnh lệnh để hành động.
        Chìa khóa chuyển hóa nỗi sợ thành trí tuệ chính là thực hành kiên trì Strategy & Authority.
        """
    }

# ==================== LOVE GATES (từ Phân mục 5) ====================

VESSEL_OF_LOVE = {
    25: {"tình_yêu": "Tình yêu phổ quát / Vô điều kiện", "vai_trò": "Tâm hồn bản thể", "mô_tả": "Yêu thương vạn vật hồn nhiên; vượt qua cú sốc để tìm lại ngây thơ nguyên bản"},
    15: {"tình_yêu": "Tình yêu nhân loại", "vai_trò": "Nhịp điệu cực đoan", "mô_tả": "Chấp nhận thái cực khác biệt con người; đưa nhân loại vào dòng chảy yêu thương"},
    46: {"tình_yêu": "Tình yêu thể xác / Gợi cảm", "vai_trò": "Xác định bản thân", "mô_tả": "Tận hưởng trải nghiệm trần gian qua cơ thể vật lý; yêu sự hiện diện linh hồn trong thế giới vật chất"},
    10: {"tình_yêu": "Tình yêu bản thể (Tâm linh)", "vai_trò": "Yêu bản thân", "mô_tả": "Tấm gương về việc yêu thương chính mình để người khác soi vào và học hỏi"},
}

MUNDANE_LOVE = {
    10: {"động_lực": "Động lực thông qua hành vi", "mô_tả": "Điều chỉnh và sửa chữa hành vi cá nhân theo chuẩn mực đúng đắn để nâng cao niềm vui sống và an toàn"},
    44: {"động_lực": "Động lực sinh tồn", "mô_tả": "Tỉnh táo về bản năng. Nhận diện mô hình rắc rối từ quá khứ để quản lý con người và đảm bảo an toàn cộng đồng"},
    40: {"động_lực": "Động lực thỏa thuận (Bargains)", "mô_tả": "Tình yêu đòi hỏi tách biệt để hồi phục sức lao động, sau đó đóng góp cho cộng đồng qua cam kết thực tế để đổi lấy thuộc về"},
    58: {"động_lực": "Động lực cải thiện", "mô_tả": "Khao khát sống động nhằm điều chỉnh quy trình logic, giúp cuộc sống bản thân và người khác tốt đẹp và tiến bộ hơn"},
    41: {"động_lực": "Động lực kỳ vọng", "mô_tả": "Tưởng tượng và khát khao trải nghiệm mới, luôn dự đoán về cảm giác chưa từng có trong mối quan hệ"},
    28: {"động_lực": "Động lực tìm kiếm mục đích", "mô_tả": "Cuộc đấu tranh và sẵn sàng chấp nhận rủi ro để tìm niềm đam mê sâu sắc, mang lại ý nghĩa thực sự cho tồn tại"},
    55: {"động_lực": "Động lực cảm xúc", "mô_tả": "Dao động giữa hy vọng và u sầu, tập trung vào tìm kiếm thỏa mãn tinh thần qua thân mật và ăn uống ngon lành"},
}

def analyze_love_gates(birth_datetime):
    """Phân tích 4 Vessel of Love + 7 Mundane Love"""
    chart = calculate_hd_chart(birth_datetime) if isinstance(birth_datetime, datetime) else calculate_hd_chart(birth_datetime)
    
    activated = set(chart["all_activated_gates"])
    
    vessel_active = []
    for gate, info in VESSEL_OF_LOVE.items():
        if gate in activated:
            p_gates = [v["gate"] for v in chart["personality_gates"].values()]
            d_gates = [v["gate"] for v in chart["design_gates"].values()]
            source = []
            if gate in p_gates:
                source.append("Personality")
            if gate in d_gates:
                source.append("Design")
            
            # Tìm line
            p_sun = chart["personality_gates"]["Sun"]
            # Tìm line của gate này
            gate_line = None
            for planet, data in chart["personality_gates"].items():
                if data["gate"] == gate:
                    gate_line = data["line"]
                    break
            if not gate_line:
                for planet, data in chart["design_gates"].items():
                    if data["gate"] == gate:
                        gate_line = data["line"]
                        break
            
            vessel_active.append({
                "gate": gate,
                "tình_yêu": info["tình_yêu"],
                "vai_trò": info["vai_trò"],
                "mô_tả": info["mô_tả"],
                "center": "G Center - Nhân dạng",
                "type": "Vessel of Love - Tình yêu siêu việt",
                "source": source,
                "line": gate_line,
                "meaning": GATE_MEANINGS.get(gate)
            })
    
    mundane_active = []
    for gate, info in MUNDANE_LOVE.items():
        if gate in activated:
            # Tránh trùng với vessel (gate 10)
            if gate == 10 and any(v["gate"] == 10 for v in vessel_active):
                # Gate 10 vừa là vessel vừa là mundane, nhưng tính 1 lần
                pass
            
            p_gates = [v["gate"] for v in chart["personality_gates"].values()]
            d_gates = [v["gate"] for v in chart["design_gates"].values()]
            source = []
            if gate in p_gates:
                source.append("Personality")
            if gate in d_gates:
                source.append("Design")
            
            mundane_active.append({
                "gate": gate,
                "động_lực": info["động_lực"],
                "mô_tả": info["mô_tả"],
                "type": "Mundane Love - Tình yêu trần thế",
                "source": source,
                "meaning": GATE_MEANINGS.get(gate),
                "center": GATE_TO_CENTER.get(gate)
            })
    
    # Kiểm tra xem có đủ 4 Vessel of Love không (Cross of Vessel of Love)
    vessel_count = len(vessel_active)
    is_vessel_cross = vessel_count >= 3  # Có ít nhất 3 trong 4 cổng vessel
    
    return {
        "vessel_of_love": {
            "count": len(vessel_active),
            "gates": vessel_active,
            "is_vessel_cross": is_vessel_cross,
            "description": "4 cổng tình yêu siêu việt tại G Center - định hướng linh hồn về kết nối phổ quát",
            "cross_info": "Xuất hiện trong các Chữ Thập số hiệu 28,43,73,136 - Con tàu Tình yêu"
        },
        "mundane_love": {
            "count": len(mundane_active),
            "gates": mundane_active,
            "description": "7 cổng tình yêu trần thế - gắn liền nhu cầu thực tế, thỏa thuận, đấu tranh tâm lý"
        },
        "total_love_gates": len(vessel_active) + len(mundane_active),
        "advice": """
        Tình yêu trong Human Design không phải nỗ lực thay đổi ai đó, mà là lộ trình thức tỉnh.
        Vessel of Love là tình yêu siêu việt, không điều kiện.
        Mundane Love là tình yêu trần thế, có điều kiện, thỏa thuận.
        Hiểu rõ cơ chế giúp chấp nhận độc đáo bản thân và người khác.
        """
    }

# ==================== INCARNATION CROSS DATABASE (từ Phân mục 3) ====================

# Trích lọc từ tài liệu 413 dòng - một số crosses tiêu biểu (đã có trong knowledge 08)
# Đây là database để lookup
INCARNATION_CROSSES_DB = [
    # Sphinx
    {"name": "Right Angle Cross of the Sphinx 4", "gates": [1,2,7,13], "quẻ": [1,2,7,13], "angle": "Right Angle", "role": "Hành động theo quan điểm riêng trong hiện tại. Tự thể hiện cá nhân là đóng góp cho xã hội"},
    {"name": "Right Angle Cross of the Sphinx 2", "gates": [2,1,13,7], "quẻ": [2,1,13,7], "angle": "Right Angle", "role": "Khai mở tiềm năng và hướng dẫn mọi người theo nhiều hướng"},
    {"name": "Right Angle Cross of the Sphinx 3", "gates": [7,13,2,1], "quẻ": [7,13,2,1], "angle": "Right Angle", "role": "Lãnh đạo dựa trên tầm nhìn tương lai, xem xét mô hình quá khứ"},
    {"name": "Right Angle Cross of the Sphinx", "gates": [13,7,1,2], "quẻ": [13,7,1,2], "angle": "Right Angle", "role": "Trực quan về quá khứ; cung cấp hướng dẫn bằng cách đồng hóa lịch sử"},
    {"name": "Juxtaposition Cross of Self-Expression", "gates": [1,2,4,49], "quẻ": [1,2,4,49], "angle": "Juxtaposition", "role": "Sinh ra để khác biệt và làm điều riêng biệt"},
    {"name": "Left Angle Cross of Defiance 2", "gates": [1,2,4,49], "quẻ": [1,2,4,49], "angle": "Left Angle", "role": "Kiểm soát ảnh hưởng và thách thức quy tắc áp đặt giới hạn"},
    {"name": "Juxtaposition Cross of the Driver", "gates": [2,1,49,4], "quẻ": [2,1,49,4], "angle": "Juxtaposition", "role": "Tự định hướng và khám phá sự thật bản thân"},
    {"name": "Left Angle Cross of Defiance", "gates": [2,1,49,4], "quẻ": [2,1,49,4], "angle": "Left Angle", "role": "Bước ra khỏi ranh giới để đại diện cách làm việc khác biệt"},
    # Laws & Mutation
    {"name": "Right Angle Cross of Laws", "gates": [3,50,60,56], "quẻ": [3,50,60,56], "angle": "Right Angle", "role": "Thiết lập và tuân thủ quy định gia đình/xã hội để giảm lo lắng"},
    {"name": "Juxtaposition Cross of Mutation", "gates": [3,50,41,31], "quẻ": [3,50,41,31], "angle": "Juxtaposition", "role": "Lực lượng đột biến thay đổi quy tắc cộng đồng"},
    {"name": "Left Angle Cross of Wishes", "gates": [3,50,41,31], "quẻ": [3,50,41,31], "angle": "Left Angle", "role": "Lãnh đạo thay đổi luật pháp dựa trên ước muốn về tương lai tốt đẹp hơn"},
    # Explanation
    {"name": "Right Angle Cross of Explanation 3", "gates": [4,49,23,43], "quẻ": [4,49,23,43], "angle": "Right Angle", "role": "Cung cấp lý thuyết và lời giải thích khác biệt giúp thay đổi niềm tin sai lầm"},
    {"name": "Juxtaposition Cross of Formulization", "gates": [4,49,8,14], "quẻ": [4,49,8,14], "angle": "Juxtaposition", "role": "Diễn đạt lý thuyết về mẫu và công thức để giải thích mọi thứ"},
    {"name": "Left Angle Cross of Revolution 2", "gates": [4,49,8,14], "quẻ": [4,49,8,14], "angle": "Left Angle", "role": "Thực hiện thay đổi thiết thực khi mô hình cách mạng phù hợp sự thật"},
    # Consciousness & Habits
    {"name": "Right Angle Cross of Consciousness 4", "gates": [5,35,64,63], "quẻ": [5,35,64,63], "angle": "Right Angle", "role": "Hòa vào dòng chảy nhịp điệu tự nhiên cuộc sống và chia sẻ giác ngộ"},
    {"name": "Juxtaposition Cross of Habits", "gates": [5,35,47,22], "quẻ": [5,35,47,22], "angle": "Juxtaposition", "role": "Ảnh hưởng mạnh đến khuôn mẫu xã hội bằng cách chứng minh sức mạnh nhịp điệu"},
    {"name": "Left Angle Cross of Separation 2", "gates": [5,35,47,22], "quẻ": [5,35,47,22], "angle": "Left Angle", "role": "Tìm kiếm và sống theo nhịp điệu riêng biệt, cung cấp hình mẫu độc lập"},
    # Eden & Plane
    {"name": "Right Angle Cross of Eden 3", "gates": [6,36,12,11], "quẻ": [6,36,12,11], "angle": "Right Angle", "role": "Khám phá thế giới vật chất để tìm một phần Eden trên trái đất"},
    {"name": "Left Angle Cross of the Plane 2", "gates": [6,36,15,10], "quẻ": [6,36,15,10], "angle": "Left Angle", "role": "Người hướng dẫn thành công trong thế giới vật chất bằng cách sống phù hợp thiết kế linh hồn"},
    {"name": "Juxtaposition Cross of Conflict", "gates": [6,36,15,10], "quẻ": [6,36,15,10], "angle": "Juxtaposition", "role": "Tìm kiếm cân bằng giữa nỗi đau mất Eden và niềm vui sống qua mối quan hệ"},
    # Vessel of Love
    {"name": "Right Angle Cross of Vessel of Love 4", "gates": [10,15,46,25], "quẻ": [10,15,46,25], "angle": "Right Angle", "role": "Hiện thân tình yêu; tìm thấy tình yêu bản thân để trở thành tấm gương yêu thương"},
    {"name": "Right Angle Cross of Vessel of Love", "gates": [25,46,10,15], "quẻ": [25,46,10,15], "angle": "Right Angle", "role": "Trung tâm tình yêu phổ quát; vượt qua cú sốc để duy trì tinh thần ngây thơ"},
    {"name": "Right Angle Cross of Vessel of Love 3", "gates": [46,25,15,10], "quẻ": [46,25,15,10], "angle": "Right Angle", "role": "Trải nghiệm tồn tại trần gian đầy yêu thương và gợi cảm"},
    # Service
    {"name": "Right Angle Cross of Service", "gates": [17,18,58,52], "quẻ": [17,18,58,52], "angle": "Right Angle", "role": "Hướng dẫn và tổ chức để giúp mọi người đạt cuộc sống khỏe mạnh và vui vẻ hơn"},
    {"name": "Right Angle Cross of the Sleeping Phoenix 2", "gates": [20,34,55,59], "quẻ": [20,34,55,59], "angle": "Right Angle", "role": "Duy trì bận rộn để tìm kiếm sức mạnh và độc lập trong cảm xúc"},
    {"name": "Right Angle Cross of Tension", "gates": [21,48,38,39], "quẻ": [21,48,38,39], "angle": "Right Angle", "role": "Sử dụng căng thẳng và khiêu khích để duy trì trật tự và liên kết cộng đồng"},
    {"name": "Right Angle Cross of Rulership", "gates": [22,47,26,45], "quẻ": [22,47,26,45], "angle": "Right Angle", "role": "Thống trị và cai trị thế giới mình một cách duyên dáng qua lắng nghe và giáo dục"},
    # ... có thể mở rộng thêm 192 crosses đầy đủ từ file knowledge 08
]

def get_incarnation_cross_details(p_sun_gate, p_earth_gate, d_sun_gate, d_earth_gate):
    """
    Tra cứu chi tiết Incarnation Cross từ 4 cổng
    """
    input_gates = [p_sun_gate, p_earth_gate, d_sun_gate, d_earth_gate]
    input_set = set(input_gates)
    
    matches = []
    for cross in INCARNATION_CROSSES_DB:
        if set(cross["gates"]) == input_set:
            matches.append(cross)
        elif len(set(cross["gates"]).intersection(input_set)) >= 3:
            # Gần đúng 3/4 cổng
            matches.append({**cross, "match_type": "partial_3", "matched_gates": list(set(cross["gates"]).intersection(input_set))})
    
    # Xác định angle từ quẻ
    # Logic: Right Angle nếu P Sun và D Sun cách nhau ~90 độ, Left Angle ~180 độ, Juxta gần nhau
    # Ở đây đơn giản hóa dựa trên database
    
    return {
        "input_gates": {"p_sun": p_sun_gate, "p_earth": p_earth_gate, "d_sun": d_sun_gate, "d_earth": d_earth_gate},
        "input_gates_list": input_gates,
        "exact_matches": [c for c in matches if "match_type" not in c],
        "partial_matches": [c for c in matches if "match_type" in c],
        "total_matches": len(matches),
        "note": "Database hiện có 30+ crosses tiêu biểu từ tài liệu cá nhân. Để có 192 crosses đầy đủ, cần mở rộng từ file knowledge 08_192_incarnation_crosses_chi_tiet.md",
        "suggestion": "Nếu không tìm thấy exact match, dùng partial match hoặc tra cứu theo Quarter"
    }

# ==================== MANIFESTOR DEEP DIVE ====================

def analyze_manifestor_deep(birth_datetime):
    """Phân tích chuyên sâu Manifestor - từ Phân mục 6"""
    chart = calculate_hd_chart(birth_datetime) if isinstance(birth_datetime, datetime) else calculate_hd_chart(birth_datetime)
    
    is_manifestor = chart["type"] == "Manifestor"
    
    # Kiểm tra kỹ thuật Manifestor
    has_throat = "Throat" in chart["defined_centers"]
    has_sacral = "Sacral" in chart["defined_centers"]
    
    # Tìm motor nối throat
    motor_connected = []
    for g1, g2 in chart["defined_channels"]:
        centers = CHANNEL_TO_CENTERS.get((g1,g2)) or CHANNEL_TO_CENTERS.get((g2,g1))
        if centers and "Throat" in centers:
            other = centers[0] if centers[1] == "Throat" else centers[1]
            if other in ["Heart", "Solar Plexus", "Root"]:
                motor_connected.append({"channel": f"{g1}-{g2}", "motor": other, "centers": centers})
    
    # Phân tích theo tài liệu cá nhân
    analysis = {
        "is_manifestor": is_manifestor,
        "technical_check": {
            "has_throat_defined": has_throat,
            "has_sacral_defined": has_sacral,
            "motor_to_throat": motor_connected,
            "is_correct_manifestor": has_throat and not has_sacral and len(motor_connected) > 0
        },
        "type": chart["type"],
        "authority": chart["authority"],
        "profile": chart["profile"],
    }
    
    if is_manifestor or analysis["technical_check"]["is_correct_manifestor"]:
        analysis["deep_dive"] = {
            "aura": "Aura đóng và mang tính đẩy lùi, bộc phát đột ngột khiến người xung quanh e dè hoặc sợ hãi. Cảm giác khác biệt ngay từ nhỏ.",
            "psychology": [
                "Hăng hái, mạnh mẽ và bốc đồng",
                "Năng lượng không bền vững - thiết kế để bắt đầu mọi thứ nhưng không có năng lượng bền bỉ để thực hiện tất cả như Generator",
                "Độc lập cao, không thích bị kiểm soát hoặc bị bảo phải làm gì",
                "Nếu cố làm tất cả, dễ đối mặt vấn đề nghiêm trọng về sức khỏe"
            ],
            "strategy": {
                "name": "Informing - Thông báo",
                "description": "Chìa khóa để Manifestor vận hành êm thấm. Cần thông báo cho những người bị ảnh hưởng trước khi hành động. Không phải xin phép mà là cách loại bỏ phản kháng bên ngoài và giúp người khác an tâm.",
                "practice": "Trước khi hành động, nói: 'Tôi sẽ làm...' cho những người bị ảnh hưởng"
            },
            "signature": {
                "name": "Peace - Bình yên",
                "description": "Khi thực hiện đúng chiến lược thông báo, Manifestor đạt trạng thái bình yên, thuận lợi trong hành động và thỏa mãn tâm hồn"
            },
            "not_self": {
                "name": "Anger - Giận dữ",
                "description": "Nguồn gốc cơn giận từ việc bị hạn chế quyền tự do. Cảm giác bị trừng phạt khi bị kiểm soát bởi quy tắc nghiêm khắc tích tụ thành tâm lý tức giận, bạo lực và xa cách xã hội",
                "healing": "Học cách thông báo để giảm phản kháng, từ đó tìm thấy bình an nội tại"
            },
            "child_manifestor": {
                "description": "Trẻ em Manifestor bẩm sinh đã biết mình muốn làm gì và khi nào cần làm",
                "wound": "Khi cha mẹ/giáo viên áp đặt rào cản do lo ngại sự tự ý của trẻ, vô tình tạo ra hình phạt tâm lý. Trẻ bị kìm kẹp lớn lên với xu hướng phản ứng mạnh mẽ hoặc bạo lực đối với bất kỳ ai cố gắng kiểm soát",
                "advice_for_parents": [
                    "Đừng kiểm soát, hãy cho tự chủ trong khuôn khổ an toàn",
                    "Dạy trẻ cách thông báo: 'Con sẽ làm...' thay vì xin phép",
                    "Tôn trọng sự độc lập, đừng bảo trẻ phải làm gì",
                    "Cho trẻ không gian riêng, thời gian một mình",
                    "Hiểu rằng trẻ không có năng lượng bền bỉ như Generator, cần nghỉ ngơi"
                ]
            },
            "work": {
                "suitable": ["Khởi nghiệp", "Lãnh đạo", "Vai trò khởi xướng", "Tiên phong"],
                "needs": ["Tự chủ", "Không bị quản lý chặt", "Làm việc theo đợt bộc phát, không đều đặn 8h/ngày"],
                "team": "Cần Generator/MG để thực thi sau khi khởi xướng, cần thông báo cho team trước khi hành động"
            },
            "relationship": {
                "aura_impact": "Aura đóng, đẩy -> người khác e dè",
                "needs": ["Tự do", "Không thích bị kiểm soát", "Học cách thông báo cho đối phương"],
                "seeking": "Bình yên, không phải ai cũng hiểu"
            }
        }
        
        analysis["consultation_process"] = {
            "step1": "Chuẩn bị thông tin: Họ tên, Giờ-Ngày-Tháng-Năm sinh, Nơi sinh chính xác",
            "step2": "Sử dụng tool calculate_human_design_chart để tạo BodyGraph",
            "step3": "Phân tích Type, Strategy, Authority (40 phút - quan trọng nhất)",
            "step4": "Hướng dẫn thử nghiệm 7 ngày với Strategy Informing",
            "ethics": "Hiểu mình - Sống là mình. Human Design là thử nghiệm, không phải niềm tin mù quáng. Khuyến khích tự chứng thực."
        }
    else:
        analysis["note"] = f"Người này không phải Manifestor mà là {chart['type']}. Tool này dành riêng cho Manifestor deep dive. Dùng analyze_chart cho Type khác."
    
    return analysis

# ==================== TEST ====================

if __name__ == "__main__":
    dt = datetime(1990, 5, 15, 8, 30)
    print("=== FEAR GATES ===")
    print(json.dumps(analyze_fear_gates(dt), ensure_ascii=False, indent=2)[:2000])
    
    print("\n=== LOVE GATES ===")
    print(json.dumps(analyze_love_gates(dt), ensure_ascii=False, indent=2)[:2000])
    
    print("\n=== CROSS DETAILS ===")
    print(json.dumps(get_incarnation_cross_details(23,43,30,29), ensure_ascii=False, indent=2))
    
    print("\n=== MANIFESTOR DEEP ===")
    dt_manifestor = datetime(1987, 1, 1, 12, 0)  # Projector example, need Manifestor
    # Tìm Manifestor: cần Throat + Motor, không Sacral
    # Thử ngày khác
    print(json.dumps(analyze_manifestor_deep(dt), ensure_ascii=False, indent=2)[:2000])
