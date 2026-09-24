"""
Human Design MCP Server v2.1 - Chuẩn Model Context Protocol
13 Tools (8 core + 4 advanced từ docs cá nhân + 1 general) + 5 Resources + 8 Prompts

Tích hợp tài liệu cá nhân 7 files 989 dòng
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
    from hd_consultation_general import analyze_consultation_general, format_consultation_report
    GENERAL_AVAILABLE = True
except:
    GENERAL_AVAILABLE = False

mcp = FastMCP(name="human-design-analyzer", instructions="Human Design v2.1 - 13 tools, Swiss Ephemeris chính xác, tích hợp docs cá nhân 989 dòng", dependencies=["pyswisseph", "pydantic"])

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

# ==================== 13 TOOLS ====================

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
        result = analyze_consultation_general(dt_utc, name=name)
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
        data = analyze_consultation_general(dt_utc, name=name)
        return format_consultation_report(data)
    except Exception as e:
        return f"Lỗi: {str(e)}"

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

if __name__ == "__main__":
    mcp.run(transport="stdio")
