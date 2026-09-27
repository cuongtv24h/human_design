# Brief asset game "Đúng Thiết Kế" (cho Design)

> Mục đích: thay toàn bộ icon/emoji tạm trong game bằng asset thiết kế riêng.
> Nền tảng: web mobile-first (ưu tiên màn 360–390px), hỗ trợ desktop.

## 1. Art direction chung

- Phong cách: **flat 2.5D** (phẳng + bóng đổ nhẹ tạo chiều sâu), đường nét tròn, thân thiện.
- Nền game luôn tối: `#14122b` (chàm đậm). Asset phải nổi rõ trên nền này.
- Màu nhấn chính: amber `#fbbf24` / `#fcd34d` (vàng), phụ: violet `#8b5cf6`, rose `#fb7185` (trùm/nguy hiểm), emerald `#34d399` (thành công).
- Chữ trong asset (nếu có): **bắt buộc hỗ trợ tiếng Việt đầy đủ dấu**. Ưu tiên font tròn, đậm.
- Tránh chi tiết quá nhỏ — asset hiển thị nhỏ nhất ~24px trên mobile.

## 2. Quy cách kỹ thuật

| Loại | Định dạng | Nền | Dung lượng tối đa |
|---|---|---|---|
| Icon/UI nhỏ | SVG (vector, ưu tiên) | Trong suốt | — |
| Minh họa, nhân vật, bài | WebP + PNG dự phòng | Trong suốt (trừ background) | ≤ 120 KB/ảnh |
| Background thế giới | WebP (ngang 1600px) + bản mobile 800px | Đục | ≤ 250 KB/ảnh |
| Hiệu ứng động | Lottie JSON | Trong suốt | ≤ 150 KB/file |

- Đặt tên file: `game-<nhom>-<ten>.webp` (vd `game-card-style-khoi-xuong.webp`, `game-world-nguoc-dong-bg.webp`).
- Bàn giao theo thư mục nhóm (xem mục 3), kèm 1 file Figma/source để dev tự export lại khi cần.
- Mọi asset dạng nhân vật/vật thể: **phiên bản nền trong suốt**.

## 3. Danh sách asset chi tiết

### A. Thế giới & bản đồ — P0 (cần đầu tiên)

| # | Asset | Mô tả | Kích thước gợi ý |
|---|---|---|---|
| A1 | BG Thế Giới Ngược Dòng | Khung cảnh "đời thường đảo ngược": cầu thang lên trời, nhà úp ngược… tông chàm + vàng | 1600×900 (desktop), 800×1200 (mobile) |
| A2 | BG Thương Vụ Sinh Tử | Tòa nhà/bàn đàm phán kịch tính về đêm, tông xanh navy + vàng gold | như A1 |
| A3 | BG Khu Rừng Linh Thú | Rừng đêm huyền bí, mắt thú phát sáng, tông xanh lá đậm + tím | như A1 |
| A4 | Node thường (3 trạng thái) | Chấm/cổng màn chơi: **mở** (sáng), **hiện tại** (phát sáng + vòng pulse), **khóa** (xám + ổ khóa) | SVG, 3 biến thể |
| A5 | Node tốc độ / trùm | Biến thể A4: tốc độ (tia sét ⚡), trùm (cổng đỏ 👹) | SVG, 2 biến thể × trạng thái mở/khóa |
| A6 | Sao 1–3 | Ngôi sao **sáng** (vàng, có lấp lánh) và **tối** (xám) | SVG, 2 biến thể |
| A7 | Đường nối node | Đoạn path cong + đầu nối, 2 màu: đã qua (vàng), chưa qua (xám mờ) | SVG |
| A8 | Banner 12 chương | Icon đại diện mỗi chương (4/concept, xem tên bên dưới) | SVG/PNG 96px |

Tên 12 chương (để vẽ đúng ý):
- Ngược Dòng: Thức Tỉnh (bình minh) → Va Chạm (vụ nổ) → Soi Gương (gương) → Bứt Phá (tên lửa).
- Thương Vụ: Nhận Dự Án (kẹp hồ sơ) → Deadline Dí (đồng hồ) → Đàm Phán (bắt tay) → Chốt Deal (cúp).
- Linh Thú: Vào Rừng (cây) → Dấu Vết (vết chân) → Đối Mặt (sư tử) → Linh Thú Vương (vương miện).

### B. Lá bài — P0

