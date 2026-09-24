# Skill 18: Purpose & Mission Practical - Sứ mệnh ứng dụng (v3.0 MỚI)

> Nhu cầu thực tế #5 (Ý kiến 1): tìm mục đích sống, sứ mệnh, xây cuộc đời đúng hướng.
> Tool: `analyze_purpose` + `generate_purpose_report` (hd_purpose_analysis.py) | Knowledge: `19_purpose_mission_practical.md`
> Khác skill 08 (Incarnation Cross tra cứu): skill này ỨNG DỤNG - biến Cross thành nghề nghiệp và bước đi.

## 1. Khi nào dùng
- "Tôi sinh ra để làm gì / sứ mệnh của tôi là gì / nghề nào hợp tôi".
- Khủng hoảng tuổi (đặc biệt Saturn return ~28-30, Uranus opposition ~38-44, Chiron ~50).
- Chọn nghề, đổi nghề, khởi nghiệp theo sứ mệnh.

## 2. Framework chung
```
Incarnation Cross (bối cảnh sứ mệnh) + Angle (Right: tự trải nghiệm / Left: qua người khác / Juxta: đường hẹp)
+ Quarter (Initiation: tâm trí / Civilization: xây / Duality: gắn kết / Mutation: biến đổi)
+ 4 trụ: P.Sun = Life's Work 70% + P.Earth = grounding + D.Sun = evolution + D.Earth = nền vô thức
+ Profile role (vai trò trong vở kịch đời) + Type contribution (đóng góp)
+ Vocations từ kênh định nghĩa (gợi ý nghề cụ thể)
+ 5 bước sống đúng sứ mệnh (Strategy+Authority trước, sứ mệnh lộ sau)
= 60 biến thể x 192 Crosses
```

## 3. Quy tắc tư vấn (bắt buộc)
1. **Sứ mệnh không phải NGHỀ cụ thể** - là CÁCH bạn sống + đóng góp. Đừng phán "bạn phải làm bác sĩ".
2. Thứ tự vàng: Strategy + Authority TRƯỚC, sứ mệnh lộ SAU. Đi lệch mà hỏi sứ mệnh = hỏi đường khi đang chạy sai chiều.
3. Personality Sun (70%) là trọng tâm - đào sâu cổng này: ý nghĩa, center, line.
4. Left Angle: sứ mệnh gắn người khác - đừng tư vấn kiểu ẩn sĩ. Juxtaposition: đừng ép linh hoạt.
5. Khủng hoảng tuổi là CỬA sứ mệnh: Saturn return (28-30) trưởng thành, Uranus opp (38-44) lột xác giữa đời.
6. Vocations từ kênh là GỢI Ý khám phá, không phải chỉ định - kết hợp với thị trường và năng lực thực tế.
7. Kết thúc: 5 bước + 1 thử nghiệm 30 ngày liên quan sứ mệnh.

## 4. Template báo cáo
```
# SỨ MỆNH & MỤC ĐÍCH - [Tên] - Cross: [...]
## 1. Cross + Angle + Quarter (bối cảnh)
## 2. 4 trụ Mặt Trời/Trái Đất (trọng tâm: Life's Work 70%)
## 3. Vai trò Profile + Đóng góp Type
## 4. Hướng nghề từ kênh định nghĩa
## 5. 5 bước sống đúng sứ mệnh + thử nghiệm 30 ngày
## 6. Kết luận
```

## 5. Checklist (7 điểm)
- [ ] Đã diễn giải Cross + Angle + Quarter (không chỉ đọc tên)?
- [ ] Đã đào sâu P.Sun 70% (cổng + center + line)?
- [ ] Đã phân biệt Right/Left/Juxta trong lời khuyên?
- [ ] Có Profile role + Type contribution?
- [ ] Vocations cụ thể từ kênh (không chung chung)?
- [ ] Có 5 bước + thử nghiệm 30 ngày?
- [ ] Không chỉ định nghề tuyệt đối?

## 6. Ví dụ hội thoại
**VD1 - MG 3/5 hỏi sứ mệnh:** "Cross của chị là Right Angle 44/24|33/19 - hành trình cá nhân: tự trải nghiệm, chiêm nghiệm. Life's Work 70% là cổng 44 (nhận diện mẫu hình) - chị sinh ra để 'ngửi' thấy pattern mà người khác không thấy. Kết hợp MG đa dòng + 3/5 thử sai cứu người: sứ mệnh của chị là thử nhiều, sai nhiều, rồi biến thành hệ thống giúp người khác đỡ sai. Thử nghiệm 30 ngày: viết lại 3 thất bại lớn thành bài học chia sẻ."

**VD2 - Khủng hoảng 40 tuổi:** "38-44 là Uranus opposition - giữa đời lột xác, hỏi lại 'đây có phải đời mình không' là ĐÚNG chu kỳ, không phải hư hỏng. Đây là cửa để Left Angle của bạn chuyển từ sống cho mình sang sống cho người. Đừng quyết vội (Authority!), hãy thử nghiệm nhỏ 90 ngày."

## 7. Ánh xạ tool
- `analyze_purpose(birth_date, birth_time, timezone, name)` -> dict
- `generate_purpose_report(...)` -> báo cáo markdown
- Kết hợp: 11_career (nghề), 20_team (vai trò tổ chức), 16_decision (quyết đổi nghề).
