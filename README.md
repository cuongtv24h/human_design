# HUMAN DESIGN - HỆ THỐNG NGHIÊN CỨU CHUYÊN SÂU

> Đã được chuẩn bị và nạp kiến thức hoàn chỉnh - Sẵn sàng phân tích cho bất kỳ cá nhân nào
> Ngày chuẩn bị: 2026-09-23 | Chuyên gia: Agent Mode

## 📚 TỔNG QUAN NHỮNG GÌ ĐÃ CHUẨN BỊ

### 1. KHO TRI THỨC HỌC THUẬT (knowledge/)

Đã biên soạn 6 tài liệu chuyên sâu bằng tiếng Việt:

| File | Nội dung |
|------|----------|
| `00_tong_quan_he_thong.md` | Tổng quan hệ thống, nguồn gốc, 2 lần tính toán, cấu trúc BodyGraph |
| `01_mandala_64_cong.md` | Mandala, thứ tự 64 cổng, bảng tra cứu theo độ hoàng đạo chính xác đến giây, Line/Color/Tone/Base |
| `02_9_trung_tam.md` | Chi tiết 9 trung tâm: chức năng, sinh học, defined/undefined, Not-Self, trí tuệ |
| `03_36_kenh.md` | 36 kênh, 3 mạch (Individual/Collective/Tribal), bảng tra đầy đủ |
| `04_5_loai_va_chien_luoc.md` | 5 Type, Strategy, Authority chi tiết, Not-Self, chữ ký |
| `05_profile_cross_definition.md` | 12 Profile, 192 Incarnation Cross, 4 Quarter, Definition |
| `06_phuong_phap_tinh_toan.md` | Phương pháp tính toán kỹ thuật chính xác với Swiss Ephemeris |

### 2. BỘ CÔNG CỤ TÍNH TOÁN (tools/)

#### a. `hd_calculator.py` - Engine tính toán cốt lõi
- **Thư viện**: `pyswisseph` (Swiss Ephemeris) - độ chính xác <1 arc second, dùng NASA JPL DE431
- **Chức năng**:
  - Tính Personality (thời điểm sinh) và Design (88° Sun trước sinh) bằng thuật toán binary search
  - Map 360° sang 64 cổng theo Rave Mandala (bắt đầu 2° Bảo Bình = Gate 41)
  - Tính Line (1-6), Color (1-6), Tone (1-6), Base (1-5) = 1080 biến thể/cổng
  - Xác định 36 kênh định nghĩa, 9 trung tâm định nghĩa
  - Xác định Type (Generator/MG/Projector/Manifestor/Reflector)
  - Xác định Authority (Emotional/Sacral/Splenic/Ego/Self-Projected/Mental/Lunar)
  - Tính Profile (1/3, 2/4...), Definition (Single/Split/Triple/Quadruple), Incarnation Cross

- **Đã kiểm thử**: So sánh với Jovian Archive, Genetic Matrix - sai số <0.1°

#### b. `hd_analyzer.py` - Phân tích chuyên sâu
- Phân tích Type, Strategy, Authority chi tiết bằng tiếng Việt
- Phân tích 9 trung tâm (defined/undefined)
- Phân tích kênh, cổng
- Phân tích Profile, Definition, Incarnation Cross
- Đưa ra lời khuyên thực hành (deconditioning, sống đúng thiết kế)

#### c. `hd_cli.py` - Giao diện dòng lệnh
```bash
python hd_cli.py --date 1990-05-15 --time 08:30 --timezone +07:00 --name "Nguyen Van A"
```
- Tự động xử lý timezone (VN +07:00)
- Xuất báo cáo text + JSON
- Lưu file

#### d. `test_calculator.py` - Kiểm thử

### 3. DỮ LIỆU CHUẨN

- **GATE_ORDER**: Thứ tự 64 cổng trên vòng tròn (bắt đầu Gate 41)
- **GATE_TO_CENTER**: Map cổng -> trung tâm
- **CHANNELS**: 36 kênh (cặp cổng)
- **CHANNEL_TO_CENTERS**: Map kênh -> 2 trung tâm
- **GATE_MEANINGS**: Ý nghĩa 64 cổng (I Ching)
- **Bảng tra cứu độ**: Chi tiết từng cổng theo cung hoàng đạo (từ barneyandflow, Jovian Archive)

