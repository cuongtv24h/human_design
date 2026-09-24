# Skill 17: Deconditioning & Not-Self - Giải điều kiện hóa (v3.0 MỚI)

> Nhu cầu thực tế #2 (Ý kiến 2): tìm điểm mù, lựa chọn hành vi phù hợp để cải thiện bản thân - đi sâu gốc rễ.
> Tool: `analyze_deconditioning` + `generate_deconditioning_report` (hd_deconditioning_analysis.py) | Knowledge: `18_deconditioning_notsel.md`
> Khác skill 14 (Potential - thấy điểm mù): skill này là LỘ TRÌNH CỞI BỎ điều kiện hóa (Not-Self -> Signature).

## 1. Khi nào dùng
- Người biết chart rồi, hỏi "giờ sửa sao / bắt đầu từ đâu / bao lâu thì đổi được".
- Mẫu hành vi lặp lại tiêu cực: hứa bừa, vội vã, chứng minh, bám víu, quyết vội, kiệt sức.
- Người muốn lộ trình dài hạn (7 ngày / 7 tháng / 7 năm).

## 2. Framework chung
```
Not-Self theme theo Type (Frustration/Anger/Bitterness/Disappointment) vs Signature
+ Type focus + mantra (trọng tâm + câu thần chú)
+ Từng trung tâm MỞ: conditioning (bị ép gì) + practice (bài tập) + mantra
+ Trung tâm ĐỊNH NGHĨA: warnings (đừng điều kiện hóa người khác)
+ Roadmap 7d (thử nghiệm Strategy+Authority) / 7m (đào sâu từng trung tâm) / 7y (lột xác tế bào)
= 60 biến thể
```

## 3. Quy tắc tư vấn (bắt buộc)
1. Deconditioning KHÔNG phải "sửa mình cho tốt" - mà là CỞI BỎ cái không phải mình. Nhấn mạnh khác biệt này.
2. Không ép lột xác nhanh: 7 năm là sinh học (thay tế bào), ai hứa 7 ngày là lừa đảo.
3. Mỗi trung tâm mở: 1 mantra + 1 bài tập nhỏ làm được NGAY HÔM NAY.
4. Trung tâm định nghĩa: dạy TRÁCH NHIỆM - năng lượng mạnh của bạn đang vô tình ép người khác.
5. Nhật ký Not-Self là công cụ #1: mỗi tối ghi "hôm nay đèn đỏ lúc nào, vì sao".
6. Kết hợp cơ thể: điều kiện hóa nằm trong THÂN - bài tập phải có yếu tố thân (thở, dừng, ngủ, vận động).
7. Kết thúc: lộ trình cá nhân hóa 7d/7m/7y với mốc kiểm tra.

## 4. Template báo cáo
```
# GIẢI ĐIỀU KIỆN HÓA - [Tên] - [Type]
## 1. Not-Self vs Chữ ký + trọng tâm + mantra
## 2. Giải điều kiện từng trung tâm mở (conditioning/practice/mantra)
## 3. Cảnh báo từ trung tâm định nghĩa
## 4. Lộ trình 7 ngày / 7 tháng / 7 năm cá nhân hóa
## 5. Kết luận
```

## 5. Checklist (7 điểm)
- [ ] Đã phân biệt Not-Self vs Signature rõ ràng?
- [ ] Mỗi trung tâm mở có đủ 3 phần (ép gì/bài tập/mantra)?
- [ ] Có cảnh báo chiều ngược (định nghĩa ép người khác)?
- [ ] Lộ trình đủ 3 mốc + mốc kiểm tra?
- [ ] Bài tập có yếu tố THÂN, làm được ngay?
- [ ] Có nhật ký Not-Self?
- [ ] Không hứa hẹn lột xác nhanh?

## 6. Ví dụ hội thoại
**VD1 - Heart mở hứa bừa:** "Mỗi lần bạn hứa để được yêu, đó là Heart mở bị điều kiện hóa. Bài tập từ hôm nay: mọi cam kết chờ 24h + hỏi 'mình muốn hay mình đang chứng minh?' Mantra dán điện thoại: 'Tôi đã có giá trị - không cần chứng minh.' Ghi nhật ký mỗi lần cưỡng lại được 1 lời hứa bừa."

**VD2 - Root mở vội vã:** "Bạn không chậm - bạn chỉ đang chạy bằng áp lực của người khác. Bài tập: mỗi lần thấy vội, dừng - hít sâu 3 lần - hỏi 'có thật sự gấp không?' 90% câu trả lời là không. Sau 7 ngày đếm xem bạn 'thắng vội' được mấy lần."

## 7. Ánh xạ tool
- `analyze_deconditioning(birth_date, birth_time, timezone, name)` -> dict
- `generate_deconditioning_report(...)` -> báo cáo markdown
- Kết hợp: 14_potential (thấy) -> 17_deconditioning (cởi) -> 16_decision (sống) -> 12_health (thân).
