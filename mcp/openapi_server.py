"""
Human Design API Server - Cầu nối cho ChatGPT Web (Custom GPT Actions)
Chuyển đổi MCP Tools thành REST API theo chuẩn OpenAPI 3.0 để ChatGPT web có thể gọi

Chạy: python openapi_server.py
Hoặc: uvicorn openapi_server:app --host 0.0.0.0 --port 8000

Sau đó dùng URL https://your-server.com/openapi.json để tạo Custom GPT Action
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json

# Thêm tools vào path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from hd_calculator import calculate_hd_chart, GATE_MEANINGS, GATE_TO_CENTER, CHANNEL_TO_CENTERS, GATE_ORDER, CHANNELS
from hd_analyzer import analyze_chart, TYPE_ANALYSIS, PROFILE_ANALYSIS, CENTER_ANALYSIS
from server import chart_to_dict, parse_birth_datetime

# Import các hàm từ server.py
from server import (
    get_gate_info as mcp_get_gate_info,
    get_center_info as mcp_get_center_info,
    get_channel_info as mcp_get_channel_info,
    get_profile_info as mcp_get_profile_info,
    explain_calculation_method as mcp_explain_calculation_method,
    analyze_centers_deep as mcp_analyze_centers_deep,
    analyze_channels_deep as mcp_analyze_channels_deep,
    analyze_type_strategy_authority as mcp_analyze_type_strategy_authority,
    analyze_profile_definition as mcp_analyze_profile_definition,
    analyze_practical_application as mcp_analyze_practical_application,
)

# Import advanced tools
try:
    from hd_advanced_tools import (
        analyze_fear_gates as adv_analyze_fear,
        analyze_love_gates as adv_analyze_love,
        get_incarnation_cross_details as adv_get_cross,
        analyze_manifestor_deep as adv_manifestor,
    )
    ADV_AVAILABLE = True
except:
    ADV_AVAILABLE = False

# Import general consultation tool (100% population)
try:
    from hd_consultation_general import (
        analyze_consultation_general as adv_general,
        format_consultation_report as adv_general_report,
    )
    GENERAL_AVAILABLE = True
except:
    GENERAL_AVAILABLE = False

# Import money tool (Full Money Map)
try:
    from hd_money_analysis import (
        analyze_money_map as adv_money,
        format_money_report as adv_money_report,
    )
    MONEY_AVAILABLE = True
except:
    MONEY_AVAILABLE = False

# Import potential & blind spots tool
try:
    from hd_potential_analysis import (
        analyze_potential_blindspots as adv_potential,
        format_potential_report as adv_potential_report,
    )
    POTENTIAL_AVAILABLE = True
except:
    POTENTIAL_AVAILABLE = False

# Import v3.0 domains (Health, Relationship, Decision, Deconditioning, Purpose, Team)
try:
    from hd_health_analysis import (
        analyze_health as adv_health,
        format_health_report as adv_health_report,
    )
    HEALTH_AVAILABLE = True
except:
    HEALTH_AVAILABLE = False

try:
    from hd_relationship_analysis import (
        analyze_relationship as adv_rel,
        format_relationship_report as adv_rel_report,
    )
    RELATIONSHIP_AVAILABLE = True
except:
    RELATIONSHIP_AVAILABLE = False

try:
    from hd_decision_analysis import (
        analyze_decision as adv_decision,
        format_decision_report as adv_decision_report,
    )
    DECISION_AVAILABLE = True
except:
    DECISION_AVAILABLE = False

try:
    from hd_deconditioning_analysis import (
        analyze_deconditioning as adv_decond,
        format_deconditioning_report as adv_decond_report,
    )
    DECOND_AVAILABLE = True
except:
    DECOND_AVAILABLE = False

try:
    from hd_purpose_analysis import (
        analyze_purpose as adv_purpose,
        format_purpose_report as adv_purpose_report,
    )
    PURPOSE_AVAILABLE = True
except:
    PURPOSE_AVAILABLE = False

try:
    from hd_team_analysis import (
        analyze_team as adv_team,
        format_team_report as adv_team_report,
    )
    TEAM_AVAILABLE = True
except:
    TEAM_AVAILABLE = False

app = FastAPI(
    title="Human Design Analyzer API",
    description="""
    ## Human Design Analyzer API v3.0.0

    FastAPI bridge cho Human Design Analyzer, dùng Swiss Ephemeris và cùng calculator với MCP stdio server.

    ### Phạm vi:
    - 36 route nghiệp vụ tương ứng với 36 MCP tools: foundation, core, advanced, general, money, potential và 6 domain v3.0.
    - Tính BodyGraph Personality + Design 88°, tra cứu và phân tích 64 Gates, 9 Centers, 36 Channels, Profile và Cross.
    - Phân tích Foundation, Money, Health, Potential, Relationship, Decision, Deconditioning, Purpose và Team.
    - OpenAPI spec tại `/openapi.json` để tích hợp REST client hoặc Custom GPT Actions.

    ### Dữ liệu và giới hạn:
    - Swiss Ephemeris được dùng cho phép tính thiên văn; ngày/giờ local được chuyển sang UTC theo timezone.
    - Human Design là công cụ tự quan sát/thử nghiệm, không thay thế tư vấn y tế, pháp lý hoặc tài chính.
    """,
    version="3.0.0",
    contact={
        "name": "Human Design MCP Server",
        "url": "https://github.com/human-design/mcp"
    }
)

# CORS cho ChatGPT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELS ====================

class ChartRequest(BaseModel):
    birth_date: str = Field(..., json_schema_extra={"example": "1990-05-15"}, description="Ngày sinh YYYY-MM-DD")
    birth_time: str = Field(..., json_schema_extra={"example": "08:30"}, description="Giờ sinh HH:MM (24h)")
    timezone: str = Field(default="+07:00", json_schema_extra={"example": "+07:00"}, description="Múi giờ, mặc định +07:00 VN")
    name: str = Field(default="", json_schema_extra={"example": "Nguyen Van A"}, description="Tên người")
    birth_location: str = Field(default="", json_schema_extra={"example": "Hanoi, Vietnam"}, description="Nơi sinh")

class RelationshipRequest(BaseModel):
    birth_date: str = Field(..., json_schema_extra={"example": "1990-05-15"})
    birth_time: str = Field(..., json_schema_extra={"example": "08:30"})
    timezone: str = Field(default="+07:00")
    name: str = Field(default="")
    birth_location: str = Field(default="")
    partner_date: str = Field(default="", description="Ngày sinh đối phương YYYY-MM-DD (để composite 2 người)")
    partner_time: str = Field(default="", description="Giờ sinh đối phương HH:MM")
    partner_timezone: str = Field(default="+07:00")
    partner_name: str = Field(default="", description="Tên đối phương")

class AnalysisRequest(BaseModel):
    birth_date: str = Field(..., json_schema_extra={"example": "1990-05-15"})
    birth_time: str = Field(..., json_schema_extra={"example": "08:30"})
    timezone: str = Field(default="+07:00")
    name: str = Field(default="")
    focus_area: str = Field(default="full", json_schema_extra={"example": "full"}, description="full, type, authority, centers, channels, profile, career, relationship, health")

class GateRequest(BaseModel):
    gate_number: int = Field(..., ge=1, le=64, json_schema_extra={"example": 10}, description="Số cổng 1-64")

class CenterRequest(BaseModel):
    center_name: str = Field(..., json_schema_extra={"example": "G"}, description="Head, Ajna, Throat, G, Heart, Spleen, Sacral, Solar Plexus, Root")

class ChannelRequest(BaseModel):
    gate1: int = Field(..., ge=1, le=64, json_schema_extra={"example": 10})
    gate2: int = Field(..., ge=1, le=64, json_schema_extra={"example": 20})

class ProfileRequest(BaseModel):
    profile: str = Field(..., json_schema_extra={"example": "2/4"}, description="1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3")

class CompareRequest(BaseModel):
    person1_date: str = Field(..., json_schema_extra={"example": "1990-05-15"})
    person1_time: str = Field(..., json_schema_extra={"example": "08:30"})
    person1_name: str = Field(default="Person 1")
    person2_date: str = Field(..., json_schema_extra={"example": "1992-08-20"})
    person2_time: str = Field(..., json_schema_extra={"example": "14:00"})
    person2_name: str = Field(default="Person 2")
    timezone: str = Field(default="+07:00")

# ==================== ENDPOINTS ====================

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Human Design Analyzer API v3.0.0 - 36 tools + 2 system routes",
        "version": "3.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "chatgpt_integration": "Dùng /openapi.json để tạo Custom GPT Action",
        "total_tools": 36,
        "endpoints": [
            "/calculate-chart",
            "/analyze-deep",
            "/gate-info",
            "/center-info",
            "/channel-info",
            "/profile-info",
            "/calculation-method",
            "/analyze-centers",
            "/analyze-channels",
            "/analyze-type-strategy-authority",
            "/analyze-profile-definition",
            "/analyze-practical-application",
            "/compare-charts",
            "/generate-report",
            "/analyze-fear-gates",
            "/analyze-love-gates",
            "/incarnation-cross-details",
            "/analyze-manifestor-deep",
            "/analyze-consultation-general",
            "/generate-consultation-report",
            "/analyze-money-map",
            "/generate-money-report",
            "/analyze-potential-blindspots",
            "/generate-potential-report",
            "/analyze-health",
            "/generate-health-report",
            "/analyze-relationship",
            "/generate-relationship-report",
            "/analyze-decision",
            "/generate-decision-report",
            "/analyze-deconditioning",
            "/generate-deconditioning-report",
            "/analyze-purpose",
            "/generate-purpose-report",
            "/analyze-team",
            "/generate-team-report"
        ],
        "coverage": "100% dân số - 5 Types x 12 Profiles = 60 biến thể + Full Money Map 6 Channels x 14 Gates + Potential & Blind Spots 11 Perspectives + v3.0 6 domains (Health/Relationship/Decision/Deconditioning/Purpose/Team)",
        "specialized_skills": "25 Markdown skills: 01-18 + 20-26 (không phải MCP prompts; 19 reserved)",
        "user_interests": "7 nhu cầu cốt lõi: Money, Health Thân-Tâm-Trí, Potential & Blind Spots, Relationships, Purpose Mission, System Building, Decision & Behavior"
    }

@app.post("/calculate-chart", tags=["Core"], summary="Tính toán Human Design Chart chính xác (CORE)")
def calculate_chart(req: ChartRequest):
    """
    TOOL CỐT LÕI - Tính toán bản đồ Human Design chính xác từ ngày giờ sinh.
    
    Sử dụng Swiss Ephemeris NASA JPL DE431, độ chính xác <1 arc second.
    Tính cả Personality (lúc sinh) và Design (88° Sun trước sinh).
    
    **Phải gọi đầu tiên khi phân tích một người.**
    """
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        chart = calculate_hd_chart(dt_utc)
        result = chart_to_dict(chart)
        result["name"] = req.name
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi tính toán: {str(e)}")

@app.post("/analyze-deep", tags=["Analysis"], summary="Phân tích chuyên sâu Human Design tiếng Việt")
def analyze_deep(req: AnalysisRequest):
    """
    Phân tích chuyên sâu Human Design bằng tiếng Việt.
    
    Tạo báo cáo chi tiết Type, Strategy, Authority, Centers, Channels, Profile.
    """
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        chart = calculate_hd_chart(dt_utc)
        
        # Import analyze_chart
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
        from hd_analyzer import analyze_chart
        
        full_analysis = analyze_chart(chart)
        
        if req.focus_area == "full":
            return {"analysis": full_analysis, "chart_summary": chart_to_dict(chart)}
        
        # Lọc theo focus
        focus_map = {
            "type": ["1. TYPE"],
            "authority": ["2. AUTHORITY"],
            "centers": ["5. 9 TRUNG TÂM"],
            "channels": ["6. KÊNH"],
            "profile": ["3. PROFILE"],
            "career": ["1. TYPE", "5. 9 TRUNG TÂM", "6. KÊNH"],
            "relationship": ["1. TYPE", "5. 9 TRUNG TÂM", "4. DEFINITION"],
            "health": ["5. 9 TRUNG TÂM", "2. AUTHORITY"]
        }
        
        return {"analysis": full_analysis, "focus": req.focus_area, "chart_summary": chart_to_dict(chart)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi phân tích: {str(e)}")

@app.get("/gate-info/{gate_number}", tags=["Lookup"], summary="Tra cứu 1 cổng Gate 1-64")
def gate_info(gate_number: int):
    """Tra cứu thông tin chi tiết 1 cổng (Gate) 1-64: ý nghĩa, trung tâm, kênh, vị trí Mandala"""
    try:
        result = mcp_get_gate_info(gate_number)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/center-info/{center_name}", tags=["Lookup"], summary="Tra cứu 1 trung tâm")
def center_info(center_name: str):
    """Tra cứu thông tin 1 trung tâm: Head, Ajna, Throat, G, Heart, Spleen, Sacral, Solar Plexus, Root"""
    try:
        result = mcp_get_center_info(center_name)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/channel-info", tags=["Lookup"], summary="Tra cứu 1 kênh Channel")
def channel_info(gate1: int = Query(..., ge=1, le=64), gate2: int = Query(..., ge=1, le=64)):
    """Tra cứu thông tin 1 kênh: ví dụ gate1=10 gate2=20"""
    try:
        result = mcp_get_channel_info(gate1, gate2)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/profile-info/{profile}", tags=["Lookup"], summary="Tra cứu Profile")
def profile_info(profile: str):
    """Tra cứu ý nghĩa Profile: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3"""
    try:
        result = mcp_get_profile_info(profile)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/calculation-method", tags=["Foundation"], summary="Giải thích phương pháp tính chart")
def calculation_method_api():
    """Giải thích pipeline Swiss Ephemeris, 88° Design và Gate mapping."""
    return mcp_explain_calculation_method()

@app.post("/analyze-centers", tags=["Foundation"], summary="Phân tích chuyên sâu 9 Centers")
def centers_deep_api(req: ChartRequest):
    result = mcp_analyze_centers_deep(req.birth_date, req.birth_time, req.timezone, req.name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/analyze-channels", tags=["Foundation"], summary="Phân tích chuyên sâu Channels")
def channels_deep_api(req: ChartRequest):
    result = mcp_analyze_channels_deep(req.birth_date, req.birth_time, req.timezone, req.name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/analyze-type-strategy-authority", tags=["Foundation"], summary="Phân tích Type, Strategy và Authority")
def type_strategy_authority_api(req: ChartRequest):
    result = mcp_analyze_type_strategy_authority(req.birth_date, req.birth_time, req.timezone, req.name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/analyze-profile-definition", tags=["Foundation"], summary="Phân tích Profile và Definition")
def profile_definition_api(req: ChartRequest):
    result = mcp_analyze_profile_definition(req.birth_date, req.birth_time, req.timezone, req.name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/analyze-practical-application", tags=["Foundation"], summary="Chuyển chart thành kế hoạch ứng dụng thực tế")
def practical_application_api(req: ChartRequest, focus_area: str = Query("general", description="general, career, relationship, health hoặc decision")):
    result = mcp_analyze_practical_application(req.birth_date, req.birth_time, req.timezone, req.name, focus_area)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/compare-charts", tags=["Relationship"], summary="So sánh 2 bản đồ (Composite)")
def compare_charts_api(req: CompareRequest):
    """
    So sánh 2 bản đồ Human Design (Composite) để phân tích mối quan hệ.
    
    Phân tích electromagnetic, dominance, common gates.
    """
    try:
        dt1_utc = parse_birth_datetime(req.person1_date, req.person1_time, req.timezone)
        dt2_utc = parse_birth_datetime(req.person2_date, req.person2_time, req.timezone)
        
        chart1 = calculate_hd_chart(dt1_utc)
        chart2 = calculate_hd_chart(dt2_utc)
        
        gates1 = set(chart1["all_activated_gates"])
        gates2 = set(chart2["all_activated_gates"])
        
        electromagnetic = []
        for g1, g2 in CHANNELS:
            if (g1 in gates1 and g2 in gates2) or (g2 in gates1 and g1 in gates2):
                already_defined_1 = (g1, g2) in chart1["defined_channels"] or (g2, g1) in chart1["defined_channels"]
                already_defined_2 = (g1, g2) in chart2["defined_channels"] or (g2, g1) in chart2["defined_channels"]
                if not already_defined_1 and not already_defined_2:
                    electromagnetic.append({
                        "channel": f"{g1}-{g2}",
                        "centers": CHANNEL_TO_CENTERS.get((g1,g2)) or CHANNEL_TO_CENTERS.get((g2,g1)),
                        "person1_gate": g1 if g1 in gates1 else g2,
                        "person2_gate": g2 if g2 in gates2 and g1 in gates1 else g1,
                        "type": "Electromagnetic"
                    })
        
        dominance_p1 = []
        dominance_p2 = []
        for center in ["Head", "Ajna", "Throat", "G", "Heart", "Spleen", "Sacral", "Solar Plexus", "Root"]:
            p1_has = center in chart1["defined_centers"]
            p2_has = center in chart2["defined_centers"]
            if p1_has and not p2_has:
                dominance_p1.append(center)
            elif p2_has and not p1_has:
                dominance_p2.append(center)
        
        common_gates = list(gates1.intersection(gates2))
        
        return {
            "person1": {"name": req.person1_name, "type": chart1["type"], "authority": chart1["authority"], "profile": chart1["profile"]},
            "person2": {"name": req.person2_name, "type": chart2["type"], "authority": chart2["authority"], "profile": chart2["profile"]},
            "electromagnetic_channels": electromagnetic,
            "electromagnetic_count": len(electromagnetic),
            "dominance": {f"{req.person1_name} dominates": dominance_p1, f"{req.person2_name} dominates": dominance_p2},
            "common_gates": common_gates,
            "common_gates_count": len(common_gates),
            "summary": f"{req.person1_name} ({chart1['type']}) và {req.person2_name} ({chart2['type']}) có {len(electromagnetic)} kênh electromagnetic, {len(common_gates)} cổng chung."
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-fear-gates", tags=["Advanced - Từ tài liệu cá nhân"], summary="Phân tích 19 cổng Sợ hãi/Lo âu/Hồi hộp (từ Phân mục 4)")
def analyze_fear_api(req: ChartRequest):
    """Phân tích 6 Splenic Fears, 6 Ajna Anxieties, 7 Solar Nervousness - từ tài liệu cá nhân"""
    if not ADV_AVAILABLE:
        raise HTTPException(status_code=500, detail="Advanced tools chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_analyze_fear(dt_utc)
        result["name"] = req.name
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-love-gates", tags=["Advanced - Từ tài liệu cá nhân"], summary="Phân tích động lực Tình yêu (từ Phân mục 5)")
def analyze_love_api(req: ChartRequest):
    """Phân tích 4 Vessel of Love + 7 Mundane Love - từ tài liệu cá nhân"""
    if not ADV_AVAILABLE:
        raise HTTPException(status_code=500, detail="Advanced tools chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_analyze_love(dt_utc)
        result["name"] = req.name
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/incarnation-cross-details", tags=["Advanced - Từ tài liệu cá nhân"], summary="Tra cứu chi tiết 192 Incarnation Crosses (từ Phân mục 3)")
def cross_details_api(
    p_sun_gate: int = Query(..., ge=1, le=64, description="Personality Sun Gate"),
    p_earth_gate: int = Query(..., ge=1, le=64, description="Personality Earth Gate"),
    d_sun_gate: int = Query(..., ge=1, le=64, description="Design Sun Gate"),
    d_earth_gate: int = Query(..., ge=1, le=64, description="Design Earth Gate"),
):
    """Tra cứu chi tiết Incarnation Cross từ 4 cổng - database 30+ crosses từ tài liệu cá nhân 413 dòng"""
    if not ADV_AVAILABLE:
        raise HTTPException(status_code=500, detail="Advanced tools chưa cài đặt")
    try:
        result = adv_get_cross(p_sun_gate, p_earth_gate, d_sun_gate, d_earth_gate)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-manifestor-deep", tags=["Advanced - Từ tài liệu cá nhân"], summary="Phân tích chuyên sâu Manifestor (từ Phân mục 6)")
def manifestor_deep_api(req: ChartRequest):
    """Deep dive Manifestor 9% - Aura, tâm lý, trẻ em Manifestor, quy trình tham vấn 4 bước"""
    if not ADV_AVAILABLE:
        raise HTTPException(status_code=500, detail="Advanced tools chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_manifestor(dt_utc)
        result["name"] = req.name
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-consultation-general", tags=["General - 100% dân số"], summary="v3.0 - Tham vấn tổng quát 5 Types x 12 Profiles = 60 biến thể")
def consultation_general_api(req: ChartRequest):
    """
    TOOL TỔNG QUÁT NHẤT - Áp dụng cho 100% dân số
    
    - 5 Types: Manifestor 9%, Generator 36%, MG 32%, Projector 22%, Reflector 1%
    - 12 Profiles: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3
    - Deep dive chi tiết cho từng Type: aura, psychology, strategy, signature, not_self, work, relationship, child
    - Profile deep dive: role, angle, description, career
    - Quy trình tham vấn chuyên nghiệp 4 bước + buổi đọc 1-2h
    - Fear/Love gates integration
    - Nguyên tắc đạo đức, lộ trình 7 ngày/7 tháng/7 năm
    
    Khác với /analyze-manifestor-deep (chỉ 9%), tool này cho TẤT CẢ.
    """
    if not GENERAL_AVAILABLE:
        raise HTTPException(status_code=500, detail="General tool chưa cài đặt - kiểm tra hd_consultation_general.py")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_general(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-consultation-report", tags=["General - 100% dân số"], summary="v3.0 - Báo cáo tham vấn tổng quát đầy đủ markdown")
def consultation_report_api(req: ChartRequest):
    """Tạo báo cáo tham vấn tổng quát đầy đủ markdown - áp dụng cho TẤT CẢ Types/Profiles, 60 biến thể"""
    if not GENERAL_AVAILABLE:
        raise HTTPException(status_code=500, detail="General tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_general(dt_utc, name=req.name)
        report = adv_general_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "authority": data["authority"], "ap_dung_cho": data["áp_dụng_cho"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-money-map", tags=["Money - Full Money Map v3.0"], summary="v3.0 - Full Money Map - Dòng tiền theo Type/Profile/Heart/Channels/Gates - 60 biến thể")
def money_map_api(req: ChartRequest):
    """
    TOOL CHUYÊN DỤNG TIỀN BẠC - Full Money Map - Dòng tiền theo Type/Profile/Heart/Channels
    
    Phân tích chuyên sâu dòng tiền, tài chính, business model, pricing, investment:
    - 5 Types Money Strategy: Manifestor khởi xướng+inform, Generator respond+Sacral uh-huh, MG đa dòng tiền, Projector invitation+premium pricing cao cho ít giờ, Reflector môi trường+lunar 28 ngày
    - 12 Profiles Money Style
    - Heart/Ego Center: Defined 35% vs Undefined 65% (bẫy chứng minh giá trị qua tiền)
    - Money Channels 6 kênh: 21-45 Money, 26-44 Surrender, 40-37 Community, 32-54 Transformation, 14-2 Beat, 5-15 Rhythm
    - Money Gates 14 cổng: 21,45,26,44,14,2,32,54,40,37,5,15,19,49
    - Definition Money: Single/Split/Triple/Quadruple
    - Authority Money
    - Pricing, Business Model, Investment, Saving/Spending
    
    Áp dụng 100% - 60 biến thể - Full Money Map
    """
    if not MONEY_AVAILABLE:
        raise HTTPException(status_code=500, detail="Money tool chưa cài đặt - kiểm tra hd_money_analysis.py")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_money(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-money-report", tags=["Money - Full Money Map v3.0"], summary="v3.0 - Báo cáo Full Money Map đầy đủ markdown - 60 biến thể")
def money_report_api(req: ChartRequest):
    """Tạo báo cáo Full Money Map đầy đủ markdown - Dòng tiền theo Type/Profile/Heart/Channels/Gates - Pricing, Business Model, Investment"""
    if not MONEY_AVAILABLE:
        raise HTTPException(status_code=500, detail="Money tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_money(dt_utc, name=req.name)
        report = adv_money_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "heart_defined": data["money_analysis"]["heart_center_money"]["defined"], "money_channels": data["money_analysis"]["money_channels"]["count"], "money_gates": data["money_analysis"]["money_gates"]["count"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-potential-blindspots", tags=["Potential - Tiềm năng & Điểm mù v3.0"], summary="v3.0 - Tiềm năng & Điểm mù - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn 11 góc - Lựa chọn hành vi")
def potential_blindspots_api(req: ChartRequest):
    """
    TOOL CHUYÊN DỤNG TIỀM NĂNG & ĐIỂM MÙ - Dựa trên ý kiến thực tế người học
    
    - Điểm mù bản thân, điểm yếu - điểm mạnh
    - Quan sát mình dưới các góc nhìn khác nhau (11 góc nhìn: Type + Profile + 9 Centers)
    - Lựa chọn hành vi phù hợp nhất để cải thiện bản thân (Strategy + Authority)
    
    Phân tích:
    - Điểm mạnh: Defined Centers (năng lượng cố định), Defined Channels (tài năng cố định), Gates, Profile Role, Incarnation Cross
    - Điểm mù & Tiềm năng: Open/Undefined Centers (Not-Self vs Wisdom), Fear Gates 19 cổng, Hanging Gates (tiềm năng treo)
    - Quan sát đa góc nhìn: 11 góc nhìn - Type Aura + Profile Role + 9 Centers
    - Lựa chọn hành vi phù hợp: Strategy + Authority (80% giá trị), Not-Self Mind (Mind không phải Authority), Deconditioning 7-year
    
    Áp dụng 100% - 60 biến thể - Self-improvement, self-awareness
    """
    if not POTENTIAL_AVAILABLE:
        raise HTTPException(status_code=500, detail="Potential tool chưa cài đặt - kiểm tra hd_potential_analysis.py")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_potential(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-potential-report", tags=["Potential - Tiềm năng & Điểm mù v3.0"], summary="v3.0 - Báo cáo Tiềm năng & Điểm mù đầy đủ markdown - 11 góc nhìn - 60 biến thể")
def potential_report_api(req: ChartRequest):
    """Tạo báo cáo Tiềm năng & Điểm mù đầy đủ markdown - Điểm mạnh/Điểm yếu - Quan sát đa góc nhìn 11 góc - Lựa chọn hành vi phù hợp"""
    if not POTENTIAL_AVAILABLE:
        raise HTTPException(status_code=500, detail="Potential tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_potential(dt_utc, name=req.name)
        report = adv_potential_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "defined_centers": len(data["defined_centers"]), "open_centers": len(data["undefined_centers"]), "perspectives": data["potential_analysis"]["perspectives"]["count"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-report", tags=["Report"], summary="Tạo báo cáo đầy đủ")
def generate_report_api(req: ChartRequest):
    """Tạo báo cáo Human Design đầy đủ markdown"""
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        chart = calculate_hd_chart(dt_utc)
        
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
        from hd_calculator import format_chart_text
        from hd_analyzer import analyze_chart
        
        text_chart = format_chart_text(chart)
        deep = analyze_chart(chart)
        
        report = f"""# BÁO CÁO HUMAN DESIGN - {req.name or 'KHÁCH HÀNG'}

