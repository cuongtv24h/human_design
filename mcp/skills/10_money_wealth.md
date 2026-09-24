# SKILL: Full Money Map - Dòng Tiền & Tài Chính Theo Human Design - 60 Biến Thể

> **v3.0 - Ưu tiên #1 theo yêu cầu user - Chuyên dụng Money/Wealth**
> Tích hợp từ knowledge: 03_36_kenh.md (21-45 Money, 26-44 Surrender, 40-37 Community, 32-54 Transformation) + 02_9_trung_tam.md (Heart/Ego - tiền bạc) + 04_5_loai_va_chien_luoc.md + 12_tham_van_tong_quat_60_bien_the.md

## Mô tả

**Skill chuyên sâu về TIỀN BẠC đầu tiên** - Phân tích dòng tiền, tài chính cá nhân, business model, pricing, investment theo Type/Profile/Heart/Channels/Gates/Authority.

- **5 Types Money Strategy:** Mỗi Type có cách thu hút tiền khác nhau (Manifestor khởi xướng + inform, Generator respond + Sacral uh-huh, MG đa dòng tiền + respond+inform, Projector invitation + premium pricing cao cho ít giờ, Reflector môi trường + lunar cycle 28 ngày)
- **12 Profiles Money Style:** Mỗi Profile có phong cách tiền khác nhau (1/3 cần nền tảng + thử sai, 4/1 hiếm 2% định mệnh cố định 1 đường tiền, 5/1 bị kỳ vọng lớn, 6/2 3 giai đoạn tỏa sáng sau 50, v.v.)
- **Heart/Ego Center:** Trung tâm tiền bạc quan trọng nhất - Defined 35% (có ý chí cố định, giữ lời hứa) vs Undefined 65% (không có ý chí cố định, trí tuệ về giá trị, bẫy chứng minh giá trị qua tiền)
- **Money Channels (6 kênh):** 21-45 Money (quản lý vật chất), 26-44 Surrender (bán hàng, thuyết phục), 40-37 Community (cộng đồng, thỏa thuận), 32-54 Transformation (tham vọng, chuyển hóa), 14-2 Beat (tài nguyên, hướng đi, power skills), 5-15 Rhythm (nhịp điệu, dòng tiền đều đặn)
- **Money Gates (14 cổng):** 21 Control, 45 Gatherer, 26 Egoist, 44 Alertness, 14 Power Skills, 2 Direction, 32 Continuity, 54 Ambition, 40 Aloneness, 37 Friendship, 5 Fixed Rhythm, 15 Extremes, 19 Wanting, 49 Revolution
- **Definition Money:** Single (solopreneur), Split (cần đối tác), Triple/Quadruple (cần team, nhiều dòng tiền)
- **Authority Money:** Ra quyết định tiền theo Authority
- **Pricing & Business Model & Investment:** Chiến lược định giá, mô hình kinh doanh, đầu tư theo Type

**Áp dụng cho:** 100% dân số - 60 biến thể - Full Money Map

## Khi nào dùng

- Khi user hỏi về tiền bạc: "Làm sao kiếm tiền theo Human Design?", "Dòng tiền của tôi?", "Tại sao tôi không giữ được tiền?", "Định giá thế nào?", "Mô hình kinh doanh phù hợp?", "Đầu tư thế nào?"
- Khi user là freelancer, coach, business owner, khởi nghiệp cần pricing, business model
- Khi user có vấn đề về tiền: Heart Open 65% bẫy chứng minh giá trị, Projector định giá thấp, Generator làm việc không yêu thích để kiếm tiền
- Khi user muốn hiểu Money Channels/Gates trong chart của mình
- Khi user hỏi: "Tôi có kênh 21-45, 26-44 nghĩa là gì về tiền?"

**Phân biệt với các skill khác:**
- Skill 02_career_guidance: Hướng nghiệp cơ bản, không chuyên sâu tiền
- Skill 09_general_consultation: Tổng quát 60 biến thể, có phần work nhưng không chuyên sâu money
- Skill 10_money_wealth: Chuyên sâu 100% về tiền - Full Money Map - pricing, business model, investment, Heart, Money Channels/Gates

## Quy trình

### Bước 1: Tính toán và gọi tool money

```
calculate_human_design_chart
  Input: birth_date, birth_time, timezone, name
  Output: chart cơ bản

analyze_money_map (TOOL CHÍNH v3.0)
  Input: birth_datetime, name
  Output:
  - type, profile, authority, definition, defined_centers
  - money_analysis:
    - type_money_strategy: {money_aura, how_to_attract[], pricing, business_model[], money_traps[], investment, saving_spending}
    - profile_money_style: {money_style, strength, challenge, strategy, career_money}
    - heart_center_money: {defined: true/false, analysis: {description, strength, challenge, money_advice, pricing, not_self}}
    - money_channels: {count, channels: [{channel, info: {name, centers, circuit, theme, description, business, not_self}}], summary}
    - money_gates: {count, gates: [{gate, info: {name, center, money_theme, business}}], summary}
    - definition_money: string
    - authority_money: string
  - full_money_map:
    - how_to_attract_money[]
    - pricing_strategy
    - business_models[]
    - money_traps[]
    - investment_style
    - saving_spending
    - heart_wisdom
    - profile_strategy
  - áp_dụng_cho: "100% dân số - Phân tích dòng tiền theo Type/Profile/Heart/Channels/Gates/Authority - Full Money Map"
```

### Bước 2: Tra cứu bổ sung (tùy chọn)

```
get_center_info center_name=Heart - Chi tiết Heart/Ego center
get_channel_info gate1=21 gate2=45 - Chi tiết kênh Money
get_channel_info gate1=26 gate2=44 - Chi tiết kênh Surrender (sales)
get_gate_info gate_number=14 - Gate Power Skills (tiền)
get_gate_info gate_number=21 - Gate Control
analyze_consultation_general - Để lấy thêm type_deep_dive, profile_deep_dive nếu cần
```

### Bước 3: Tổng hợp báo cáo Full Money Map

