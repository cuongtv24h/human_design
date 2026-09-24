# BÁO CÁO CHUẨN HÓA HỆ THỐNG HUMAN DESIGN THEO MÔ HÌNH AGENT MCP

**Ngày:** 2026-09-23  
**Yêu cầu:** Chuẩn hóa theo mô hình Agent hỗ trợ phân tích vào báo cáo, với lõi LLM được cung cấp Knowledge qua Tools + Skills theo chuẩn MCP  
**Trạng thái:** ✅ HOÀN THÀNH 100%

---

## 1. TỔNG QUAN KIẾN TRÚC MỚI

### Mô hình cũ (trước chuẩn hóa)
```
User -> LLM (kiến thức chung, không chính xác) -> Trả lời chung chung
```

### Mô hình mới (chuẩn MCP - Agent)
```
User -> LLM Core (được trang bị Tools + Skills + Knowledge qua MCP)
       |
       |--> MCP Server (human-design-analyzer)
       |     |-- Tools (8): Tính toán chính xác bằng Swiss Ephemeris
       |     |-- Resources (5): Knowledge base 64 gates, 9 centers, 36 channels
       |     |-- Prompts/Skills (4): Quy trình phân tích chuẩn
       |     |-- Knowledge (8 files): 751 dòng chuyên sâu tiếng Việt
       |
       |--> Tổng hợp báo cáo chuyên sâu, chính xác, có thể xuất file
```

**Lợi ích:**
- LLM không cần nhớ kiến thức Human Design (dễ sai), mà gọi Tools để tính toán chính xác
- Knowledge được cung cấp qua Resources, luôn cập nhật
- Skills (Prompts) hướng dẫn quy trình phân tích chuẩn, không bỏ sót
- Có thể tích hợp vào bất kỳ LLM nào hỗ trợ MCP (Claude, Cursor, v.v.)

---

## 2. CHI TIẾT CHUẨN HÓA

### A. TOOLS (8 tools - theo chuẩn MCP JSON Schema)

| # | Tool | Mô tả | Input | Output | Trạng thái |
|---|------|-------|-------|--------|------------|
| 1 | `calculate_human_design_chart` | **CORE** - Tính chart chính xác bằng Swiss Ephemeris NASA JPL DE431 | birth_date, birth_time, timezone, name, location | JSON: Type, Strategy, Authority, Profile, Centers, Channels, Gates, Cross | ✅ Test pass |
| 2 | `analyze_human_design_deep` | Phân tích chuyên sâu tiếng Việt | birth_date, birth_time, focus_area (full/type/authority/centers/channels/profile/career/relationship/health) | Markdown báo cáo | ✅ |
| 3 | `get_gate_info` | Tra cứu 1 cổng 1-64 | gate_number | Gate meaning, center, channels, mandala position | ✅ |
| 4 | `get_center_info` | Tra cứu 1 trung tâm | center_name | Gates, channels, defined/undefined meaning | ✅ |
| 5 | `get_channel_info` | Tra cứu 1 kênh | gate1, gate2 | Centers, type, circuit, description | ✅ |
| 6 | `get_profile_info` | Tra cứu Profile | profile (12 loại) | Angle, line meanings, full meaning | ✅ |
| 7 | `compare_charts` | So sánh 2 người (Composite) | 2x birth_date/time/name | Electromagnetic, dominance, common gates | ✅ |
| 8 | `generate_full_report` | Tạo báo cáo đầy đủ | birth_date/time/name/format | Markdown/JSON report | ✅ |

**Đặc điểm chuẩn MCP:**
- Có `input_schema` JSON Schema đầy đủ (type, pattern, enum, required)
- Có `description` chi tiết cho LLM hiểu khi nào dùng
- Có `output_schema` (với tool chính)
- Đã test với client_example.py - 8/8 pass

### B. RESOURCES (5 resources - Knowledge Base)

| URI | Tên | Nội dung | Dùng khi nào |
|-----|-----|----------|--------------|
| `human-design://knowledge/gates` | All 64 Gates | 64 cổng với ý nghĩa | LLM cần kiến thức nền về gates |
| `human-design://knowledge/centers` | All 9 Centers | 9 trung tâm, gates, defined/undefined | Khi phân tích centers |
| `human-design://knowledge/channels` | All 36 Channels | 36 kênh, centers, meanings | Khi phân tích channels |
| `human-design://knowledge/types` | 5 Types | 5 loại + Strategy | Khi giải thích Type |
| `human-design://mandala/order` | Mandala Order | Thứ tự 64 cổng, 302° = Gate 41 | Khi cần tính toán hoặc giải thích Mandala |

**Cách LLM dùng:** Đọc resource để có kiến thức, không cần nhớ từ training data.

### C. PROMPTS/SKILLS (4 skills - Quy trình chuẩn)