**Ngày sinh**: {req.birth_date} {req.birth_time} {req.timezone} {req.birth_location}
**Ngày sinh UTC**: {dt_utc}

## TÓM TẮT
- Type: {chart['type']}
- Strategy: {chart['strategy']}
- Authority: {chart['authority']}
- Profile: {chart['profile']}
- Definition: {chart['definition']}

{text_chart}

{deep}
"""
        return {"report": report, "chart": chart_to_dict(chart)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-health", tags=["Health - Sức khỏe v3.0"], summary="MỚI v3.0 - Sức khỏe Thân-Tâm-Trí - Quy luật Type + 9 Centers + Tín hiệu cơ thể + Ngủ/Vận động + 7 ngày")
def health_api(req: ChartRequest):
    """TOOL SỨC KHỎE THÂN-TÂM-TRÍ - Quy luật sức khỏe theo Type + 9 Centers Defined/Open + Kênh + 7 tín hiệu cơ thể + Giấc ngủ/Vận động đúng + Thực hành 7 ngày - 60 biến thể"""
    if not HEALTH_AVAILABLE:
        raise HTTPException(status_code=500, detail="Health tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_health(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-health-report", tags=["Health - Sức khỏe v3.0"], summary="MỚI v3.0 - Báo cáo Sức khỏe đầy đủ markdown")
def health_report_api(req: ChartRequest):
    """Báo cáo Sức khỏe Thân-Tâm-Trí đầy đủ markdown"""
    if not HEALTH_AVAILABLE:
        raise HTTPException(status_code=500, detail="Health tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_health(dt_utc, name=req.name)
        report = adv_health_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "open_centers": len(data["open_centers"]), "defined_centers": len(data["defined_centers"])}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-relationship", tags=["Relationship - Mối quan hệ v3.0"], summary="MỚI v3.0 - Mối quan hệ chuyên sâu + Composite 2 người - Aura + 26 cổng yêu + Điện từ/Compromise/Dominance")
def relationship_api(req: RelationshipRequest):
    """TOOL MỐI QUAN HỆ CHUYÊN SÂU - Aura + Profile love style + 26 cổng tình yêu + mảnh ghép cổng treo + Composite 2 người (Electromagnetics/Compromise/Dominance) - Đơn hoặc đôi"""
    if not RELATIONSHIP_AVAILABLE:
        raise HTTPException(status_code=500, detail="Relationship tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        pdt = None
        if req.partner_date and req.partner_time:
            pdt = parse_birth_datetime(req.partner_date, req.partner_time, req.partner_timezone)
        result = adv_rel(dt_utc, name=req.name, partner_datetime=pdt, partner_name=req.partner_name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-relationship-report", tags=["Relationship - Mối quan hệ v3.0"], summary="MỚI v3.0 - Báo cáo Mối quan hệ đầy đủ markdown")
def relationship_report_api(req: RelationshipRequest):
    """Báo cáo Mối quan hệ & Thân mật đầy đủ markdown"""
    if not RELATIONSHIP_AVAILABLE:
        raise HTTPException(status_code=500, detail="Relationship tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        pdt = None
        if req.partner_date and req.partner_time:
            pdt = parse_birth_datetime(req.partner_date, req.partner_time, req.partner_timezone)
        data = adv_rel(dt_utc, name=req.name, partner_datetime=pdt, partner_name=req.partner_name)
        report = adv_rel_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "love_gates": data["relationship_analysis"]["count_love_gates"], "composite": data["relationship_analysis"]["composite"] is not None}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-decision", tags=["Decision - Ra quyết định v3.0"], summary="MỚI v3.0 - Ra quyết định theo Authority - 7 Authorities + quy trình + thời gian + bẫy")
def decision_api(req: ChartRequest):
    """TOOL RA QUYẾT ĐỊNH - 7 Authorities (Emotional/Sacral/Splenic/Heart/Self/Mental/Lunar) + quy trình từng bước + thời gian + câu hỏi + bẫy + Mind traps - 60 biến thể"""
    if not DECISION_AVAILABLE:
        raise HTTPException(status_code=500, detail="Decision tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_decision(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-decision-report", tags=["Decision - Ra quyết định v3.0"], summary="MỚI v3.0 - Báo cáo Ra quyết định đầy đủ markdown")
def decision_report_api(req: ChartRequest):
    """Báo cáo Ra quyết định đúng đầy đủ markdown"""
    if not DECISION_AVAILABLE:
        raise HTTPException(status_code=500, detail="Decision tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_decision(dt_utc, name=req.name)
        report = adv_decision_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "authority": data["decision_analysis"]["authority_full"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-deconditioning", tags=["Deconditioning - Giải điều kiện v3.0"], summary="MỚI v3.0 - Giải điều kiện hóa - Not-Self vs Signature + lộ trình 7 ngày/7 tháng/7 năm")
def decond_api(req: ChartRequest):
    """TOOL GIẢI ĐIỀU KIỆN HÓA - Not-Self vs Signature theo Type + điều kiện hóa từng trung tâm mở (bài tập + mantra) + cảnh báo trung tâm định nghĩa + lộ trình 7d/7m/7y"""
    if not DECOND_AVAILABLE:
        raise HTTPException(status_code=500, detail="Deconditioning tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_decond(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-deconditioning-report", tags=["Deconditioning - Giải điều kiện v3.0"], summary="MỚI v3.0 - Báo cáo Giải điều kiện hóa đầy đủ markdown")
def decond_report_api(req: ChartRequest):
    """Báo cáo Giải điều kiện hóa đầy đủ markdown - Lộ trình 7d/7m/7y"""
    if not DECOND_AVAILABLE:
        raise HTTPException(status_code=500, detail="Deconditioning tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_decond(dt_utc, name=req.name)
        report = adv_decond_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "notself": data["deconditioning_analysis"]["notself_theme"], "open_centers": data["deconditioning_analysis"]["count_open"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-purpose", tags=["Purpose - Sứ mệnh v3.0"], summary="MỚI v3.0 - Sứ mệnh ứng dụng - Cross + Angle + Quarter + Life's Work 70% + hướng nghề")
def purpose_api(req: ChartRequest):
    """TOOL SỨ MỆNH ỨNG DỤNG - Incarnation Cross + Angle + Quarter + 4 trụ Sun/Earth (Life's Work 70%) + vai trò Profile + đóng góp Type + hướng nghề từ kênh + 5 bước - 192 Crosses"""
    if not PURPOSE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Purpose tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_purpose(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-purpose-report", tags=["Purpose - Sứ mệnh v3.0"], summary="MỚI v3.0 - Báo cáo Sứ mệnh đầy đủ markdown")
def purpose_report_api(req: ChartRequest):
    """Báo cáo Sứ mệnh & Mục đích đầy đủ markdown"""
    if not PURPOSE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Purpose tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_purpose(dt_utc, name=req.name)
        report = adv_purpose_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "cross": data["purpose_analysis"]["cross"], "angle": data["purpose_analysis"]["angle"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-team", tags=["Team - Hệ thống v3.0"], summary="MỚI v3.0 - Team & Hệ thống - Vai trò Type + lãnh đạo Profile + bản đồ 10 ghế + quản lý")
def team_api(req: ChartRequest):
    """TOOL TEAM & HỆ THỐNG - Vai trò Type trong team + phong cách lãnh đạo Profile + môi trường lý tưởng + bản đồ 10 ghế ngồi + quản lý từng Type - Đúng người đúng việc"""
    if not TEAM_AVAILABLE:
        raise HTTPException(status_code=500, detail="Team tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        result = adv_team(dt_utc, name=req.name)
        result["birth_location"] = req.birth_location
        result["birth_date_local"] = req.birth_date
        result["birth_time_local"] = req.birth_time
        result["timezone"] = req.timezone
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-team-report", tags=["Team - Hệ thống v3.0"], summary="MỚI v3.0 - Báo cáo Team đầy đủ markdown")
def team_report_api(req: ChartRequest):
    """Báo cáo Team & Hệ thống đầy đủ markdown"""
    if not TEAM_AVAILABLE:
        raise HTTPException(status_code=500, detail="Team tool chưa cài đặt")
    try:
        dt_utc = parse_birth_datetime(req.birth_date, req.birth_time, req.timezone)
        data = adv_team(dt_utc, name=req.name)
        report = adv_team_report(data)
        return {"report": report, "summary": {"type": data["type"], "profile": data["profile"], "role": data["team_analysis"]["your_role"]["role"], "share": data["team_analysis"]["your_role"]["share"]}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------------------------------------------------------------------------
# Report layer — chuẩn báo cáo: thông tin + BodyGraph tự sinh + template/LLM
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from fastapi import Response  # noqa: E402

from backend.reporting.contract import ReportRequest as _ReportRequest  # noqa: E402
from backend.reporting.export import bodygraph_svg as _bodygraph_svg  # noqa: E402
from backend.reporting.llm_editor import build_llm_brief as _build_llm_brief  # noqa: E402
from backend.reporting.orchestrator import ReportOrchestrator as _ReportOrchestrator  # noqa: E402
from backend.reporting.service import (  # noqa: E402
    apply_draft as _apply_draft,
    generate_report as _generate_report,
    report_payload as _report_payload,
)
from backend.reporting.llm_client import LLMError as _LLMError  # noqa: E402


class ReportDraftRequest(BaseModel):
    request: _ReportRequest
    drafts: Dict[str, str] = Field(..., description="JSON {section_id: markdown} do LLM biên tập")
    editor_model: str = ""


@app.post("/reports/generate", tags=["Reports"], summary="Báo cáo chuẩn: thông tin + BodyGraph + nội dung template/LLM")
def reports_generate(req: _ReportRequest, include_bodygraph_svg: bool = Query(False, description="Kèm SVG BodyGraph dạng chuỗi")):
    try:
        document = _generate_report(req)
        return _report_payload(document, include_bodygraph_svg=include_bodygraph_svg and req.include_bodygraph)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/reports/llm-brief", tags=["Reports"], summary="Brief biên tập cho LLM (persona + quy tắc + dữ liệu nguồn)")
def reports_llm_brief(req: _ReportRequest):
    try:
        document = _ReportOrchestrator().run(req)
        return {"brief": _build_llm_brief(document), "section_ids": [s.id for s in document.sections if s.status == "included"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/reports/apply-draft", tags=["Reports"], summary="Ghép bản biên tập LLM + kiểm tra giữ nguyên sự kiện kỹ thuật")
def reports_apply_draft(req: ReportDraftRequest, include_bodygraph_svg: bool = Query(False)):
    try:
        document = _apply_draft(req.request, req.drafts, editor_model=req.editor_model)
        return _report_payload(document, include_bodygraph_svg=include_bodygraph_svg)
    except _LLMError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/reports/bodygraph.svg", tags=["Reports"], summary="BodyGraph SVG tự sinh cho người được phân tích")
def reports_bodygraph(req: _ReportRequest):
    try:
        document = _ReportOrchestrator().run(req)
        return Response(content=_bodygraph_svg(document), media_type="image/svg+xml")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Health check
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "human-design-analyzer", "version": "3.0.0", "engine": "Swiss Ephemeris", "tools": 39, "api_routes": 42, "coverage": "Foundation + 5x12=60 variants + Money 6x14 + Potential 11 Perspectives + v3.0 6 domains", "user_interests": "7 nhu cầu: Money, Health Thân-Tâm-Trí, Potential & Blind Spots, Relationships, Purpose Mission, System Building, Decision & Behavior", "specialized_skills": "25 Markdown skills (01-18, 20-26; 19 reserved), 0 MCP prompts"}

if __name__ == "__main__":
    import uvicorn
    print("""
╔════════════════════════════════════════════════════════════╗
║  Human Design API Server - Cho ChatGPT Web (Custom GPT)    ║
║  Chạy tại: http://localhost:8000                           ║
║  Docs: http://localhost:8000/docs                          ║
║  OpenAPI: http://localhost:8000/openapi.json               ║
║                                                            ║
║  Để tích hợp ChatGPT Web:                                  ║
║  1. Deploy server này lên public URL (ngrok, railway, v.v.)║
║  2. Tạo Custom GPT tại https://chat.openai.com/gpts/editor ║
║  3. Thêm Action với URL openapi.json                       ║
╚════════════════════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
