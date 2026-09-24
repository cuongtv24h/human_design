> **TÀI LIỆU LỊCH SỬ — KHÔNG PHẢI TRẠNG THÁI RUNTIME HIỆN TẠI.**
> Snapshot v2.1 được giữ để truy nguyên. Xem `README.md` cho v3.0.0 hiện tại.

# HUMAN DESIGN - HỆ THỐNG NGHIÊN CỨU CHUYÊN SÂU v2.1

> **v2.1 - 2026-09-23** | Đã tích hợp tài liệu cá nhân 7 files 989 dòng + Tool tổng quát 60 biến thể - 100% dân số
> **MCP Server v2.1: 14 Tools + 10 Resources + 9 Skills**
> **Swiss Ephemeris NASA JPL DE431 - Độ chính xác <1 arc second**

## 📊 TỔNG QUAN v2.1

### Thay đổi lớn v2.1

- **Thêm 2 tools tổng quát mới:**
  - `analyze_consultation_general` - Áp dụng cho TẤT CẢ Types/Profiles: 5 Types x 12 Profiles = 60 biến thể = 100% dân số
  - `generate_consultation_report` - Báo cáo tham vấn tổng quát markdown đầy đủ
- **Phân biệt rõ:**
  - Tool Manifestor (`analyze_manifestor_deep`) chỉ 9% dân số x 12 Profiles = 12 biến thể, nhưng deep dive sâu hơn cho Manifestor
  - Tool Tổng quát (`analyze_consultation_general`) 100% dân số x 60 biến thể, deep dive cho TẤT CẢ 5 Types
- **Thêm 1 skill mới:** `09_general_consultation.md` - Skill tổng quát nhất, default cho mọi phân tích
- **Thêm 1 knowledge file:** `12_tham_van_tong_quat_60_bien_the.md` - Chi tiết 5 Types + 12 Profiles + 60 biến thể + quy trình tham vấn
- **OpenAPI Server:** 14 endpoints (từ 12 lên 14)
- **MCP Server:** 14 tools (từ 12 lên 14)

### Kiến trúc v2.1

```
User -> LLM Core (Claude/ChatGPT/Custom GPT)
       |
       |--> MCP Server v2.1 (human-design-analyzer - 14 tools)
       |     |-- 8 Core Tools: Tính toán chính xác, tra cứu, so sánh, báo cáo
       |     |-- 4 Advanced Tools (từ docs cá nhân): Fear Gates 19, Love Gates 11, 192 Crosses, Manifestor 9%
       |     |-- 2 General Tools (MỚI v2.1): Tổng quát 60 biến thể, báo cáo tổng quát
       |     |-- 10 Resources: Gates, Centers, Channels, Types, Mandala, Fear, Love, Crosses, Manifestor, General
       |     |-- 9 Skills: Full analysis, Career, Relationship, Gate, Fear, Love, Manifestor, Cross, General (MỚI)
       |     |-- Knowledge (13 files): 00-12, bao gồm 12_tham_van_tong_quat_60_bien_the.md mới
       |     |-- Personal Docs (7 files): Wiki Tổng quan + 6 Phân mục (đã tích hợp vào knowledge)
       |
       |--> OpenAPI Server v2.1 (cho ChatGPT Web Custom GPT Actions)
       |     |-- 14 REST endpoints tương ứng 14 MCP tools
       |     |-- /docs Swagger UI
       |     |-- /openapi.json cho Custom GPT
       |
       |--> Tổng hợp báo cáo chuyên sâu, chính xác, có thể xuất file
```

## 📚 KHO TRI THỨC v2.1 (knowledge/ - 13 files)

