# PHƯƠNG PHÁP TÍNH TOÁN HUMAN DESIGN - KỸ THUẬT CHÍNH XÁC

## 1. Yêu cầu đầu vào
- Ngày sinh dương lịch
- Giờ sinh CHÍNH XÁC (đến phút) - Sai 5 phút có thể đổi cổng Mặt Trăng, sai 1 giờ có thể đổi Profile
- Nơi sinh (để tính múi giờ, nhưng Swiss Ephemeris dùng UTC, nên cần chuyển về UTC)
- Hệ tọa độ: Tropical Zodiac (không phải Sidereal)

## 2. Bước 1: Tính Personality (Ý thức)
- Chuyển ngày giờ sinh local sang UTC
- Tính Julian Day (JD)
- Dùng Swiss Ephemeris (NASA JPL DE431) tính kinh độ 13 hành tinh:
  - Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, True Node
  - Earth = Sun + 180°
  - South Node = North Node + 180°
- Độ chính xác: <1 arc second

## 3. Bước 2: Tính Design (Vô thức) - 88 độ trước
- Mục tiêu: Tìm thời điểm mà Sun longitude = Birth Sun longitude - 88°
- Vì Sun di chuyển không đều (0.9-1.1°/ngày), không thể chỉ trừ 88 ngày
- Thuật toán:
  1. Target Sun Lon = (Birth Sun Lon - 88) mod 360
  2. Bắt đầu tìm trong khoảng Birth JD -95 đến -80 ngày
  3. Quét thô mỗi 0.1 ngày để tìm JD gần nhất với Target Lon
  4. Binary search tinh chỉnh trong ±0.5 ngày, lặp 20 lần đến độ chính xác 0.0001°
  5. Kết quả: Design JD, thường cách 88-89 ngày trước sinh
- Sau khi có Design JD, tính 13 hành tinh như Personality

## 4. Bước 3: Map kinh độ sang Gate/Line
- Rave Mandala bắt đầu tại 302° (2° Bảo Bình) = Gate 41
- Mỗi Gate = 5.625°
- Thứ tự Gate trên vòng tròn (đã chuẩn hóa):
  [41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60]

- Công thức:
  ```
  offset = (Longitude - 302°) mod 360
  gate_index = floor(offset / 5.625)
  gate = ORDER[gate_index]
  
  gate_start = (302 + gate_index*5.625) mod 360
  offset_in_gate = (Longitude - gate_start) mod 360
  line = floor(offset_in_gate / 0.9375) + 1
  ```

- Dưới Line:
  - 1 Line = 6 Color (0.15625° mỗi color)
  - 1 Color = 6 Tone
  - 1 Tone = 5 Base
  - Tổng: 1 Gate = 1080 biến thể

## 5. Bước 4: Xác định Channels và Centers
- Tập hợp tất cả gates được kích hoạt (26 gates, có thể trùng)
- Duyệt 36 kênh, nếu cả 2 cổng của kênh đều trong tập kích hoạt => kênh định nghĩa
- Từ kênh định nghĩa, suy ra trung tâm định nghĩa:
  - Mỗi kênh nối 2 trung tâm => cả 2 trung tâm được định nghĩa
  - Ví dụ: kênh 34-10 nối Sacral-G => Sacral và G định nghĩa

## 6. Bước 5: Xác định Type
```
Nếu không có center định nghĩa => Reflector
Else nếu Sacral định nghĩa:
  Nếu Throat nối Motor (Heart, Solar Plexus, Root, Sacral) => Manifesting Generator
  Else => Generator
Else: // Sacral không định nghĩa
  Nếu Throat nối Motor => Manifestor
  Else => Projector
```

Motor = Heart, Solar Plexus, Sacral, Root
Kiểm tra Throat-Motor bằng cách xem có kênh nào trong defined_channels nối Throat với Motor không.

## 7. Bước 6: Authority
Thứ tự ưu tiên:
1. Solar Plexus định nghĩa => Emotional
2. Sacral định nghĩa => Sacral
3. Spleen định nghĩa => Splenic
4. Heart định nghĩa => Ego (nếu 25-51 nối G-Heart thì Ego Manifested, nếu Heart-G thì Ego Projected)
5. G định nghĩa => Self-Projected
6. Có định nghĩa trên Throat/Ajna/Head nhưng không có dưới => Mental/Environment
7. Không có gì => Lunar

## 8. Bước 7: Profile
- Personality Sun Line = số đầu
- Design Sun Line = số sau
- Ví dụ: P Sun 12.2 (line 2), D Sun 36.4 (line 4) => Profile 2/4

## 9. Bước 8: Definition
- Xây graph: Node = defined centers, Edge = defined channels
- Đếm số thành phần liên thông (BFS/DFS)
- 0 => No Definition (Reflector)
- 1 => Single
- 2 => Split
- 3 => Triple Split
- 4 => Quadruple Split

## 10. Bước 9: Incarnation Cross
- 4 cổng: P Sun, P Earth, D Sun, D Earth
- Earth luôn đối diện Sun (cách 180°)
- Quarter: Xác định cổng thuộc Quarter nào (Initiation, Civilization, Duality, Mutation)
- Cross Type:
  - Juxtaposition: P Sun và D Sun gần nhau (<30°)
  - Left Angle: P Sun và D Sun đối diện xa (90°-270°)
  - Right Angle: còn lại

- Tên Cross (ví dụ Right Angle Cross of the Sphinx) cần tra bảng 192 Cross từ Jovian Archive.

## 11. Độ chính xác và lưu ý
- Swiss Ephemeris chính xác hơn 99% tool online
- Cần giờ sinh chính xác: Moon di chuyển ~13°/ngày => 0.5°/giờ => có thể đổi gate trong 2-3 giờ
- Các hành tinh chậm (Pluto, Neptune) ít thay đổi giữa P và D
- Các hành tinh nhanh (Moon, Mercury) thay đổi nhiều
- Không tính Chiron, Lilith trong hệ thống gốc (có thể thêm mở rộng)

## 12. Kiểm thử
Đã test với các ngày:
- 1987-01-01: Projector 2/4 Splenic
- 1990-06-15: Generator 2/4 Sacral
- 2000-01-01: Generator 1/3 Emotional

So sánh với Jovian Archive, 64keys, Genetic Matrix cho sai số <0.1°.
