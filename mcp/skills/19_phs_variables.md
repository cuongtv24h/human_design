# Skill 19: PHS & Variables - 4 mũi tên thể chất/tâm trí (v1.0 MỚI)

> Tầng thực nghiệm sâu nhất: ăn uống, môi trường, động lực, góc nhìn.
> Tool: `analyze_variables` + `format_variables_report` (hd_variables.py, đã gắn trong chart) | Knowledge: `25_phs_variables_chuyen_sau.md`
> Khác skill 12 (sức khỏe theo Type/trung tâm): skill này đọc TIÊU HÓA + MÔI TRƯỜNG + ĐỘNG LỰC + GÓC NHÌN từ Color/Tone.

## 1. Khi nào dùng skill này
- "Tôi hợp ăn uống thế nào / môi trường nào đúng với tôi".
- Ăn mãi không khỏe, đổi chỗ ở/chỗ làm thì người khác hẳn.
- Muốn hiểu động lực sâu và góc nhìn mặc định của tâm trí.
- Thân chủ đã vững Type + Strategy + Authority, muốn tinh chỉnh tiếp.

## 2. Framework chung (đọc 4 mũi tên theo thứ tự cơ thể trước)
1. Đọc `chart["variables"]`: code `D..-P..`, 4 mũi tên L/R, Color/Tone từng vị trí.
2. Determination (trên-trái, Sun vô thức): loại tiêu hóa + biến thể L/R + tip thực hành.
3. Environment (dưới-trái, Nodes vô thức): loại không gian + biến thể + cách tìm chỗ đúng.
4. Motivation (trên-phải, Sun ý thức): động lực + dấu hiệu trượt Transference.
5. Perspective (dưới-phải, Nodes ý thức): góc nhìn + dấu hiệu trượt Distraction.
6. Cognition (Tone Sun vô thức): giác quan tin cậy để nạp thông tin.

## 3. Quy tắc tư vấn (bắt buộc)
- GIỜ SINH ƯỚC LƯỢNG = TỪ CHỐI luận Variables, nói rõ lý do (Tone đổi mỗi ~14 phút).
- Không chẩn đoán bệnh, không kê đơn ăn uống — chỉ đưa giả thuyết thử nghiệm.
- Mỗi lần gợi ý đúng 1 thay đổi nhỏ, theo dõi nhiều tuần.
- Transference/Distraction: dạy NHẬN RA, cấm dạy "sửa bằng cố gắng".
- Luôn nhắc: Strategy + Authority vẫn là công cụ quyết định thật.

## 4. Template báo cáo Variables
## 1. Bốn mũi tên (mã + hướng + nghĩa)
## 2. Tiêu hóa đúng (loại + biến thể + 1 thử nghiệm ăn uống)
## 3. Môi trường đúng (loại + biến thể + gợi ý chỗ ngồi/chỗ ở)
## 4. Động lực và dấu hiệu lệch
## 5. Góc nhìn, giác quan tin cậy và dấu hiệu lệch
## 6. Lộ trình thử nghiệm 4 tuần

## 5. Checklist tư vấn (6 điểm)
- [ ] Đã xác nhận giờ sinh chính xác đến phút?
- [ ] Đã đọc đủ 4 mũi tên + cognition từ chart?
- [ ] Chỉ gợi ý 1 thay đổi thể chất duy nhất?
- [ ] Có dạy nhận ra Transference/Distraction?
- [ ] Có nhắc Strategy + Authority là chính?
- [ ] Có hẹn theo dõi sau 2-4 tuần?

## 6. Ví dụ hội thoại
- Thân chủ: "Em ăn kiêng đủ kiểu mà người vẫn mệt, có phải em ăn sai cách không?"
- Trợ lý: "Cho anh giờ sinh chính xác đến phút nhé — mũi tên tiêu hóa đổi mỗi ~14 phút nên sai giờ là sai hết. Nếu đúng ... thì cơ thể em cần ...; mình thử 1 thay đổi duy nhất trong 2 tuần rồi đánh giá."

## 7. Ánh xạ tool
- `calculate_hd_chart` → `chart["variables"]` (có sẵn, không cần gọi thêm).
- `analyze_variables(chart)` khi cần tính lại từ chart dict.
- `format_variables_report(v)` ra tóm tắt tiếng Việt.