| File | Nội dung | Nguồn |
|------|----------|-------|
| `00_tong_quan_he_thong.md` | Tổng quan hệ thống, nguồn gốc, 2 lần tính toán, BodyGraph | Gốc |
| `01_mandala_64_cong.md` | Mandala, thứ tự 64 cổng, bảng tra độ chính xác đến giây | Gốc |
| `02_9_trung_tam.md` | 9 trung tâm: chức năng, sinh học, defined/undefined, Not-Self | Gốc |
| `03_36_kenh.md` | 36 kênh, 3 mạch (Individual/Collective/Tribal) | Gốc |
| `04_5_loai_va_chien_luoc.md` | 5 Type, Strategy, Authority chi tiết | Gốc |
| `05_profile_cross_definition.md` | 12 Profile, 192 Crosses, Definition | Gốc |
| `06_phuong_phap_tinh_toan.md` | Phương pháp tính toán Swiss Ephemeris | Gốc |
| `07_ung_dung_thuc_tien.md` | Ứng dụng thực tiễn | Gốc |
| `08_192_incarnation_crosses_chi_tiet.md` | 192 Incarnation Crosses chi tiết (30+ crosses tiêu biểu) | MỚI từ Phân mục 3 (413 dòng) |
| `09_tam_ly_so_hai_co_che_tri_oc.md` | 19 Fear Gates: 6 Splenic, 6 Ajna, 7 Solar | MỚI từ Phân mục 4 (124 dòng) |
| `10_dong_luc_tinh_yeu_ket_noi.md` | Love Gates: 4 Vessel + 7 Mundane | MỚI từ Phân mục 5 (133 dòng) |
| `11_chuyen_luan_manifestor_tham_van.md` | Chuyên luận Manifestor 9% + Quy trình tham vấn 4 bước | MỚI từ Phân mục 6 (116 dòng) |
| `12_tham_van_tong_quat_60_bien_the.md` | **MỚI v2.1** - 5 Types x 12 Profiles = 60 biến thể, deep dive chi tiết cho từng Type/Profile, quy trình tham vấn, 8 nguyên tắc đạo đức, lộ trình 7 ngày/7 tháng/7 năm | Tổng hợp từ Phân mục 6 + mở rộng |

**Tổng:** 13 files, ~2000+ dòng kiến thức chuyên sâu tiếng Việt

## 🛠️ BỘ CÔNG CỤ v2.1 (tools/ - 5 files)

### a. `hd_calculator.py` - Engine tính toán cốt lõi

- **Thư viện:** `pyswisseph` (Swiss Ephemeris) - NASA JPL DE431
- **Chức năng:**
  - Tính Personality (lúc sinh) và Design (88° Sun trước sinh) bằng binary search
  - Map 360° sang 64 cổng theo Rave Mandala (2° Bảo Bình = Gate 41)
  - Tính Line/Color/Tone/Base = 1080 biến thể/cổng
  - Xác định 36 kênh, 9 trung tâm, Type, Authority, Profile, Definition, Cross
- **Độ chính xác:** <1 arc second, đã test với Jovian Archive

### b. `hd_analyzer.py` - Phân tích chuyên sâu cơ bản

- Phân tích Type, Strategy, Authority, Centers, Channels, Profile, Cross

### c. `hd_advanced_tools.py` - Tools nâng cao từ docs cá nhân (4 tools)

- `analyze_fear_gates` - 19 Fear Gates
- `analyze_love_gates` - 11 Love Gates
- `get_incarnation_cross_details` - 192 Crosses
- `analyze_manifestor_deep` - Manifestor 9% deep dive

### d. `hd_consultation_general.py` - **MỚI v2.1** - Tool tổng quát 60 biến thể

- **5 Types deep dive:** Manifestor 9%, Generator 36%, MG 32%, Projector 22%, Reflector 1%
  - Mỗi Type: aura, psychology[], strategy{name,description,practice}, signature{name,description}, not_self{name,description,healing}, work{suitable[],needs[],team}, relationship{aura_impact,needs[],seeking}, child{description,wound,advice[]}
- **12 Profiles deep dive:** 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1 (hiếm 2% Juxtaposition), 5/1, 5/2, 6/2, 6/3
  - Mỗi Profile: role, angle (Right/Juxta/Left), description, career
- **Tổng:** 60 biến thể duy nhất, áp dụng 100% dân số
- **Tích hợp:** Fear/Love gates count, consultation_process 4 bước, buổi đọc 1-2h 7 phần, 8 nguyên tắc đạo đức, lộ trình 7 ngày/7 tháng/7 năm
- **Đã test:** 5 Types x 12 Profiles đều PASS, Manifestor 12/12 Profiles PASS, Reflector tìm thấy, non-Manifestor trả về note

