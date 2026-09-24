# TÀI LIỆU NGHIÊN CỨU CÁ NHÂN - Human Design v2.1

> Thư mục lưu trữ bộ tài liệu nghiên cứu cá nhân của bạn, được tổ chức gọn gàng và tích hợp vào hệ thống MCP v2.1 - 14 tools

## 📚 Danh mục tài liệu (7 files - 989 dòng) - Đã tích hợp 100% vào v2.1

| # | File | Dòng | Nội dung chính | Tích hợp vào |
|---|------|------|----------------|--------------|
| 0 | `Báo cáo Wiki Tổng quan Master` | 136 | Tổng quan toàn hệ thống, 5 Types, Authority, Definition, Circuits, 64 Gates, 192 Crosses, Fear, Love, Manifestor | Knowledge tổng quan + MCP Resources |
| 1 | `Wiki Phân mục 1_ Cấu trúc Nền tảng & Cơ học BodyGraph` | 160 | BodyGraph chi tiết, 5 Types deep dive, 9 Centers, Authorities, 12 Profiles, Definition, Circuitry, Cross ví dụ | Knowledge 00, 02, 04, 05 |
| 2 | `Wiki Phân mục 2_ Cơ học Vi cấp — 64 Cổng, 6 Dòng & 36 Kênh` | 69 | 64 Gates phân nhóm, 36 Channels, 6 Lines, 13 Planets, Conscious/Subconscious | Knowledge 01, 03 |
| 3 | `Wiki Phân mục 3_ Bản đồ Sứ mệnh — 192 Chữ Thập Hóa Thân` | 413 | **QUAN TRỌNG NHẤT** - Danh mục chi tiết 192 Incarnation Crosses với 4 cổng, vai trò, bài học | Knowledge mới 08 + Tool get_incarnation_cross_details |
| 4 | `Wiki Phân mục 4_ Tâm lý học Sợ hãi & Cơ chế Trí óc` | 49 | 6 Splenic Fears, 6 Ajna Anxieties, 7 Solar Plexus Nervousness, Not-Self Mind | Knowledge mới 09 + Tool analyze_fear_gates |
| 5 | `Wiki Phân mục 5_ Động lực Tình yêu & Cơ chế Kết nối` | 46 | 4 Vessel of Love, 7 Mundane Love Gates, Composite: Dominance/Compromise/Electromagnetic | Knowledge mới 10 + Tool analyze_love_gates |
| 6 | `Wiki Phân mục 6_ Chuyên luận Manifestor & Quy trình Tham vấn` | 116 | Deep dive Manifestor 9%, tâm lý, Aura, Strategy Inform, Signature Peace, Not-Self Anger, trẻ em Manifestor, quy trình tham vấn 4 bước | Knowledge mới 11, 12 + Skill Manifestor + General 60 biến thể + Tools general |

## 🔗 Tích hợp vào hệ thống v2.1

### Knowledge đã tích hợp (v2.1 - 13 files):

Đã tạo 5 file knowledge mới trong `/knowledge/` từ tài liệu cá nhân (v2.0 + v2.1):

- `08_192_incarnation_crosses_chi_tiet.md` - Từ Phân mục 3 (413 dòng -> trích lọc 192 crosses) - v2.0
- `09_tam_ly_so_hai_co_che_tri_oc.md` - Từ Phân mục 4 - v2.0
- `10_dong_luc_tinh_yeu_ket_noi.md` - Từ Phân mục 5 - v2.0
- `11_chuyen_luan_manifestor_tham_van.md` - Từ Phân mục 6 - v2.0
- `12_tham_van_tong_quat_60_bien_the.md` - **MỚI v2.1** - Từ Phân mục 6 mở rộng 5 Types x 12 Profiles = 60 biến thể - 100% dân số

Và cập nhật các file cũ với insights từ Phân mục 0,1,2.

### Tools bổ sung đã build (v2.1 - 14 tools):

**v2.0 - 4 advanced tools từ docs cá nhân:**
1. **analyze_fear_gates** - Phân tích 19 cổng sợ hãi/lo âu/hồi hộp trong chart - Từ Phân mục 4
2. **analyze_love_gates** - Phân tích 4 Vessel of Love + 7 Mundane Love - Từ Phân mục 5
3. **get_incarnation_cross_details** - Tra cứu chi tiết 192 Cross từ 4 cổng - Từ Phân mục 3
4. **analyze_manifestor_deep** - Phân tích chuyên sâu Manifestor 9% - Từ Phân mục 6 - Chỉ 12 biến thể

**v2.1 - 2 general tools - 100% dân số - 60 biến thể (MỚI):**
5. **analyze_consultation_general** - **TOOL TỔNG QUÁT NHẤT** - 5 Types x 12 Profiles = 60 biến thể - 100% dân số - Deep dive chi tiết cho từng Type (8 keys) + Profile (4 keys) + Fear/Love + quy trình 4 bước + buổi đọc 1-2h - Khác Manifestor chỉ 9%
6. **generate_consultation_report** - Báo cáo tham vấn tổng quát markdown đầy đủ - 60 biến thể

### Skills bổ sung (v2.1 - 9 skills):

**v2.0:**
1. **fear_psychology_analysis** - Skill phân tích tâm lý sợ hãi
2. **love_relationship_dynamics** - Skill phân tích động lực tình yêu
3. **manifestor_consultation** - Skill tham vấn Manifestor chuyên nghiệp - Chỉ 9%
4. **incarnation_cross_deep_dive** - Skill giải mã sứ mệnh 192 Cross

**v2.1 MỚI:**
5. **general_consultation** - **Skill tổng quát nhất** - 100% dân số - 60 biến thể - Default cho mọi phân tích - 19KB - Template 9 phần - 4 ví dụ - Checklist 10 điểm

## 📖 Cách sử dụng

### Đọc tài liệu gốc:
```bash
ls /home/user/human_design/docs/
cat "/home/user/human_design/docs/Wiki Phân mục 3_ Bản đồ Sứ mệnh — 192 Chữ Thập Hóa Thân.md"
```

### Knowledge tích hợp:
```bash
ls /home/user/human_design/knowledge/
# 08, 09, 10, 11 là từ docs cá nhân
```

### Tools mới:
```python
from mcp.server import analyze_fear_gates, analyze_love_gates, get_incarnation_cross_details
```

## 🎯 Giá trị của bộ tài liệu cá nhân

Bộ tài liệu của bạn bổ sung những gì hệ thống trước thiếu:

1. **192 Incarnation Crosses chi tiết** - Trước chỉ có công thức tính, nay có danh mục đầy đủ với vai trò, quẻ Kinh Dịch, bài học (413 dòng)
2. **Tâm lý học sợ hãi** - Phân loại 19 cổng sợ hãi theo 3 trung tâm nhận thức, cơ chế Not-Self Mind - rất quan trọng cho tham vấn
3. **Động lực tình yêu** - Vessel of Love + Mundane Love + Composite Dynamics (Dominance/Compromise/Electromagnetic) - chuyên sâu hơn tool compare_charts cũ
4. **Chuyên luận Manifestor** - Deep dive 9% dân số, tâm lý trẻ em Manifestor, quy trình tham vấn 4 bước chuyên nghiệp

Đây là tài liệu nghiên cứu cá nhân rất có giá trị, đã được chuẩn hóa vào hệ thống MCP.

---

*Docs cá nhân - Tích hợp 2026-09-23*
