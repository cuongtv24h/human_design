"use client";

import { Markdown } from "@/components/Markdown";
import { Card, PageHeader } from "@/components/ui";

const TAO_BAO_CAO = `## Tạo báo cáo

[Tạo báo cáo](/reports/new) gồm 4 bước. Cột **Xem trước** bên phải luôn hiện BodyGraph và nội dung nháp để bạn kiểm tra trước khi tạo.

**Bước 1 — Khách hàng.** Chọn khách hàng có sẵn (danh sách gần đây, tìm kiếm hoặc [thêm mới](/clients)). Ngày giờ sinh và nơi sinh lấy từ hồ sơ khách.

**Bước 2 — Loại báo cáo.** Chọn *mức độ chuyên sâu*, *cách trình bày* (mẫu dựng sẵn hoặc mẫu riêng soạn trong [Studio](/templates)) và *chủ đề chuyên sâu* (có thể chọn nhiều).

**Bước 3 — Cách viết nội dung.** Hai chế độ:

- **Nội dung chuẩn**: tạo ngay, văn phong cố định của hệ thống.
- **AI biên tập**: AI viết lại lời văn theo giọng chuyên gia (không tính lại chart — dữ liệu kỹ thuật giữ nguyên). Mất khoảng 1–2 phút, chạy nền nên bạn có thể rời trang; tốn phí AI theo số token, xem ở Cài đặt → AI / LLM. Nếu nhà cung cấp chính lỗi, hệ thống tự thử nhà cung cấp dự phòng.

Nếu dùng mẫu riêng có văn phong, bước này có thêm công tắc **Dùng văn phong của mẫu** (kèm nút **Thử giọng** để nghe trước một đoạn).

**Bước 4 — Xác nhận.** Kiểm tra lại tóm tắt rồi bấm **Tạo báo cáo**.

### Sau khi tạo

Trang chi tiết báo cáo có các tab **Nội dung**, **Infographic**, **BodyGraph**, **Xuất file** (PDF/DOCX) và **Chia sẻ**. Những việc thường làm:

- **Biên tập**: sửa từng mục; nút **AI biên tập phần này** viết lại một mục (giữ văn phong đã chọn).
- **Áp văn phong**: viết lại toàn bộ báo cáo cũ theo giọng của mẫu (kể cả mượn giọng mẫu khác).
- **Tải về / Link 5 phút**: tải file hoặc tạo link xem không cần đăng nhập, hết hạn sau 5 phút.
- **Lưu trữ**: ẩn báo cáo khỏi danh sách đang dùng.`;

const DUNG_MAU = `## Dùng mẫu báo cáo

[Studio mẫu](/templates) là nơi tổ chức soạn mẫu riêng. Ngoài các mẫu dựng sẵn của hệ thống, bạn có thể tạo không giới hạn mẫu theo thương hiệu của mình.

### Soạn mẫu

Mỗi mẫu gồm các **mục**: mục dựng sẵn (lấy từ hệ thống, có thể đổi tiêu đề) hoặc **khối tự viết** (mở bài, nội dung chính, thực hành, kết bài, miễn trừ trách nhiệm). Khối hay dùng nên lưu vào **thư viện khối** để tái sử dụng cho nhiều mẫu; trong thân khối có thể đặt **biến**, giá trị biến điền theo từng tổ chức.

Đính kèm **bài mẫu** (bài viết thật đúng giọng bạn muốn): vừa để người duyệt hình dung, vừa là nguyên liệu để AI học văn phong (cần ít nhất 2 bài).

### Duyệt và chia sẻ

Mẫu mới ở trạng thái **nháp**, chỉ chủ sở hữu (và admin) thấy. Gửi duyệt → admin **phê duyệt** thì mẫu mới hiện trong danh sách chọn ở bước tạo báo cáo. Mẫu ưng ý có thể **chia sẻ lên thư viện chung** cho tổ chức khác dùng; ngược lại, bạn có thể **đem mẫu từ thư viện chung về** hoặc **nhân bản** mẫu có sẵn để chỉnh sửa.

Huy hiệu **Có văn phong** cho biết mẫu đã có hồ sơ giọng AI sẵn sàng dùng.`;

const VAN_PHONG = `## Văn phong AI

Mỗi mẫu riêng có thể sở hữu một **hồ sơ văn phong** (giọng điệu, nhịp câu, từ vựng, cấu trúc, điều nên/tránh) để AI viết đúng giọng của bạn thay vì giọng mặc định.

1. **Phân tích**: khi mẫu có ít nhất 2 bài mẫu, bấm **Phân tích văn phong** — AI đọc bài mẫu và trích thành hồ sơ (tốn 1 lượt gọi AI). Sửa/thêm/xóa bài mẫu sau đó sẽ đánh dấu **Cần phân tích lại**.
2. **Duyệt giọng**: nút **Viết thử** cho AI viết một đoạn ngắn theo hồ sơ; **So sánh A/B** đặt giọng mặc định và giọng mẫu cạnh nhau. Không ưng thì **Sửa tay** từng trường, **Sao chép** giọng từ mẫu khác, hoặc **Khôi phục** một bản cũ trong **Lịch sử**.
3. **Dùng**: khi tạo báo cáo ở chế độ AI biên tập với mẫu có văn phong, bật công tắc **Dùng văn phong của mẫu** (có nút **Thử giọng** ngay trong bước tạo). Báo cáo đính kèm bản chụp hồ sơ lúc tạo — đổi giọng sau này không ảnh hưởng báo cáo cũ.
4. **Đánh giá và cải tiến**: mỗi báo cáo có nút thích/không thích cho văn phong; trang mẫu thống kê theo từng bản để biết bản nào được lòng người đọc. Báo cáo cũ có thể **Áp văn phong** để viết lại theo giọng mới (đánh giá cũ bị xóa vì nhận xét giọng cũ).`;

const SECTIONS = [
  { id: "tao-bao-cao", label: "Tạo báo cáo", body: TAO_BAO_CAO },
  { id: "dung-mau", label: "Dùng mẫu báo cáo", body: DUNG_MAU },
  { id: "van-phong", label: "Văn phong AI", body: VAN_PHONG },
];

export default function GuidePage() {
  return (
    <>
      <PageHeader
        title="Hướng dẫn sử dụng"
        description="Cách tạo báo cáo, soạn mẫu riêng và dạy AI viết đúng giọng của bạn."
      />
      <Card className="mb-6 p-5">
        <ol className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {SECTIONS.map((s, i) => (
            <li key={s.id}>
              <a href={`#${s.id}`} className="font-medium text-brand-700 hover:underline">
                {i + 1}. {s.label}
              </a>
            </li>
          ))}
        </ol>
      </Card>
      <div className="space-y-6">
        {SECTIONS.map((s) => (
          <Card key={s.id} className="p-5">
            <div id={s.id} className="scroll-mt-6">
              <Markdown>{s.body}</Markdown>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}