| # | Asset | Mô tả | Kích thước gợi ý |
|---|---|---|---|
| B1 | Lưng bài chung | Họa tiết nhận diện game (la bàn/cổng sao), viền vàng | PNG/WebP 400×560 |
| B2 | Bài Khởi Xướng 🔥 | Nhân vật/biểu tượng **ngọn lửa** lao về trước, tông cam-đỏ | 400×560 |
| B3 | Bài Kiến Tạo ⚒️ | Nhân vật/biểu tượng **thợ rèn/cỗ máy** bền bỉ, tông cam đất | 400×560 |
| B4 | Bài Dẫn Đường 🦉 | Nhân vật/biểu tượng **cú/hải đăng** quan sát, tông xanh dương | 400×560 |
| B5 | Bài Tấm Gương 🪞 | Nhân vật/biểu tượng **gương/nước** phản chiếu, tông tím-xanh | 400×560 |
| B6 | Thẻ Đổi Câu 🔄 | Lá mini: 2 mũi tên xoay vòng | 200×280 |
| B7 | Thẻ Soi Gương 🪞 | Lá mini: gương phát sáng | 200×280 |
| B8 | Thẻ Nhân Đôi ✖️2 | Lá mini: số ×2 nổi bật | 200×280 |

### C. Boss & mascot — P1

| # | Asset | Mô tả | Kích thước gợi ý |
|---|---|---|---|
| C1 | Boss Ngược Dòng | "Kỳ Vọng Khổng Lồ" — bóng người/bộ mặt áp đặt (gông, khuôn mẫu) | PNG 600px |
| C2 | Boss Thương Vụ | "Deadline Quái" — đồng hồ/quái vật giấy tờ | PNG 600px |
| C3 | Boss Linh Thú | "Linh Thú Vương" — sư tử vương miện uy nghi | PNG 600px |
| C4 | Mascot game | Linh vật nhỏ dẫn dắt (cú la bàn?), 3 cảm xúc: vui / cổ vũ / an ủi | PNG 240px × 3 |

### D. UI & hiệu ứng — P0/P1

| # | Asset | Mô tả | Ghi chú |
|---|---|---|---|
| D1 | Lửa combo | Ngọn lửa 3 cấp độ (×2 cam, ×4 vàng, ×6+ tím) | SVG hoặc Lottie — P0 |
| D2 | Lottie qua màn | Ăn mừng: sao bay + confetti vàng | Lottie — P0 |
| D3 | Lottie mở khóa | Ổ khóa mở + tia sáng | Lottie — P1 |
| D4 | Lottie trùm xuất hiện | Cổng đỏ + rung màn hình | Lottie — P1 |
| D5 | Icon đồng hồ | Vòng đếm ngược màn tốc độ/trùm | SVG — P0 |
| D6 | Huy hiệu 8 chiếc | Thay emoji huy hiệu hiện tại (🧭 🦎 📅 🔥 🌋 ⚔️ 🪞 🏆) | SVG 64px — P1 |

### E. Share/OG — P1

| # | Asset | Mô tả | Kích thước |
|---|---|---|---|
| E1 | Khung ảnh share kết quả | Nền + khung cho 4 phong cách (dev ghép chữ động lên trên) | 1200×630 |
| E2 | Khung khoe sao/bảng vàng | Nền + khung khoe hạng | 1200×630 |

## 4. Thứ tự ưu tiên bàn giao

1. **Đợt 1 (P0):** A4–A8, B1–B8, D1, D2, D5 — đủ để game "lột xác" khỏi emoji.
2. **Đợt 2 (P1):** A1–A3, C1–C4, D3–D4, D6.
3. **Đợt 3:** E1–E2 + tinh chỉnh theo phản hồi người chơi.

## 5. Checklist nghiệm thu (dev kiểm tra)

- [ ] Đủ file theo bảng, đúng tên, đúng thư mục.
- [ ] Nền trong suốt (trừ BG), không viền trắng khi đặt lên `#14122b`.
- [ ] Chữ Việt (nếu có) hiển thị đúng dấu ở mọi kích thước.
- [ ] Dung lượng trong giới hạn mục 2 (ảnh hưởng tốc độ mobile).
- [ ] Lottie chạy được trên iOS + Android (test bằng LottieFiles preview).
- [ ] Có file Figma/source đính kèm.

## 6. Liên hệ kỹ thuật

- Dev tích hợp asset tại: `web/public/game/...` (sẽ tạo khi nhận đợt 1).
- Mọi asset hiện tại là emoji/icon tạm có gắn kèm tên asset tương ứng trong bảng trên (cột mô tả giữ emoji gốc để đối chiếu).
