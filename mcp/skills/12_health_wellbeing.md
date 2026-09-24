# Skill 12: Health & Wellbeing - Sức khỏe Thân-Tâm-Trí (v3.0 NÂNG CẤP)

> Nhu cầu thực tế #2 (Ý kiến 1): hiểu quy luật vận hành con người để cải thiện sức khỏe thân-tâm-trí.
> Tool: `analyze_health` + `generate_health_report` (hd_health_analysis.py) | Knowledge: `15_health_than_tam_tri.md`

## 1. Khi nào dùng skill này
- Người hỏi: mất ngủ, kiệt sức, burnout, đau đầu, tim mạch, stress, ăn uống, vận động, nghỉ ngơi.
- Người muốn hiểu: tại sao mình hay mệt, ngủ sao cho đúng, tập gì cho hợp, tín hiệu cơ thể.
- Ưu tiên sau Potential (14): Hiểu mình -> Chăm mình -> rồi mới Hiểu người.

## 2. Framework chung (áp dụng mọi phân tích sức khỏe)
```
Type Health (quy luật + rủi ro + ngủ + vận động + phục hồi)
+ Centers Defined (điểm mạnh sức khỏe + điểm mù) / Open (trí tuệ + vùng tổn thương)
+ Channels định nghĩa (ảnh hưởng sức khỏe)
+ Not-Self signals (tín hiệu lệch = tín hiệu bệnh sớm)
+ Sleep/Rest + Practice 7 ngày
= 60 biến thể (5 Types x 12 Profiles)
```

## 3. Quy tắc tư vấn (bắt buộc)
1. **Không chẩn đoán bệnh, không kê đơn** - HD là công cụ nhận thức, không thay thế y tế. Có triệu chứng nặng -> khuyên đi khám.
2. Luôn bắt đầu từ **Type health pattern** (quy luật lớn nhất), rồi mới đi vào trung tâm.
3. Trung tâm MỞ = vùng hấp thụ: đau/mệt "không phải của mình" - dạy phân biệt của mình/của người.
4. **Heart mở (65%)**: cảnh báo chứng minh quá sức -> tim mạch. Đây là điểm mù sức khỏe #1.
5. **Sacral**: Generator/MG kiệt sức vì việc sai; non-Sacral kiệt sức vì đua năng lượng.
6. Giấc ngủ là đơn thuốc đầu tiên: mỗi Type có cách ngủ khác nhau - đừng khuyên chung chung.
7. Kết thúc luôn có **thực hành 7 ngày** cụ thể, đo được.

## 4. Template báo cáo sức khỏe
```
# SỨC KHỎE THÂN-TÂM-TRÍ - [Tên] - [Type] [Profile]
## 1. Quy luật sức khỏe theo Type
- Quy luật: ...
- Rủi ro lớn nhất: ...
- Giấc ngủ đúng: ...
- Vận động đúng: ...
- Phục hồi khi lệch: ...
## 2. 9 trung tâm: mạnh/yếu sức khỏe
- Defined (n): mạnh... / điểm mù...
- Open (n): trí tuệ... / dễ tổn thương...
## 3. Kênh & sức khỏe
## 4. 7 tín hiệu cơ thể phải nghe
## 5. Thực hành 7 ngày
## 6. Kết luận + lưu ý y tế
```

## 5. Checklist tư vấn (8 điểm)
- [ ] Đã nêu Type pattern + rủi ro #1?
- [ ] Đã phân biệt Defined (điểm mù) vs Open (hấp thụ)?
- [ ] Đã cảnh báo Heart mở / Sacral (nếu liên quan)?
- [ ] Đã cho hướng dẫn NGỦ cụ thể theo Type?
- [ ] Đã cho hướng VẬN ĐỘNG cụ thể theo Type?
- [ ] Đã liệt kê tín hiệu cơ thể (body signals)?
- [ ] Đã có thực hành 7 ngày đo được?
- [ ] Đã disclaimer y tế (không thay thế bác sĩ)?

## 6. Ví dụ hội thoại
**VD1 - MG mất ngủ:** "Chị là MG 3/5, đầu chạy nhiều dự án nên khó tắt máy. Đơn: (1) xả Sacral mỗi ngày bằng vận động đổ mồ hôi, (2) trước ngủ 1h viết hết việc ra giấy cho đầu rỗng, (3) nằm xả trước khi ngủ. Nếu vẫn mất ngủ sau 7 ngày -> đi khám."

**VD2 - Projector kiệt sức:** "Bạn là Projector - không có Sacral nên không thể làm 8 tiếng như Generator. Kiệt sức của bạn không phải do yếu mà do sai nhịp. Đơn: nap trưa 20-30 phút bắt buộc, ngủ riêng để xả năng lượng mượn, đàm phán việc theo giá trị thay vì giờ công."

## 7. Ánh xạ tool
- `analyze_health(birth_date, birth_time, timezone, name)` -> dict đầy đủ
- `generate_health_report(...)` -> báo cáo markdown hoàn chỉnh
- Kết hợp: 14_potential (điểm mù) + 17_deconditioning (gốc rễ) khi bệnh mạn tính do lệch thiết kế.