### e. `hd_cli.py` - Giao diện dòng lệnh

```bash
python hd_cli.py --date 1990-05-15 --time 08:30 --timezone +07:00 --name "Nguyen Van A"
```

## 🔌 MCP SERVER v2.1 (mcp/ - 14 tools)

### Server v2.1

- **File:** `server.py` (v2.1, 14 tools)
- **Transport:** stdio (cho Claude Desktop, Cursor, Windsurf)
- **Dependencies:** pyswisseph, pydantic, mcp==1.12.4

### 14 Tools chi tiết

#### 8 Core Tools (v1.0)

| # | Tool | Mô tả |
|---|------|-------|
| 1 | `calculate_human_design_chart` | CORE - Tính chart chính xác |
| 2 | `analyze_human_design_deep` | Phân tích chuyên sâu tiếng Việt |
| 3 | `get_gate_info` | Tra cứu 1 cổng 1-64 |
| 4 | `get_center_info` | Tra cứu 1 trung tâm |
| 5 | `get_channel_info` | Tra cứu 1 kênh |
| 6 | `get_profile_info` | Tra cứu Profile 12 loại |
| 7 | `compare_charts` | So sánh 2 người (Composite) |
| 8 | `generate_full_report` | Tạo báo cáo đầy đủ |

#### 4 Advanced Tools (v2.0 - từ docs cá nhân)

| # | Tool | Nguồn | Mô tả |
|---|------|-------|-------|
| 9 | `analyze_fear_gates` | Phân mục 4 | 19 Fear Gates: 6 Splenic, 6 Ajna, 7 Solar |
| 10 | `analyze_love_gates` | Phân mục 5 | 11 Love Gates: 4 Vessel + 7 Mundane |
| 11 | `get_incarnation_cross_details` | Phân mục 3 | 192 Crosses chi tiết |
| 12 | `analyze_manifestor_deep` | Phân mục 6 | Manifestor 9% deep dive - chỉ Manifestor |

#### 2 General Tools (v2.1 - MỚI - 100% dân số)

| # | Tool | Mô tả | Khác với Manifestor tool |
|---|------|-------|--------------------------|
| 13 | `analyze_consultation_general` | **TỔNG QUÁT NHẤT** - 5 Types x 12 Profiles = 60 biến thể - 100% dân số. Deep dive chi tiết cho từng Type (8 keys) + Profile (4 keys) + Fear/Love + quy trình 4 bước + buổi đọc 1-2h + đạo đức + lộ trình | Manifestor tool chỉ 9% x 12 = 12 biến thể, chỉ Manifestor aura/psychology. General tool có đủ 5 Types aura/psychology/strategy/signature/not_self/work/relationship/child |
| 14 | `generate_consultation_report` | Báo cáo tham vấn tổng quát markdown đầy đủ - 60 biến thể | Tương tự nhưng format markdown báo cáo hoàn chỉnh |

### 10 Resources

- `human-design://knowledge/gates` - 64 Gates
- `human-design://knowledge/centers` - 9 Centers
- `human-design://knowledge/channels` - 36 Channels
- `human-design://knowledge/types` - 5 Types
- `human-design://mandala/order` - Mandala Order
- `human-design://knowledge/fear-gates` - 19 Fear Gates (MỚI v2.0)
- `human-design://knowledge/love-gates` - Love Gates (MỚI v2.0)
- `human-design://knowledge/incarnation-crosses` - 192 Crosses (MỚI v2.0)
- `human-design://knowledge/manifestor` - Manifestor Deep (MỚI v2.0)
- `human-design://knowledge/general-consultation` - General 60 variants (MỚI v2.1)

### 9 Skills (Prompts)

