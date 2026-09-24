# Chuẩn nội dung: "Bản Thiết Kế Bản Thân — Cẩm Nang Vận Hành"

Tài liệu này là **chuẩn bắt buộc** cho template báo cáo tự sự `operating_manual`
trong `backend/reporting/`. Mọi thay đổi nội dung của template này phải (1) cập nhật
đúng chuẩn ở đây và (2) đi qua test `tests/test_narrative_report.py`.

## 1. Mục tiêu

Báo cáo phải được **người chưa từng nghe qua Human Design** đọc hiểu và dùng được ngay.
Phong cách là **"Personal Operating Manual" — cẩm nang vận hành cho chính mình**,
không phải bản giải mã học thuật.

Lộ trình học của nội dung (từ dễ đến sâu, theo yêu cầu sản phẩm):

1. **Tự giải mã bản thân** — Cấu trúc năng lượng cá nhân (Part 1–3).
2. **Ứng dụng vào đời sống** — Vai diễn, công việc, tình yêu, 7 ngày thực chiến (Part 4–5).
3. **Lớp sâu / tiến hóa** — Gates/Channels chi tiết, Variables/PHS: *chưa nằm trong
   template v1*; sẽ là các module domain (xem `REPORTING_ARCHITECTURE.md`).

Bốn nhóm chủ đề cốt lõi và cách chúng được gán cho từng phần:

| Nhóm chủ đề | Nội dung | Phần trong báo cáo |
| --- | --- | --- |
| 1. Cấu trúc năng lượng cá nhân | Type/Hào quang/Population %, Strategy & Authority, Signature & Not-Self | Part 1, Part 2 |
| 2. Tâm lý & hành vi vô thức | 12 Profile, 9 Centers (defined/open — điều kiện hóa & Not-Self), Definition | Part 3, Part 4 |
| 3. Ứng dụng thực tế | Công việc/môi trường (cháy năng lượng), quan hệ & ranh giới, 7 ngày thử nghiệm | Part 5 |
| 4. Lớp sâu (Gates/Channels 64/36, Incarnation Cross, Variables) | Incarnation Cross + Quarters ở mức khung; phần còn lại chờ module domain | Part 4 (khung) |

## 2. Cấu trúc 5 phần (bắt buộc)

Mọi báo cáo `operating_manual` render đúng 5 phần theo đúng thứ tự, đúng tiêu đề:

| # | Section id | Tiêu đề | Yêu cầu nội dung tối thiểu |
| --- | --- | --- | --- |
| 1 | `part1_identity` | Phần 1 — Bức tranh toàn cảnh: Bạn thực sự là ai khi bỏ qua mọi kỳ vọng? | Lời chào theo tên; ẩn dụ chiếc xe; **Type bằng ngôn ngữ đời sống** (tên + % dân số + hào quang); **đèn xanh (Signature) / đèn đỏ (Not-Self)**; 1 lời kêu gọi hành động 7 ngày; dòng thuật ngữ. |
| 2 | `part2_decision_compass` | Phần 2 — La bàn ra quyết định: Làm sao để ngừng hối hận sau mỗi lựa chọn? | Nguyên tắc "ngừng dùng não để quyết định"; **Strategy bằng ngôn ngữ đời sống**; **Authority: tên la bàn + nguyên tắc vàng + đúng 3 bước thực hiện**; 2 kịch bản ứng dụng (lời mời hợp tác; mua sắm/mối quan hệ); dòng thuật ngữ. |
| 3 | `part3_burden_release` | Phần 3 — Tháo gỡ gánh nặng: Những điều bạn đang gánh mà vốn không phải của bạn | Khung "9 trạm năng lượng"; mỗi **trạm có màu** = điểm tựa đáng tin (dòng mô tả đời sống); mỗi **trạm mở = bọt biển** + *câu hỏi nhận diện cụ thể*; kết bằng nguyên tắc "không tắc — mà nhận diện"; dòng thuật ngữ. |
| 4 | `part4_role_profile` | Phần 4 — Phong cách sống & vai diễn cuộc đời: Người bên trong và hình ảnh bên ngoài | Profile = kịch bản 2 lớp (bên trong/bên ngoài) theo **chuyện kể của cặp profile**; "bài học từ những lần vấp" (sai lầm = dữ liệu thí nghiệm, không phải bản án); Definition bằng ngôn ngữ đời sống; Incarnation Cross = "bài toán lớn của linh hồn" (tên cross giữ dạng kỹ thuật kèm ghi chú tham chiếu); Quarters; dòng thuật ngữ. |
| 5 | `part5_field_application` | Phần 5 — Ứng dụng thực chiến: Đưa thiết kế vào đời sống 24/7 | "Trong công việc" (môi trường phù hợp + bảo vệ năng lượng, phòng cháy năng lượng); "Trong tình yêu & giao tiếp" (nhịp + ranh giới); **Nhật ký thử nghiệm 7 ngày với đúng 3 việc nhỏ** — việc 1 cá nhân hóa theo Authority, việc 2 theo số trạm mở, việc 3 theo vùng mạnh; lời kêu gọi chọn đúng 1 việc; **disclaimer** (không thay thế y tế/pháp lý/tài chính). |

