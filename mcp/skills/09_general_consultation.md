# SKILL: Tham Vấn Tổng Quát Human Design - 100% Dân Số - 60 Biến Thể

> MỚI v2.1 - Tích hợp từ Wiki Phân mục 6 - Quy trình tham vấn 4 bước + Deep dive 5 Types x 12 Profiles = 60 biến thể

## Mô tả

**TOOL TỔNG QUÁT NHẤT** - Áp dụng cho **100% dân số**, khác hoàn toàn với tool Manifestor chỉ 9%.

- **5 Types**: Manifestor (9% - Khởi tạo), Generator (36% - Xây dựng), Manifesting Generator (32% - Đa nhiệm), Projector (22% - Hướng dẫn), Reflector (1% - Phản chiếu)
- **12 Profiles**: 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6, 4/1 (hiếm 2% - Juxtaposition), 5/1, 5/2, 6/2, 6/3
- **Tổng**: 60 biến thể duy nhất
- **Deep dive**: Mỗi Type có aura, psychology, strategy, signature, not-self, work, relationship, child chi tiết

Đây là skill mặc định khi user hỏi chung chung "Phân tích Human Design cho tôi" mà không chỉ định Type.

## Khi nào dùng

- Khi user hỏi chung chung: "Phân tích cho tôi", "Xem Human Design cho tôi"
- Khi user không biết mình Type gì: "Tôi không biết mình là gì"
- Khi cần báo cáo tổng quát áp dụng cho bất kỳ ai
- Khi cần quy trình tham vấn chuyên nghiệp cho coach/reader
- Khi user muốn hiểu toàn bộ hệ thống: "Giải thích 5 Types", "So sánh các Types"

**Phân biệt với skill Manifestor (07):**
- Skill 07 chỉ áp dụng khi chart = Manifestor (9%) - có check is_manifestor
- Skill 09 áp dụng cho TẤT CẢ - không cần check Type, luôn chạy được

## Quy trình

### Bước 1: Tính toán và gọi tool tổng quát

```
calculate_human_design_chart
  Input: birth_date, birth_time, timezone, name
  Output: chart cơ bản (Type, Profile, Authority...)

analyze_consultation_general (TOOL CHÍNH)
  Input: birth_date, birth_time, timezone, name, birth_location
  Output: 
  - type: Manifestor/Generator/MG/Projector/Reflector
  - profile: 1/3...6/3
  - authority: Emotional/Sacral/Splenic/Ego/Self-Projected/None/Mental/Lunar
  - type_deep_dive: {aura, psychology[], strategy{name,description,practice}, signature{name,description}, not_self{name,description,healing}, work{suitable[],needs[],team}, relationship{aura_impact,needs[],seeking}, child{description,wound,advice[]}}
  - profile_deep_dive: {role, angle (Right/Juxta/Left), description, career}
  - fear_gates: {count, summary}
  - love_gates: {count, summary}
  - consultation_process: 4 bước
  - buổi_đọc_chuyên_nghiệp: 1-2h, 7 phần
  - nguyên_tắc_đạo_đức: 8 điểm
  - lộ_trình_thực_hành: 7 ngày/7 tháng/7 năm
  - áp_dụng_cho: "100% dân số - 5x12=60 biến thể"
```

### Bước 2: Tra cứu bổ sung (tùy chọn)

```
get_center_info cho các defined centers
get_channel_info cho các defined channels nổi bật
analyze_fear_gates / analyze_love_gates nếu cần chi tiết hơn
get_incarnation_cross_details nếu cần chi tiết Cross
```

### Bước 3: Tổng hợp báo cáo tổng quát

Sử dụng format_consultation_report hoặc tự tổng hợp theo template dưới đây.

## Template báo cáo (60 biến thể)