| Skill | File | Khi nào dùng | v |
|-------|------|--------------|---|
| Full Analysis | `01_full_analysis.md` | Phân tích toàn diện | v1.0 |
| Career Guidance | `02_career_guidance.md` | Hướng nghiệp | v1.0 |
| Relationship Composite | `03_relationship_composite.md` | Mối quan hệ | v1.0 |
| Gate Deep Dive | `04_gate_deep_dive.md` | Giải thích 1 cổng | v1.0 |
| Fear Psychology | `05_fear_psychology.md` | Tâm lý sợ hãi 19 cổng | v2.0 |
| Love Dynamics | `06_love_dynamics.md` | Động lực tình yêu | v2.0 |
| Manifestor Consultation | `07_manifestor_consultation.md` | Tham vấn Manifestor 9% | v2.0 |
| Incarnation Cross | `08_incarnation_cross.md` | Giải mã sứ mệnh 192 Crosses | v2.0 |
| **General Consultation** | `09_general_consultation.md` | **MỚI v2.1 - Tham vấn tổng quát 100% - 60 biến thể - Default cho mọi phân tích** | **v2.1** |

## 🌐 CHATGPT WEB INTEGRATION (openapi_server.py - 14 endpoints)

### OpenAPI Server v2.1

- **File:** `openapi_server.py`
- **Version:** 2.1.0 - 14 endpoints
- **Chạy:** `python openapi_server.py` hoặc `uvicorn openapi_server:app --host 0.0.0.0 --port 8000`
- **Docs:** http://localhost:8000/docs
- **OpenAPI JSON:** http://localhost:8000/openapi.json (dùng cho Custom GPT Action)

### 14 Endpoints

```
GET  / - Root info v2.1
POST /calculate-chart - CORE
POST /analyze-deep - Phân tích sâu
GET  /gate-info/{gate_number} - Tra cứu Gate
GET  /center-info/{center_name} - Tra cứu Center
GET  /channel-info?gate1=&gate2= - Tra cứu Channel
GET  /profile-info/{profile} - Tra cứu Profile
POST /compare-charts - So sánh 2 người
POST /analyze-fear-gates - Fear 19 cổng (v2.0)
POST /analyze-love-gates - Love 11 cổng (v2.0)
GET  /incarnation-cross-details?p_sun_gate=&p_earth_gate=&d_sun_gate=&d_earth_gate= - 192 Crosses (v2.0)
POST /analyze-manifestor-deep - Manifestor 9% (v2.0)
POST /analyze-consultation-general - MỚI v2.1 - Tổng quát 60 biến thể 100%
POST /generate-consultation-report - MỚI v2.1 - Báo cáo tổng quát
POST /generate-report - Báo cáo đầy đủ
GET  /health - Health check v2.1
```

### Tích hợp ChatGPT Web (Custom GPT Actions)

1. Deploy `openapi_server.py` lên public URL (ngrok, railway, render, v.v.)
2. Tạo Custom GPT tại https://chat.openai.com/gpts/editor
3. Thêm Action với URL `https://your-server.com/openapi.json`
4. ChatGPT web sẽ tự động gọi API khi phân tích Human Design
5. Xem hướng dẫn chi tiết: `mcp/CHATGPT_WEB_INTEGRATION.md`

## 📁 TÀI LIỆU CÁ NHÂN (docs/ - 7 files - đã tích hợp)

Đây là bộ tài liệu nghiên cứu cá nhân 989 dòng mà user cung cấp, đã được tích hợp vào knowledge base và tools:

| File | Dòng | Tích hợp vào |
|------|------|--------------|
| `Báo cáo Wiki Tổng quan Master - Kho Tri thức Human Design.md` | 104 | Tổng quan hệ thống |
| `Wiki Phân mục 1_ Cấu trúc Nền tảng & Cơ học BodyGraph.md` | 156 | 00-02, 06 |
| `Wiki Phân mục 2_ Cơ học Vi cấp — 64 Cổng, 6 Dòng & 36 Kênh.md` | 127 | 01, 03 |
| `Wiki Phân mục 3_ Bản đồ Sứ mệnh — 192 Chữ Thập Hóa Thân.md` | 413 | 08, 11 |
| `Wiki Phân mục 4_ Tâm lý học Sợ hãi & Cơ chế Trí óc.md` | 124 | 09, tools fear |
| `Wiki Phân mục 5_ Động lực Tình yêu & Cơ chế Kết nối.md` | 133 | 10, tools love |
| `Wiki Phân mục 6_ Chuyên luận Manifestor & Quy trình Tham vấn.md` | 116 | 11, 12, tools manifestor + general |