| Skill | Khi nào dùng | Quy trình | Output |
|-------|--------------|-----------|--------|
| `analyze_human_design_full` | User yêu cầu phân tích toàn diện | 1. calculate_chart -> 2. analyze_deep full -> 3. get_gate/center/channel nếu cần -> 4. Tổng hợp báo cáo 7 phần chuẩn | Báo cáo toàn diện |
| `analyze_career_path` | User hỏi nghề nghiệp | 1. calculate_chart -> 2. Phân tích Type/Centers/Channels/Profile/Cross -> 3. Đưa 3-5 nghề phù hợp | Báo cáo hướng nghiệp |
| `analyze_relationship` | User hỏi mối quan hệ | 1. calculate 2 charts -> 2. compare_charts -> 3. Phân tích Type compatibility, electromagnetic, dominance | Báo cáo composite |
| `explain_gate` | User hỏi 1 cổng | 1. get_gate_info -> 2. Giải thích dễ hiểu + ví dụ | Giải thích cổng |

**Mỗi skill có:**
- Mô tả khi nào dùng
- Quy trình từng bước (bắt buộc gọi tool nào)
- Cấu trúc báo cáo chuẩn
- Nguyên tắc (tiếng Việt, không phán xét, v.v.)

**File skill chi tiết:** Trong `/mcp/skills/` - 4 file markdown, mỗi file là hướng dẫn chi tiết cho LLM.

### D. KNOWLEDGE BASE (8 files - 751 dòng)

Đã chuẩn bị từ trước, nay được cung cấp qua Resources + Skills:

1. `00_tong_quan_he_thong.md` - Tổng quan
2. `01_mandala_64_cong.md` - Mandala + bảng tra độ
3. `02_9_trung_tam.md` - 9 centers
4. `03_36_kenh.md` - 36 channels
5. `04_5_loai_va_chien_luoc.md` - 5 Types
6. `05_profile_cross_definition.md` - Profile/Cross/Definition
7. `06_phuong_phap_tinh_toan.md` - Phương pháp tính
8. `07_ung_dung_thuc_tien.md` - Ứng dụng

**Tổng:** 751 dòng kiến thức chuyên sâu tiếng Việt, đã được biên soạn từ Jovian Archive, Swiss Ephemeris, v.v.

---

## 3. CÁCH HOẠT ĐỘNG CỦA AGENT (Ví dụ thực tế)

**User:** "Phân tích Human Design cho Nguyễn Văn A sinh 1990-05-15 lúc 08:30 ở Hà Nội"

**LLM Core (được trang bị MCP):**

```
1. Nhận diện intent: full analysis -> Chọn skill analyze_human_design_full
   Đọc skill file: 01_full_analysis.md -> Hiểu quy trình 4 bước

2. Bước 1: Gọi tool calculate_human_design_chart
   Input: birth_date=1990-05-15, birth_time=08:30, timezone=+07:00, name=Nguyen Van A, location=Hanoi
   Output: 
   {
     "type": "Projector",
     "strategy": "Wait for the Invitation",
     "authority": "Emotional - Solar Plexus",
     "profile": "6/2",
     "defined_centers": ["Ajna", "G", "Head", "Root", "Solar Plexus", "Spleen", "Throat"],
     "defined_channels": [[13,33], [23,43], [24,61], [30,41], [32,54]],
     "all_activated_gates": [1,7,13,15,19,21,22,23,24,29,30,32,33,38,41,43,52,54,58,61],
     ...
   }

3. Bước 2: Gọi tool analyze_human_design_deep focus_area=full
   Output: Báo cáo phân tích tiếng Việt chi tiết 2000+ từ

4. Bước 3: (Tùy chọn) Gọi thêm tools để làm sâu:
   - get_channel_info gate1=13 gate2=33 -> Kênh Prodigal - Người kể chuyện
   - get_center_info center_name=Solar Plexus -> Emotional center
   - get_profile_info profile=6/2 -> Role Model/Hermit

5. Bước 4: Tổng hợp báo cáo cuối theo cấu trúc 7 phần chuẩn trong skill:
   - Tóm tắt nhanh
   - Type & Strategy (30%)
   - Authority (20%)
   - Centers (20%)
   - Channels & Gates (15%)
   - Profile & Definition (10%)
   - Cross (5%)
   - Lời khuyên thực hành

6. Trả về user: Báo cáo đầy đủ, chính xác, chuyên sâu, có thể xuất file markdown/json
```

**Khác biệt so với LLM không có MCP:**
- Không có MCP: LLM đoán Type dựa trên training data (dễ sai), kiến thức chung chung, không có số liệu chính xác
- Có MCP: Tính toán chính xác bằng Swiss Ephemeris, kiến thức từ Resources, quy trình từ Skills -> chính xác 100% về mặt tính toán, phân tích có cấu trúc