## 3. Quy tắc viết (bắt buộc)

1. **Trục tâm lý của mỗi đoạn:** thấu cảm nỗi đau hiện tại → chỉ ra cơ chế gốc →
   hành động cụ thể. Không đoạn nào chỉ giải thích khái niệm.
2. **Ngôn ngữ đời sống đi trước, thuật ngữ đi sau.** Mỗi thuật ngữ kỹ thuật phải có
   cụm "đời sống" đi kèm. **Chống mẫu (anti-pattern):** in nguyên chuỗi song ngữ máy
   của calculator như `Wait to Respond and Inform - Chờ Đáp Ứng rồi Thông Báo` vào thân
   bài **hoặc** dòng thuật ngữ. Chuỗi song ngữ máy không được xuất hiện ở bất kỳ đâu;
   dòng "Thuật ngữ:" cuối mỗi phần dùng **thuật ngữ chuẩn đã trau chuốt** từ
   `tools/hd_language.py` (ví dụ: `Chiến lược sống = Chờ lời mời`,
   `Quyền nội tại = Quyền Cảm xúc — Đám rối Thái Dương`).
3. **Tỉ lệ 70/30:** ~70% hành vi thực tế (làm gì, khi nào, nói câu gì, hỏi câu nào);
   ~30% khái niệm kỹ thuật (Type, Authority, Center, Profile, Cross, Definition) giữ
   nguyên để người đọc tra cứu.
4. **Hệ ẩn dụ chuẩn** (dùng nhất quán, không sáng tạo ẩn dụ mới khi chưa đồng ý):
   - cơ thể/vessel = **chiếc xe** (mỗi Type một loại xe — bảng `TYPE_LANGUAGE.car`);
   - 9 centers = **9 trạm năng lượng**;
   - open center = **chiếc bọt biển**;
   - authority = **la bàn/bộ la bàn** (mỗi authority một tên la bàn — `AUTHORITY_LANGUAGE.compass_name`);
   - signature/not-self = **đèn xanh / đèn đỏ**;
   - definition = **cách đóng gói năng lượng**;
   - incarnation cross = **bài toán lớn của cuộc đời**.
5. **Không phóng đại, không y khoa hóa, không tiên đoán:** không hứa "bạn sẽ giàu có",
   không chỉ định bệnh; sức khỏe chỉ là ngôn ngữ năng lượng tự quan sát.
6. **Cá nhân hóa bằng dữ liệu, không bằng may rủi:** mọi câu cá nhân hóa phải truy
   ngược được về một key trong `hd_calculator.calculate_hd_chart()` (type, strategy,
   authority, profile, definition, centers, cross, quarters).
7. **Mỗi phần kết bằng dòng:** `_Thuật ngữ: <các từ khóa kỹ thuật của phần đó>._`

## 4. Lớp ngôn ngữ (`tools/hd_language.py` + `backend/reporting/language_vn.py`)

Hai tầng, cùng một hướng: **tầng thuật ngữ dùng chung** và **tầng kể chuyện báo cáo**.