```markdown
# BÁO CÁO THAM VẤN TỔNG QUÁT HUMAN DESIGN - [Tên] - [Type] [Profile]

**Áp dụng cho:** 100% dân số - 5 Types x 12 Profiles = 60 biến thể
**Tool:** analyze_consultation_general (tổng quát) vs analyze_manifestor_deep (chỉ Manifestor 9%)

## TÓM TẮT NHANH

- **Type:** [Type] ([% dân số] - [vai trò ngắn])
- **Strategy:** [Strategy name]
- **Authority:** [Authority]
- **Signature:** [Signature] - khi sống đúng
- **Not-Self:** [Not-Self] - khi sống sai
- **Profile:** [Profile] - [Role] - [Angle]
- **Cross:** [Incarnation Cross]
- **Definition:** [Definition]

## 1. TYPE DEEP DIVE - [Type]

### Aura

[Type_deep_dive.aura]

**Ví dụ:**
- Manifestor: Aura đóng và mang tính đẩy lùi, bộc phát đột ngột khiến người xung quanh e dè
- Generator: Aura mở, bao bọc, hút - thỏi nam châm thu hút cơ hội
- MG: Aura mở như Generator nhưng nhanh hơn, đa nhiệm, có khả năng bỏ qua bước
- Projector: Aura tập trung, xuyên thấu, hút vào người khác - Non-Energy Being
- Reflector: Aura lấy mẫu, phản chiếu, như tắc kè hoa - thay đổi theo môi trường, chu kỳ Mặt Trăng

### Tâm lý học

- [psychology item 1]
- [psychology item 2]
- ...

### Strategy - CHÌA KHÓA SỐNG ĐÚNG

**Tên:** [strategy.name]

**Mô tả:** [strategy.description]

**Thực hành:** [strategy.practice]

**Chi tiết theo Type:**

- **Manifestor:** Informing - Thông báo cho những người bị ảnh hưởng trước khi hành động. Không phải xin phép. Ví dụ: "Tôi sẽ đi ra ngoài 1 tiếng" thay vì đứng dậy đi luôn. Tại sao? Aura đóng khiến người khác không biết bạn sẽ làm gì -> sợ hãi -> phản kháng. Inform giúp họ an tâm -> giảm phản kháng -> bạn được tự do.

- **Generator:** Wait to Respond - Chờ để Đáp Ứng. Đừng khởi xướng. Chờ cuộc sống mang đến tín hiệu (câu hỏi, cơ hội, người), rồi để Sacral phản ứng. Sacral uh-huh (âm thanh mở, cao, ngực nở) = CÓ, uh-uh (đóng, thấp, co lại) = KHÔNG. Hỏi câu hỏi có/không thay vì mở.

- **MG:** Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo. Bước 1: Chờ tín hiệu, lắng nghe Sacral. Bước 2: Nếu uh-huh, thông báo rồi hành động. Cho phép bản thân thay đổi hướng, làm tắt, đa nhiệm.

- **Projector:** Wait for the Invitation - Chờ Lời Mời. Chờ sự công nhận và lời mời chính thức, đặc biệt cho 4 việc lớn: Tình yêu, Công việc, Nơi ở, Mối quan hệ quan trọng. Thành công đến khi được mời đúng.

- **Reflector:** Wait a Lunar Cycle - Chờ Chu Kỳ Mặt Trăng (28-29 ngày). Đừng quyết định vội, đặc biệt việc lớn. Nói chuyện với nhiều người, ở nhiều môi trường, cảm nhận sự nhất quán theo thời gian.

### Signature vs Not-Self

- **Signature [signature.name]:** [signature.description] - Dấu hiệu sống đúng
- **Not-Self [not_self.name]:** [not_self.description] - Dấu hiệu sống sai, tín hiệu để dừng
- **Chữa lành:** [not_self.healing]

**Bảng tóm tắt 5 Types:**

| Type | % | Strategy | Signature | Not-Self |
|------|---|----------|-----------|----------|
| Manifestor | 9% | Inform | Peace | Anger |
| Generator | 36% | Respond | Satisfaction | Frustration |
| MG | 32% | Respond+Inform | Satisfaction+Peace | Frustration+Anger |
| Projector | 22% | Invitation | Success | Bitterness |
| Reflector | 1% | Lunar Cycle | Surprise | Disappointment |

## 2. PROFILE DEEP DIVE - [Profile]

**Vai trò:** [profile_deep_dive.role]
**Góc độ:** [angle] - Right Angle (Personal Destiny), Juxtaposition (Fixed Fate - hiếm 2% - chỉ 4/1), Left Angle (Transpersonal Karma)
**Mô tả:** [description]
**Nghề nghiệp phù hợp:** [career]

**12 Profiles chi tiết:**

- **1/3 Investigator/Martyr (14.7%):** Nghiên cứu thử sai. Cần nền tảng vững chắc, học qua va chạm. An toàn từ kiến thức.
- **1/4 Investigator/Opportunist (2.4%):** Nghiên cứu cơ hội. Cần nền tảng để chia sẻ với mạng lưới bạn bè. Bạn bè là chìa khóa.
- **2/4 Hermit/Opportunist (14.1%):** Ẩn sĩ cơ hội. Tài năng tự nhiên, cần ở một mình để phát triển, rồi được gọi ra qua mạng lưới.
- **2/5 Hermit/Heretic (8.1%):** Ẩn sĩ dị giáo. Tài năng tự nhiên nhưng bị chiếu rọi kỳ vọng. Cần biên giới.
- **3/5 Martyr/Heretic (14.1%):** Tử vì đạo dị giáo. Cuộc đời thử sai, va chạm lớn, mang giải pháp thực tế để cứu người.
- **3/6 Martyr/Role Model (8.7%):** Tử vì đạo hình mẫu. 3 giai đoạn: 0-30 thử sai, 30-50 quan sát trên mái nhà, 50+ hình mẫu.
- **4/6 Opportunist/Role Model (8.7%):** Cơ hội hình mẫu. Ảnh hưởng qua mạng lưới, quan sát để trở thành hình mẫu.
- **4/1 Opportunist/Investigator (2% - hiếm - Juxtaposition):** Cơ hội điều tra. Định mệnh cố định, không thể bị ảnh hưởng, một con đường duy nhất. Cần nền tảng vững chắc.
- **5/1 Heretic/Investigator (14.3%):** Dị giáo điều tra. Giải pháp thực tế có nền tảng. Bị kỳ vọng lớn, chiếu rọi.
- **5/2 Heretic/Hermit (8.1%):** Dị giáo ẩn sĩ. Giải pháp thực tế + tài năng tự nhiên. Cần ở một mình.
- **6/2 Role Model/Hermit (14.4%):** Hình mẫu ẩn sĩ. 3 giai đoạn, tài năng tự nhiên, quan sát rồi hình mẫu sau 50.
- **6/3 Role Model/Martyr (8.9%):** Hình mẫu tử vì đạo. 3 giai đoạn, thử sai để trở thành hình mẫu.

## 3. CENTERS & CHANNELS & GATES

- **Defined Centers ([count]):** [list] - Năng lượng cố định, đáng tin cậy, nơi bạn ảnh hưởng người khác
- **Defined Channels ([count]):** [list] - Tài năng cố định, sứ mệnh cuộc đời
- **All Gates ([count]):** [list] - Cổng treo và cổng trong kênh
- **Fear Gates:** [count] - [summary] - 6 Splenic Fears (18,28,32,44,50,57), 6 Ajna Anxieties (4,11,17,24,43,47), 7 Solar Nervousness (6,22,30,36,37,49,55)
- **Love Gates:** [count] - [summary] - 4 Vessel of Love (10,15,25,46) + 7 Mundane Love (10,28,40,41,44,55,58)

## 4. CÔNG VIỆC - MỐI QUAN HỆ - TRẺ EM (Theo Type)

### Công việc

**Phù hợp:** [work.suitable]
**Cần:** [work.needs]
**Team:** [work.team]

**Chi tiết theo Type:**
- Generator: Làm việc mình YÊU -> Sacral cho năng lượng vô tận. Làm việc không yêu -> Frustration + kiệt sức Sacral. Cần được hỏi câu hỏi có/không.
- MG: Đa nhiệm, nhanh, cần hiệu quả, cho phép thay đổi hướng, làm tắt. Cần thông báo khi đổi hướng.
- Projector: Quản lý, hướng dẫn, cố vấn, coach, chuyên gia hệ thống. KHÔNG làm việc 8 tiếng như Generator. Cần nghỉ ngơi nhiều, ngủ một mình. Lương cao cho ít giờ.
- Reflector: Đánh giá cộng đồng, môi trường. Môi trường đúng là TẤT CẢ. Cần thời gian, không gian, thiên nhiên.
- Manifestor: Khởi nghiệp, lãnh đạo, khởi xướng. Tự chủ cao, làm việc theo đợt bộc phát.

### Mối quan hệ

**Aura tác động:** [relationship.aura_impact]
**Cần:** [relationship.needs]
**Tìm kiếm:** [relationship.seeking]

### Trẻ em [Type]

**Mô tả:** [child.description]
**Vết thương:** [child.wound]
**Lời khuyên phụ huynh:**
- [advice 1]
- [advice 2]
- ...

## 5. QUY TRÌNH THAM VẤN CHUYÊN NGHIỆP (Áp dụng cho TẤT CẢ Types/Profiles)

### Chuẩn bị

Thu thập: Họ tên, Giờ-Ngày-Tháng-Năm sinh (CÀNG CHÍNH XÁC CÀNG TỐT - sai 5 phút đổi Moon gate, sai 1 giờ đổi Profile), Nơi sinh (để xác định timezone)

### 4 Bước kỹ thuật

1. **Chuẩn bị thông tin đầu vào:** Thu thập chính xác
2. **Tính toán:** Sử dụng tool calculate_human_design_chart với Swiss Ephemeris NASA JPL DE431, <1 arc second. Tính cả Personality (lúc sinh) và Design (88° Sun trước sinh)
3. **Phân tích:** Theo thứ tự ưu tiên: Type + Strategy + Authority (80% giá trị) -> Centers (defined/open) -> Channels (tài năng cố định) -> Gates (cổng treo) -> Profile (vai trò) -> Cross (mục đích) -> Definition
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

## 6. NGUYÊN TẮC ĐẠO ĐỨC (8 điểm)

- Hiểu mình - Sống là mình
- Human Design là thử nghiệm (Experiment), không phải niềm tin mù quáng
- Khuyến khích khách hàng tự chứng thực Strategy và Authority trong đời sống thực tế
- Không dùng để phán xét, dán nhãn
- Không thay thế y tế, tâm lý chuyên nghiệp
- Tôn trọng Type: Đừng bảo Generator "hãy khởi xướng", đừng bảo Projector "hãy làm việc chăm chỉ hơn"
- Không có chart xấu - mỗi thiết kế có mục đích
- Tâm trí (Mind) KHÔNG BAO GIỜ là Authority - Mind để đo lường, không phải ra quyết định

## 7. LỘ TRÌNH THỰC HÀNH

- **7 ngày:** Thử nghiệm Strategy + Authority - Ví dụ: Generator thử chờ Respond với câu hỏi có/không, Projector thử chờ Invitation, Manifestor thử Inform
- **7 tháng:** Quan sát Centers mở - nơi bạn học trí tuệ, không phải ra quyết định. Open Centers là nơi bạn thông minh về người khác, nhưng không đáng tin để ra quyết định
- **7 năm:** Deconditioning - Giải điều kiện hóa, tế bào cơ thể thay mới hoàn toàn (chu kỳ Uranus). Mỗi năm giải phóng một lớp điều kiện hóa

## 8. SO SÁNH VỚI TOOL MANIFESTOR

| Tiêu chí | Tool Manifestor (07) | Tool Tổng Quát (09) |
|----------|----------------------|---------------------|
| Áp dụng | Chỉ Manifestor (9%) | TẤT CẢ (100%) |
| Biến thể | 9% x 12 Profiles = 12 | 5 Types x 12 Profiles = 60 |
| Aura | Chỉ Manifestor đóng đẩy | Đủ 5 Types |
| Strategy | Chỉ Informing | Đủ 5 Strategies |
| Signature/Not-Self | Peace/Anger | Đủ 5 cặp |
| Child | Chỉ Manifestor wound | Đủ 5 Types child |
| Khi dùng | "Tôi là Manifestor" | "Phân tích cho tôi" (mặc định) |

## 9. TỔNG KẾT - Hiểu Mình Sống Là Mình

Bạn là [Type] [Profile] - [Signature] khi sống đúng, [Not-Self] khi sống sai.

Hãy thử nghiệm 7 ngày với Strategy: [Strategy] và Authority: [Authority] và quan sát.

> "Đừng tin, hãy thử nghiệm" - Ra Uru Hu
> "Hiểu mình - Sống là mình"
> "Không có chart xấu - mỗi thiết kế có mục đích"

Mục tiêu tối thượng: Giải phóng bản thân khỏi việc "đuổi theo những điều không thuộc về mình". Sự độc đáo không phải rào cản mà là món quà quý giá.

Chỉ khi sống đúng với thiết kế gốc, con người mới có thể trải nghiệm sự nhẹ nhõm, bình an và đóng góp hiệu quả nhất vào sự tiến hóa chung của nhân loại.

**Tool này áp dụng cho:** 100% dân số - 5 Types x 12 Profiles = 60 biến thể
```