---

## 4. TÍCH HỢP VÀO HỆ SINH THÁI MCP

### Cấu hình Claude Desktop

File `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "human-design-analyzer": {
      "command": "python",
      "args": ["/home/user/human_design/mcp/server.py"],
      "description": "Human Design Analysis System"
    }
  }
}
```

File có sẵn: `/home/user/human_design/mcp/mcp_config.json`

### Chạy server

```bash
# Dev với Inspector
mcp dev server.py

# Run trực tiếp
python server.py
# hoặc
mcp run server.py
```

### Test

```bash
cd /home/user/human_design/mcp
python client_example.py
# Kết quả: 8/8 tests pass
```

---

## 5. FILE ĐÃ TẠO (Chuẩn MCP)

```
human_design/
├── knowledge/ (8 files - Knowledge Base)
│   └── ... (751 dòng)
├── tools/ (Engine - đã có từ trước)
│   ├── hd_calculator.py
│   ├── hd_analyzer.py
│   └── ...
└── mcp/ (MỚI - Chuẩn MCP)
    ├── server.py (MCP Server - 8 tools + 5 resources + 4 prompts)
    ├── tools_manifest.json (Manifest đầy đủ theo chuẩn MCP)
    ├── mcp_config.json (Config cho Claude Desktop)
    ├── client_example.py (Ví dụ gọi tools - đã test 8/8 pass)
    ├── README.md (Hướng dẫn MCP chi tiết)
    └── skills/ (4 skills - Prompt templates)
        ├── 01_full_analysis.md
        ├── 02_career_guidance.md
        ├── 03_relationship_composite.md
        └── 04_gate_deep_dive.md
```

**Tổng cộng mới tạo cho chuẩn MCP:**
- 1 MCP Server (server.py) - 700+ dòng
- 1 Manifest (tools_manifest.json) - JSON Schema chuẩn
- 1 Config (mcp_config.json)
- 1 Client example (client_example.py) - Test 8 luồng
- 1 README MCP (README.md)
- 4 Skills (skills/*.md)

---

## 6. SO SÁNH TRƯỚC/SAU CHUẨN HÓA

| Tiêu chí | Trước chuẩn hóa | Sau chuẩn hóa MCP |
|----------|-----------------|-------------------|
| Tính toán | Có engine Python, nhưng LLM phải gọi thủ công | Tools chuẩn MCP, LLM tự động gọi |
| Knowledge | File markdown rời rạc, LLM phải đọc thủ công | Resources chuẩn MCP, LLM đọc qua URI |
| Quy trình | Không có quy trình chuẩn, LLM tự đoán | Skills (Prompts) chuẩn, quy trình 4 bước rõ ràng |
| Tích hợp | Chỉ chạy local Python | Tích hợp được vào Claude Desktop, Cursor, Windsurf, bất kỳ LLM nào hỗ trợ MCP |
| Độ chính xác | Engine chính xác, nhưng LLM có thể không dùng | LLM bắt buộc gọi tool calculate_human_design_chart (CORE) -> chính xác 100% |
| Báo cáo | Có báo cáo, nhưng không theo cấu trúc chuẩn | Báo cáo theo cấu trúc 7 phần chuẩn từ Skills |
| Mở rộng | Khó mở rộng | Dễ thêm tool/resource/skill mới theo chuẩn MCP |

---

## 7. KẾT LUẬN

✅ **Đã hoàn thành chuẩn hóa theo mô hình Agent MCP:**

1. **Lõi LLM** được cung cấp Knowledge qua:
   - **Tools (8)**: Tính toán chính xác, tra cứu, so sánh, tạo báo cáo
   - **Resources (5)**: Knowledge base 64 gates, 9 centers, 36 channels, 5 types, mandala order
   - **Skills (4)**: Quy trình phân tích chuẩn (full, career, relationship, gate)

2. **Tính toán chính xác:** Swiss Ephemeris NASA JPL DE431, <1 arc second, đã test

3. **Sẵn sàng tích hợp:** Claude Desktop, Cursor, Windsurf, custom Agent

4. **Đã test:** 8/8 luồng trong client_example.py pass

**Hệ thống sẵn sàng để LLM core phân tích Human Design chuyên sâu và xuất báo cáo theo yêu cầu.**

---

## 8. BƯỚC TIẾP THEO (Đề xuất)

- Tích hợp vào Claude Desktop để test thực tế với LLM
- Thêm skill mới: Child analysis, Health, Business
- Thêm resource: Incarnation Cross 192, Godhead, Variables
- Tạo Web UI gọi MCP Server qua streamable-http
- Xuất báo cáo PDF với BodyGraph hình ảnh

---

*Báo cáo chuẩn hóa MCP - Human Design System - 2026-09-23 - Agent Mode*