**Tầng 1 — `tools/hd_language.py` (thuật ngữ chuẩn, dùng cho MỌI nơi hiển thị):**
BodyGraph, báo cáo PDF, MCP/REST đều lấy thuật ngữ từ đây qua `vn_strategy`,
`vn_authority`, `vn_definition`, `vn_type`, `vn_center`; dữ liệu gồm `STRATEGY_VN`,
`AUTHORITY_VN`, `DEFINITION_VN`, `TYPE_VN`, `NOT_SELF_SIGNATURE`, `CENTER_VN`
(tên trung tâm theo `knowledge/02_9_trung_tam.md`) và nhãn giao diện `UI`.
Quy tắc: không bao giờ hiển thị chuỗi thô kiểu "Chờ Đáp Ứng rồi Thông Báo".

**Tầng 2 — `backend/reporting/language_vn.py` (ngữ liệu kể chuyện của báo cáo),**
re-export toàn bộ tầng 1 và thêm dữ liệu thuần (không phụ thuộc report):

| Hằng số | Phạm vi | Chìa khóa |
| --- | --- | --- |
| `TYPE_LANGUAGE` | 5 Type | `Generator`, `Manifesting Generator`, `Projector`, `Manifestor`, `Reflector` |
| `AUTHORITY_LANGUAGE` | 7 authority (rút từ raw string) | `emotional`, `sacral`, `splenic`, `ego`, `self_projected`, `mental`, `lunar`; `resolve_authority()` ánh xạ chuỗi calculator → key |
| `CENTER_LANGUAGE` | 9 centers (theo `CENTER_ORDER`) | tên center tiếng Anh |
| `PROFILE_STORIES` | 12 profile | `"1/3"`, `"2/4"`, ... `"6/x"` |
| `DEFINITION_LANGUAGE` | 4 definition + fallback | `Single/Split/Triple/Quadruple Split Definition` |
| `CROSS_TYPE_LANGUAGE` | 3 kiểu cross | `Juxtaposition`, `Left Angle`, `Right Angle` |
| `seven_day_log(authority, open_center_count)` | 3 việc nhỏ 7 ngày | cá nhân hóa theo authority + số trạm mở |

**Quy tắc mở rộng:** khi calculator thêm giá trị mới (authority mới, cross mới, ...),
phải bổ sung entry đủ trường — bắt đầu từ `tools/hd_language.py` cho thuật ngữ chuẩn,
sau đó mới đến entry kể chuyện trong `language_vn` — **trước** khi render; renderer
`narrative.py` chỉ ghép entry vào khung, không chứa câu tiếng Việt cố định ngoài khung
giao tiếp chung. Bản ánh xạ 192 Incarnation Cross sang tiếng Việt là phạm vi *lớp
sâu* — v1 giữ cross dạng kỹ thuật kèm ghi chú tham chiếu.

## 5. Render và xác minh

- Renderer: `backend/reporting/narrative.py::render_operating_manual(chart, name)` —
  deterministic, không LLM, không network; cùng chart + tên → cùng output từng byte.
- Orchestrator: `template: "operating_manual"` trong `ReportRequest` (mặc định
  `sections` — template cũ không đổi hành vi). Domain add-on (ví dụ `money`) vẫn gắn
  sau 5 phần chuẩn trong cùng một `ReportDocument`.
- Xác minh: `PYTHONPATH=tools:mcp .venv/bin/pytest -q` (gồm
  `tests/test_hd_language.py` và `tests/test_narrative_report.py`): thứ tự 5 phần,
  đúng 3 bước authority, ẩn dụ bọt biển hiện diện cho mọi trạm mở, chuỗi song ngữ máy
  không lọt vào báo cáo (kể cả dòng thuật ngữ), thuật ngữ chuẩn tiếng Việt hiện ở
  dòng "Thuật ngữ:", tính deterministic, domain gắn sau 5 phần.

## 6. Tiêu chí chấp nhận khi thay đổi nội dung

- [ ] Người mới đọc hiểu không cần tra từ điển (đọc thử 1 lần, không dừng lại).
- [ ] Không chuỗi `" - " song ngữ` của calculator nào trong toàn bộ báo cáo (chỉ thuật ngữ chuẩn tiếng Việt ở dòng thuật ngữ).
- [ ] Tỉ lệ 70/30 được giữ: đếm ước lượng câu hành vi / câu khái niệm.
- [ ] 5 phần, đúng tiêu đề, đúng thứ tự; test `test_narrative_report.py` xanh.
- [ ] Disclaimer y tế/pháp lý/tài chính vẫn nằm ở cuối Part 5.
