# Skill 16: Decision & Authority - Ra quyết định đúng (v3.0 MỚI)

> Nhu cầu thực tế #7 (Ý kiến 2): lựa chọn hành vi phù hợp, quyết định đúng để cải thiện bản thân.
> Tool: `analyze_decision` + `generate_decision_report` (hd_decision_analysis.py) | Knowledge: `17_decision_authority.md`

## 1. Khi nào dùng
- Mọi câu hỏi "nên/không nên": đổi việc, đầu tư, yêu/cưới, mua nhà, chọn trường, hợp tác.
- Người phân vân kinh niên, hỏi ý kiến khắp nơi vẫn không quyết được.
- Người hay hối hận sau quyết định (dấu hiệu quyết sai Authority).

## 2. Framework chung
```
Authority (1 trong 7: Emotional/Sacral/Splenic/Heart/Self/Mental/Lunar)
+ How it works (cơ chế) + Process từng bước + Timing (bao lâu)
+ Questions (câu hỏi phải tự hỏi) + Traps (bẫy)
+ Strategy flow theo Type (luồng Strategy + Authority)
+ Mind traps (đầu óc không phải Authority)
+ Big vs Small (việc lớn đi đủ quy trình, việc nhỏ rút gọn)
= 60 biến thể (5 Types x 12 Profiles, Authority suy từ Centers)
```

## 3. Quy tắc tư vấn (bắt buộc)
1. **Không quyết thay người khác** - chỉ dẫn quy trình để Authority của họ lên tiếng. HD coach là người hỏi, không phải người phán.
2. Xác định đúng Authority từ chart (đừng đoán): Solar định nghĩa -> Emotional; Sacral định nghĩa + Solar mở -> Sacral; Spleen... theo thứ tự ưu tiên chuẩn.
3. Emotional (50% dân số): nhấn mạnh "không có sự thật trong khoảnh khắc" + thời gian chờ cụ thể.
4. Sacral: dạy phân biệt uh-huh/uh-uh + đặt câu hỏi đúng/sai cụ thể.
5. Splenic: dạy phân biệt trực giác (nhẹ, 1 lần) vs nỗi sợ (to, lặp lại).
6. Mental/Lunar: bảo vệ họ khỏi áp lực "quyết ngay" - cho quyền được chậm.
7. Kết thúc: viết lại quy trình quyết định CÁ NHÂN HÓA thành 3-5 bước cho đúng người này.

## 4. Template báo cáo
```
# RA QUYẾT ĐỊNH ĐÚNG - [Tên] - Authority: [X]
## 1. Authority của bạn hoạt động thế nào
## 2. Quy trình từng bước (áp ngay cho quyết định hiện tại)
## 3. Thời gian: chờ bao lâu
## 4. Câu hỏi phải tự hỏi
## 5. Bẫy cần tránh
## 6. Luồng Strategy + Authority của bạn
## 7. Bẫy đầu óc + Việc lớn vs việc nhỏ + Kết luận
```

## 5. Checklist (7 điểm)
- [ ] Authority xác định đúng từ chart?
- [ ] Quy trình đủ bước + áp được ngay?
- [ ] Thời gian chờ cụ thể (giờ/ngày/tuần)?
- [ ] Có câu hỏi tự vấn + bẫy?
- [ ] Có luồng Strategy + Authority kết hợp?
- [ ] Có vạch rõ Mind traps?
- [ ] Không quyết thay, chỉ dẫn đường?

## 6. Ví dụ hội thoại
**VD1 - Emotional phân vân đổi việc:** "Bạn là Emotional - đừng quyết hôm nay dù đang hứng hay đang chán. Quy trình: (1) ghi lại cảm giác hiện tại, (2) chờ 7 ngày, ngủ với nó, (3) mỗi ngày chấm điểm muốn/không 1-10, (4) hết tuần xem đường nào NHẤT QUÁN qua cả đỉnh và đáy. Đó là câu trả lời của bạn, không phải của tôi."

**VD2 - Sacral hỏi có nên hợp tác:** "Đừng hỏi 'anh thấy sao' - hỏi Sacral của bạn: 'Có muốn hợp tác với người này không - chỉ được uh-huh hoặc uh-uh?' (nghe âm đầu tiên). Uh-uh rồi mà đầu óc vẫn tiếc -> đó chính là bẫy Mind. Tin tiếng đầu tiên."

## 7. Ánh xạ tool
- `analyze_decision(birth_date, birth_time, timezone, name)` -> dict
- `generate_decision_report(...)` -> báo cáo markdown
- Kết hợp: mọi skill khác (quyết tiền -> 10, quyết yêu -> 15, quyết nghề -> 18/20).
