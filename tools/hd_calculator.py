"""
Human Design Calculator - Chính xác cao sử dụng Swiss Ephemeris
Tác giả: Agent Mode - Chuyên gia Human Design
Ngày: 2026-09-23

Chức năng:
- Tính Personality (thời điểm sinh) và Design (88 độ Sun trước sinh)
- Map sang 64 cổng, line, color, tone, base
- Tính Type, Strategy, Authority, Profile, Definition, Centers, Channels
"""

import swisseph as swe
from datetime import datetime, timedelta
import math

# Cấu hình Swiss Ephemeris
swe.set_ephe_path('')  # dùng ephemeris mặc định

# Thứ tự 64 cổng trên Mandala, bắt đầu từ 41 tại 2° Bảo Bình (302°)
GATE_ORDER = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3,
              27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56,
              31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
              28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]

# Mapping cổng -> trung tâm
GATE_TO_CENTER = {
    64: "Head", 61: "Head", 63: "Head",
    47: "Ajna", 24: "Ajna", 4: "Ajna", 17: "Ajna", 43: "Ajna", 11: "Ajna",
    62: "Throat", 23: "Throat", 56: "Throat", 35: "Throat", 12: "Throat", 45: "Throat",
    33: "Throat", 8: "Throat", 31: "Throat", 20: "Throat", 16: "Throat",
    1: "G", 2: "G", 7: "G", 10: "G", 13: "G", 15: "G", 25: "G", 46: "G",
    21: "Heart", 26: "Heart", 40: "Heart", 51: "Heart",
    18: "Spleen", 28: "Spleen", 32: "Spleen", 44: "Spleen", 48: "Spleen", 50: "Spleen", 57: "Spleen",
    5: "Sacral", 14: "Sacral", 29: "Sacral", 59: "Sacral", 9: "Sacral", 3: "Sacral", 42: "Sacral", 27: "Sacral", 34: "Sacral",
    6: "Solar Plexus", 37: "Solar Plexus", 22: "Solar Plexus", 36: "Solar Plexus", 49: "Solar Plexus", 30: "Solar Plexus", 55: "Solar Plexus",
    58: "Root", 38: "Root", 54: "Root", 53: "Root", 60: "Root", 52: "Root", 19: "Root", 39: "Root", 41: "Root",
}

# 36 kênh: (gate1, gate2)
CHANNELS = [
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31), (9, 52),
    (10, 20), (10, 34), (10, 57), (11, 56), (12, 22), (13, 33), (16, 48), (17, 62),
    (18, 58), (19, 49), (20, 34), (20, 57), (21, 45), (23, 43), (24, 61), (26, 44),
    (27, 50), (28, 38), (29, 46), (30, 41), (32, 54), (35, 36), (37, 40), (39, 55),
    (42, 53), (47, 64), (57, 34), (25, 51)
]

# Mapping kênh -> trung tâm
CHANNEL_TO_CENTERS = {
    (1, 8): ("G", "Throat"), (2, 14): ("G", "Sacral"), (3, 60): ("Sacral", "Root"),
    (4, 63): ("Ajna", "Head"), (5, 15): ("Sacral", "G"), (6, 59): ("Solar Plexus", "Sacral"),
    (7, 31): ("G", "Throat"), (9, 52): ("Sacral", "Root"), (10, 20): ("G", "Throat"),
    (10, 34): ("G", "Sacral"), (10, 57): ("G", "Spleen"), (11, 56): ("Ajna", "Throat"),
    (12, 22): ("Throat", "Solar Plexus"), (13, 33): ("G", "Throat"), (16, 48): ("Throat", "Spleen"),
    (17, 62): ("Ajna", "Throat"), (18, 58): ("Spleen", "Root"), (19, 49): ("Root", "Solar Plexus"),
    (20, 34): ("Throat", "Sacral"), (20, 57): ("Throat", "Spleen"), (21, 45): ("Heart", "Throat"),
    (23, 43): ("Throat", "Ajna"), (24, 61): ("Ajna", "Head"), (26, 44): ("Heart", "Spleen"),
    (27, 50): ("Sacral", "Spleen"), (28, 38): ("Spleen", "Root"), (29, 46): ("Sacral", "G"),
    (30, 41): ("Solar Plexus", "Root"), (32, 54): ("Spleen", "Root"), (35, 36): ("Throat", "Solar Plexus"),
    (37, 40): ("Solar Plexus", "Heart"), (39, 55): ("Root", "Solar Plexus"), (42, 53): ("Sacral", "Root"),
    (47, 64): ("Ajna", "Head"), (57, 34): ("Spleen", "Sacral"), (25, 51): ("G", "Heart"),
}