## Ví dụ hội thoại

### Ví dụ 1: Phân tích tổng quát mặc định

User: "Phân tích Human Design cho tôi, sinh 1990-05-15 08:30"
-> Gọi analyze_consultation_general birth_date=1990-05-15 birth_time=08:30 timezone=+07:00
-> Output: Generator 2/4, Sacral Authority, Strategy Respond, Signature Satisfaction
-> Tổng hợp theo template trên, tập trung vào Generator deep dive + 2/4 deep dive

### Ví dụ 2: So sánh tool Manifestor vs General

User: "Tôi là Manifestor, phân tích sâu cho tôi, khác gì tool tổng quát?"
-> Giải thích: Tool Manifestor chỉ 9% nhưng deep dive Manifestor sâu hơn (child wound chi tiết, motor to throat check). Tool tổng quát cũng có Manifestor deep dive nhưng còn có thêm 4 Types khác. Nếu bạn là Manifestor, cả 2 tools đều áp dụng, nhưng Manifestor tool chuyên sâu hơn cho Manifestor.
-> Gọi cả analyze_manifestor_deep và analyze_consultation_general để so sánh

### Ví dụ 3: Trẻ em

User: "Con tôi sinh 2015-03-10 14:30, làm sao nuôi dạy?"
-> Gọi analyze_consultation_general
-> Tập trung vào phần child của Type tương ứng (ví dụ Projector child cần công nhận + mời + nghỉ ngơi nhiều)
-> Đưa ra lời khuyên nuôi dạy cụ thể theo Type