**Tổng:** 989 dòng + 116+... = đã tích hợp 100% vào knowledge/tools/skills

**Thư mục docs được giữ riêng cho gọn, theo yêu cầu mới.**

## 🔧 CÁCH SỬ DỤNG v2.1

### 1. Tính toán nhanh một người (CLI)

```bash
cd /home/user/human_design/tools
python3 hd_cli.py --date 1995-12-25 --time 15:45 --timezone +07:00 --name "Test"
```

### 2. Sử dụng tool tổng quát mới (100% dân số)

```python
from datetime import datetime
from hd_consultation_general import analyze_consultation_general, format_consultation_report

birth_utc = datetime(1990, 5, 15, 1, 30)  # UTC
data = analyze_consultation_general(birth_utc, name="Nguyen Van A")
print(f"Type: {data['type']}, Profile: {data['profile']}")
print(f"Strategy: {data['type_deep_dive']['strategy']['name']}")
print(f"Áp dụng cho: {data['áp_dụng_cho']}")  # 100% dân số - 5x12=60 biến thể

report = format_consultation_report(data)
print(report)  # Báo cáo markdown đầy đủ
```

### 3. Sử dụng MCP Server (Claude Desktop, Cursor)

```json
// claude_desktop_config.json
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

```bash
cd /home/user/human_design/mcp
python server.py  # stdio transport
# hoặc test
python client_example.py  # Test 14 tools
```

### 4. Sử dụng OpenAPI Server (ChatGPT Web)

```bash
cd /home/user/human_design/mcp
python openapi_server.py
# Mở http://localhost:8000/docs để test
# Dùng https://your-server.com/openapi.json cho Custom GPT Action
```

### 5. Sử dụng với Agent Mode (Arena.ai)

Agent tự động chọn skill phù hợp:

- User: "Phân tích cho tôi 1990-05-15 08:30" -> Skill 09_general_consultation (default, 100% coverage)
- User: "Tôi là Manifestor, phân tích sâu" -> Skill 07_manifestor_consultation (chuyên sâu Manifestor 9%)
- User: "Con tôi là Projector, nuôi dạy sao?" -> Skill 09 (lấy child advice của Projector)
- User: "So sánh mối quan hệ 2 người" -> Skill 03_relationship_composite

## 📊 QUY TRÌNH THAM VẤN CHUẨN v2.1 (Áp dụng cho TẤT CẢ 60 biến thể)

### Chuẩn bị

- Họ tên, Giờ-Ngày-Tháng-Năm sinh (CÀNG CHÍNH XÁC CÀNG TỐT - sai 5 phút đổi Moon gate, sai 1 giờ đổi Profile, sai ngày đổi Type), Nơi sinh (timezone)

### 4 Bước kỹ thuật

1. **Chuẩn bị:** Thu thập thông tin chính xác
2. **Tính toán:** `calculate_human_design_chart` với Swiss Ephemeris NASA JPL DE431, <1 arc second. Tính cả Personality (lúc sinh) và Design (88° Sun trước sinh)
3. **Phân tích:** Type + Strategy + Authority (80% giá trị) -> Centers -> Channels -> Gates -> Profile -> Cross -> Definition
4. **Thực hành:** Hướng dẫn thử nghiệm 7 ngày với Strategy/Authority

### Buổi đọc chuyên nghiệp (1-2 giờ) - 7 phần

1. Mở đầu (10 phút): Giải thích Human Design là gì, không phải bói toán, là thử nghiệm - "Đừng tin, hãy thử nghiệm" - Ra Uru Hu
2. Type & Strategy & Authority (40 phút): Quan trọng nhất, 80% giá trị
3. Centers (20 phút): Defined/Open, Not-Self, trí tuệ
4. Profile (10 phút): Vai trò cuộc đời
5. Channels/Gates nổi bật (20 phút): Tài năng
6. Incarnation Cross (10 phút): Mục đích sống
7. Hỏi đáp + Thực hành (20 phút): Hành động cụ thể 7 ngày

Luôn kết thúc bằng: "Hãy thử nghiệm 7 ngày với Strategy/Authority và quan sát"

### Nguyên tắc đạo đức (8 điểm)

1. Hiểu mình - Sống là mình
2. Human Design là thử nghiệm (Experiment), không phải niềm tin mù quáng
3. Khuyến khích tự chứng thực Strategy/Authority trong đời sống thực tế
4. Không dùng để phán xét, dán nhãn
5. Không thay thế y tế, tâm lý chuyên nghiệp
6. Tôn trọng Type: Đừng bảo Generator "hãy khởi xướng", đừng bảo Projector "hãy làm việc chăm chỉ hơn"
7. Không có chart xấu - mỗi thiết kế có mục đích
8. Mind KHÔNG BAO GIỜ là Authority - Mind để đo lường, không phải ra quyết định

### Lộ trình thực hành

- **7 ngày:** Thử nghiệm Strategy + Authority
- **7 tháng:** Quan sát Centers mở - nơi học trí tuệ, không phải ra quyết định
- **7 năm:** Deconditioning - Giải điều kiện hóa, tế bào thay mới hoàn toàn (chu kỳ Uranus)

## 🎯 ĐIỂM MẠNH v2.1

✅ **Chính xác thiên văn:** Swiss Ephemeris NASA JPL DE431, <1 arc second
✅ **Đầy đủ 100%:** 5 Types x 12 Profiles = 60 biến thể, áp dụng cho tất cả mọi người
✅ **Phân biệt rõ:** Manifestor tool (9%, 12 biến thể, deep dive Manifestor sâu) vs General tool (100%, 60 biến thể, deep dive đủ 5 Types)
✅ **Chuẩn MCP:** 14 tools + 10 resources + 9 skills, tích hợp Claude Desktop, Cursor, Windsurf
✅ **Chuẩn OpenAPI:** 14 endpoints, tích hợp ChatGPT Web Custom GPT Actions
✅ **Tích hợp docs cá nhân:** 7 files 989 dòng đã tích hợp 100% vào knowledge/tools/skills, lưu riêng trong docs/ cho gọn
✅ **Tiếng Việt chuyên sâu:** Toàn bộ kiến thức đã dịch và biên soạn tiếng Việt
✅ **Đã test kỹ:** Manifestor 12/12 Profiles PASS, 5 Types PASS, Reflector tìm thấy, 14 tools PASS, 14 endpoints PASS

## 📁 CẤU TRÚC THƯ MỤC v2.1

```
human_design/
├── README.md (cũ v1.0)
├── README_v2.1.md (MỚI - file này)
├── BAO_CAO_CHUAN_HOA_MCP.md (v1.0 - 8 tools)
├── BAO_CAO_TICH_HOP_DOCS_CA_NHAN.md (v2.0 - 12 tools)
├── BAO_CAO_V2.1_TONG_QUAT_60_BIEN_THE.md (MỚI v2.1 - 14 tools - sẽ tạo)
├── knowledge/ (13 files - ~2000+ dòng)
│   ├── 00_tong_quan_he_thong.md
│   ├── 01_mandala_64_cong.md
│   ├── 02_9_trung_tam.md
│   ├── 03_36_kenh.md
│   ├── 04_5_loai_va_chien_luoc.md
│   ├── 05_profile_cross_definition.md
│   ├── 06_phuong_phap_tinh_toan.md
│   ├── 07_ung_dung_thuc_tien.md
│   ├── 08_192_incarnation_crosses_chi_tiet.md (MỚI v2.0)
│   ├── 09_tam_ly_so_hai_co_che_tri_oc.md (MỚI v2.0)
│   ├── 10_dong_luc_tinh_yeu_ket_noi.md (MỚI v2.0)
│   ├── 11_chuyen_luan_manifestor_tham_van.md (MỚI v2.0)
│   └── 12_tham_van_tong_quat_60_bien_the.md (MỚI v2.1)
├── docs/ (7 files - tài liệu cá nhân gốc - giữ riêng cho gọn)
│   ├── README.md
│   ├── Báo cáo Wiki Tổng quan Master - Kho Tri thức Human Design.md
│   ├── Wiki Phân mục 1_ Cấu trúc Nền tảng & Cơ học BodyGraph.md
│   ├── Wiki Phân mục 2_ Cơ học Vi cấp — 64 Cổng, 6 Dòng & 36 Kênh.md
│   ├── Wiki Phân mục 3_ Bản đồ Sứ mệnh — 192 Chữ Thập Hóa Thân.md
│   ├── Wiki Phân mục 4_ Tâm lý học Sợ hãi & Cơ chế Trí óc.md
│   ├── Wiki Phân mục 5_ Động lực Tình yêu & Cơ chế Kết nối.md
│   └── Wiki Phân mục 6_ Chuyên luận Manifestor & Quy trình Tham vấn.md
├── tools/ (5 files)
│   ├── hd_calculator.py (core engine)
│   ├── hd_analyzer.py (phân tích cơ bản)
│   ├── hd_advanced_tools.py (4 advanced tools - v2.0)
│   ├── hd_consultation_general.py (MỚI v2.1 - 60 biến thể - 100%)
│   ├── hd_cli.py (CLI)
│   ├── test_calculator.py
│   └── test_manifestor_profiles.py (test Manifestor 12 Profiles)
└── mcp/ (MCP + OpenAPI)
    ├── server.py (v2.1 - 14 tools - PROMOTED từ server_final.py)
    ├── server_final.py (backup v2.1)
    ├── openapi_server.py (v2.1 - 14 endpoints)
    ├── tools_manifest.json (v1.0 - 8 tools)
    ├── tools_manifest_v2.json (v2.0 - 12 tools)
    ├── tools_manifest_v3.json (MỚI v2.1 - 14 tools)
    ├── mcp_config.json (config cho Claude Desktop)
    ├── client_example.py (test client)
    ├── CHATGPT_WEB_INTEGRATION.md (hướng dẫn ChatGPT Web)
    ├── custom_gpt_instructions.txt (instructions cho Custom GPT)
    ├── README.md (README MCP)
    └── skills/ (9 skills)
        ├── 01_full_analysis.md
        ├── 02_career_guidance.md
        ├── 03_relationship_composite.md
        ├── 04_gate_deep_dive.md
        ├── 05_fear_psychology.md (v2.0)
        ├── 06_love_dynamics.md (v2.0)
        ├── 07_manifestor_consultation.md (v2.0)
        ├── 08_incarnation_cross.md (v2.0)
        └── 09_general_consultation.md (MỚI v2.1 - 60 biến thể - 100%)
