# Catalog tài liệu Human Design v3.0

> Tài liệu vận hành chuẩn cập nhật 2026-09-24. Đây là catalog cho `knowledge/`, Wiki nguồn trong `docs/` và skill markdown trong `mcp/skills/`.

## 1. Nguồn sự thật và phạm vi

| Khu vực | Số lượng | Vai trò |
|---|---:|---|
| `knowledge/` | 21 file (`00`–`20`) | Nội dung chuẩn để engine/MCP tham chiếu |
| Wiki cá nhân trong `docs/` | 7 file, 989 dòng | Tài liệu nguồn đã tích hợp vào knowledge và tools |
| `mcp/skills/` | 25 file Markdown (`01`–`18`, `20`–`26`) | Hướng dẫn phân tích cho LLM/client; không phải MCP prompt runtime |
| `mcp/server.py` | 36 tools, 22 resources | MCP entrypoint hiện tại |
| `mcp/openapi_server.py` | 38 route decorator | REST/OpenAPI bridge |

Không dùng các con số trong README hoặc report v2.x để mô tả runtime hiện tại. Số liệu runtime được kiểm tra từ source và phản ánh trong `mcp/tools_manifest_latest.json`.

## 2. Knowledge chuẩn (`knowledge/`)

| # | File | Phạm vi |
|---:|---|---|
| 00 | `00_tong_quan_he_thong.md` | Tổng quan hệ thống, BodyGraph và hai lần tính toán |
| 01 | `01_mandala_64_cong.md` | Mandala và 64 Gates |
| 02 | `02_9_trung_tam.md` | 9 Centers, defined/undefined và Not-Self |
| 03 | `03_36_kenh.md` | 36 Channels và ba mạch |
| 04 | `04_5_loai_va_chien_luoc.md` | 5 Types, Strategy, Signature và Authority |
| 05 | `05_profile_cross_definition.md` | 12 Profiles, Cross và Definition |
| 06 | `06_phuong_phap_tinh_toan.md` | Swiss Ephemeris và quy trình tính kỹ thuật |
| 07 | `07_ung_dung_thuc_tien.md` | Ứng dụng thực hành |
| 08 | `08_192_incarnation_crosses_chi_tiet.md` | Incarnation Crosses và bản đồ sứ mệnh |
| 09 | `09_tam_ly_so_hai_co_che_tri_oc.md` | Fear Gates, lo âu và cơ chế trí óc |
| 10 | `10_dong_luc_tinh_yeu_ket_noi.md` | Vessel/Mundane Love và động lực kết nối |
| 11 | `11_chuyen_luan_manifestor_tham_van.md` | Manifestor và quy trình tham vấn |
| 12 | `12_tham_van_tong_quat_60_bien_the.md` | 5 Types × 12 Profiles = 60 biến thể |
| 13 | `13_money_wealth_full_map.md` | Money Map, pricing, business và investment |
| 14 | `14_potential_blindspots.md` | Tiềm năng, điểm mù và 11 góc nhìn |
| 15 | `15_health_than_tam_tri.md` | Health: thân–tâm–trí |
| 16 | `16_relationship_intimacy_deep.md` | Relationship, intimacy và composite |
| 17 | `17_decision_authority.md` | Decision và 7 Authorities |
| 18 | `18_deconditioning_notsel.md` | Deconditioning, Not-Self và lộ trình 7 ngày/7 tháng/7 năm |
| 19 | `19_purpose_mission_practical.md` | Purpose, Mission, Quarters và nghề nghiệp |
| 20 | `20_team_leadership_dynamics.md` | Team, leadership và đúng người đúng việc |

## 3. Wiki nguồn cá nhân (`docs/`)

Bảy Wiki dưới đây là nguồn nghiên cứu đã được tích hợp, không phải API contract:

1. `Báo cáo Wiki Tổng quan Master - Kho Tri thức Human Design.md`
2. `Wiki Phân mục 1_ Cấu trúc Nền tảng & Cơ học BodyGraph.md`
3. `Wiki Phân mục 2_ Cơ học Vi cấp — 64 Cổng, 6 Dòng & 36 Kênh.md`
4. `Wiki Phân mục 3_ Bản đồ Sứ mệnh — 192 Chữ Thập Hóa Thân.md`
5. `Wiki Phân mục 4_ Tâm lý học Sợ hãi & Cơ chế Trí óc.md`
6. `Wiki Phân mục 5_ Động lực Tình yêu & Cơ chế Kết nối.md`
7. `Wiki Phân mục 6_ Chuyên luận Manifestor & Quy trình Tham vấn.md`

Các Wiki này có tổng 989 dòng và được giữ lại để truy nguyên nguồn. Nội dung triển khai hiện tại nằm trong 21 file knowledge, các analyzer ở `tools/` và các wrapper ở `mcp/`.

## 4. Skill markdown

`mcp/skills/` có 25 skill: `01`–`18` và `20`–`26`; số `19` được để trống theo lịch sử phiên bản. Đây là tài liệu hướng dẫn, không phải 25 MCP prompt đã đăng ký. `server.py` hiện không có decorator `@mcp.prompt()`; vì vậy manifest chuẩn ghi **0 MCP prompts**.

Sáu skill foundation mới (`21`–`26`) bổ sung Centers, Channels, Type/Strategy/Authority, Profile/Definition, phương pháp tính và ứng dụng thực tiễn. Nhóm skill còn lại bao phủ phân tích toàn diện, nghề nghiệp, quan hệ, Gate, fear, love, Manifestor, Cross, consultation general, money, career/business, health, parenting, potential, relationship deep, decision, deconditioning, purpose và team.

## 5. Quy tắc cập nhật

- Khi thêm knowledge mới, cập nhật bảng ở đây và trường `knowledge_base.files` trong manifest.
- Khi thêm tool/resource, kiểm tra decorator thực tế trong `mcp/server.py` rồi cập nhật `mcp/tools_manifest_latest.json`.
- Không gọi skill Markdown là MCP prompt nếu chưa có `@mcp.prompt()`.
- Không sửa số liệu runtime trong tài liệu lịch sử; nếu cần mô tả trạng thái mới, cập nhật các tài liệu canonical: root `README.md`, file này và `mcp/README.md`.
- Khi nội dung đề cập đến sức khỏe, tiền bạc hoặc quan hệ, luôn giữ cảnh báo đây là công cụ tự quan sát, không thay thế tư vấn chuyên môn.