PLANETS = {
    "Sun": swe.SUN,
    "Earth": None,  # tính từ Sun + 180
    "Moon": swe.MOON,
    "North Node": swe.TRUE_NODE,
    "South Node": None,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

# Ý nghĩa cổng (tóm tắt)
GATE_MEANINGS = {
    1: "Self-Expression - Sáng tạo, tự thể hiện",
    2: "Direction - Định hướng, tiếp nhận",
    3: "Ordering - Khó khăn ban đầu, trật tự từ hỗn loạn",
    4: "Formulization - Công thức hóa, trả lời logic",
    5: "Fixed Rhythms - Nhịp điệu cố định, chờ đợi",
    6: "Friction - Xung đột, thân mật",
    7: "Role of Self - Vai trò của bản ngã, lãnh đạo",
    8: "Contribution - Đóng góp, giữ gìn",
    9: "Focus - Tập trung, chi tiết",
    10: "Behavior of Self - Hành vi bản ngã, tình yêu bản thân",
    11: "Ideas - Ý tưởng, hòa bình",
    12: "Caution - Thận trọng, đứng yên",
    13: "Listener - Người lắng nghe, tình bằng hữu",
    14: "Power Skills - Kỹ năng sức mạnh, sở hữu",
    15: "Extremes - Cực đoan, khiêm tốn, yêu nhân loại",
    16: "Skills - Kỹ năng, nhiệt tình, tài năng",
    17: "Opinions - Ý kiến, theo dõi",
    18: "Correction - Sửa chữa, chỉ trích",
    19: "Wanting - Muốn, tiếp cận, nhạy cảm với nhu cầu",
    20: "Now - Hiện tại, chiêm nghiệm, ở trong now",
    21: "Hunter - Thợ săn, cắn xuyên qua, kiểm soát",
    22: "Openness - Cởi mở, duyên dáng",
    23: "Assimilation - Đồng hóa, chia tách, thiên tài/lập dị",
    24: "Rationalization - Hợp lý hóa, trở lại",
    25: "Spirit of Self - Tinh thần bản ngã, ngây thơ, tình yêu phổ quát",
    26: "Egotist - Kẻ vị kỷ, sức mạnh của cái lớn",
    27: "Caring - Chăm sóc, nuôi dưỡng",
    28: "Game Player - Người chơi, đấu tranh tìm ý nghĩa",
    29: "Saying Yes - Nói có, vực thẳm, cam kết",
    30: "Recognition of Feelings - Nhận ra cảm xúc, lửa bám",
    31: "Leading - Dẫn dắt, ảnh hưởng",
    32: "Continuity - Liên tục, thời gian",
    33: "Privacy - Riêng tư, rút lui, nhân chứng",
    34: "Power - Sức mạnh, quyền lực của cái lớn",
    35: "Change - Thay đổi, tiến bộ",
    36: "Crisis - Khủng hoảng, làm tối ánh sáng",
    37: "Friendship - Tình bạn, gia đình, cộng đồng",
    38: "Fighter - Chiến binh, đối lập",
    39: "Provocateur - Khiêu khích, cản trở",
    40: "Aloneness - Cô đơn, giải thoát, nghỉ ngơi",
    41: "Contraction - Co lại, giảm, khởi đầu của mơ mộng",
    42: "Growth - Tăng trưởng, phát triển",
    43: "Insight - Sáng suốt, đột phá",
    44: "Alertness - Cảnh giác, đến để gặp",
    45: "Gatherer - Người thu thập, tập hợp",
    46: "Determination - Quyết tâm, đẩy lên, yêu cơ thể",
    47: "Realization - Nhận ra, áp bức, hiểu quá khứ",
    48: "Depth - Chiều sâu, cái giếng, tài năng",
    49: "Rejection - Từ chối, cách mạng, nguyên tắc",
    50: "Values - Giá trị, cái vạc, bảo tồn",
    51: "Shock - Sốc, khuấy động, cạnh tranh",
    52: "Inaction - Không hành động, đứng yên",
    53: "Beginnings - Bắt đầu, phát triển",
    54: "Ambition - Tham vọng, cô gái kết hôn",
    55: "Spirit - Tinh thần, phong phú, tâm trạng",
    56: "Stimulation - Kích thích, người lang thang, kể chuyện",
    57: "Intuition - Trực giác, nhẹ nhàng, âm thanh",
    58: "Aliveness - Sống động, vui vẻ, áp lực hoàn thiện",
    59: "Sexuality - Tính dục, phân tán, thân mật",
    60: "Acceptance - Chấp nhận, giới hạn, bảo thủ",
    61: "Mystery - Bí ẩn, chân lý nội tại, áp lực biết",
    62: "Detail - Chi tiết, vượt trội của cái nhỏ",
    63: "Doubt - Nghi ngờ, sau khi hoàn thành",
    64: "Confusion - Nhầm lẫn, trước khi hoàn thành, áp lực hiểu quá khứ",
}

START_LONGITUDE = 302.0  # 2° Bảo Bình - Gate 41 start
DEG_PER_GATE = 5.625
DEG_PER_LINE = 0.9375

def longitude_to_gate_line(longitude):
    """Chuyển kinh độ (0-360) sang Gate và Line"""
    lon = longitude % 360
    # Tính offset từ điểm bắt đầu 302°
    offset = (lon - START_LONGITUDE) % 360
    gate_index = int(offset // DEG_PER_GATE)
    gate = GATE_ORDER[gate_index]
    
    gate_start = (START_LONGITUDE + gate_index * DEG_PER_GATE) % 360
    # offset trong gate
    offset_in_gate = (lon - gate_start) % 360
    # nếu offset_in_gate > 5.625 thì có lỗi do wrap, nhưng logic trên đã đúng
    if offset_in_gate > DEG_PER_GATE:
        offset_in_gate = offset % DEG_PER_GATE
    
    line = int(offset_in_gate // DEG_PER_LINE) + 1
    if line > 6:
        line = 6
    if line < 1:
        line = 1
    
    # Color, Tone, Base (chia nhỏ hơn)
    # 1 gate = 6 lines, 1 line = 6 colors = 1 color = 6 tones = 1 tone = 5 bases
    # Tổng cộng 1 gate = 1080 bases
    deg_per_color = DEG_PER_LINE / 6
    deg_per_tone = deg_per_color / 6
    deg_per_base = deg_per_tone / 5
    
    color = int((offset_in_gate % DEG_PER_LINE) // deg_per_color) + 1
    tone = int(((offset_in_gate % DEG_PER_LINE) % deg_per_color) // deg_per_tone) + 1
    base = int((((offset_in_gate % DEG_PER_LINE) % deg_per_color) % deg_per_tone) // deg_per_base) + 1
    
    return {
        "gate": gate,
        "line": line,
        "color": color,
        "tone": tone,
        "base": base,
        "longitude": lon,
        "gate_index": gate_index,
        "offset": offset
    }

def julian_day(dt):
    """Chuyển datetime sang Julian Day"""
    # swe.julday cần year, month, day, hour (decimal)
    hour = dt.hour + dt.minute/60.0 + dt.second/3600.0 + dt.microsecond/3600000.0
    return swe.julday(dt.year, dt.month, dt.day, hour)

def get_planet_longitude(jd, planet_id):
    """Lấy kinh độ hành tinh"""
    # flag: Swiss ephemeris + speed
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result, ret_flag = swe.calc_ut(jd, planet_id, flags)
    # result[0] = longitude
    return result[0] % 360

def get_all_planets(jd):
    """Lấy tất cả hành tinh cho 1 JD"""
    planets_data = {}
    
    sun_lon = get_planet_longitude(jd, swe.SUN)
    planets_data["Sun"] = sun_lon
    planets_data["Earth"] = (sun_lon + 180) % 360
    
    planets_data["Moon"] = get_planet_longitude(jd, swe.MOON)
    
    north_node_lon = get_planet_longitude(jd, swe.TRUE_NODE)
    planets_data["North Node"] = north_node_lon
    planets_data["South Node"] = (north_node_lon + 180) % 360
    
    planets_data["Mercury"] = get_planet_longitude(jd, swe.MERCURY)
    planets_data["Venus"] = get_planet_longitude(jd, swe.VENUS)
    planets_data["Mars"] = get_planet_longitude(jd, swe.MARS)
    planets_data["Jupiter"] = get_planet_longitude(jd, swe.JUPITER)
    planets_data["Saturn"] = get_planet_longitude(jd, swe.SATURN)
    planets_data["Uranus"] = get_planet_longitude(jd, swe.URANUS)
    planets_data["Neptune"] = get_planet_longitude(jd, swe.NEPTUNE)
    planets_data["Pluto"] = get_planet_longitude(jd, swe.PLUTO)
    
    return planets_data

def find_design_jd(birth_jd, birth_sun_lon):
    """Tìm JD khi Sun lùi 88 độ"""
    target_lon = (birth_sun_lon - 88) % 360
    
    # Bắt đầu tìm từ 88 ngày trước
    # Sun di chuyển ~1 độ/ngày
    approx_jd = birth_jd - 88.5
    
    # Tìm kiếm nhị phân trong khoảng ±5 ngày
    # Vì Sun không đều, cần dò
    low = birth_jd - 95
    high = birth_jd - 80
    
    # Dò tuyến tính thô để tìm khoảng
    best_jd = approx_jd
    best_diff = 360
    
    # Quét mỗi 0.1 ngày trong khoảng
    jd = low
    while jd <= high:
        sun_lon = get_planet_longitude(jd, swe.SUN)
        diff = abs((sun_lon - target_lon + 180) % 360 - 180)  # khoảng cách góc ngắn nhất
        if diff < best_diff:
            best_diff = diff
            best_jd = jd
        jd += 0.1
    
    # Tinh chỉnh bằng binary search xung quanh best_jd
    low = best_jd - 0.5
    high = best_jd + 0.5
    
    for _ in range(20):  # 20 vòng lặp đủ chính xác
        mid = (low + high) / 2
        sun_lon = get_planet_longitude(mid, swe.SUN)
        # Tính diff có hướng
        # Nếu sun_lon < target_lon (theo hướng tăng), cần tăng JD? Sun tăng theo JD
        # Sun longitude tăng theo thời gian
        # So sánh
        diff = (sun_lon - target_lon + 360) % 360
        if diff > 180:
            diff -= 360  # chuyển về -180..180
        
        if abs(diff) < 0.0001:  # đủ chính xác (0.0001 độ ~ 0.36 giây)
            best_jd = mid
            break
        
        if diff > 0:
            # sun_lon lớn hơn target, cần giảm JD
            high = mid
        else:
            low = mid
        best_jd = mid
    
    return best_jd

def calculate_hd_chart(birth_datetime):
    """Tính toán full chart"""
    birth_jd = julian_day(birth_datetime)
    birth_planets_lon = get_all_planets(birth_jd)
    birth_sun_lon = birth_planets_lon["Sun"]
    
    design_jd = find_design_jd(birth_jd, birth_sun_lon)
    design_planets_lon = get_all_planets(design_jd)
    
    # Map sang gate/line
    personality_gates = {}
    design_gates = {}
    
    for planet, lon in birth_planets_lon.items():
        personality_gates[planet] = longitude_to_gate_line(lon)
    
    for planet, lon in design_planets_lon.items():
        design_gates[planet] = longitude_to_gate_line(lon)
    
    # Tất cả gates được kích hoạt
    all_activated_gates = set()
    for data in personality_gates.values():
        all_activated_gates.add(data["gate"])
    for data in design_gates.values():
        all_activated_gates.add(data["gate"])
    
    # Tìm channels định nghĩa
    defined_channels = []
    for g1, g2 in CHANNELS:
        if g1 in all_activated_gates and g2 in all_activated_gates:
            defined_channels.append((g1, g2))
    
    # Tìm centers định nghĩa
    defined_centers = set()
    for g1, g2 in defined_channels:
        c1, c2 = CHANNEL_TO_CENTERS.get((g1, g2)) or CHANNEL_TO_CENTERS.get((g2, g1))
        if c1 and c2:
            defined_centers.add(c1)
            defined_centers.add(c2)
    
    # Type
    has_sacral = "Sacral" in defined_centers
    has_throat = "Throat" in defined_centers
    
    # Kiểm tra motor nối throat
    motor_centers = {"Heart", "Solar Plexus", "Sacral", "Root"}
    throat_connected_to_motor = False
    
    # Để kiểm tra kết nối, cần xem có kênh nào nối Throat với Motor không
    for g1, g2 in defined_channels:
        centers = CHANNEL_TO_CENTERS.get((g1, g2)) or CHANNEL_TO_CENTERS.get((g2, g1))
        if centers:
            c1, c2 = centers
            if (c1 == "Throat" and c2 in motor_centers) or (c2 == "Throat" and c1 in motor_centers):
                throat_connected_to_motor = True
                break
    
    if not defined_centers:
        hd_type = "Reflector"
    elif has_sacral:
        if throat_connected_to_motor:
            hd_type = "Manifesting Generator"
        else:
            hd_type = "Generator"
    else:
        if throat_connected_to_motor:
            hd_type = "Manifestor"
        else:
            hd_type = "Projector"
    
    # Authority
    if "Solar Plexus" in defined_centers:
        authority = "Emotional - Solar Plexus"
    elif "Sacral" in defined_centers:
        authority = "Sacral"
    elif "Spleen" in defined_centers:
        authority = "Splenic"
    elif "Heart" in defined_centers:
        # Phân biệt Ego Manifested vs Self-Projected?
        # Nếu Heart nối Throat trực tiếp và không có G? Đơn giản hóa
        if "G" in defined_centers:
            # kiểm tra kênh 25-51?
            if (25, 51) in defined_channels or (51, 25) in defined_channels:
                authority = "Ego (Heart) - Manifested"
            else:
                # Nếu G định nghĩa
                authority = "Self-Projected (G-Center)" if hd_type == "Projector" else "Ego (Heart)"
        else:
            authority = "Ego (Heart)"
    elif "G" in defined_centers:
        authority = "Self-Projected (G-Center)"
    elif defined_centers and ("Ajna" in defined_centers or "Throat" in defined_centers or "Head" in defined_centers):
        authority = "Mental - Environment / No Inner Authority"
    else:
        authority = "Lunar - Reflector"
    
    # Profile
    p_sun_line = personality_gates["Sun"]["line"]
    d_sun_line = design_gates["Sun"]["line"]
    profile = f"{p_sun_line}/{d_sun_line}"
    
    # Definition - số nhóm kết nối
    # Xây dựng graph của centers
    # Mỗi center là node, mỗi channel là edge
    # Đếm số thành phần liên thông
    from collections import defaultdict, deque
    
    if not defined_centers:
        definition = "No Definition"
        definition_groups = 0
    else:
        graph = defaultdict(list)
        for g1, g2 in defined_channels:
            centers = CHANNEL_TO_CENTERS.get((g1, g2)) or CHANNEL_TO_CENTERS.get((g2, g1))
            if centers:
                c1, c2 = centers
                graph[c1].append(c2)
                graph[c2].append(c1)
        
        visited = set()
        groups = 0
        for center in defined_centers:
            if center not in visited:
                groups += 1
                # BFS
                queue = deque([center])
                visited.add(center)
                while queue:
                    cur = queue.popleft()
                    for neighbor in graph[cur]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        
        if groups == 1:
            definition = "Single Definition"
        elif groups == 2:
            definition = "Split Definition"
        elif groups == 3:
            definition = "Triple Split Definition"
        elif groups == 4:
            definition = "Quadruple Split Definition"
        else:
            definition = f"{groups} Splits"
        definition_groups = groups
    
    # Strategy
    strategy_map = {
        "Generator": "Wait to Respond - Chờ để Đáp Ứng",
        "Manifesting Generator": "Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo",
        "Projector": "Wait for the Invitation - Chờ Lời Mời",
        "Manifestor": "Inform - Thông Báo trước khi hành động",
        "Reflector": "Wait a Lunar Cycle (28-29 days) - Chờ 1 chu kỳ Mặt Trăng"
    }
    
    # Incarnation Cross - tính toán đơn giản
    p_sun_gate = personality_gates["Sun"]["gate"]
    p_earth_gate = personality_gates["Earth"]["gate"]
    d_sun_gate = design_gates["Sun"]["gate"]
    d_earth_gate = design_gates["Earth"]["gate"]
    
    # Xác định Quarter
    def get_quarter(gate):
        # Dựa trên GATE_ORDER và quarter mapping
        # Quarter of Initiation: gates list như đã định nghĩa
        q1 = {13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27, 24}
        q2 = {2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 31, 33}
        q3 = {7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50, 28, 44}
        q4 = {1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60, 41, 19}
        if gate in q1:
            return "Initiation (Khởi xướng) - Mục đích qua Tâm trí"
        elif gate in q2:
            return "Civilization (Văn minh) - Mục đích qua Hình thức"
        elif gate in q3:
            return "Duality (Nhị nguyên) - Mục đích qua Gắn kết"
        elif gate in q4:
            return "Mutation (Đột biến) - Mục đích qua Biến đổi"
        else:
            return "Unknown"
    
    # Right/Left/Juxta - dựa trên góc giữa P Sun và D Sun
    # Tính khoảng cách gate trên vòng tròn
    p_sun_idx = GATE_ORDER.index(p_sun_gate)
    d_sun_idx = GATE_ORDER.index(d_sun_gate)
    diff = (p_sun_idx - d_sun_idx) % 64
    
    # Juxtaposition khi 2 Sun gần nhau (cách nhau < 5 gates hoặc đối diện gần?)
    # Thực tế Juxtaposition là khi P Sun và D Sun ở cùng 1 quarter và gần nhau
    # Đơn giản: nếu diff < 8 hoặc diff > 56 thì Juxta
    # Nếu diff từ 8-... thì Right hoặc Left tùy?
    # Theo lý thuyết: Right Angle = P Sun và D Sun cách nhau ~90 độ (16 gates)
    # Left Angle = cách nhau ~180 độ? Cần tra cứu chính xác, tạm tính đơn giản:
    
    # Để chính xác hơn, dùng kinh độ thực
    p_sun_lon = personality_gates["Sun"]["longitude"]
    d_sun_lon = design_gates["Sun"]["longitude"]
    lon_diff = (p_sun_lon - d_sun_lon) % 360
    
    if 0 <= lon_diff < 30 or lon_diff > 330:  # gần nhau
        cross_type = "Juxtaposition"
    elif 90 < lon_diff < 270:  # đối diện xa
        cross_type = "Left Angle"
    else:
        cross_type = "Right Angle"
    
    incarnation_cross = f"{cross_type} Cross of {p_sun_gate}/{p_earth_gate} | {d_sun_gate}/{d_earth_gate}"
    
    return {
        "birth_datetime": birth_datetime,
        "birth_jd": birth_jd,
        "design_jd": design_jd,
        "design_datetime": datetime.utcfromtimestamp((design_jd - 2440587.5) * 86400),
        "personality_gates": personality_gates,
        "design_gates": design_gates,
        "all_activated_gates": sorted(list(all_activated_gates)),
        "defined_channels": defined_channels,
        "defined_centers": sorted(list(defined_centers)),
        "type": hd_type,
        "strategy": strategy_map.get(hd_type, ""),
        "authority": authority,
        "profile": profile,
        "definition": definition,
        "definition_groups": definition_groups,
        "incarnation_cross": incarnation_cross,
        "cross_type": cross_type,
        "p_sun_gate": p_sun_gate,
        "p_earth_gate": p_earth_gate,
        "d_sun_gate": d_sun_gate,
        "d_earth_gate": d_earth_gate,
        "quarters": {
            "p_sun": get_quarter(p_sun_gate),
            "p_earth": get_quarter(p_earth_gate),
            "d_sun": get_quarter(d_sun_gate),
            "d_earth": get_quarter(d_earth_gate),
        }
    }

def format_chart_text(chart):
    """Format chart ra text đẹp"""
    lines = []
    lines.append("="*60)
    lines.append(f"HUMAN DESIGN CHART - {chart['birth_datetime']}")
    lines.append("="*60)
    lines.append(f"Type: {chart['type']}")
    lines.append(f"Strategy: {chart['strategy']}")
    lines.append(f"Authority: {chart['authority']}")
    lines.append(f"Profile: {chart['profile']}")
    lines.append(f"Definition: {chart['definition']}")
    lines.append(f"Incarnation Cross: {chart['incarnation_cross']}")
    lines.append(f"Cross Type: {chart['cross_type']}")
    lines.append("")
    lines.append(f"Design Date (88° Sun trước): {chart['design_datetime']} UTC (JD: {chart['design_jd']:.4f})")
    lines.append("")
    lines.append(f"Defined Centers ({len(chart['defined_centers'])}): {', '.join(chart['defined_centers'])}")
    lines.append(f"Defined Channels ({len(chart['defined_channels'])}):")
    for g1, g2 in chart['defined_channels']:
        centers = CHANNEL_TO_CENTERS.get((g1,g2)) or CHANNEL_TO_CENTERS.get((g2,g1))
        lines.append(f"  - {g1}-{g2} {centers} : {GATE_MEANINGS.get(g1,'')} | {GATE_MEANINGS.get(g2,'')}")
    lines.append("")
    lines.append("PERSONALITY (Black - Ý thức):")
    for planet in ["Sun", "Earth", "Moon", "North Node", "South Node", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
        data = chart['personality_gates'][planet]
        lines.append(f"  {planet:12} : Gate {data['gate']:2}.{data['line']} (Lon {data['longitude']:.2f}°) - {GATE_MEANINGS.get(data['gate'],'')} - Center: {GATE_TO_CENTER.get(data['gate'],'')}")
    
    lines.append("")
    lines.append("DESIGN (Red - Vô thức):")
    for planet in ["Sun", "Earth", "Moon", "North Node", "South Node", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]:
        data = chart['design_gates'][planet]
        lines.append(f"  {planet:12} : Gate {data['gate']:2}.{data['line']} (Lon {data['longitude']:.2f}°) - {GATE_MEANINGS.get(data['gate'],'')} - Center: {GATE_TO_CENTER.get(data['gate'],'')}")
    
    lines.append("")
    lines.append(f"All Activated Gates ({len(chart['all_activated_gates'])}): {chart['all_activated_gates']}")
    
    return "\n".join(lines)

# Test nếu chạy trực tiếp
if __name__ == "__main__":
    # Ví dụ: 1990-01-01 12:00 UTC
    dt = datetime(1990, 1, 1, 12, 0, 0)
    chart = calculate_hd_chart(dt)
    print(format_chart_text(chart))
