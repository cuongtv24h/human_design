# HUMAN DESIGN MCP SERVER - Model Context Protocol

> Chuẩn hóa theo mô hình Agent với lõi LLM được cung cấp Knowledge qua Tools + Skills theo chuẩn MCP

## 📋 Tổng quan

MCP Server này cung cấp **8 Tools + 5 Resources + 4 Prompts (Skills)** cho bất kỳ LLM nào hỗ trợ MCP (Claude Desktop, Cursor, Windsurf, v.v.)

- **Transport**: stdio (cho Claude Desktop) hoặc streamable-http
- **SDK**: mcp==1.12.4 (FastMCP)
- **Engine**: Swiss Ephemeris (NASA JPL DE431) chính xác <1 arc second
- **Knowledge**: 8 file markdown chuyên sâu tiếng Việt + 4 skills

---

## 🏗️ Kiến trúc Agent

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM CORE (Claude, GPT, etc.)             │
│  - Nhận yêu cầu người dùng: "Phân tích Human Design cho..." │
│  - Gọi MCP Tools để lấy dữ liệu chính xác                   │
│  - Dùng Skills (Prompts) để định hướng phân tích            │
│  - Tổng hợp báo cáo cuối                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────▼──────────────────────────────────────┐
│              HUMAN DESIGN MCP SERVER (server.py)            │
│                                                             │
│  TOOLS (8):                                                 │
│  ├─ calculate_human_design_chart (CORE)                     │
│  ├─ analyze_human_design_deep                               │
│  ├─ get_gate_info                                           │
│  ├─ get_center_info                                         │
│  ├─ get_channel_info                                        │
│  ├─ get_profile_info                                        │
│  ├─ compare_charts (Composite)                              │
│  └─ generate_full_report                                    │
│                                                             │
│  RESOURCES (5):                                             │
│  ├─ human-design://knowledge/gates (64 gates)               │
│  ├─ human-design://knowledge/centers (9 centers)            │
│  ├─ human-design://knowledge/channels (36 channels)         │
│  ├─ human-design://knowledge/types (5 types)                │
│  └─ human-design://mandala/order (64 gate order)            │
│                                                             │
│  PROMPTS/SKILLS (4):                                        │
│  ├─ analyze_human_design_full                               │
│  ├─ analyze_career_path                                     │
│  ├─ analyze_relationship                                    │
│  └─ explain_gate                                            │
│                                                             │
│  KNOWLEDGE BASE (8 files):                                  │
│  └─ ../knowledge/*.md (751 dòng chuyên sâu)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              CALCULATION ENGINE (hd_calculator.py)          │
│  - Swiss Ephemeris                                          │
│  - Gate mapping: 302° = Gate 41 start                       │
│  - 64 gates x 6 lines x 6 colors x 6 tones x 5 bases        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Cài đặt

### Yêu cầu
```bash
pip install mcp==1.12.4 pyswisseph pydantic
```

### Cấu hình Claude Desktop

Thêm vào `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "human-design-analyzer": {
      "command": "python",
      "args": ["/home/user/human_design/mcp/server.py"],
      "env": {},
      "description": "Human Design Analysis System"
    }
  }
}
```

Hoặc dùng file có sẵn: `mcp_config.json`

### Chạy server độc lập

```bash
# Development với Inspector
mcp dev server.py

# Chạy trực tiếp
python server.py

# Hoặc
mcp run server.py
```

---

## 🛠️ Danh sách Tools chi tiết

### 1. calculate_human_design_chart (CORE - BẮT BUỘC GỌI ĐẦU TIÊN)

Tính toán chart chính xác.

**Input:**
- birth_date: YYYY-MM-DD
- birth_time: HH:MM
- timezone: +07:00 (mặc định VN)
- name, birth_location (tùy chọn)

**Output:** JSON với Type, Strategy, Authority, Profile, Centers, Channels, Gates, Cross

**Ví dụ LLM gọi:**
```json
{
  "tool": "calculate_human_design_chart",
  "arguments": {
    "birth_date": "1990-05-15",
    "birth_time": "08:30",
    "timezone": "+07:00",
    "name": "Nguyen Van A"
  }
}
```

### 2. analyze_human_design_deep

Phân tích chuyên sâu tiếng Việt.

**Input:** birth_date, birth_time, timezone, name, focus_area (full/type/authority/centers/channels/profile/career/relationship/health)

### 3. get_gate_info

Tra cứu 1 cổng 1-64.

### 4. get_center_info

Tra cứu 1 trung tâm: Head, Ajna, Throat, G, Heart, Spleen, Sacral, Solar Plexus, Root

### 5. get_channel_info

Tra cứu 1 kênh: gate1, gate2

### 6. get_profile_info

Tra cứu Profile: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1, 5/1, 5/2, 6/2, 6/3

### 7. compare_charts

So sánh 2 người (Composite) - electromagnetic, dominance, common gates

### 8. generate_full_report

Tạo báo cáo đầy đủ markdown/json

---

## 📚 Resources (Knowledge)

LLM có thể đọc resources để có kiến thức nền:

- `human-design://knowledge/gates` - 64 gates
- `human-design://knowledge/centers` - 9 centers
- `human-design://knowledge/channels` - 36 channels
- `human-design://knowledge/types` - 5 types
- `human-design://mandala/order` - Thứ tự Mandala

---

## 🎯 Skills (Prompts)

Skills là prompt templates hướng dẫn LLM phân tích:

### Skill 1: analyze_human_design_full
**Khi dùng:** Người dùng yêu cầu phân tích toàn diện
**Quy trình:**
1. Gọi calculate_human_design_chart
2. Gọi analyze_human_design_deep full
3. Gọi thêm get_gate_info, get_center_info nếu cần
4. Tổng hợp báo cáo theo cấu trúc chuẩn 7 phần

### Skill 2: analyze_career_path
**Khi dùng:** Hướng nghiệp
**Tập trung:** Type, Centers, Channels, Profile, Cross -> nghề phù hợp

### Skill 3: analyze_relationship
**Khi dùng:** Phân tích mối quan hệ
**Quy trình:** calculate 2 charts + compare_charts -> electromagnetic, dominance

### Skill 4: explain_gate
**Khi dùng:** Giải thích 1 cổng cho người mới
**Quy trình:** get_gate_info -> giải thích dễ hiểu + ví dụ

---

## 📁 Cấu trúc thư mục

```
human_design/
├── knowledge/ (8 files - 751 dòng)
│   ├── 00_tong_quan_he_thong.md
│   ├── 01_mandala_64_cong.md
│   ├── 02_9_trung_tam.md
│   ├── 03_36_kenh.md
│   ├── 04_5_loai_va_chien_luoc.md
│   ├── 05_profile_cross_definition.md
│   ├── 06_phuong_phap_tinh_toan.md
│   └── 07_ung_dung_thuc_tien.md
├── tools/ (Engine)
│   ├── hd_calculator.py (569 dòng - Swiss Ephemeris)
│   ├── hd_analyzer.py (305 dòng)
│   ├── hd_cli.py
│   └── test_calculator.py
└── mcp/ (MCP Standard)
    ├── server.py (MCP Server - 8 tools + 5 resources + 4 prompts)
    ├── tools_manifest.json (Manifest đầy đủ)
    ├── mcp_config.json (Config cho Claude Desktop)
    ├── client_example.py (Ví dụ gọi tools)
    ├── README.md (File này)
    └── skills/ (4 skills)
        ├── 01_full_analysis.md
        ├── 02_career_guidance.md
        ├── 03_relationship_composite.md
        └── 04_gate_deep_dive.md
```

---

## 🧪 Test

```bash
cd /home/user/human_design/mcp
python client_example.py
```

Kết quả: 8 tests pass, bao gồm tính chart, phân tích, tra cứu gate/center/channel/profile, composite, báo cáo.

---

## 🔄 Luồng hoạt động Agent chuẩn

**User:** "Phân tích Human Design cho Nguyễn Văn A sinh 1990-05-15 lúc 08:30 ở Hà Nội"

**LLM Core:**

1. Nhận diện intent: full analysis
2. Gọi Skill: `analyze_human_design_full` -> nhận prompt hướng dẫn
3. Gọi Tool: `calculate_human_design_chart` với birth_date=1990-05-15, birth_time=08:30, timezone=+07:00, name=Nguyen Van A
   -> Nhận: Type=Projector, Authority=Emotional, Profile=6/2, Centers=7 defined, Channels=5
4. Gọi Tool: `analyze_human_design_deep` focus_area=full
   -> Nhận báo cáo chi tiết tiếng Việt
5. (Tùy chọn) Gọi thêm `get_channel_info` cho 5 kênh định nghĩa để giải thích sâu
6. Tổng hợp thành báo cáo cuối cho user theo cấu trúc 7 phần chuẩn

**User nhận:** Báo cáo đầy đủ, chuyên sâu, chính xác, có thể xuất file.

---

## ✅ Đã chuẩn hóa theo MCP

- ✅ Tools có input_schema/output_schema JSON Schema chuẩn
- ✅ Resources có URI chuẩn human-design://
- ✅ Prompts (Skills) có arguments rõ ràng
- ✅ Knowledge base được cung cấp qua Resources + Skills
- ✅ Server chạy được với mcp dev, mcp run, Claude Desktop
- ✅ Có manifest, config, client example, README
- ✅ Đã test 8 luồng

---

## 🚀 Sẵn sàng tích hợp

MCP Server này có thể tích hợp vào:
- Claude Desktop
- Cursor
- Windsurf
- Any LLM hỗ trợ MCP
- Custom Agent với MCP Client

Chỉ cần cấu hình `mcp_config.json` và LLM sẽ tự động có khả năng phân tích Human Design chuyên sâu.

---

*Tác giả: Agent Mode - 2026-09-23 - Human Design MCP Server v1.0.0*
