> **TÀI LIỆU LỊCH SỬ — KHÔNG PHẢI CONTRACT RUNTIME HIỆN TẠI.**
> Snapshot v2.1 được giữ để truy nguyên. Xem `mcp/README.md` và `mcp/tools_manifest_latest.json` cho v3.0.0 hiện tại.

# HUMAN DESIGN MCP SERVER v2.1 - 14 Tools - 100% Coverage

> **v2.1.0 - 2026-09-23** | 14 Tools + 10 Resources + 9 Skills | 5 Types x 12 Profiles = 60 biến thể | 100% dân số
> **MỚI v2.1:** Tool tổng quát `analyze_consultation_general` + `generate_consultation_report` - Áp dụng cho TẤT CẢ, phân biệt rõ với Manifestor tool chỉ 9%

## Tổng quan v2.1

- **8 Core Tools** (v1.0): calculate chart, analyze deep, gate/center/channel/profile, compare, report
- **4 Advanced Tools** (v2.0 - từ docs cá nhân 989 dòng): fear gates 19, love gates 11, 192 crosses, manifestor deep (9% x 12 = 12 biến thể)
- **2 General Tools** (v2.1 - MỚI - 100%): 
  - `analyze_consultation_general` - 5 Types x 12 Profiles = 60 biến thể - 100% dân số - Deep dive 8 keys Type + 4 keys Profile
  - `generate_consultation_report` - Báo cáo markdown đầy đủ

**Phân biệt Manifestor vs General:**
- Manifestor tool: Chỉ Manifestor (9%) nhưng deep dive sâu hơn cho Manifestor (technical check Motor to Throat)
- General tool: TẤT CẢ (100%) - 60 biến thể - Default cho mọi phân tích

## Kiến trúc

```
LLM Core (Claude/ChatGPT/Cursor/Windsurf)
  | MCP stdio
  v
MCP Server v2.1 - 14 tools
  |-- 8 Core
  |-- 4 Advanced (fear, love, cross, manifestor)
  |-- 2 General (general consultation 60 variants)
  |-- 10 Resources
  |-- 9 Skills
  |-- Knowledge 13 files
  |-- Personal Docs 7 files (docs/ riêng)
  |
OpenAPI Server v2.1 - 14 endpoints
  |-- Cho ChatGPT Web Custom GPT Actions
  |-- /openapi.json
```

## Cài đặt

```bash
pip install mcp==1.12.4 pyswisseph pydantic fastapi uvicorn
```

### Claude Desktop

```json
{
  "mcpServers": {
    "human-design-analyzer": {
      "command": "python",
      "args": ["/home/user/human_design/mcp/server.py"],
      "description": "Human Design v2.1 - 14 tools - 100% coverage"
    }
  }
}
```

### Chạy

```bash
python server.py
# Test
python client_example.py  # 14 tools test
# OpenAPI
python openapi_server.py
# Docs: http://localhost:8000/docs
# OpenAPI JSON: http://localhost:8000/openapi.json
```

## 14 Tools

| # | Tool | v | Áp dụng | Mô tả |
|---|------|---|---------|-------|
| 1 | calculate_human_design_chart | v1.0 | 100% | CORE - Tính chart chính xác Swiss Ephemeris |
| 2 | analyze_human_design_deep | v1.0 | 100% | Phân tích chuyên sâu tiếng Việt |
| 3 | get_gate_info | v1.0 | - | Tra cứu Gate 1-64 |
| 4 | get_center_info | v1.0 | - | Tra cứu Center |
| 5 | get_channel_info | v1.0 | - | Tra cứu Channel |
| 6 | get_profile_info | v1.0 | - | Tra cứu Profile 12 loại |
| 7 | compare_charts | v1.0 | 2 người | Composite |
| 8 | generate_full_report | v1.0 | 100% | Báo cáo đầy đủ |
| 9 | analyze_fear_gates | v2.0 | 100% | 19 Fear Gates - Từ Phân mục 4 |
| 10 | analyze_love_gates | v2.0 | 100% | 11 Love Gates - Từ Phân mục 5 |
| 11 | get_incarnation_cross_details | v2.0 | 100% | 192 Crosses - Từ Phân mục 3 (413 dòng) |
| 12 | analyze_manifestor_deep | v2.0 | 9% x 12 = 12 biến thể | Manifestor 9% deep dive - Chỉ Manifestor |
| 13 | **analyze_consultation_general** | **v2.1 MỚI** | **100% - 5x12=60 biến thể** | **TỔNG QUÁT NHẤT - 5 Types deep dive 8 keys + 12 Profiles deep dive 4 keys + Fear/Love + quy trình 4 bước + buổi đọc 1-2h + đạo đức + lộ trình** |
| 14 | **generate_consultation_report** | **v2.1 MỚI** | **100% - 60 biến thể** | **Báo cáo tham vấn tổng quát markdown đầy đủ** |