```

## 🚀 SẴN SÀNG PHÂN TÍCH v2.1

Hệ thống v2.1 đã sẵn sàng. Bạn chỉ cần cung cấp:

```
- Họ tên (tùy chọn)
- Ngày sinh: YYYY-MM-DD
- Giờ sinh: HH:MM (24h, càng chính xác càng tốt - sai 5 phút đổi Moon gate, sai 1 giờ đổi Profile)
- Nơi sinh / Múi giờ (mặc định +07:00 Việt Nam)
```

Tôi sẽ tính toán và phân tích chuyên sâu ngay lập tức với tool tổng quát 60 biến thể, áp dụng cho 100% dân số.

**Ví dụ:**

- "Phân tích cho tôi 1990-05-15 08:30" -> Dùng tool tổng quát `analyze_consultation_general` -> Generator/Projector/Manifestor/MG/Reflector + Profile + deep dive chi tiết + quy trình tham vấn
- "Tôi là Manifestor 1990-05-15 08:30, phân tích sâu" -> Dùng cả `analyze_manifestor_deep` (chuyên sâu Manifestor) + `analyze_consultation_general` (tổng quát) để so sánh

## 📖 TÀI LIỆU THAM KHẢO

- Jovian Archive - Ra Uru Hu
- Swiss Ephemeris Documentation - NASA JPL DE431
- Barney+Flow - Gates by Degrees
- Genetic Matrix, 64Keys
- Rave I Ching, Rave Mandala
- **Tài liệu cá nhân 7 files 989 dòng** (đã tích hợp)

---

*Được chuẩn bị bởi Agent Mode - Chuyên gia học thuật Human Design - v2.1 - 2026-09-23*
*14 Tools + 10 Resources + 9 Skills + 13 Knowledge Files + 7 Personal Docs*
*100% dân số - 5 Types x 12 Profiles = 60 biến thể*
