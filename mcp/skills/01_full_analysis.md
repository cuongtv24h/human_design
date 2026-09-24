# SKILL: Phân tích Human Design Toàn Diện

## Mô tả
Skill này hướng dẫn LLM thực hiện phân tích Human Design đầy đủ, chuyên sâu cho một cá nhân từ A-Z.

## Khi nào dùng
- Người dùng yêu cầu "phân tích Human Design", "xem bản đồ", "đọc chart", "phân tích toàn diện"
- Có đầy đủ ngày, giờ sinh

## Input yêu cầu
- birth_date: YYYY-MM-DD
- birth_time: HH:MM
- timezone: +07:00 (mặc định VN)
- name: Tên (tùy chọn)
- birth_location: Nơi sinh (tùy chọn)

## Quy trình chuẩn (BẮT BUỘC)

### Bước 1: Tính toán chính xác
```
Gọi tool: calculate_human_design_chart
Input: birth_date, birth_time, timezone, name, birth_location
Output: Chart JSON với Type, Authority, Profile, Centers, Channels, Gates
```

### Bước 2: Phân tích chuyên sâu
```
Gọi tool: analyze_human_design_deep
Input: birth_date, birth_time, timezone, name, focus_area="full"
Output: Báo cáo phân tích tiếng Việt chi tiết
```

### Bước 3: Mở rộng (nếu cần)
- Nếu chart có kênh quan trọng: gọi get_channel_info cho từng kênh định nghĩa
- Nếu có cổng Sun/Earth nổi bật: gọi get_gate_info
- Nếu cần giải thích trung tâm: gọi get_center_info

### Bước 4: Tổng hợp báo cáo cuối

Cấu trúc báo cáo CHUẨN:

```markdown
# BÁO CÁO HUMAN DESIGN - [Tên]

## TÓM TẮT NHANH (5 dòng)
- Type: ...
- Strategy: ...
- Authority: ...
- Profile: ...
- Cross: ...

## 1. TYPE & STRATEGY (30% báo cáo)
- Giải thích Type chi tiết
- Aura, năng lượng
- Strategy thực hành hàng ngày
- Not-Self và Chữ ký
- Ví dụ thực tế

## 2. AUTHORITY (20%)
- Cách ra quyết định đúng
- Sai lầm thường gặp
- Bài tập thực hành

## 3. 9 CENTERS (20%)
- Liệt kê Defined (có màu) vs Undefined (trắng)
- Mỗi trung tâm: ý nghĩa, Not-Self, trí tuệ
- Đặc biệt nhấn mạnh trung tâm mở

## 4. CHANNELS & GATES (15%)
- Kênh định nghĩa: tài năng cố định
- Cổng treo: bài học, nơi tìm kiếm người khác
- Đặc biệt Sun, Earth, Moon

## 5. PROFILE & DEFINITION (10%)
- Profile: vai trò cuộc đời
- Definition: cách kết nối năng lượng

## 6. INCARNATION CROSS (5%)
- Mục đích sống tổng quát
- 4 cổng Sun/Earth

## 7. LỜI KHUYÊN THỰC HÀNH
- 7 ngày: thử Strategy/Authority
- 7 tháng: quan sát Centers mở
- 7 năm: Deconditioning
- Hành động cụ thể ngay hôm nay
```

## Nguyên tắc
- Tiếng Việt, chuyên gia nhưng dễ hiểu
- Không phán xét, không có chart xấu
- Nhấn mạnh: Mind không phải Authority, thử nghiệm
- Kết thúc bằng hành động cụ thể
- Dùng dữ liệu từ tool, không bịa

## Ví dụ prompt gọi skill
"Phân tích toàn diện Human Design cho Nguyễn Văn A sinh 1990-05-15 lúc 08:30 ở Hà Nội"
-> LLM sẽ gọi skill này và thực hiện quy trình
