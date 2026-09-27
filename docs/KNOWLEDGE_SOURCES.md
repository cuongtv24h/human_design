# Sổ nguồn kho tri thức (Knowledge Sources Log)

Mọi nội dung crawl từ web trước khi vào `knowledge/*.md` đều phải ghi vào sổ này:
URL, ngày crawl, trích điểm chính, file đích. Tuyệt đối không copy nguyên văn —
chỉ tổng hợp và viết lại bằng tiếng Việt.

## Đợt 1 — 2026-09-28 (Profile/Lines + Nuôi dạy con)

| # | Nguồn | Ngày crawl | Điểm chính khai thác | File đích |
|---|-------|-----------|----------------------|-----------|
| 1 | Christie Inge — "Human Design Profile and Lines Deep Dive" (https://christieinge.com/human-design-profiles-and-lines/) | 2026-09-28 | Vai trò nghiệp 6 Dòng; hồ sơ cho biết cách chia sẻ quà tặng, cách nhận hỗ trợ trong quan hệ/sự nghiệp, cân bằng trí-cơ thể; tương ứng hào Kinh Dịch (âm/dương, 8 trigram) và độ chiêm tinh của Dòng (ví dụ Cổng 57 Thiên Bình 15°07'30"–20°45'00" chia 6 Dòng) | `21_profile_lines_chuyen_sau.md` |
| 2 | HumanCharts — "Human Design Profiles: The Complete Guide" (https://humancharts.com/human-design/profile/) | 2026-09-28 | Tóm tắt 6 Dòng (Dòng 1 cần nền tảng-an toàn; Dòng 2 tài năng vô thức); số ý thức/vô thức; chu kỳ gắn-bám/dứt của 1/3 | `21_profile_lines_chuyen_sau.md` |
| 3 | Katti — "Feel the Yes: Unlocking Generator Energy" (https://katti.me/2025/11/03/feel-the-yes-unlocking-generator-energy/) | 2026-09-28 | Sacral uh-huh/uh-uh; frustration là đèn đỏ; 7 lời khuyên Generator; 6 nguyên tắc nuôi con Generator (hỏi có/không, dạy nói không, không ép hoàn thành...) | `22_nuoi_day_con_theo_thiet_ke.md` |
| 4 | Katti — "Projectors Don't Chase — They Guide" (https://katti.me/2025/11/20/projectors-dont-chase-they-guide/) | 2026-09-28 | Chờ lời mời + công nhận; hào quang hội tụ; chu kỳ nghỉ; 5 nguyên tắc nuôi con Projector (công nhận cụ thể, không ép đua tranh...) | `22_nuoi_day_con_theo_thiet_ke.md` |
| 5 | Katti — "Mirror, Observe, Shine: Life as a Reflector" (https://katti.me/2025/12/04/mirror-observe-shine-life-as-a-reflector/) | 2026-09-28 | 1% dân số, không trung tâm xác định; chờ chu kỳ mặt trăng 28 ngày; môi trường quyết định; 6 nguyên tắc nuôi con Reflector | `22_nuoi_day_con_theo_thiet_ke.md` |
| 6 | Katti — "Own Your Energy: The Manifesting Generator's Journey" (https://katti.me/2025/10/01/own-your-energy-the-manifesting-generators-journey/) + "The Power of Manifestors" (https://katti.me/2025/09/10/the-power-of-manifestors-starting-leading-and-inspiring-change/) | 2026-09-28 | Chưa crawl full (ghi nhận để đợt sau); mục MG/Manifestor trong file 22 hiện tổng hợp từ cơ học chuẩn | `22_nuoi_day_con_theo_thiet_ke.md` (tạm) |

## Phân loại bổ sung

- File 21 thuộc nhóm **cơ học nền** (đi cùng 01, 04, 05): làm sâu Profile/Lines,
  không gắn domain báo cáo nào — trợ lý dùng qua `search_knowledge`.
- File 22 thuộc nhóm **ứng dụng**: nền tri thức cho chủ đề chuyên sâu mới
  **Nuôi dạy con (parenting)** — đã có skill `mcp/skills/13_parenting_child.md`,
  chưa có domain wired.

## Đề xuất chủ đề chuyên sâu mới (đợt tiếp theo)

1. **Nuôi dạy con (parenting)** — tri thức đã có (file 22 + skill 13). Việc còn
   lại: tạo `tools/hd_parenting_analysis.py` (`analyze_parenting`,
   `format_parenting_report`), thêm `DomainName.PARENTING`, `DomainSpec` trỏ
   `knowledge_refs=("22_nuoi_day_con_theo_thiet_ke.md",)`, UI chọn domain, test.
2. **Sự nghiệp & Kinh doanh (career)** — đã có skill `mcp/skills/11_career_business.md`.
   Cần crawl thêm nguồn chuyên sâu rồi lập file `23_career_business_deep.md`
   trước khi wire domain tương tự.
3. Các file domain mỏng cần làm sâu tiếp theo: 16_relationship (4KB),
   17_decision (3.7KB), 18_deconditioning (3.4KB), 19_purpose (3.3KB),
   20_team (3.3KB), 15_health (5KB).
