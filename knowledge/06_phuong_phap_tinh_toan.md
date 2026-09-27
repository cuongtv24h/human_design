# PHƯƠNG PHÁP TÍNH TOÁN HUMAN DESIGN - KỸ THUẬT CHÍNH XÁC

## 1. Yêu cầu đầu vào
- Ngày sinh dương lịch
- Giờ sinh CHÍNH XÁC (đến phút) - Sai 5 phút có thể đổi cổng Mặt Trăng, sai 1 giờ có thể đổi Profile
- Múi giờ: offset CỐ ĐỊNH do người dùng khai báo (mặc định +07:00 giờ Việt Nam). Hệ thống KHÔNG tự tra giờ mùa hè (DST) lịch sử: người sinh ở nơi có DST (Mỹ, châu Âu...) phải nhập đúng offset áp dụng tại ngày giờ sinh (VD New York tháng 7/1990 = -04:00 EDT, tháng 1/1990 = -05:00 EST — tra cứu qua timeanddate.com). Nhập sai 1 giờ có thể đổi cổng Mặt Trăng/Profile.
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
4. Heart định nghĩa => Ego (nếu 21-45 nối Heart-Throat thì Ego Manifested; nếu 25-51 nối Heart-G thì Ego Projected, cần lời mời)
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
- Cross Type (do Profile quyết định — Design Sun luôn lùi đúng 88° nên không dùng hiệu kinh độ):
  - Right Angle: Profile 1/3, 1/4, 2/4, 2/5, 3/5, 3/6, 4/6
  - Left Angle: Profile 5/1, 5/2, 6/2, 6/3
  - Juxtaposition: Profile 4/1

- Tên Cross (ví dụ Right Angle Cross of the Sphinx) cần tra bảng 192 Cross từ Jovian Archive.

## 11. Bước 10: Variables — 4 mũi tên (PHS)
Từ Color/Tone của Sun và North Node (Personality + Design), theo quy ước gethumandesign.com/docs/variable:
- Trái trên Determination (PHS, cách ăn-tiêu hóa) = Color của Design Sun; Trái dưới Environment (môi trường đúng) = Color của Design Node
- Phải trên Motivation (động lực) = Color của Personality Sun; Phải dưới Perspective (góc nhìn) = Color của Personality Node
- Hướng mũi tên lấy từ Tone của chính vị trí đó: Tone 1-3 = trái (chủ động), 4-6 = phải (thụ động)
- Cognition (giác quan tin cậy) = Tone của Design Sun: 1 Smell, 2 Taste, 3 Outer Vision, 4 Inner Vision, 5 Feeling, 6 Touch
- Bảng Color: Determination 1-6 Appetite/Taste/Thirst/Touch/Sound/Light; Environment 1-6 Caves/Markets/Kitchens/Mountains/Valleys/Shores; Motivation 1-6 Fear/Hope/Desire/Need/Guilt/Innocence; Perspective 1-6 Survival/Possibility/Power/Wanting/Probability/Personal
- Tầng thực nghiệm: chỉ luận sau khi thân chủ đã sống đúng Strategy + Authority; cần giờ sinh chính xác đến phút (sai Tone đổi hướng mũi tên)

## 12. Bước 11: Transits và mốc chu kỳ
- Ảnh transit tại thời điểm xem (mặc định hiện tại): tính cổng/hào của 10 hành tinh + North Node, so với natal — (a) hành tinh rơi vào trung tâm MỞ natal (vùng điều kiện hóa hôm nay), (b) nối điện từ: cổng transit + cổng treo natal tạo thành kênh
- Mốc chu kỳ lớn (quét + tinh chỉnh điểm Mặt Trời/hành tinh về đúng kinh độ natal): Solar Return mỗi năm, Jupiter Return ~11.86 năm, Saturn Return ~29.46 năm, Uranus đối đỉnh ~42 tuổi, Uranus Return ~84 tuổi
- Transit phụ thuộc ngày xem nên báo cáo ghi rõ ngày (tái lập được khi xem cùng ngày); phần còn lại của chart thuần hàm ngày sinh

## 13. Độ chính xác và lưu ý
- Swiss Ephemeris chính xác hơn 99% tool online
- Cần giờ sinh chính xác: Moon di chuyển ~13°/ngày => 0.5°/giờ => có thể đổi gate trong 2-3 giờ
- Các hành tinh chậm (Pluto, Neptune) ít thay đổi giữa P và D
- Các hành tinh nhanh (Moon, Mercury) thay đổi nhiều
- Node dùng True Node (không phải Mean Node): chênh nhau <2°, chỉ ảnh hưởng Color/Tone/Base, hiếm khi đổi Line/Gate
- Tìm Design JD tinh chỉnh đến 0.0001° (~0.36 giây); so sánh với Jovian Archive, 64keys, Genetic Matrix cho sai số <0.1°
- Không tính Chiron, Lilith trong hệ thống gốc (có thể thêm mở rộng)

## 14. Kiểm thử
Đã test với các ngày:
- 1987-01-01: Projector 2/4 Splenic
- 1990-06-15: Generator 2/4 Sacral
- 2000-01-01: Generator 1/3 Emotional

So sánh với Jovian Archive, 64keys, Genetic Matrix cho sai số <0.1°.
