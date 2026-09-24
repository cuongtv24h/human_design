"""
Human Design MCP Server v3.0 - Chuẩn Model Context Protocol
30 Tools (8 core + 4 advanced + 2 general + 2 money + 2 potential + 12 v3.0) + 11 Resources

Tích hợp tài liệu cá nhân 7 files 989 dòng + Full Money Map 60 biến thể
v2.2 MỚI: Thêm 2 tools money chuyên dụng - Full Money Map theo Type/Profile/Heart/Channels
v3.0 MỚI (Option C Full): +12 tools 6 domains (Health, Relationship+Composite, Decision, Deconditioning, Purpose, Team) - Hoàn chỉnh 7 nhu cầu + FIX shadowing bug 6 wrappers (alias imports)
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from mcp.server.fastmcp import FastMCP, Context
from hd_calculator import calculate_hd_chart, format_chart_text, GATE_MEANINGS, GATE_TO_CENTER, CHANNEL_TO_CENTERS, GATE_ORDER, CHANNELS
from hd_analyzer import analyze_chart, TYPE_ANALYSIS, PROFILE_ANALYSIS, CENTER_ANALYSIS

try:
    from hd_advanced_tools import analyze_fear_gates as adv_fear, analyze_love_gates as adv_love, get_incarnation_cross_details as adv_cross, analyze_manifestor_deep as adv_manifestor
    ADV_AVAILABLE = True
except:
    ADV_AVAILABLE = False

try:
    from hd_consultation_general import analyze_consultation_general as mod_analyze_consultation, format_consultation_report as mod_format_consultation
    GENERAL_AVAILABLE = True
except:
    GENERAL_AVAILABLE = False

try:
    from hd_money_analysis import analyze_money_map as mod_analyze_money, format_money_report as mod_format_money
    MONEY_AVAILABLE = True
except:
    MONEY_AVAILABLE = False

try:
    from hd_potential_analysis import analyze_potential_blindspots as mod_analyze_potential, format_potential_report as mod_format_potential
    POTENTIAL_AVAILABLE = True
except:
    POTENTIAL_AVAILABLE = False


try:
    from hd_health_analysis import analyze_health as mod_analyze_health, format_health_report as mod_format_health
    HEALTH_AVAILABLE = True
except:
    HEALTH_AVAILABLE = False

try:
    from hd_relationship_analysis import analyze_relationship as mod_analyze_relationship, format_relationship_report as mod_format_relationship
    RELATIONSHIP_AVAILABLE = True
except:
    RELATIONSHIP_AVAILABLE = False

try:
    from hd_decision_analysis import analyze_decision as mod_analyze_decision, format_decision_report as mod_format_decision
    DECISION_AVAILABLE = True
except:
    DECISION_AVAILABLE = False

try:
    from hd_deconditioning_analysis import analyze_deconditioning as mod_analyze_decond, format_deconditioning_report as mod_format_decond
    DECOND_AVAILABLE = True
except:
    DECOND_AVAILABLE = False

try:
    from hd_purpose_analysis import analyze_purpose as mod_analyze_purpose, format_purpose_report as mod_format_purpose
    PURPOSE_AVAILABLE = True
except:
    PURPOSE_AVAILABLE = False

try:
    from hd_team_analysis import analyze_team as mod_analyze_team, format_team_report as mod_format_team
    TEAM_AVAILABLE = True
except:
    TEAM_AVAILABLE = False

mcp = FastMCP(name="human-design-analyzer", instructions="Human Design v3.0 - 30 tools (8 core + 4 advanced + 2 general + 2 money + 2 potential + 12 v3.0: health/relationship/decision/deconditioning/purpose/team), Swiss Ephemeris, 7 nhu cầu thực tế hoàn chỉnh", dependencies=["pyswisseph", "pydantic"])

def parse_birth_datetime(date_str: str, time_str: str, tz_str: str = "+07:00") -> datetime:
    dt_str = f"{date_str} {time_str}"
    try:
        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except:
        dt_naive = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    if tz_str.startswith("+") or tz_str.startswith("-"):
        sign = 1 if tz_str[0] == "+" else -1
        tz_clean = tz_str.replace(":", "")
        hours = int(tz_clean[1:3]) if len(tz_clean) >=3 else int(tz_clean[1:])
        mins = int(tz_clean[3:5]) if len(tz_clean) >=5 else 0
        offset = timedelta(hours=sign*hours, minutes=sign*mins)
        tz = timezone(offset)
        dt_aware = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        offset = timedelta(hours=7)
        tz = timezone(offset)
        dt_aware = dt_naive.replace(tzinfo=tz)
        dt_utc = dt_aware.astimezone(timezone.utc).replace(tzinfo=None)
    return dt_utc

def chart_to_dict(chart: dict) -> dict:
    return {
        "birth_datetime_utc": str(chart["birth_datetime"]),
        "design_datetime_utc": str(chart["design_datetime"]),
        "type": chart["type"],
        "strategy": chart["strategy"],
        "authority": chart["authority"],
        "profile": chart["profile"],
        "definition": chart["definition"],
        "incarnation_cross": chart["incarnation_cross"],
        "cross_type": chart["cross_type"],
        "defined_centers": chart["defined_centers"],
        "defined_channels": [{"gates": list(ch), "centers": CHANNEL_TO_CENTERS.get(ch) or CHANNEL_TO_CENTERS.get((ch[1], ch[0]))} for ch in chart["defined_channels"]],
        "all_activated_gates": chart["all_activated_gates"],
        "p_sun_gate": chart["p_sun_gate"],
        "p_earth_gate": chart["p_earth_gate"],
        "d_sun_gate": chart["d_sun_gate"],
        "d_earth_gate": chart["d_earth_gate"],
    }

# ==================== 18 TOOLS ====================

@mcp.tool()
def calculate_human_design_chart(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """TOOL CỐT LÕI - Tính toán bản đồ Human Design chính xác từ ngày giờ sinh. Swiss Ephemeris NASA JPL DE431"""
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        chart = calculate_hd_chart(dt_utc)
        result = chart_to_dict(chart)
        result["name"] = name
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_human_design_deep(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", focus_area: str = "full") -> str:
    """Phân tích chuyên sâu Human Design tiếng Việt"""
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        chart = calculate_hd_chart(dt_utc)
        return analyze_chart(chart)
    except Exception as e:
        return f"Lỗi: {str(e)}"

@mcp.tool()
def get_gate_info(gate_number: int) -> Dict[str, Any]:
    """Tra cứu 1 cổng Gate 1-64"""
    if not 1 <= gate_number <= 64:
        return {"error": "Gate 1-64"}
    channels_of_gate = []
    for g1, g2 in CHANNELS:
        if gate_number in (g1, g2):
            other = g2 if g1 == gate_number else g1
            centers = CHANNEL_TO_CENTERS.get((g1, g2)) or CHANNEL_TO_CENTERS.get((g2, g1))
            channels_of_gate.append({"channel": f"{g1}-{g2}", "other_gate": other, "centers": centers, "other_meaning": GATE_MEANINGS.get(other)})
    gate_index = GATE_ORDER.index(gate_number) if gate_number in GATE_ORDER else -1
    return {"gate": gate_number, "meaning": GATE_MEANINGS.get(gate_number), "center": GATE_TO_CENTER.get(gate_number), "channels": channels_of_gate, "mandala_index": gate_index}

@mcp.tool()
def get_center_info(center_name: str) -> Dict[str, Any]:
    """Tra cứu 1 trung tâm: Head, Ajna, Throat, G, Heart, Spleen, Sacral, Solar Plexus, Root"""
    valid = ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]
    cmap = {c.lower(): c for c in valid}
    cmap["solar"] = "Solar Plexus"
    cmap["ego"] = "Heart"
    norm = cmap.get(center_name.lower(), center_name)
    if norm not in valid:
        return {"error": f"Chọn trong {valid}"}
    gates = [g for g,c in GATE_TO_CENTER.items() if c==norm]
    info = CENTER_ANALYSIS.get(norm, {})
    return {"center": norm, "gates": gates, "gates_count": len(gates), "defined_meaning": info.get("defined",""), "undefined_meaning": info.get("undefined",""), "is_motor": norm in ["Heart","Solar Plexus","Sacral","Root"]}

@mcp.tool()
def get_channel_info(gate1: int, gate2: int) -> Dict[str, Any]:
    """Tra cứu 1 kênh Channel"""
    channel = (gate1, gate2)
    if channel not in CHANNEL_TO_CENTERS and (gate2, gate1) in CHANNEL_TO_CENTERS:
        channel = (gate2, gate1)
    if channel not in CHANNEL_TO_CENTERS:
        for g1,g2 in CHANNELS:
            if {g1,g2}=={gate1,gate2}:
                channel=(g1,g2)
                break
    if channel not in CHANNEL_TO_CENTERS:
        return {"error": f"Kênh {gate1}-{gate2} không tồn tại"}
    centers = CHANNEL_TO_CENTERS.get(channel)
    g1,g2 = channel
    return {"channel": f"{g1}-{g2}", "gates": [g1,g2], "gate_meanings": [GATE_MEANINGS.get(g1), GATE_MEANINGS.get(g2)], "centers": centers}

@mcp.tool()
def get_profile_info(profile: str) -> Dict[str, Any]:
    """Tra cứu Profile 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3"""
    valid = ["1/3","1/4","2/4","2/5","3/5","3/6","4/6","4/1","5/1","5/2","6/2","6/3"]
    if profile not in valid:
        return {"error": f"Profile hợp lệ: {valid}"}
    return {"profile": profile, "meaning": PROFILE_ANALYSIS.get(profile)}

@mcp.tool()
def compare_charts(person1_date: str, person1_time: str, person1_name: str = "Person 1", person2_date: str = "", person2_time: str = "", person2_name: str = "Person 2", timezone: str = "+07:00") -> Dict[str, Any]:
    """So sánh 2 bản đồ (Composite) - electromagnetic, dominance"""
    try:
        dt1 = parse_birth_datetime(person1_date, person1_time, timezone)
        dt2 = parse_birth_datetime(person2_date, person2_time, timezone)
        c1 = calculate_hd_chart(dt1)
        c2 = calculate_hd_chart(dt2)
        g1 = set(c1["all_activated_gates"])
        g2 = set(c2["all_activated_gates"])
        electromag = []
        for a,b in CHANNELS:
            if (a in g1 and b in g2) or (b in g1 and a in g2):
                if (a,b) not in c1["defined_channels"] and (b,a) not in c1["defined_channels"] and (a,b) not in c2["defined_channels"] and (b,a) not in c2["defined_channels"]:
                    electromag.append(f"{a}-{b}")
        return {"person1": {"name": person1_name, "type": c1["type"], "profile": c1["profile"]}, "person2": {"name": person2_name, "type": c2["type"], "profile": c2["profile"]}, "electromagnetic": electromag, "common_gates": list(g1.intersection(g2))}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_full_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "", format: str = "markdown") -> str:
    """Tạo báo cáo đầy đủ markdown/json"""
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        chart = calculate_hd_chart(dt_utc)
        text_chart = format_chart_text(chart)
        deep = analyze_chart(chart)
        if format=="json":
            return json.dumps(chart_to_dict(chart), ensure_ascii=False, indent=2)
        return f"# BÁO CÁO HUMAN DESIGN - {name}\n\n{text_chart}\n\n{deep}"
    except Exception as e:
        return f"Lỗi: {str(e)}"

# Advanced tools từ docs cá nhân
@mcp.tool()
def analyze_fear_gates(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "") -> Dict[str, Any]:
    """MỚI từ Phân mục 4 - Phân tích 19 cổng Sợ hãi/Lo âu/Hồi hộp"""
    if not ADV_AVAILABLE:
        return {"error": "Advanced tools chưa cài"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = adv_fear(dt_utc)
        result["name"]=name
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_love_gates(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "") -> Dict[str, Any]:
    """MỚI từ Phân mục 5 - Phân tích 4 Vessel of Love + 7 Mundane Love"""
    if not ADV_AVAILABLE:
        return {"error": "Advanced tools chưa cài"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = adv_love(dt_utc)
        result["name"]=name
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_incarnation_cross_details(p_sun_gate: int, p_earth_gate: int, d_sun_gate: int, d_earth_gate: int) -> Dict[str, Any]:
    """MỚI từ Phân mục 3 - Tra cứu 192 Incarnation Crosses"""
    if not ADV_AVAILABLE:
        return {"error": "Advanced tools chưa cài"}
    try:
        return adv_cross(p_sun_gate, p_earth_gate, d_sun_gate, d_earth_gate)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def analyze_manifestor_deep(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "") -> Dict[str, Any]:
    """MỚI từ Phân mục 6 - Chuyên luận Manifestor 9%"""
    if not ADV_AVAILABLE:
        return {"error": "Advanced tools chưa cài"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = adv_manifestor(dt_utc)
        result["name"]=name
        return result
    except Exception as e:
        return {"error": str(e)}

# GENERAL TOOL - ÁP DỤNG CHO TẤT CẢ TYPES/PROFILES
@mcp.tool()
def analyze_consultation_general(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    TOOL TỔNG QUÁT - Áp dụng cho TẤT CẢ Types/Profiles - 5 Types x 12 Profiles = 60 biến thể
    
    Đây là tool TỔNG QUÁT NHẤT, áp dụng cho 100% dân số:
    - 5 Types: Manifestor (9%), Generator (36%), MG (32%), Projector (22%), Reflector (1%)
    - 12 Profiles: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3
    - Quy trình tham vấn chuyên nghiệp 4 bước + buổi đọc 1-2 giờ chuẩn
    - Deep dive chi tiết cho từng Type/Profile cụ thể
    
    Khác với analyze_manifestor_deep (chỉ cho Manifestor), tool này cho TẤT CẢ.
    
    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    
    Returns:
        Báo cáo tham vấn tổng quát với deep dive Type + Profile + Fear + Love + quy trình
    """
    if not GENERAL_AVAILABLE:
        return {"error": "General tool chưa cài đặt - kiểm tra hd_consultation_general.py"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_consultation(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_consultation_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """Tạo báo cáo tham vấn tổng quát đầy đủ (markdown) - Áp dụng cho TẤT CẢ Types/Profiles"""
    if not GENERAL_AVAILABLE:
        return "General tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_consultation(dt_utc, name=name)
        return mod_format_consultation(data)
    except Exception as e:
        return f"Lỗi: {str(e)}"

# MONEY TOOLS - CHUYÊN DỤNG DÒNG TIỀN - MỚI v2.2
@mcp.tool()
def analyze_money_map(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v2.2 - TOOL CHUYÊN DỤNG TIỀN BẠC - Full Money Map - Dòng tiền theo Type/Profile/Heart/Channels
    
    Phân tích chuyên sâu dòng tiền, tài chính, business model, pricing, investment theo Human Design:
    - 5 Types Money Strategy: Manifestor khởi xướng+inform, Generator respond+Sacral uh-huh, MG đa dòng tiền, Projector invitation+premium pricing cao cho ít giờ, Reflector môi trường+lunar 28 ngày
    - 12 Profiles Money Style: 1/3 nghiên cứu thử sai, 4/1 hiếm 2% định mệnh cố định 1 đường tiền, 5/1 bị kỳ vọng lớn, 6/2 3 giai đoạn tỏa sáng sau 50
    - Heart/Ego Center: Trung tâm tiền bạc quan trọng nhất - Defined 35% (có ý chí, giữ lời hứa) vs Undefined 65% (trí tuệ về giá trị, bẫy chứng minh giá trị qua tiền)
    - Money Channels 6 kênh: 21-45 Money (quản lý vật chất), 26-44 Surrender (bán hàng), 40-37 Community (cộng đồng), 32-54 Transformation (tham vọng), 14-2 Beat (tài nguyên), 5-15 Rhythm (dòng tiền đều đặn)
    - Money Gates 14 cổng: 21 Control, 45 Gatherer, 26 Egoist, 44 Alertness, 14 Power Skills, 2 Direction, 32 Continuity, 54 Ambition, 40 Aloneness, 37 Friendship, 5 Fixed Rhythm, 15 Extremes, 19 Wanting, 49 Revolution
    - Definition Money: Single (solopreneur), Split (cần đối tác), Triple/Quadruple (cần team)
    - Authority Money: Ra quyết định tiền theo Authority
    - Pricing, Business Model, Investment, Saving/Spending theo Type
    
    Áp dụng cho 100% dân số - 60 biến thể - Full Money Map
    Khác với general consultation (tổng quát), tool này CHUYÊN SÂU về TIỀN.
    
    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not MONEY_AVAILABLE:
        return {"error": "Money tool chưa cài đặt - kiểm tra hd_money_analysis.py"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_money(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_money_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v2.2 - Tạo báo cáo Full Money Map đầy đủ markdown - Dòng tiền theo Type/Profile/Heart/Channels - 60 biến thể"""
    if not MONEY_AVAILABLE:
        return "Money tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_money(dt_utc, name=name)
        return mod_format_money(data)
    except Exception as e:
        return f"Lỗi: {str(e)}"

# POTENTIAL & BLIND SPOTS TOOLS - CHUYÊN DỤNG TIỀM NĂNG & ĐIỂM MÙ - MỚI v2.3
@mcp.tool()
def analyze_potential_blindspots(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v2.3 - TOOL CHUYÊN DỤNG TIỀM NĂNG & ĐIỂM MÙ - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn - Lựa chọn hành vi
    
    Dựa trên ý kiến thực tế người học:
    - Điểm mù bản thân, điểm yếu - điểm mạnh
    - Quan sát mình dưới các góc nhìn khác nhau (11 góc nhìn: Type + Profile + 9 Centers)
    - Lựa chọn hành vi phù hợp nhất để cải thiện bản thân (Strategy + Authority)
    
    Phân tích:
    - Điểm mạnh (Strengths): Defined Centers (năng lượng cố định đáng tin cậy), Defined Channels (tài năng cố định), Gates trong Channels, Profile Role, Incarnation Cross
    - Điểm mù & Tiềm năng (Blind Spots & Potential): Open/Undefined Centers (nơi nhạy cảm, dễ bị điều kiện hóa, là điểm mù và cũng là trí tuệ - 9 Centers Not-Self vs Wisdom), Fear Gates 19 cổng (6 Splenic Fears, 6 Ajna Anxieties, 7 Solar Nervousness), Hanging Gates (cổng treo - tiềm năng chưa kết nối)
    - Quan sát đa góc nhìn (Multiple Perspectives): 11 góc nhìn - Type (Aura), Profile (vai trò), 9 Centers (9 góc nhìn khác nhau) - Open Centers là góc nhìn học từ người khác, Defined Centers là góc nhìn cố định
    - Lựa chọn hành vi phù hợp (Appropriate Behavior): Strategy + Authority (80% giá trị) - Cách hành động đúng cho từng Type (Manifestor inform, Generator respond Sacral uh-huh, MG respond+inform, Projector invitation, Reflector lunar cycle), Authority ra quyết định đúng, Not-Self Mind (Mind không bao giờ là Authority), Deconditioning 7-year
    
    Áp dụng cho 100% dân số - 60 biến thể - Đặc biệt cho self-improvement, self-awareness - Ý kiến 2
    Khác với general consultation (tổng quát), tool này CHUYÊN SÂU về TIỀM NĂNG & ĐIỂM MÙ.
    
    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not POTENTIAL_AVAILABLE:
        return {"error": "Potential tool chưa cài đặt - kiểm tra hd_potential_analysis.py"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_potential(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_potential_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v2.3 - Tạo báo cáo Tiềm năng & Điểm mù đầy đủ markdown - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn 11 góc - Lựa chọn hành vi - 60 biến thể"""
    if not POTENTIAL_AVAILABLE:
        return "Potential tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_potential(dt_utc, name=name)
        return mod_format_potential(data)
    except Exception as e:
        return f"Lỗi: {str(e)}"

@mcp.tool()
def analyze_health(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v3.0 - TOOL SỨC KHỎE THÂN-TÂM-TRÍ - Quy luật sức khỏe theo Type + 9 Centers (Defined/Open) + Kênh + Tín hiệu cơ thể + Giấc ngủ/Vận động + Thực hành 7 ngày - 60 biến thể

    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not HEALTH_AVAILABLE:
        return {"error": "Health tool chưa cài đặt"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_health(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_health_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v3.0 - Báo cáo Sức khỏe Thân-Tâm-Trí đầy đủ markdown - 60 biến thể"""
    if not HEALTH_AVAILABLE:
        return "Health tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_health(dt_utc, name=name)
        return mod_format_health(data)
    except Exception as e:
        return "Lỗi: " + str(e)

@mcp.tool()
def analyze_relationship(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "", partner_date: str = "", partner_time: str = "", partner_timezone: str = "+07:00", partner_name: str = "") -> Dict[str, Any]:
    """
    MỚI v3.0 - TOOL MỐI QUAN HỆ CHUYÊN SÂU - Aura + Profile love style + 26 cổng tình yêu + mảnh ghép cổng treo + Composite 2 người (Electromagnetics/Compromise/Dominance) - 60 biến thể

    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not RELATIONSHIP_AVAILABLE:
        return {"error": "Relationship tool chưa cài đặt"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        pdt = None
        if partner_date and partner_time:
            pdt = parse_birth_datetime(partner_date, partner_time, partner_timezone)
        result = mod_analyze_relationship(dt_utc, name=name, partner_datetime=pdt, partner_name=partner_name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_relationship_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "", partner_date: str = "", partner_time: str = "", partner_timezone: str = "+07:00", partner_name: str = "") -> str:
    """MỚI v3.0 - Báo cáo Mối quan hệ & Thân mật đầy đủ markdown - Đơn hoặc Composite 2 người"""
    if not RELATIONSHIP_AVAILABLE:
        return "Relationship tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        pdt = None
        if partner_date and partner_time:
            pdt = parse_birth_datetime(partner_date, partner_time, partner_timezone)
        data = mod_analyze_relationship(dt_utc, name=name, partner_datetime=pdt, partner_name=partner_name)
        return mod_format_relationship(data)
    except Exception as e:
        return "Lỗi: " + str(e)

@mcp.tool()
def analyze_decision(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v3.0 - TOOL RA QUYẾT ĐỊNH theo Authority - 7 Authorities (Emotional/Sacral/Splenic/Heart/Self/Mental/Lunar) + quy trình từng bước + thời gian + câu hỏi + bẫy + Mind traps - 60 biến thể

    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not DECISION_AVAILABLE:
        return {"error": "Decision tool chưa cài đặt"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_decision(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_decision_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v3.0 - Báo cáo Ra quyết định đúng đầy đủ markdown - 60 biến thể"""
    if not DECISION_AVAILABLE:
        return "Decision tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_decision(dt_utc, name=name)
        return mod_format_decision(data)
    except Exception as e:
        return "Lỗi: " + str(e)

@mcp.tool()
def analyze_deconditioning(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v3.0 - TOOL GIẢI ĐIỀU KIỆN HÓA - Not-Self vs Signature theo Type + điều kiện hóa từng trung tâm mở (bài tập + mantra) + cảnh báo trung tâm định nghĩa + lộ trình 7 ngày/7 tháng/7 năm

    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not DECOND_AVAILABLE:
        return {"error": "Deconditioning tool chưa cài đặt"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_decond(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_deconditioning_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v3.0 - Báo cáo Giải điều kiện hóa đầy đủ markdown - Lộ trình 7d/7m/7y"""
    if not DECOND_AVAILABLE:
        return "Deconditioning tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_decond(dt_utc, name=name)
        return mod_format_decond(data)
    except Exception as e:
        return "Lỗi: " + str(e)

@mcp.tool()
def analyze_purpose(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v3.0 - TOOL SỨ MỆNH ỨNG DỤNG - Incarnation Cross + Angle + Quarter + 4 trụ Sun/Earth (Life's Work 70%) + vai trò Profile + đóng góp Type + hướng nghề từ kênh + 5 bước thực hành

    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not PURPOSE_AVAILABLE:
        return {"error": "Purpose tool chưa cài đặt"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_purpose(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_purpose_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v3.0 - Báo cáo Sứ mệnh & Mục đích đầy đủ markdown - 192 Crosses"""
    if not PURPOSE_AVAILABLE:
        return "Purpose tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_purpose(dt_utc, name=name)
        return mod_format_purpose(data)
    except Exception as e:
        return "Lỗi: " + str(e)

@mcp.tool()
def analyze_team(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> Dict[str, Any]:
    """
    MỚI v3.0 - TOOL TEAM & HỆ THỐNG - Vai trò Type trong team + phong cách lãnh đạo Profile + môi trường lý tưởng + bản đồ 10 ghế ngồi + quản lý từng Type - Đúng người đúng việc

    Args:
        birth_date: Ngày sinh YYYY-MM-DD
        birth_time: Giờ sinh HH:MM
        timezone: Múi giờ +07:00 VN
        name: Tên người
        birth_location: Nơi sinh
    """
    if not TEAM_AVAILABLE:
        return {"error": "Team tool chưa cài đặt"}
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        result = mod_analyze_team(dt_utc, name=name)
        result["birth_location"] = birth_location
        result["birth_date_local"] = birth_date
        result["birth_time_local"] = birth_time
        result["timezone"] = timezone
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def generate_team_report(birth_date: str, birth_time: str, timezone: str = "+07:00", name: str = "", birth_location: str = "") -> str:
    """MỚI v3.0 - Báo cáo Team & Hệ thống đầy đủ markdown - Tuyển dụng & quản lý"""
    if not TEAM_AVAILABLE:
        return "Team tool chưa cài đặt"
    try:
        dt_utc = parse_birth_datetime(birth_date, birth_time, timezone)
        data = mod_analyze_team(dt_utc, name=name)
        return mod_format_team(data)
    except Exception as e:
        return "Lỗi: " + str(e)

# Resources
@mcp.resource("human-design://knowledge/gates")
def get_gates_res() -> str:
    return "\n".join([f"Gate {g}: {GATE_MEANINGS.get(g)} - {GATE_TO_CENTER.get(g)}" for g in range(1,65)])

@mcp.resource("human-design://knowledge/centers")
def get_centers_res() -> str:
    return "\n".join([f"{c}: {CENTER_ANALYSIS.get(c,{}).get('defined','')}" for c in ["Head","Ajna","Throat","G","Heart","Spleen","Sacral","Solar Plexus","Root"]])

@mcp.resource("human-design://knowledge/types")
def get_types_res() -> str:
    return "\n".join([f"{t}: {d}" for t,d in TYPE_ANALYSIS.items()])

@mcp.resource("human-design://knowledge/money-channels")
def get_money_channels_res() -> str:
    try:
        from hd_money_analysis import MONEY_CHANNELS
        return "\n".join([f"{ch}: {info['name']} - {info['theme']} - {info['description'][:150]}" for ch, info in MONEY_CHANNELS.items()])
    except:
        return "Money channels: 21-45 Money, 26-44 Surrender, 40-37 Community, 32-54 Transformation, 14-2 Beat, 5-15 Rhythm"

@mcp.resource("human-design://knowledge/money-gates")
def get_money_gates_res() -> str:
    try:
        from hd_money_analysis import MONEY_GATES
        return "\n".join([f"Gate {g}: {info['name']} - {info['money_theme']}" for g, info in MONEY_GATES.items()])
    except:
        return "Money gates: 21,45,26,44,14,2,32,54,40,37,5,15,19,49"

@mcp.resource("human-design://knowledge/health-type")
def get_health_res() -> str:
    try:
        from hd_health_analysis import TYPE_HEALTH
        return "\n".join([t + ": " + v["pattern"][:100] + " | Rủi ro: " + v["risk"][:100] for t, v in TYPE_HEALTH.items()])
    except:
        return "Health: Generator/MG xả Sacral, Projector nghỉ, Manifestor xả giận, Reflector môi trường"

@mcp.resource("human-design://knowledge/love-gates")
def get_love_gates_res() -> str:
    try:
        from hd_relationship_analysis import LOVE_GATES
        return "\n".join(["Gate " + str(g) + ": " + m for g, m in LOVE_GATES.items()])
    except:
        return "Love gates: 6,59,27,10,15,46,25,44,40,37,19,49,30,41,55,39,12,22,35,36,5,14,29,9,8,1"

@mcp.resource("human-design://knowledge/authorities")
def get_authorities_res() -> str:
    try:
        from hd_decision_analysis import AUTHORITY_GUIDE
        return "\n".join([v["full"] + ": " + v["how"][:150] for v in AUTHORITY_GUIDE.values()])
    except:
        return "7 Authorities: Emotional, Sacral, Splenic, Heart, Self, Mental, Lunar"

@mcp.resource("human-design://knowledge/notself")
def get_notsel_res() -> str:
    try:
        from hd_deconditioning_analysis import TYPE_NOTSELF
        return "\n".join([t + ": Not-Self=" + v["notself"] + " | Signature=" + v["signature"] for t, v in TYPE_NOTSELF.items()])
    except:
        return "Not-Self: Generator Frustration, MG Frustration+Anger, Projector Bitterness, Manifestor Anger, Reflector Disappointment"

@mcp.resource("human-design://knowledge/purpose-quarters")
def get_purpose_res() -> str:
    try:
        from hd_purpose_analysis import QUARTERS, ANGLES
        return "\n".join([k + ": " + v["vn"] + " - " + v["purpose"][:120] for k, v in QUARTERS.items()] + ["Angles: " + " | ".join(ANGLES.keys())])
    except:
        return "Quarters: Initiation, Civilization, Duality, Mutation | Angles: Right, Left, Juxtaposition"

@mcp.resource("human-design://knowledge/team-roles")
def get_team_res() -> str:
    try:
        from hd_team_analysis import TYPE_TEAM_ROLE
        return "\n".join([t + " (" + v["share"] + "): " + v["role"] + " - " + v["seat"] for t, v in TYPE_TEAM_ROLE.items()])
    except:
        return "Team: Generator 37% xây, MG 33% xây nhanh, Projector 20% dẫn, Manifestor 9% mở đường, Reflector 1% soi"

if __name__ == "__main__":
    mcp.run(transport="stdio")