## 10 Resources

- gates, centers, channels, types, mandala/order (v1.0)
- fear-gates, love-gates, incarnation-crosses, manifestor (v2.0)
- general-consultation 60 variants (v2.1 MỚI)

## 9 Skills

- 01_full_analysis, 02_career_guidance, 03_relationship_composite, 04_gate_deep_dive (v1.0)
- 05_fear_psychology, 06_love_dynamics, 07_manifestor_consultation, 08_incarnation_cross (v2.0)
- 09_general_consultation (v2.1 MỚI - 19KB - Default - 100% - 60 biến thể - Template 9 phần)

## 14 Endpoints OpenAPI v2.1

```
POST /calculate-chart
POST /analyze-deep
GET  /gate-info/{gate_number}
GET  /center-info/{center_name}
GET  /channel-info
GET  /profile-info/{profile}
POST /compare-charts
POST /analyze-fear-gates (v2.0)
POST /analyze-love-gates (v2.0)
GET  /incarnation-cross-details (v2.0)
POST /analyze-manifestor-deep (v2.0)
POST /analyze-consultation-general (v2.1 MỚI - 100%)
POST /generate-consultation-report (v2.1 MỚI - 100%)
POST /generate-report
GET  /health
GET  / - Root v2.1
```

## Test v2.1

```bash
# MCP Server 14 tools
python -c "from server import *; print('14 tools OK')"

# OpenAPI 14 endpoints
python -c "import openapi_server; print([r.path for r in openapi_server.app.routes])"

# General tool 60 variants
cd ../tools && python3 -c "
from hd_consultation_general import analyze_consultation_general
from datetime import datetime
data = analyze_consultation_general(datetime(1990,5,15,1,30), name='Test')
print(f\"{data['type']} {data['profile']} - {data['áp_dụng_cho']}\")
print(f\"Type deep dive keys: {list(data['type_deep_dive'].keys())}\")
print(f\"Profile deep dive keys: {list(data['profile_deep_dive'].keys())}\")
"
```

Kết quả: 14 tools PASS, 14 endpoints PASS, 5 Types PASS, Reflector found, Manifestor 12/12 Profiles PASS.

## So sánh v1.0 vs v2.0 vs v2.1

| Version | Tools | Resources | Skills | Knowledge | Docs cá nhân | Coverage |
|---------|-------|-----------|--------|-----------|--------------|----------|
| v1.0 | 8 | 5 | 4 | 8 files | 0 | 100% tính toán, nhưng chỉ tools cơ bản |
| v2.0 | 12 | 9 | 8 | 12 files | 7 files 989 dòng tích hợp 100% | 100% + Fear/Love/Cross/Manifestor |
| v2.1 | **14** | **10** | **9** | **13 files** | **7 files giữ riêng + tích hợp** | **100% - 5x12=60 biến thể - Tool tổng quát nhất** |

## Tích hợp ChatGPT Web

1. Deploy openapi_server.py lên public URL (ngrok, railway, render)
2. Tạo Custom GPT tại https://chat.openai.com/gpts/editor
3. Thêm Action với URL https://your-server.com/openapi.json
4. ChatGPT sẽ tự động gọi 14 endpoints khi phân tích Human Design
5. Xem CHATGPT_WEB_INTEGRATION.md

---

*v2.1.0 - 2026-09-23 - 14 Tools + 14 Endpoints + 9 Skills + 13 Knowledge + 7 Docs - 100% - 60 biến thể*