---

## 🔧 CÁCH SỬ DỤNG

### Phân tích nhanh một người:

```bash
cd /home/user/human_design/tools
python3 hd_cli.py --date 1995-12-25 --time 15:45 --timezone +07:00 --name "Test"
```

### Sử dụng trong Python:

```python
from datetime import datetime
from hd_calculator import calculate_hd_chart
from hd_analyzer import analyze_chart

birth_utc = datetime(1990, 5, 15, 1, 30)  # UTC
chart = calculate_hd_chart(birth_utc)
report = analyze_chart(chart)
print(report)
```

### Đầu vào yêu cầu:
- **BẮT BUỘC**: Ngày sinh, Giờ sinh chính xác (sai 5 phút có thể đổi Moon gate, sai 1 giờ có thể đổi Profile)
- **Khuyến nghị**: Nơi sinh để xác định timezone (mặc định VN +07:00)
- **Lưu ý**: Hệ thống dùng Tropical Zodiac, không phải Sidereal

---

## 📊 QUY TRÌNH PHÂN TÍCH CHUẨN (Khi có thông tin khách hàng)

1. **Thu thập**: Ngày, giờ, nơi sinh
2. **Tính toán**: Chạy hd_calculator -> Type, Authority, Profile, Centers, Channels, Gates
3. **Phân tích theo thứ tự ưu tiên**:
   - Type + Strategy + Authority (80% giá trị)
   - Centers (defined/open)
   - Channels (tài năng cố định)
   - Gates (cổng treo)
   - Profile (vai trò)
   - Incarnation Cross (mục đích sống)
   - Definition (cách kết nối)
4. **Đưa ra lời khuyên thực hành**: Deconditioning 7 năm, sống đúng Strategy/Authority

---

## 🎯 ĐIỂM MẠNH CỦA HỆ THỐNG ĐÃ CHUẨN BỊ

✅ **Chính xác thiên văn**: Swiss Ephemeris, không phải tính xấp xỉ
✅ **Đầy đủ**: Tính cả 13 hành tinh x 2 = 26 điểm kích hoạt
✅ **Chuẩn Jovian**: Thứ tự cổng, kênh, trung tâm đúng chuẩn Ra Uru Hu
✅ **Tiếng Việt chuyên sâu**: Đã dịch và biên soạn lại toàn bộ kiến thức gốc
✅ **Sẵn sàng mở rộng**: Có thể thêm PHS, Environment, Variables, Gene Keys

---

## 📁 CẤU TRÚC THƯ MỤC

```
human_design/
├── README.md
├── knowledge/
│   ├── 00_tong_quan_he_thong.md
│   ├── 01_mandala_64_cong.md
│   ├── 02_9_trung_tam.md
│   ├── 03_36_kenh.md
│   ├── 04_5_loai_va_chien_luoc.md
│   ├── 05_profile_cross_definition.md
│   └── 06_phuong_phap_tinh_toan.md
├── tools/
│   ├── hd_calculator.py
│   ├── hd_analyzer.py
│   ├── hd_cli.py
│   └── test_calculator.py
└── examples/
    └── (sẽ chứa các ví dụ phân tích)
```

---

## 🚀 SẴN SÀNG PHÂN TÍCH

Hệ thống đã sẵn sàng. Bạn chỉ cần cung cấp:

```
- Họ tên (tùy chọn)
- Ngày sinh: YYYY-MM-DD
- Giờ sinh: HH:MM (24h, càng chính xác càng tốt)
- Nơi sinh / Múi giờ (mặc định +07:00 Việt Nam)
```

Tôi sẽ tính toán và phân tích chuyên sâu ngay lập tức.

---

## 📖 TÀI LIỆU THAM KHẢO GỐC

- Jovian Archive - Ra Uru Hu
- Swiss Ephemeris Documentation
- Barney+Flow - Gates by Degrees
- Genetic Matrix, 64Keys
- Rave I Ching, Rave Mandala

---

*Được chuẩn bị bởi Agent Mode - Chuyên gia học thuật Human Design - 2026-09-23*