Sử dụng format_money_report hoặc template dưới đây.

## Template báo cáo Full Money Map (60 biến thể)

```markdown
# FULL MONEY MAP - BẢN ĐỒ DÒNG TIỀN HUMAN DESIGN - [Tên] - [Type] [Profile]

**Type:** [Type] | **Profile:** [Profile] | **Authority:** [Authority] | **Definition:** [Definition]
**Heart Defined:** [Có/Không (65%)] | **Money Channels:** [count] | **Money Gates:** [count]

## 1. TYPE MONEY STRATEGY - [Type] - Cách Thu Hút Tiền

### Aura tiền bạc

[money_aura]

**Chi tiết theo Type:**

- **Manifestor 9%:** Aura đóng, đẩy - Bạn không thu hút tiền bằng cách chờ đợi, mà bằng cách KHỞI XƯỚNG và THÔNG BÁO. Tiền đến khi bạn khởi xướng dự án mới và thông báo cho người khác. Làm việc theo đợt bộc phát - Có thể kiếm tiền lớn trong thời gian ngắn, rồi nghỉ ngơi.

- **Generator 36%:** Aura mở, hút - Bạn là thỏi nam châm thu hút tiền khi làm việc bạn YÊU. Tiền đến khi Sacral nói uh-huh với cơ hội. Làm việc bạn YÊU - Sacral sẽ cho năng lượng vô tận để kiếm tiền.

- **MG 32%:** Aura mở, nhanh, đa nhiệm - Bạn thu hút tiền bằng tốc độ, hiệu quả, đa dạng. Tiền đến từ nhiều nguồn, nhiều dòng. Được phép thay đổi hướng, làm nhiều việc cùng lúc, tìm con đường tắt hiệu quả nhất.

- **Projector 22%:** Aura tập trung, xuyên thấu - Bạn không có năng lượng bền bỉ để kiếm tiền như Generator. Bạn kiếm tiền bằng TRÍ TUỆ, HƯỚNG DẪN, không phải làm việc chăm chỉ. Tiền đến khi được CÔNG NHẬN và được MỜI. Xây dựng sự công nhận trước - Khi được công nhận đúng, lời mời tiền sẽ đến.

- **Reflector 1%:** Aura lấy mẫu, phản chiếu - Bạn phản chiếu môi trường tiền bạc xung quanh. Bạn là ai về tiền phụ thuộc vào bạn ở đâu và với ai. Tiền đến khi ở ĐÚNG MÔI TRƯỜNG với ĐÚNG NGƯỜI. Môi trường là TẤT CẢ cho tiền bạc.

### Cách thu hút tiền (How to Attract Money)

- [how_to_attract item 1]
- [how_to_attract item 2]
- ...

**Ví dụ Manifestor:**
- Khởi xướng dự án, ý tưởng mới về tiền - Bạn là người bắt đầu dòng tiền
- Thông báo trước khi hành động về tiền: "Tôi sẽ đầu tư vào X", "Tôi sẽ tăng giá lên Y"
- Đừng chờ đợi, đừng đáp ứng - Hãy khởi xướng
- Tiền đến từ việc tạo ra tác động, khởi xướng xu hướng mới
- Làm việc theo đợt bộc phát - Có thể kiếm tiền lớn trong thời gian ngắn, rồi nghỉ ngơi

**Ví dụ Generator:**
- Chờ để Đáp Ứng cơ hội tiền bạc - Đừng khởi xướng việc kiếm tiền
- Lắng nghe Sacral: uh-huh (mở, cao, ngực nở) = CÓ với cơ hội tiền, uh-uh (đóng, thấp) = KHÔNG
- Làm việc bạn YÊU - Sacral sẽ cho năng lượng vô tận để kiếm tiền
- Hỏi câu hỏi có/không về tiền: "Bạn có muốn đầu tư vào X không?" thay vì "Bạn muốn đầu tư gì?"
- Kiên nhẫn - Tiền đến từ việc làm đúng việc, không phải làm nhiều việc

**Ví dụ Projector:**
- Chờ Lời Mời cho cơ hội tiền lớn: công việc, dự án, tăng lương, hợp tác
- Tập trung vào học hệ thống, hiểu người khác, trở thành chuyên gia
- Đừng cố gắng kiếm tiền như Generator (làm việc chăm chỉ 8h) -> kiệt sức, cay đắng, mất tiền
- Xây dựng sự công nhận (recognition) trước - Khi được công nhận đúng, lời mời tiền sẽ đến
- Tiền đến từ việc hướng dẫn, quản lý năng lượng người khác, không phải làm việc

### Định giá (Pricing Strategy)

[pricing]

**Chi tiết theo Type:**

- **Manifestor:** Định giá cao, premium. Bạn mang năng lượng khởi xướng hiếm (9%), đừng bán rẻ. Giá phản ánh tác động bạn tạo ra, không phải giờ làm việc. Phù hợp: High-ticket, consulting, khởi nghiệp.

- **Generator:** Định giá theo giá trị bạn tạo ra khi làm việc bạn yêu. Khi bạn hài lòng (Satisfaction), bạn tạo ra giá trị lớn. Đừng định giá theo giờ, định giá theo kết quả. Phù hợp: Value-based pricing, làm việc bền bỉ với khách hàng yêu thích.

- **MG:** Định giá linh hoạt, đa tầng. Bạn có thể có nhiều mức giá, nhiều sản phẩm. Giá phản ánh tốc độ và hiệu quả bạn mang lại. Phù hợp: Nhiều dòng tiền, nhiều sản phẩm, upsell, cross-sell, làm nhanh nên có thể charge cao cho tốc độ.

- **Projector:** Định giá CAO cho ÍT GIỜ - Đây là chìa khóa. Bạn không bán thời gian, bạn bán TRÍ TUỆ, HƯỚNG DẪN. Lương cao cho ít giờ, không phải lương thấp cho nhiều giờ. Ví dụ: $500/giờ tư vấn thay vì $20/giờ làm việc. Premium pricing, high-ticket, retainer cho trí tuệ.

- **Reflector:** Định giá theo môi trường và chu kỳ. Giá có thể thay đổi theo môi trường, theo chu kỳ Mặt Trăng. Phù hợp mô hình linh hoạt, theo môi trường. Bạn phản chiếu giá trị môi trường, nên ở môi trường cao cấp, giá sẽ cao cấp.

### Mô hình kinh doanh phù hợp

[business_model]

**Chi tiết:**
- Manifestor: Khởi nghiệp, founder, consulting cao cấp high-ticket, sản phẩm đột phá tiên phong, tự chủ cao không thích bị quản lý
- Generator: Làm việc bền bỉ xây dựng lâu dài, nghề thủ công chuyên môn sâu, bất kỳ việc gì BẠN YÊU - Sacral cho năng lượng vô tận, phù hợp làm việc cho công ty hoặc freelancer với khách hàng yêu thích
- MG: Đa nhiệm nhiều dòng tiền cùng lúc, mô hình nhanh hiệu quả tìm đường tắt, khởi nghiệp đa dạng nhiều dự án, cho phép thay đổi hướng kinh doanh, phù hợp solopreneur đa năng hoặc agency nhanh
- Projector: Tư vấn, coach, cố vấn, chuyên gia hệ thống, quản lý hướng dẫn quản lý năng lượng nhân sự, không làm việc 8h cần nghỉ ngơi nhiều cần ngủ một mình để giải phóng năng lượng, phù hợp consulting coaching advisory quản lý dự án chuyên gia
- Reflector: Đánh giá cộng đồng môi trường trung gian, vai trò cần thấu cảm nhìn thấy tổng thể tài chính cộng đồng, linh hoạt không gò bó nhiều không gian, phù hợp community manager đánh giá trung gian phản chiếu consultant môi trường

### Bẫy tiền bạc (Money Traps - Not-Self)

[money_traps]

**Ví dụ:**
- Manifestor: Cố gắng làm việc như Generator 8h/ngày bền bỉ -> kiệt sức mất tiền, không thông báo về tiền -> gặp phản kháng mất cơ hội, giận dữ về tiền Not-Self Anger khi bị kiểm soát tài chính, bị kiểm soát tài chính bởi người khác -> mất tự do
- Generator: Làm việc không yêu thích để kiếm tiền -> Frustration + kiệt sức Sacral + mất tiền, khởi xướng cơ hội tiền thay vì đáp ứng -> sai thiết kế, quyết định tiền bằng đầu óc thay vì Sacral, làm việc quá sức như MG nhanh -> kiệt sức
- MG: Bị ép làm 1 việc kiếm tiền duy nhất -> Frustration, làm chậm lại làm theo từng bước -> mất lợi thế tốc độ, không thông báo khi đổi hướng kiếm tiền -> gặp kháng cự mất tiền, bỏ qua bước quan trọng vì làm nhanh -> mất tiền, Frustration + Anger về tiền
- Projector: Cố gắng làm việc chăm chỉ như Generator để kiếm tiền -> kiệt sức cay đắng burnout mất tiền, định giá thấp theo giờ -> không phản ánh giá trị trí tuệ, làm việc quá sức không nghỉ ngơi -> mất khả năng hướng dẫn, cố gắng hướng dẫn khi chưa được mời -> bị từ chối cay đắng, Bitterness về tiền khi không được công nhận không được mời
- Reflector: Ở môi trường không đúng về tiền -> phản chiếu tiêu cực thất vọng về tiền, quyết định tiền nhanh không chờ 28 ngày -> sai, ở với người không đúng về tiền -> ảnh hưởng tiêu cực, Disappointment về tiền khi môi trường sai, cố gắng có bản sắc tiền bạc cố định -> không phải thiết kế

### Đầu tư (Investment Style)

[investment]

**Chi tiết:**
- Manifestor: Đầu tư theo đợt bộc phát theo trực giác khởi xướng. Không phù hợp đầu tư đều đặn nhỏ giọt như Generator. Phù hợp đầu tư lớn vào ý tưởng đột phá bạn tin tưởng. Cần thông báo cho đối tác/gia đình trước khi đầu tư lớn.
- Generator: Đầu tư vào điều bạn YÊU và hiểu rõ. Sacral uh-huh với khoản đầu tư. Đầu tư bền bỉ dài hạn đều đặn. Phù hợp DCA (dollar-cost averaging) vào thứ bạn yêu. Đừng đầu tư theo trend nếu Sacral uh-uh.
- MG: Đầu tư đa dạng nhiều khoản nhỏ thử nghiệm nhanh. Cho phép thay đổi danh mục đầu tư. Phù hợp đầu tư linh hoạt thử nghiệm nhiều cơ hội. Thông báo cho đối tác khi đổi hướng đầu tư.
- Projector: Đầu tư theo lời mời và sự công nhận. Chờ lời mời đầu tư hoặc được công nhận là nhà đầu tư. Không đầu tư theo FOMO. Cần nghỉ ngơi suy nghĩ sâu trước khi đầu tư. Phù hợp đầu tư vào kiến thức hệ thống con người bạn hướng dẫn.
- Reflector: Chờ 28-29 ngày cho quyết định đầu tư lớn. Nói chuyện với nhiều người ở nhiều môi trường khác nhau. Cảm nhận điều gì nhất quán. Môi trường đúng là TẤT CẢ cho đầu tư. Đầu tư vào môi trường đúng.

### Tiết kiệm & Chi tiêu

[saving_spending]

## 2. HEART/EGO CENTER - Trung Tâm Tiền Bạc Quan Trọng Nhất

**Heart/Ego là trung tâm tiền bạc, vật chất, ý chí, lòng tự trọng, cam kết.**

### Heart Defined (35% dân số)

**Mô tả:** Bạn có ý chí cố định, có thể giữ lời hứa về tiền, động lực vật chất nhất quán.

**Điểm mạnh:** Có ý chí mạnh, có thể cam kết về tiền, giữ lời hứa tài chính, động lực vật chất bền bỉ. Phù hợp làm việc với tiền, cam kết tài chính.

**Thách thức:** Cần sử dụng ý chí đúng cách, không lạm dụng ý chí cho tiền, dễ vấn đề tim mạch, dạ dày nếu ép ý chí quá mức. Cần nghỉ ngơi.

**Lời khuyên tiền bạc:** Bạn có thể giữ lời hứa về tiền, nhưng đừng hứa bừa. Sử dụng ý chí cho điều bạn thực sự muốn. Định giá theo ý chí - Bạn có thể charge cao vì ý chí mạnh. Cần nghỉ ngơi để bảo vệ tim.

**Định giá theo Heart Defined:** Có thể định giá cao, giữ cam kết giá. Phù hợp mô hình retainer, cam kết dài hạn.

**Not-Self:** Ép ý chí để kiếm tiền, hứa hẹn quá mức về tiền, vấn đề tim mạch.

### Heart Undefined (65% dân số)

**Mô tả:** Bạn không có ý chí cố định, không nên hứa hẹn bừa bãi về tiền, không cố chứng minh giá trị qua tiền.

**Điểm mạnh:** Không có ý chí cố định - Đây là trí tuệ, không phải điểm yếu. Bạn khôn ngoan về giá trị, tiền bạc, cam kết. Bạn thấy ai có ý chí tốt, ai không. Bạn linh hoạt về giá trị.

**Thách thức:** Dễ cố gắng chứng minh giá trị qua tiền, hứa hẹn bừa bãi về tiền để chứng minh, làm việc quá sức để chứng minh giá trị. Dễ bị lợi dụng về tiền.

**Lời khuyên tiền bạc:** Đừng hứa hẹn bừa bãi về tiền. Đừng cố chứng minh giá trị qua tiền. Bạn không cần chứng minh. Học cách nói không với cam kết tiền bạc không phù hợp. Trí tuệ của bạn là khôn ngoan về giá trị - Bạn biết giá trị thực.

**Định giá theo Heart Undefined:** Đừng định giá thấp để chứng minh giá trị. Đừng hứa hẹn giảm giá để được yêu thích. Định giá theo giá trị thực, không phải để chứng minh. Phù hợp value-based pricing, không phải hourly để chứng minh.

**Not-Self:** Cố chứng minh giá trị qua tiền, hứa hẹn bừa bãi, làm việc quá sức để chứng minh, bị lợi dụng về tiền, vấn đề giá trị bản thân.

**Đây là bẫy tiền lớn nhất cho 65% dân số!**

## 3. PROFILE MONEY STYLE - [Profile] - Phong Cách Tiền Bạc

**12 Profiles phong cách tiền khác nhau:**

- **1/3 Investigator/Martyr (14.7%):** Cần nền tảng vững chắc về tiền trước khi hành động. Nghiên cứu sâu về tài chính, đầu tư. Học qua thử và sai về tiền - Va chạm tài chính là bài học. Sợ không đủ kiến thức về tiền -> trì hoãn đầu tư. Thử sai về tiền có thể mất tiền ban đầu. Chiến lược: Nghiên cứu kỹ trước khi đầu tư, nhưng cho phép thử sai nhỏ để học. Xây dựng nền tảng kiến thức tài chính vững chắc. An toàn tài chính đến từ kiến thức. Phù hợp nghiên cứu tài chính, phân tích đầu tư, chuyên gia tài chính có nền tảng vững chắc.

- **1/4 Investigator/Opportunist (2.4%):** Cần nền tảng vững chắc để chia sẻ với mạng lưới bạn bè. Tiền đến qua bạn bè, mạng lưới. Cần cân bằng giữa nghiên cứu và cơ hội qua bạn bè. Chiến lược: Xây dựng nền tảng tài chính vững chắc, rồi chia sẻ với mạng lưới bạn bè để tạo cơ hội tiền bạc. Bạn bè là chìa khóa cho tiền. Phù hợp chuyên gia tài chính + cộng đồng, ảnh hưởng qua bạn bè, network marketing có nền tảng.

- **2/4 Hermit/Opportunist (14.1%):** Tài năng tự nhiên về tiền, cần ở một mình để phát triển tài năng, rồi được gọi ra qua mạng lưới. Cân bằng ẩn dật và kết nối. Không biết mình có tài năng về tiền, cần người khác gọi ra. Có thể ngại kết nối mạng lưới. Chiến lược: Ở một mình để phát triển tài năng tự nhiên về tiền (ví dụ: kỹ năng đầu tư, kỹ năng bán hàng), rồi để mạng lưới bạn bè gọi ra và mang cơ hội tiền đến. Phù hợp nghệ sĩ, chuyên gia tài năng tự nhiên về tiền được gọi ra, freelancer tài năng.

- **2/5 Hermit/Heretic (8.1%):** Tài năng tự nhiên về tiền nhưng bị người khác chiếu rọi kỳ vọng lớn. Cần ở một mình, cẩn thận với kỳ vọng. Bị kỳ vọng lớn về tiền, dễ bị chiếu rọi là "người cứu tiền", "người mang giải pháp tài chính". Chiến lược: Ở một mình để phát triển tài năng, đặt biên giới rõ ràng với kỳ vọng về tiền của người khác. Đừng hứa hẹn cứu tài chính cho người khác nếu không có nền tảng. Phù hợp cố vấn tài chính tài năng tự nhiên nhưng cần biên giới với kỳ vọng.

- **3/5 Martyr/Heretic (14.1%):** Cuộc đời thử và sai về tiền, va chạm lớn, nhưng để cứu người, mang giải pháp thực tế về tiền. Học qua thất bại tài chính. Thử sai về tiền có thể mất nhiều tiền, va chạm tài chính lớn. Chiến lược: Cho phép thử sai về tiền, xem thất bại tài chính là bài học. Mang giải pháp thực tế về tiền cho người khác từ trải nghiệm của mình. Phù hợp thử nghiệm tài chính, giải pháp thực tế về tiền, cứu người qua trải nghiệm tài chính.

- **3/6 Martyr/Role Model (8.7%):** 3 giai đoạn: 0-30 thử sai về tiền, 30-50 quan sát trên mái nhà, 50+ làm hình mẫu về tiền. Giai đoạn đầu thử sai nhiều về tiền. Chiến lược: 0-30 cho phép thử sai về tiền để học. 30-50 quan sát, học hỏi về tiền. 50+ trở thành hình mẫu về tiền cho người khác. Phù hợp lãnh đạo tài chính qua trải nghiệm, hình mẫu về tiền sau 50 tuổi.

- **4/6 Opportunist/Role Model (8.7%):** Tiền đến qua mạng lưới bạn bè, cần quan sát để trở thành hình mẫu về tiền. Cần cân bằng giữa mạng lưới và quan sát. Chiến lược: Xây dựng mạng lưới bạn bè vững chắc cho cơ hội tiền bạc, quan sát để trở thành hình mẫu về tiền. Phù hợp lãnh đạo cộng đồng về tiền, hình mẫu tài chính qua mạng lưới.

- **4/1 Opportunist/Investigator (2% hiếm - Juxtaposition - Định mệnh cố định):** Profile hiếm, định mệnh cố định về tiền. Không thể bị ảnh hưởng về tiền, cần nền tảng vững chắc để ảnh hưởng người khác. Một con đường duy nhất về tiền. Định mệnh cố định, không linh hoạt về tiền. Có thể cảm thấy cô đơn về đường tiền. Chiến lược: Chấp nhận một con đường duy nhất về tiền, không cố gắng làm nhiều đường. Xây dựng nền tảng vững chắc về tiền để ảnh hưởng người khác. Không thể bị ảnh hưởng về tiền, nhưng ảnh hưởng người khác qua nền tảng vững chắc. Phù hợp chuyên gia một lĩnh vực tài chính cố định, không thể bị ảnh hưởng, ảnh hưởng người khác qua nền tảng vững chắc.

- **5/1 Heretic/Investigator (14.3%):** Người mang giải pháp thực tế về tiền có nền tảng. Bị kỳ vọng lớn, chiếu rọi về tiền. Bị kỳ vọng lớn về tiền, chiếu rọi là người cứu tài chính. Chiến lược: Xây dựng nền tảng vững chắc về tiền để đáp ứng kỳ vọng. Mang giải pháp thực tế về tiền cho người khác. Cẩn thận với kỳ vọng quá mức. Phù hợp lãnh đạo tài chính, cứu rỗi tài chính, giải pháp thực tế có nền tảng, chịu kỳ vọng lớn về tiền.

- **5/2 Heretic/Hermit (8.1%):** Giải pháp thực tế về tiền + tài năng tự nhiên. Cần ở một mình. Cần cân bằng giữa giải pháp thực tế và ở một mình. Chiến lược: Ở một mình để phát triển tài năng tự nhiên về tiền, mang giải pháp thực tế về tiền cho người khác khi được gọi ra. Phù hợp cố vấn tài chính giải pháp thực tế + tài năng tự nhiên.

- **6/2 Role Model/Hermit (14.4%):** 3 giai đoạn, tài năng tự nhiên về tiền, quan sát rồi trở thành hình mẫu. Cần ở một mình. 0-30 thử sai, 30-50 trên mái nhà quan sát, 50+ hình mẫu. Giai đoạn đầu thử sai về tiền, cần ở một mình. Chiến lược: 0-30 thử sai về tiền, 30-50 quan sát, 50+ trở thành hình mẫu về tiền. Tài năng tự nhiên về tiền cần được phát triển trong sự ẩn dật. Phù hợp hình mẫu về tiền, quan sát, tài năng tự nhiên, tỏa sáng về tiền sau 50.

- **6/3 Role Model/Martyr (8.9%):** 3 giai đoạn, thử sai về tiền để trở thành hình mẫu. Cuộc đời là hành trình quan sát và thử nghiệm về tiền. Thử sai về tiền để trở thành hình mẫu. Chiến lược: Cho phép thử sai về tiền để học, quan sát để trở thành hình mẫu. Cuộc đời là hành trình thử nghiệm tài chính. Phù hợp hình mẫu về tiền qua thử sai, quan sát và trải nghiệm.

## 4. MONEY CHANNELS - Kênh Tiền Bạc Định Nghĩa

**6 kênh tiền bạc quan trọng:**

- **21-45 Money - Dòng tiền Bộ lạc (Heart-Throat - Tribal/Ego):** Kênh tiền bạc quan trọng nhất. Gate 21 Control (kiểm soát) + Gate 45 Gatherer (tập hợp). Người có kênh này có khả năng tự nhiên quản lý dòng tiền, kiểm soát tài nguyên, lãnh đạo tài chính bộ lạc. Phù hợp làm CEO, quản lý tài chính, chủ doanh nghiệp. Phù hợp lãnh đạo, quản lý tiền, định hướng vật chất cho cộng đồng. Cần kiểm soát nhưng không kiểm soát quá mức. Not-Self: Kiểm soát tiền bạc quá mức hoặc không kiểm soát được, vấn đề với quyền lực vật chất.

- **26-44 Surrender - Bán hàng & Thuyết phục (Heart-Spleen - Tribal/Ego):** Kênh bán hàng. Gate 26 Egoist (bán hàng, thuyết phục) + Gate 44 Alertness (nhận diện pattern, quá khứ). Khả năng bán hàng tự nhiên, thuyết phục, kể chuyện. Cần học cách bán hàng trung thực, không thao túng. Phù hợp Sales, marketing, thuyết trình, đàm phán. Phù hợp bán hàng cao cấp, storytelling. Not-Self: Thao túng, bán hàng không trung thực, hoặc sợ bán hàng.

- **40-37 Community - Cộng đồng & Thỏa thuận (Heart-Solar Plexus - Tribal):** Kênh cộng đồng. Gate 40 Aloneness (cô đơn, làm việc) + Gate 37 Friendship (tình bạn, thỏa thuận). Năng lượng thỏa thuận, hợp đồng, cộng đồng. Cần cân bằng giữa làm việc và nghỉ ngơi, giữa cho và nhận trong cộng đồng. Phù hợp xây dựng cộng đồng, membership, thỏa thuận, hợp đồng, gia đình business. Not-Self: Làm việc quá sức cho cộng đồng, hoặc từ chối thỏa thuận.

- **32-54 Transformation - Tham vọng & Chuyển hóa (Spleen-Root - Tribal):** Kênh tham vọng. Gate 32 Continuity (liên tục, đánh giá) + Gate 54 Ambition (tham vọng, drive). Động lực mạnh mẽ để cải tiến, tham vọng, leo thang. Phù hợp kinh doanh, khởi nghiệp, transformation business. Phù hợp Khởi nghiệp, scale business, transformation, cải tiến liên tục. Cần quản lý tham vọng, không để tham vọng chi phối. Not-Self: Tham vọng không lành mạnh, hoặc sợ tham vọng, sợ thành công.

- **14-2 Beat - Tài nguyên & Hướng đi (Sacral-G - Individual):** Gate 14 Power Skills (kỹ năng quyền lực, tài nguyên) + Gate 2 Direction (hướng đi). Khả năng quản lý tài nguyên, kỹ năng tạo tiền. Gate 14 là một trong những cổng tiền quan trọng - kỹ năng biến tài nguyên thành tiền. Phù hợp Quản lý tài nguyên, đầu tư, kỹ năng tạo tiền, hướng đi cá nhân. Not-Self: Lãng phí tài nguyên, không có hướng đi.

- **5-15 Rhythm - Nhịp điệu & Tài chính đều đặn (Sacral-G - Collective/Logic):** Gate 5 Fixed Rhythm + Gate 15 Extremes. Nhịp điệu cố định, thói quen. Phù hợp dòng tiền đều đặn, thói quen tài chính, passive income. Phù hợp Xây dựng thói quen tài chính, dòng tiền đều đặn, passive income, routine business. Not-Self: Không có nhịp điệu, dòng tiền bấp bênh.

**Nếu không có kênh tiền nào định nghĩa:** Bạn linh hoạt về tiền bạc, học trí tuệ về tiền qua người khác. Bạn không có cách kiếm tiền cố định, mà cởi mở với nhiều cách. Đây là trí tuệ, không phải điểm yếu.

## 5. MONEY GATES - Cổng Tiền Bạc Kích Hoạt

**14 cổng tiền quan trọng:**

- **Gate 21 Control (Heart):** Kiểm soát tiền bạc, quản lý, lãnh đạo. Cần học kiểm soát lành mạnh, không kiểm soát quá mức. Business: Quản lý, kiểm soát tài chính, lãnh đạo.
- **Gate 45 Gatherer (Throat):** Tập hợp tài nguyên, phân phối cho bộ lạc. Khả năng tập hợp tiền, tài nguyên. Business: Tập hợp vốn, phân phối tài nguyên, lãnh đạo cộng đồng.
- **Gate 26 Egoist (Heart):** Thuyết phục, bán hàng, ego. Kỹ năng bán hàng tự nhiên. Business: Sales, marketing, thuyết phục.
- **Gate 44 Alertness (Spleen):** Nhận diện pattern, quá khứ, cơ hội. Khả năng nhận diện cơ hội tiền bạc. Business: Nhận diện xu hướng, cơ hội đầu tư, pattern thị trường.
- **Gate 14 Power Skills (Sacral):** Một trong những cổng tiền mạnh nhất. Kỹ năng biến tài nguyên thành tiền, quản lý tài nguyên. Business: Kỹ năng tạo tiền, quản lý tài nguyên, đầu tư.
- **Gate 2 Direction (G):** Hướng đi, la bàn. Biết hướng đi tài chính. Business: Định hướng chiến lược, tầm nhìn.
- **Gate 32 Continuity (Spleen):** Đánh giá, liên tục, cải tiến. Khả năng đánh giá dự án tài chính có bền vững không. Business: Đánh giá business, due diligence, continuity.
- **Gate 54 Ambition (Root):** Tham vọng, drive, leo thang. Động lực kiếm tiền, tham vọng vật chất. Business: Tham vọng kinh doanh, drive, scale.
- **Gate 40 Aloneness (Heart):** Làm việc, nghỉ ngơi, thỏa thuận. Cần cân bằng làm việc và nghỉ ngơi để có tiền bền vững. Business: Work-life balance, thỏa thuận làm việc.
- **Gate 37 Friendship (Solar Plexus):** Thỏa thuận, cộng đồng, gia đình. Tiền qua cộng đồng, thỏa thuận. Business: Community business, thỏa thuận, gia đình business.
- **Gate 5 Fixed Rhythm (Sacral):** Nhịp điệu, thói quen. Dòng tiền đều đặn qua thói quen. Business: Thói quen tài chính, passive income.
- **Gate 15 Extremes (G):** Cực đoan, nhịp điệu, tình yêu nhân loại. Cần nhịp điệu tài chính đa dạng. Business: Đa dạng dòng tiền.
- **Gate 19 Wanting (Root):** Nhu cầu, muốn, nhạy cảm. Nhu cầu vật chất, tiền bạc. Business: Hiểu nhu cầu thị trường.
- **Gate 49 Revolution (Solar Plexus):** Cách mạng, nguyên tắc, từ chối. Nguyên tắc về tiền bạc. Business: Nguyên tắc tài chính, cách mạng mô hình.

## 6. DEFINITION - Cách Bạn Kiếm Tiền Theo Cấu Trúc

- **Single Definition:** Bạn có thể làm việc một mình, tự chủ về tiền, không cần đối tác để kiếm tiền. Phù hợp solopreneur, freelancer.
- **Split Definition:** Bạn cần cầu nối (người, nơi, hoạt động) để kết nối các phần của mình. Tiền đến qua đối tác, cầu nối. Phù hợp partnership, cần đối tác kinh doanh.
- **Triple Split:** Bạn có 3 phần tách biệt, cần nhiều cầu nối. Tiền đến qua nhiều đối tác, nhiều lĩnh vực. Phù hợp nhiều dòng tiền, nhiều đối tác.
- **Quadruple Split:** Bạn có 4 phần tách biệt, cần nhiều cầu nối. Tiền đến qua team, nhiều người. Phù hợp team business, cần team để kiếm tiền.

## 7. AUTHORITY MONEY - Ra Quyết Định Tiền Bạc Theo Authority

- **Emotional - Solar Plexus:** Không có sự thật về tiền trong khoảnh khắc. Cần chờ sóng cảm xúc rõ ràng (vài giờ đến vài ngày) trước khi quyết định tiền lớn. Đừng quyết định tiền khi đang cao trào hoặc thấp trào cảm xúc.
- **Sacral:** Lắng nghe tiếng bụng uh-huh/uh-uh cho quyết định tiền. Uh-huh = CÓ với cơ hội tiền, uh-uh = KHÔNG. Đừng quyết định tiền bằng đầu óc.
- **Splenic:** Trực giác tức thì về tiền. Trực giác nói 1 lần, khẽ, trong khoảnh khắc. Tin tưởng trực giác tức thì về tiền, đừng chờ đợi.
- **Ego:** Ý chí - Hỏi: "Tôi có ý chí cam kết cho điều này không?" Tiền đến khi bạn có ý chí cam kết. Đừng cam kết tiền nếu không có ý chí.
- **Self-Projected:** G Center - Cần nói ra thành tiếng với người tin cậy để nghe sự thật về tiền. Sự thật tiền bạc đến qua giọng nói của bạn.
- **Mental:** Cần nói chuyện với nhiều người tin cậy ở nhiều môi trường khác nhau để có sự rõ ràng về tiền. Không quyết định tiền một mình.
- **Lunar:** Chu kỳ Mặt Trăng - Chờ 28-29 ngày cho quyết định tiền lớn. Nói chuyện với nhiều người ở nhiều môi trường trong 28 ngày.
- **None (Reflector):** Không có Authority cố định - Chờ chu kỳ Mặt Trăng 28-29 ngày, môi trường là tất cả cho tiền.

## 8. FULL MONEY MAP - Tổng Hợp Chiến Lược Dòng Tiền

### Cách thu hút tiền

[how_to_attract_money]

### Pricing Strategy

[pricing_strategy]

### Business Models

[business_models]

### Bẫy tiền (Money Traps)

[money_traps]

### Đầu tư (Investment Style)

[investment_style]

### Tiết kiệm & Chi tiêu

[saving_spending]

### Heart Wisdom

[heart_wisdom]

### Profile Strategy

[profile_strategy]

## 9. KẾT LUẬN - Hiểu Mình Để Giàu Có Đúng Cách

Bạn là [Type] [Profile] - Heart [Defined/Open] - [count] kênh tiền - [count] cổng tiền

Chiến lược tiền bạc của bạn là: [how_to_attract_money first item]

Hãy thử nghiệm 7 ngày với Strategy tiền bạc: [Type] + Authority: [Authority]

> "Tiền là năng lượng - Khi bạn sống đúng thiết kế, tiền sẽ chảy"
> "Đừng cố chứng minh giá trị qua tiền - Bạn đã có giá trị" (Đặc biệt cho Heart Open 65%)
> "Định giá cao cho ít giờ, không phải lương thấp cho nhiều giờ" (Đặc biệt cho Projector)
> "Tiền đến từ việc làm điều bạn yêu - Sacral uh-huh" (Đặc biệt cho Generator/MG)
> "Tiền đến khi bạn khởi xướng và thông báo" (Đặc biệt cho Manifestor)
> "Môi trường là tất cả cho tiền - Ở nơi đúng, với người đúng" (Đặc biệt cho Reflector)

**Mục tiêu:** Không phải kiếm nhiều tiền nhất, mà là kiếm tiền đúng cách, bền vững, hài lòng, bình yên, thành công, ngạc nhiên theo Signature của bạn.

**Lộ trình thực hành tiền bạc:**

- **7 ngày:** Thử nghiệm Strategy tiền bạc + Authority cho quyết định tiền nhỏ
- **7 tháng:** Quan sát Heart Open - Nơi bạn học trí tuệ về giá trị, không phải nơi để chứng minh giá trị qua tiền
- **7 năm:** Deconditioning về tiền - Giải phóng điều kiện hóa về tiền từ gia đình, xã hội

---

## Ví dụ hội thoại

### Ví dụ 1: Projector định giá thấp

User: "Tôi là Projector 6/2, tôi đang charge $20/giờ và kiệt sức, làm sao?"
-> Gọi analyze_money_map
-> Output: Projector 6/2 Heart Open (ví dụ) - Pricing: Định giá CAO cho ÍT GIỜ - Bạn không bán thời gian, bạn bán TRÍ TUỆ
-> Giải thích: Bạn là Projector, bạn không có năng lượng bền bỉ để làm việc 8h như Generator. Bạn kiếm tiền bằng trí tuệ, hướng dẫn. $20/giờ là định giá thấp, không phản ánh giá trị. Bạn cần $200-500/giờ tư vấn, hoặc retainer $2000/tháng cho trí tuệ, không phải $20/giờ làm việc. Heart Open 65% bẫy chứng minh giá trị qua tiền, định giá thấp để được yêu thích -> cần định giá theo giá trị thực.
-> Đưa ra bài tập: Thử nghiệm 7 ngày với pricing mới cao cho ít giờ, quan sát.

### Ví dụ 2: Generator làm việc không yêu thích để kiếm tiền

User: "Tôi là Generator 1/3, tôi làm công việc không yêu thích để kiếm tiền và thất vọng"
-> Gọi analyze_money_map
-> Output: Generator 1/3 Heart Open/Defined, Sacral Authority, Money Channels 0, Money Gates 3
-> Giải thích: Bạn là Generator, bạn là thỏi nam châm thu hút tiền khi làm việc bạn YÊU. Sacral uh-huh là la bàn. Làm việc không yêu thích -> Frustration + kiệt sức Sacral + mất tiền. Bạn cần chờ để đáp ứng cơ hội tiền bạc, lắng nghe Sacral uh-huh/uh-uh. 1/3 cần nền tảng vững chắc về tiền trước khi hành động, cho phép thử sai nhỏ để học. Đừng quyết định tiền bằng đầu óc, hãy lắng nghe Sacral.
-> Đưa ra bài tập: Hỏi câu hỏi có/không về tiền, lắng nghe Sacral.

### Ví dụ 3: Manifestor không thông báo về tiền

User: "Tôi là Manifestor 5/1, tôi đầu tư lớn mà không thông báo cho vợ/chồng và gặp phản kháng"
-> Gọi analyze_money_map
-> Output: Manifestor 5/1 Heart Defined, Money Channel 21-45, Authority Emotional
-> Giải thích: Bạn là Manifestor, Aura đóng, đẩy. Bạn cần thông báo trước khi hành động về tiền: "Tôi sẽ đầu tư vào X". Không phải xin phép, mà là cách loại bỏ phản kháng và giúp người khác an tâm. Aura đóng khiến người khác không biết bạn sẽ làm gì -> sợ hãi -> phản kháng. Inform giúp họ an tâm -> giảm phản kháng -> bạn được tự do. 5/1 bị kỳ vọng lớn về tiền, cần nền tảng vững chắc. Emotional Authority cần chờ sóng cảm xúc rõ ràng trước khi quyết định tiền lớn, đừng quyết định khi cao trào/thấp trào. Kênh 21-45 Money là kênh tiền quan trọng nhất, bạn có khả năng quản lý tiền tự nhiên.
-> Đưa ra bài tập: Trước khi đầu tư lớn, thông báo cho người bị ảnh hưởng, chờ sóng cảm xúc rõ ràng.

### Ví dụ 4: Heart Open bẫy chứng minh giá trị qua tiền

User: "Tôi có Heart Open, tôi luôn định giá thấp và hứa hẹn bừa bãi về tiền để được yêu thích"
-> Gọi analyze_money_map
-> Output: Heart Open 65% - Trí tuệ về giá trị, không phải điểm yếu
-> Giải thích: Bạn có Heart Open 65% dân số, bạn không có ý chí cố định, không nên hứa hẹn bừa bãi về tiền, không cố chứng minh giá trị qua tiền. Đây là trí tuệ, không phải điểm yếu. Bạn khôn ngoan về giá trị, tiền bạc, cam kết. Bạn thấy ai có ý chí tốt, ai không. Bẫy: Cố chứng minh giá trị qua tiền, hứa hẹn bừa bãi, làm việc quá sức để chứng minh, bị lợi dụng về tiền. Lời khuyên: Đừng hứa hẹn bừa bãi về tiền. Đừng cố chứng minh giá trị qua tiền. Bạn không cần chứng minh. Học cách nói không với cam kết tiền bạc không phù hợp. Định giá theo giá trị thực, không phải để chứng minh. Value-based pricing, không phải hourly để chứng minh.
-> Đưa ra bài tập: Quan sát khi nào bạn hứa hẹn bừa bãi về tiền để chứng minh, thực hành nói không.

## Lưu ý kỹ thuật

- Tool money đã tích hợp sẵn Type money strategy, Profile money style, Heart money, Money channels/gates, Definition, Authority money
- Nếu cần chi tiết Heart: gọi get_center_info center_name=Heart
- Nếu cần chi tiết Money Channel: gọi get_channel_info gate1=21 gate2=45, gate1=26 gate2=44, v.v.
- Nếu cần chi tiết Money Gate: gọi get_gate_info gate_number=14, 21, 45, v.v.
- Nếu cần tổng quát: gọi analyze_consultation_general để lấy type_deep_dive, profile_deep_dive
- Luôn nhấn mạnh: Heart Open 65% bẫy chứng minh giá trị qua tiền, Projector định giá cao cho ít giờ, Generator/MG Sacral uh-huh cho tiền, Manifestor inform về tiền, Reflector môi trường là tất cả cho tiền

## Kết nối với các skills khác

- Skill 02_career_guidance: Hướng nghiệp cơ bản, skill 10_money_wealth chuyên sâu tiền
- Skill 09_general_consultation: Tổng quát 60 biến thể, có phần work nhưng không chuyên sâu money như skill 10
- Skill 11_career_business_model (sắp tới): Business model, mở rộng từ money
- Skill 12_pricing_sales_mastery (sắp tới): Pricing & Sales, tách từ money
- Skill 10 là skill chuyên sâu đầu tiên về tiền, nên dùng khi user hỏi về tiền

## Checklist cho Agent

- [ ] Đã gọi analyze_money_map với birth_datetime, name?
- [ ] Đã xác định Type và Profile và Heart Defined?
- [ ] Đã lấy type_money_strategy (money_aura, how_to_attract, pricing, business_model, money_traps, investment, saving_spending)?
- [ ] Đã lấy profile_money_style (money_style, strength, challenge, strategy, career_money)?
- [ ] Đã lấy heart_center_money (defined true/false, analysis với pricing, not_self)?
- [ ] Đã lấy money_channels (count, channels với business, not_self)?
- [ ] Đã lấy money_gates (count, gates)?
- [ ] Đã lấy definition_money và authority_money?
- [ ] Đã giải thích pricing strategy theo Type + Heart?
- [ ] Đã giải thích business models phù hợp?
- [ ] Đã cảnh báo money traps (đặc biệt Heart Open 65% bẫy chứng minh giá trị)?
- [ ] Đã giải thích investment style theo Type?
- [ ] Đã đưa ra bài tập thực hành 7 ngày về tiền?
- [ ] Đã nhấn mạnh "Tiền là năng lượng - Khi sống đúng thiết kế, tiền sẽ chảy"?
