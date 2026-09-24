# Skill 20: Team & Leadership Dynamics - Hệ thống đúng người đúng việc (v3.0 MỚI)

> Nhu cầu thực tế #6 (Ý kiến 1): xây hệ thống đúng mắt xích, đúng chức năng.
> Tool: `analyze_team` + `generate_team_report` (hd_team_analysis.py) | Knowledge: `20_team_leadership_dynamics.md`
> Số 19 được giữ dành cho mở rộng (PHS/biến thể nâng cao).

## 1. Khi nào dùng
- Founder/sếp: tuyển ai, đặt ai vào ghế nào, sao team xung đột, quản lý từng người sao.
- Cá nhân: ghế nào hợp tôi, môi trường nào đúng, sao đi làm kiệt sức.
- Xây hệ thống: cơ cấu team theo năng lượng (không chỉ theo bằng cấp).

## 2. Framework chung
```
Type team role (Generator 37% xây / MG 33% xây nhanh / Projector 20% dẫn / Manifestor 9% mở đường / Reflector 1% soi)
+ Profile leadership (12 phong cách dẫn dắt)
+ Ideal environment (môi trường đúng theo Type + Centers)
+ Seat map 10 ghế (tài chính/sales/vận hành/quản lý/chiến lược/CSKH/sáng tạo/kỹ thuật/HR/khởi động <- centers/channels/gates cần tìm)
+ Manage by Type (quản từng Type khác nhau)
+ Collaboration (cách phối hợp với 4 Type còn lại)
= đúng người đúng việc
```

## 3. Quy tắc tư vấn (bắt buộc)
1. **HD là 1 lớp dữ liệu, không thay thế năng lực/kinh nghiệm** - dùng để ĐẶT ĐÚNG GHẾ, không để loại người.
2. Không dùng Type để phân biệt đối xử ("chỉ tuyển Generator") - mỗi Type đều cần trong hệ thống đủ.
3. Projector: trả theo GIÁ TRỊ không theo GIỜ - đây là điểm sếp Việt hay sai nhất.
4. Manifestor: giao mục tiêu, thả cách làm + bắt inform - soi chi tiết là mất người.
5. Generator/MG: HỎI để đáp ứng thay vì ra lệnh khô; Frustration = đặt sai việc.
6. Reflector: đừng ép quyết nhanh, đặt ở ghế quan sát/văn hóa - 1% nhưng là gương sức khỏe tổ chức.
7. Kết thúc: sơ đồ ghế đề xuất + 3 thay đổi quản lý áp dụng ngay.

## 4. Template báo cáo
```
# TEAM & HỆ THỐNG - [Tên/Tổ chức]
## 1. Vai trò của bạn trong hệ thống (Type role + seat hợp)
## 2. Phong cách lãnh đạo (Profile)
## 3. Môi trường làm việc lý tưởng
## 4. Bản đồ ghế ngồi - tuyển đúng người (10 ghế)
## 5. Quản lý từng Type + phối hợp
## 6. Sơ đồ đề xuất + 3 thay đổi ngay + Kết luận
```

## 5. Checklist (7 điểm)
- [ ] Đã định vị Type role + ghế hợp (không chung chung)?
- [ ] Có Profile leadership?
- [ ] Môi trường lý tưởng cụ thể (theo Type + Centers)?
- [ ] Seat map đủ ghế liên quan + dấu hiệu chart cần tìm?
- [ ] Quản lý từng Type khác nhau rõ ràng?
- [ ] Không phân biệt/loại trừ Type nào?
- [ ] Có sơ đồ + 3 thay đổi áp dụng ngay?

## 6. Ví dụ hội thoại
**VD1 - Sếp MG quản Projector:** "Bạn chạy nhanh, nhân viên Projector cần nhịp chậm + lời mời. Đừng dí deadline kiểu MG - hãy MỜI bạn ấy nhận vai điều phối, trả theo giá trị nhìn thấy, và công nhận công khai. Bạn ấy sẽ giúp bạn thấy cái bạn bỏ sót khi chạy nhanh."

**VD2 - Tuyển sales:** "Ghế sales cần: Throat định nghĩa (nói có trọng lượng) + kênh 26-44 (truyền bá) + năng lượng Sacral bền. Khi phỏng vấn ứng viên có chart: hỏi để Sacral họ đáp ứng thay vì ép trả lời ngay. Và nhớ: chart chỉ là 1 lớp, vẫn cần thử việc thực tế."

## 7. Ánh xạ tool
- `analyze_team(birth_date, birth_time, timezone, name)` -> dict
- `generate_team_report(...)` -> báo cáo markdown
- Kết hợp: 11_career (nghề cá nhân), 18_purpose (sứ mệnh tổ chức), 15_relationship (đối tác).