### Ví dụ 4: Hướng nghiệp

User: "Tôi là Projector, công việc nào phù hợp?"
-> Gọi analyze_consultation_general
-> Lấy work.suitable, work.needs, work.team của Projector + career của Profile
-> Kết hợp: Ví dụ Projector 6/2: Quản lý/hướng dẫn + tài năng tự nhiên + hình mẫu sau 50

## Lưu ý kỹ thuật

- Tool tổng quát đã tích hợp sẵn Fear/Love gates nên không cần gọi thêm trừ khi user yêu cầu chi tiết
- Nếu cần chi tiết Fear: gọi analyze_fear_gates
- Nếu cần chi tiết Love: gọi analyze_love_gates
- Nếu cần chi tiết Cross: gọi get_incarnation_cross_details với p_sun, p_earth, d_sun, d_earth từ chart
- Luôn nhấn mạnh: Mind không phải Authority, Strategy/Authority là 80% giá trị, thử nghiệm 7 ngày

## Kết nối với các skills khác

- Skill 01_full_analysis: Dùng analyze_human_design_deep - phân tích cơ bản, không có deep dive Type chi tiết như skill 09
- Skill 02_career_guidance: Tập trung career, có thể dùng skill 09 để lấy work.suitable + career của Profile
- Skill 03_relationship: Dùng compare_charts + relationship của Type từ skill 09
- Skill 07_manifestor_consultation: Chuyên sâu Manifestor, là subset của skill 09 nhưng sâu hơn cho Manifestor
- Skill 09 là skill tổng quát nhất, nên là default khi không biết dùng skill nào

## Checklist cho Agent

- [ ] Đã gọi analyze_consultation_general với birth_date, birth_time, timezone?
- [ ] Đã xác định Type và Profile?
- [ ] Đã lấy type_deep_dive và profile_deep_dive?
- [ ] Đã giải thích Strategy + thực hành cụ thể cho Type đó?
- [ ] Đã giải thích Signature vs Not-Self và cách chữa lành?
- [ ] Đã đề cập công việc, mối quan hệ, trẻ em theo Type?
- [ ] Đã đưa quy trình tham vấn 4 bước + buổi đọc 1-2h nếu user là coach?
- [ ] Đã đưa nguyên tắc đạo đức + lộ trình 7 ngày/7 tháng/7 năm?
- [ ] Đã kết thúc bằng "Hãy thử nghiệm 7 ngày với Strategy/Authority và quan sát"?
- [ ] Đã nhấn mạnh "Không có chart xấu" và "Mind không phải Authority"?
