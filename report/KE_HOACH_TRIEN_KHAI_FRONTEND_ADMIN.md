# Kế hoạch triển khai Frontend / Admin — Human Design Analyzer

> Phiên bản 1.3.3 · 2026-09-24 · Trạng thái: **đã chốt D6b-giờ VN +07:00 cố định, D8-pm2/VPS, D10-template tự sinh; các mục còn lại theo đề xuất mặc định**
>
> Thay đổi v1.3.3: **P0-10, P2-6, P3-1, P3-2 hoàn thành** — link tải ký tên 5 phút, cấu hình AI/LLM (khóa mã hóa) + kiểm tra kết nối, link chia sẻ cho khách + trang `/r/[token]`.
>
> Thay đổi v1.3.2: **P2-1, P2-3, P2-4 hoàn thành** — trình biên tập từng phần, phiên bản/khôi phục, cảnh báo mất sự kiện kỹ thuật, AI biên tập từng phần kèm so sánh.
>
> Thay đổi v1.3.1: **P0-5 PDF, P0-6 DOCX hoàn thành** (BodyGraph PNG qua resvg — không cần libcairo).
>
> Thay đổi v1.3: **đã có lát cắt chạy được P0 + P1** — API `/api/v1` (`backend/api/`) và Admin MVP (`web/`); xem mục 8.0 *Tiến độ*.
>
> Thay đổi v1.2: **không tự áp offset lịch sử** — tính đúng theo giờ khai báo với chuẩn Việt Nam = UTC+07:00; P0-4 đã hoàn thành (`tools/hd_time.py`).
>
> Thay đổi v1.1: thêm mục 1.3 *Quy ước thời gian* (nhập & hiển thị giờ Việt Nam, tính theo UTC với offset lịch sử); bỏ Docker/CI → **pm2 trên VPS riêng**; thương hiệu dùng **template tự sinh**; bỏ geocoding; rút gọn lộ trình.
> Nền tảng hiện có: branch `arena/01a0d215-human-design` @ `240d670` — 40 MCP tools, 44 REST routes, 48 test xanh.

---

## 0. Tóm tắt

Backend đã có đủ **lõi nghiệp vụ**: tính chart, báo cáo theo chuẩn (thông tin người được
phân tích + BodyGraph + nội dung template/LLM), infographic HTML, PDF, MCP/REST. Cái còn thiếu
để có sản phẩm Admin dùng được là **lớp ứng dụng**: lưu trữ, đăng nhập/phân quyền, hàng đợi
job cho LLM, API v1 riêng cho frontend, và chính giao diện.

Đề xuất triển khai **5 giai đoạn trong khoảng 9 tuần** với đội 1 Backend + 1 Frontend
(+ designer bán thời gian):

| Giai đoạn | Nội dung | Thời lượng |
| --- | --- | --- |
| **P0** | Nền móng backend: DB, API v1, auth, job queue, **giờ Việt Nam lịch sử**, PDF/DOCX theo chuẩn | 2 tuần |
| **P1** | Admin MVP: đăng nhập, khách hàng, wizard tạo báo cáo, xem/tải báo cáo | 3 tuần |
| **P2** | Trình biên tập báo cáo + LLM + đủ định dạng xuất (MD/PDF/DOCX/Infographic) | 2 tuần |
| **P3** | Chia sẻ cho khách hàng (link bảo mật) | 1 tuần |
| **P4** | Hardening, bảo mật, giám sát, triển khai production bằng **pm2 trên VPS** | 1 tuần |

Mốc quan trọng: **cuối P1 (tuần 5)** coach đã dùng được nội bộ với chế độ template;
**cuối P4 (tuần 9)** sẵn sàng go-live.

---

## 1. Hiện trạng backend (đo trên code thực tế)

### 1.1 Đã sẵn sàng — frontend dùng lại trực tiếp

| Năng lực | Vị trí | Ghi chú |
| --- | --- | --- |
| Tính chart (Swiss Ephemeris) | `tools/hd_calculator.py` | Machine contract, không sửa |
| Báo cáo chuẩn, 2 tier × 2 template × 8 domain | `backend/reporting/orchestrator.py`, `catalog.py` | **5–8 ms**/báo cáo (kể cả deep_core + 8 domain) |
| Content mode `template` / `llm` + fallback | `backend/reporting/service.py`, `llm_client.py`, `llm_editor.py` | LLM validate giữ nguyên sự kiện kỹ thuật |
| BodyGraph SVG | `tools/hd_bodygraph.py` → `export.bodygraph_svg` | ~19 ms, ~117 KB |
| Infographic HTML tự chứa | `backend/reporting/infographic.py` | ~20 ms, ~135 KB |
| PDF | `tools/hd_report_pdf.py::build_pdf` | ~390 ms, ~95 KB — **xem gap B5** |
| Thuật ngữ VN chuẩn dùng chung | `tools/hd_language.py`, `backend/reporting/language_vn.py` | Dùng lại cho nhãn UI |
| Schema chuẩn (Pydantic) | `backend/reporting/contract.py` | Sinh type TypeScript từ OpenAPI |

### 1.2 Khoảng trống phải lấp trước khi làm UI

| # | Gap | Hiện trạng | Hệ quả nếu bỏ qua |
| --- | --- | --- | --- |
| B1 | **Lưu trữ** | Không có DB; `ReportDocument` chỉ sống trong request | Không có lịch sử khách hàng/báo cáo |
| B2 | **API riêng cho frontend** | `mcp/openapi_server.py` là cầu nối ChatGPT, 44 route phẳng | Trộn contract GPT Actions với contract app |
| B3 | **Xác thực & phân quyền** | Không có | Không thể đưa lên Internet |
| B4 | **Job nền** | Mọi thứ chạy đồng bộ | LLM mất 30–120 giây → timeout HTTP |
| B5 | **PDF theo chuẩn báo cáo** | `build_pdf(chart, ...)` nhận chart thô, nội dung riêng, định dạng ngày `dd/mm/YYYY` | PDF lệch nội dung với Markdown/LLM/Infographic |
| B6 | **DOCX** | Chưa có | Không đáp ứng yêu cầu "xuất pdf/doc" |
| B7 | ~~Quy ước giờ sinh~~ ✅ | Đã thống nhất ở `tools/hd_time.py` — mục 1.3 | — |
| B8 | **Sửa từng phần + kiểm tra lại** | Chỉ merge draft LLM | Coach sửa tay có thể làm mất sự kiện kỹ thuật mà không ai biết |
| B9 | **Catalog cho UI** | Nằm trong `catalog.py`, chưa có endpoint | Frontend phải hard-code tier/domain/section |
| B10 | **CORS** | `allow_origins=["*"]` + `allow_credentials=True` | Không hợp lệ cho app có cookie đăng nhập; rủi ro bảo mật |
| B11 | **Cấu hình chạy production** | Chưa có cấu hình pm2, reverse proxy, biến môi trường | Không triển khai lặp lại được |

### 1.3 Quy ước thời gian (đã chốt & đã triển khai)

**Nguyên tắc: nhập giờ Việt Nam → hiển thị giờ đã khai báo → tính toán bằng UTC, với chuẩn Việt Nam = UTC+07:00 cố định.**

| Bước | Giá trị | Ghi chú |
| --- | --- | --- |
| Nhập | Giờ đồng hồ tại Việt Nam lúc sinh, đúng như người dùng khai báo (VD `15/05/1990 08:30`) | Người dùng không cần biết múi giờ |
| Hiển thị | Đúng giờ đã khai báo — báo cáo, BodyGraph, infographic, PDF, brief LLM | `Ngày sinh: 15/05/1990 · Giờ sinh: 08:30 (giờ Việt Nam)`; **không hiển thị giờ UTC** |
| Tính toán | **UTC = giờ khai báo − 7 giờ** (mọi ngày sinh) | Swiss Ephemeris tính theo Julian Day thang UT; Design = thời điểm Mặt Trời lùi 88° |

**Vì sao phải quy về UTC:** vị trí hành tinh là một thời điểm vật lý duy nhất trên toàn cầu; 08:30 ở
Hà Nội và 08:30 ở London cách nhau 7 giờ, nên phải quy về cùng một thang giờ rồi mới tra lịch thiên văn.
Bước này hoàn toàn nội bộ.

**Quyết định của chủ dự án:** **không** tự áp offset lịch sử theo ngày sinh. Mọi ngày sinh đều trừ đúng
7 giờ. Tham khảo (không áp dụng): tzdata ghi một số giai đoạn Việt Nam dùng offset khác (VD miền Nam
1960 – 13/06/1975 dùng UTC+8); nếu người dùng khai báo giờ theo đồng hồ thời đó, kết quả là theo giờ
khai báo — đúng quy ước đã chốt.

**Đã triển khai (P0-4 ✅):**

- `tools/hd_time.py` — nguồn duy nhất: `local_to_utc`, `display_birth`, `normalize_offset`… Thay thế 5
  bản sao logic đổi giờ trước đây (orchestrator, MCP server, CLI, BodyGraph CLI, PDF CLI) vốn xử lý
  không nhất quán (VD orchestrator nhận `Asia/Ho_Chi_Minh` và tự áp offset lịch sử; MCP/CLI âm thầm
  đổi mọi tên múi giờ lạ thành +7).
- `timezone` mặc định `+07:00`; các cách viết giờ Việt Nam (`+7`, `UTC+7`, `Asia/Ho_Chi_Minh`,
  `Asia/Saigon`, `VN`…) đều quy về `+07:00` cố định. Offset cố định khác (`+08:00`…) vẫn nhận khi người
  gọi API chủ động truyền; tên múi giờ khác bị từ chối rõ ràng (422) thay vì đoán sai.
- BodyGraph và PDF bỏ dòng "GMT …" / "Giờ UTC tính toán"; brief LLM bỏ các trường giờ nội bộ
  (UTC, Julian Day) để LLM không nhắc giờ UTC trong báo cáo.
- `tests/test_time_convention.py` — công thức (qua ngày/năm/nhuận/giây), không áp lịch sử, mọi entry
  point ra cùng chart, mọi bề mặt hiển thị chỉ có giờ khai báo.

---

## 2. Phạm vi & đối tượng người dùng

| Vai trò | Mô tả | Giai đoạn |
| --- | --- | --- |
| **Admin** | Quản trị hệ thống: người dùng, cấu hình LLM, thương hiệu, nhật ký | P1 |
| **Coach** | Chuyên gia tư vấn: quản lý khách hàng của mình, tạo/biên tập/xuất/chia sẻ báo cáo | P1 |
| **Khách hàng** | Người được phân tích: xem/tải báo cáo được chia sẻ | P3 |

**Ngoài phạm vi kế hoạch này** (cần quyết định riêng): thanh toán/billing, landing page
marketing, tự đăng ký tài khoản khách hàng, ứng dụng di động native, đa ngôn ngữ ngoài tiếng Việt.

---

## 3. Quyết định cần chốt trước khi bắt đầu

Mỗi dòng có **đề xuất mặc định** — nếu không có phản hồi khác, kế hoạch đi theo cột này.

| # | Câu hỏi | Đề xuất | Lý do | Phương án khác |
| --- | --- | --- | --- | --- |
| D1 | Người dùng giai đoạn đầu | **Admin + Coach nội bộ** | Kiểm soát chất lượng trước khi mở cho khách | Mở cổng khách hàng ngay |
| D2 | Frontend stack | **Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui + TanStack Query** | Hệ sinh thái lớn, SSR cho trang chia sẻ, dễ tuyển | Vite + React SPA (đơn giản hơn, không SSR) |
| D3 | Backend app | **FastAPI mới tại `backend/api/` (`/api/v1`)**, giữ `mcp/openapi_server.py` cho GPT | Tách contract app khỏi contract GPT | Mở rộng thẳng `openapi_server.py` |
| D4 | CSDL | **PostgreSQL 16** + SQLAlchemy 2 + Alembic | JSONB lưu `ReportDocument` nguyên vẹn | SQLite (chỉ demo) |
| D5 | Lưu file | **Ổ đĩa VPS** (`/var/lib/hd/artifacts`) + endpoint tải có token ký tên, hết hạn | Đơn giản, hợp VPS riêng; nếu cần scale chuyển sang Cloudflare R2 mà không đổi API | S3/R2 ngay từ đầu |
| D6 | Đăng nhập | **Email + mật khẩu, session cookie httpOnly do backend cấp**; magic link cho khách (P3) | Không phụ thuộc bên thứ ba, tuân thủ dữ liệu trong nước | Clerk/Auth0/Supabase Auth |
| D6b | Giờ sinh | ✅ **Đã chốt & triển khai:** nhập & hiển thị giờ khai báo; tính bằng UTC với chuẩn Việt Nam **+07:00 cố định**, không áp offset lịch sử (mục 1.3) | Đơn giản, nhất quán, đúng giờ người dùng khai báo | — |
| D7 | Job nền | **Redis + arq** (async, nhẹ) | Hợp FastAPI async; chỉ cần cho LLM/PDF/DOCX | Celery (nặng hơn), RQ |
| D8 | Hosting | ✅ **Đã chốt: VPS riêng, chạy bằng pm2** (web, api, worker) + Nginx; PostgreSQL & Redis cài trực tiếp; **không Docker, không CI** | Theo hạ tầng sẵn có của chủ dự án | — |
| D9 | Nhà cung cấp LLM | **Endpoint OpenAI-compatible cấu hình qua Admin** (mặc định `gpt-4o-mini`) | Code đã hỗ trợ `HD_LLM_BASE_URL` | Cố định một nhà cung cấp |
| D10 | Thương hiệu trên báo cáo | ✅ **Đã chốt (tạm thời): template mẫu tự sinh** — màu theo Type như infographic hiện tại, tên hệ thống mặc định; màn Thương hiệu chuyển vào backlog | Thay bằng bộ nhận diện thật sau, không ảnh hưởng kiến trúc (chỉ là cấu hình theme) | Làm màn Thương hiệu ngay |

---

## 4. Kiến trúc đề xuất

```text
                  Nginx (TLS Let's Encrypt, reverse proxy)
                         ┌──────────────────────────────┐
  Trình duyệt ──HTTPS──▶ │  web  (Next.js · pm2)         │
  (Admin/Coach/Khách)    │  - UI Admin/Coach             │
                         │  - Trang chia sẻ /r/[token]   │
                         │  - /api/* → proxy tới api     │  ← cùng origin, không lộ localhost
                         └──────────────┬───────────────┘
                                        │ HTTP nội bộ
                         ┌──────────────▼───────────────┐
                         │  api  (FastAPI /api/v1 · pm2) │
                         │  backend/api/                 │──▶ PostgreSQL (users, clients, reports…)
                         │  auth · RBAC · CRUD · catalog │──▶ Ổ đĩa VPS (pdf, docx, html, svg)
                         │  gọi backend/reporting/*      │──▶ Redis (queue, rate limit)
                         └──────────────┬───────────────┘
                                        │ enqueue
                         ┌──────────────▼───────────────┐
                         │  worker (arq · pm2)           │
                         │  - LLM edit (30–120 s)        │──▶ LLM OpenAI-compatible
                         │  - PDF / DOCX render          │
                         └──────────────────────────────┘

  Giữ nguyên:  mcp/server.py (MCP stdio)  ·  mcp/openapi_server.py (ChatGPT Actions)
  Cả ba cửa dùng CHUNG backend/reporting/service.py — một nguồn logic duy nhất.
```

**Nguyên tắc:**

1. `backend/reporting/` giữ **thuần** (không biết DB/HTTP). `backend/api/` là lớp ứng dụng bọc ngoài.
2. **Đồng bộ khi nhanh, bất đồng bộ khi chậm:** template/infographic/SVG (≤ 20 ms) trả ngay;
   LLM, PDF, DOCX đi qua job + polling (hoặc SSE).
3. `ReportDocument` lưu **nguyên JSON** (JSONB) → render lại bất kỳ định dạng nào mà không tính lại chart.
4. Type TypeScript **sinh tự động** từ `/api/v1/openapi.json` (`openapi-typescript`) — không viết tay.
5. Frontend chỉ gọi URL tương đối `/api/...`; Next.js proxy sang `api` (không bao giờ gọi `localhost` từ trình duyệt).

---

## 5. Mô hình dữ liệu

| Bảng | Cột chính | Ghi chú |
| --- | --- | --- |
| `organizations` | id, name, theme (JSONB, mặc định = template tự sinh), llm_settings (JSONB, key mã hóa) | D10: theme tự sinh, thay bằng thương hiệu thật sau |
| `users` | id, org_id, email, password_hash, role (`admin`/`coach`), is_active, last_login_at | Argon2 hash |
| `clients` | id, org_id, owner_user_id, full_name, email, phone, birth_date, birth_time (giờ khai báo), birth_time_known, birth_place (chữ, chỉ hiển thị), timezone (mặc định `+07:00`), notes, consent_at, deleted_at | Mục 1.3; dữ liệu cá nhân — xóa mềm + xóa cứng theo yêu cầu |
| `reports` | id (= `report_id`), org_id, client_id, created_by, tier, template, content_mode, domains[], status (`draft`/`generating`/`ready`/`failed`/`archived`), request (JSONB), document (JSONB), editor, warnings_count, version, created_at, updated_at | `document` = `ReportDocument` đầy đủ |
| `report_revisions` | id, report_id, version, author (user / `llm:<model>`), change_type (`generate`/`llm_edit`/`manual_edit`/`regenerate`), sections_diff (JSONB), warnings (JSONB), created_at | Lịch sử + hoàn tác |
| `report_artifacts` | id, report_id, version, format (`md`/`pdf`/`docx`/`infographic_html`/`bodygraph_svg`/`bodygraph_png`), storage_key, bytes, sha256, created_at | Cache theo (report, version, format) |
| `jobs` | id, report_id, kind (`llm_edit`/`render_pdf`/`render_docx`), status, progress, error, started_at, finished_at | Bản sao trạng thái để UI hiển thị |
| `share_links` | id, report_id, token_hash, formats_allowed[], expires_at, revoked_at, view_count, last_viewed_at | Token chỉ hiện một lần |
| `audit_logs` | id, org_id, actor_id, action, entity, entity_id, meta (JSONB), ip, created_at | Mọi thao tác xem/xuất/chia sẻ/xóa dữ liệu khách |

---

## 6. API v1 cho frontend (`/api/v1`)

| Nhóm | Endpoint | Đồng bộ? | Dùng lại |
| --- | --- | --- | --- |
| Auth | `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `POST /auth/password/reset` | ✔ | — |
| Catalog | `GET /catalog` → tiers, templates, content_modes, domains, sections (tiêu đề song ngữ) | ✔ | `catalog.py` |
| Khách hàng | `GET/POST /clients`, `GET/PATCH/DELETE /clients/{id}`, `POST /clients/{id}/erase` | ✔ | — |
| Xem trước | `POST /reports/preview` → document + markdown + infographic (không lưu) | ✔ ≤ 50 ms | `service.generate_report` |
| Báo cáo | `POST /reports` (template → `ready` ngay; llm → `generating` + job_id), `GET /reports?client_id=&status=`, `GET /reports/{id}` | ✔ / job | `service`, `orchestrator` |
| Biên tập | `PATCH /reports/{id}/sections/{section_id}` {markdown} → lưu revision + **warnings kiểm tra sự kiện** | ✔ | `merge_llm_draft` (B8) |
| LLM | `POST /reports/{id}/llm-edit` {section_ids?} → job; `GET /reports/{id}/llm-brief` (cho coach xem prompt) | job | `llm_editor`, `llm_client` |
| Phiên bản | `GET /reports/{id}/revisions`, `POST /reports/{id}/revisions/{v}/restore`, `POST /reports/{id}/regenerate` | ✔ | — |
| Xuất file | `POST /reports/{id}/artifacts` {format} → nhanh thì trả link, chậm thì job; `GET /reports/{id}/artifacts/{format}` → link tải ký tên (5 phút) | ✔ / job | `export`, `infographic`, PDF/DOCX mới |
| Job | `GET /jobs/{id}` (poll) hoặc `GET /jobs/{id}/events` (SSE) | ✔ | — |
| Chia sẻ | `POST /reports/{id}/share` → token (hiện 1 lần), `DELETE /share/{id}`; công khai: `GET /public/r/{token}` | ✔ | `infographic` |
| Admin | `GET/POST/PATCH /users`, `GET/PUT /settings/llm` (+ `POST /settings/llm/test`), `GET /audit` | ✔ | — |

**Quy ước:** lỗi theo RFC 9457 (`application/problem+json`); phân trang cursor; mọi route
(trừ `/public/*`, `/auth/login`) yêu cầu session; kiểm tra quyền theo `org_id` + `owner_user_id`.

---

## 7. Màn hình (sitemap) & tiêu chí nghiệm thu

```text
/login
/                         Tổng quan
/clients                  Danh sách khách hàng
/clients/new              Thêm khách hàng
/clients/[id]             Hồ sơ khách hàng (+ danh sách báo cáo)
/reports/new?client=…     Wizard tạo báo cáo (4 bước)
/reports/[id]             Xem báo cáo (tab: Nội dung · Infographic · BodyGraph · Tệp xuất · Lịch sử)
/reports/[id]/edit        Trình biên tập báo cáo
/settings/llm             Cấu hình LLM            (admin)
/settings/users           Người dùng & vai trò    (admin)
/audit                    Nhật ký hệ thống        (admin)
/r/[token]                Trang báo cáo chia sẻ cho khách (công khai, SSR)
```

### 7.1 Wizard tạo báo cáo — màn hình quan trọng nhất

| Bước | Nội dung | Chi tiết UX |
| --- | --- | --- |
| 1. Người được phân tích | Chọn khách có sẵn hoặc nhập mới: họ tên, ngày sinh, **giờ sinh (giờ Việt Nam)**, nơi sinh (chữ tự do, chỉ để hiển thị) | Nhãn ô giờ: "Giờ sinh (giờ Việt Nam)"; ô ngày dạng `dd/mm/yyyy`; công tắc "Không rõ giờ sinh" → cảnh báo các phần phụ thuộc giờ |
| 2. Gói phân tích | `free_basic` / `deep_core` + chọn domain add-on (8 thẻ có mô tả) | Lấy từ `GET /catalog`; hiển thị danh sách phần sẽ có |
| 3. Cách viết | Template `sections` / `operating_manual`; Content mode **Mẫu chuẩn** / **Chuyên gia AI biên tập** | Giải thích ngắn 2 chế độ; nếu chưa cấu hình LLM → vô hiệu hóa kèm lý do |
| 4. Xem trước & tạo | Preview tức thì (tóm tắt Type/Strategy/Authority/Profile + mini BodyGraph) → nút **Tạo báo cáo** | Preview gọi `/reports/preview` (< 50 ms) mỗi khi đổi lựa chọn |

**Nghiệm thu:** tạo báo cáo template trong **≤ 4 bước và < 60 giây**; chế độ LLM hiển thị tiến
trình, cho phép rời trang và quay lại; nhập sai ngày/giờ báo lỗi ngay tại ô (dùng validator của `SubjectInput`).

### 7.2 Xem báo cáo `/reports/[id]`

- Đầu trang: thẻ **thông tin người được phân tích** + huy hiệu `content_mode` / `editor`
  (`template`, `llm:<model>`, `template (llm fallback)`) + số cảnh báo.
- Tab **Nội dung** (Markdown render, mục lục theo section) · **Infographic** (iframe sandbox) ·
  **BodyGraph** (SVG, nút tải PNG) · **Tệp xuất** (MD/PDF/DOCX/HTML, trạng thái job) · **Lịch sử** (revisions).
- **Panel cảnh báo** luôn hiển thị nếu `warnings` khác rỗng — bấm vào nhảy tới section liên quan.

### 7.3 Trình biên tập `/reports/[id]/edit`

- Trái: danh sách section (kéo thả **không** cho phép — thứ tự phần là chuẩn). Giữa: editor
  Markdown (TipTap/Milkdown) có preview. Phải: **dữ liệu nguồn** của section (`ReportSection.data`)
  + bảng thuật ngữ chuẩn để coach tra.
- Nút **"AI biên tập phần này"** → job LLM cho một section → hiển thị **diff** cũ/mới → Chấp nhận / Bỏ.
- Mỗi lần lưu → server kiểm tra sự kiện kỹ thuật; mất sự kiện → cảnh báo vàng ngay dưới editor (không chặn lưu).
- Lưu tự động bản nháp mỗi 10 giây; mỗi lần "Lưu phiên bản" tạo một revision.

**Nghiệm thu:** sửa và lưu một section < 300 ms; hoàn tác về phiên bản bất kỳ; cảnh báo xuất hiện
khi xóa tên Type/Strategy/Authority khỏi section vốn chứa chúng.

### 7.4 Các màn còn lại (tóm tắt)

| Màn | Thành phần chính | Nghiệm thu |
| --- | --- | --- |
| Tổng quan | Số khách, số báo cáo theo trạng thái, job đang chạy, báo cáo gần đây | Tải < 1 giây |
| Khách hàng | Bảng tìm kiếm/lọc, hồ sơ, nút "Tạo báo cáo", nút "Xóa dữ liệu" (2 bước xác nhận) | Coach chỉ thấy khách của mình; admin thấy tất cả |
| Cấu hình LLM | base URL, model, key (chỉ ghi, hiển thị `••••1234`), temperature, nút **Kiểm tra kết nối** | Key lưu mã hóa, không bao giờ trả về frontend |
| Người dùng | Mời qua email, đổi vai trò, khóa | Chỉ admin |
| Nhật ký | Lọc theo người/hành động/thời gian | Ghi nhận xem/xuất/chia sẻ/xóa |
| Trang chia sẻ `/r/[token]` | Infographic + nút tải định dạng được phép, theme tự sinh | Token hết hạn/thu hồi → trang 410; không index (`noindex`) |

### 7.5 Nguyên tắc giao diện

- Toàn bộ nhãn tiếng Việt, **thuật ngữ song ngữ** lấy từ bảng chuẩn (`hd_language.py`) — endpoint
  `GET /catalog` trả kèm nhãn để frontend không tự dịch.
- Màu nhận diện Type dùng chung với infographic (`TYPE_ACCENT` trong `infographic.py`).
- Responsive: Admin tối ưu desktop ≥ 1280px, dùng được trên tablet; trang chia sẻ tối ưu **mobile trước**.
- Accessibility: WCAG 2.1 AA (tương phản, focus, nhãn form).

---

## 8. Lộ trình chi tiết

Ước lượng theo ngày công (d). BE = Backend, FE = Frontend.

### 8.0 Tiến độ (cập nhật v1.3)

| Hạng mục | Trạng thái | Ghi chú |
| --- | --- | --- |
| P0-1 khung API, pm2, check.sh | ✅ | `backend/api/main.py`, `deploy/ecosystem.config.cjs`, `deploy/check.sh`, `deploy/deploy.sh` |
| P0-2 models + Alembic | ✅ | 7 bảng; migration `0001`, `alembic check` sạch; JSONB trên PostgreSQL |
| P0-3 auth + RBAC | ✅ | Argon2, cookie httpOnly `hd_session` (chỉ lưu SHA-256), header chống CSRF `X-HD-Request`, admin/coach |
| P0-4 quy ước giờ sinh | ✅ | `tools/hd_time.py` |
| P0-5 PDF theo `ReportDocument` | ✅ | `backend/reporting/render_pdf.py`: bìa + BodyGraph + mục lục + bookmark; ẩn cảnh báo nội bộ |
| P0-6 DOCX theo `ReportDocument` | ✅ | `backend/reporting/render_docx.py`: style Word gốc (Heading/List), ảnh BodyGraph, số trang |
| P0-7 worker arq | ⏳ tạm thay | LLM chạy bằng FastAPI `BackgroundTasks`; fallback template khi lỗi/thiếu key |
| P0-8 CORS whitelist, rate limit | ◐ | CORS theo `CORS_ORIGINS`; giới hạn đăng nhập sai 5 lần/15 phút (trong tiến trình, chưa Redis) |
| P0-9 `/catalog` | ✅ | Kiểu TS viết tay trong `web/lib/types.ts` (chưa sinh tự động) |
| P0-10 artifact trên đĩa + link ký tên | ✅ | Cache PDF/DOCX theo phiên bản ở `ARTIFACT_DIR` (render sẵn, xóa bản cũ); `POST /reports/{id}/links` → `/api/v1/files/{token}` (HMAC-SHA256, hết hạn 5 phút, không cần đăng nhập, ghi nhật ký) |
| P1-1 khung web | ✅ | Next.js 15, Tailwind 4, TanStack Query; component tự viết (chưa dùng shadcn CLI) |
| P1-2 đăng nhập + guard | ✅ | |
| P1-3 API clients/reports/preview | ✅ | `tests/test_api_v1.py` (7 test) |
| P1-4 khách hàng | ✅ | Ô ngày dd/mm/yyyy, giờ 24h “Giờ sinh (giờ Việt Nam)”, xác nhận đồng ý xử lý dữ liệu |
| P1-5 wizard 4 bước + preview | ✅ | Preview BodyGraph + chỉ số + nội dung nháp |
| P1-6 xem báo cáo | ✅ | Tab Nội dung / Infographic (iframe sandbox) / BodyGraph / Xuất file (MD, HTML, SVG) |
| P1-7 tổng quan + nhật ký | ✅ | Bảng `audit_logs`: đăng nhập, tạo/sửa/xóa, xuất file |
| P2-1 API sửa section + revision + restore + regenerate | ✅ | `backend/api/routers/editor.py`: `PUT /reports/{id}/sections/{sid}` (khóa lạc quan `base_version` → 409), `GET …/revisions`, `POST …/revisions/{v}/restore` (tạo phiên bản mới), `POST …/regenerate`; lưu 18–60 ms; PDF/DOCX render lại nền, xóa cache bản cũ |
| P2-2 API LLM | ◐ | `POST …/sections/{sid}/llm` đồng bộ, chỉ trả **đề xuất** (không lưu), 503 khi thiếu key; LLM cả báo cáo = `regenerate` với `content_mode=llm`. SSE tiến trình: chưa làm (trang tự thăm dò) |
| P2-3 trình biên tập | ✅ | `web/app/(admin)/reports/[id]/edit`: danh sách phần · Markdown Soạn thảo/Xem trước · dữ liệu nguồn / thuật ngữ chuẩn / lịch sử; cảnh báo vàng khi mất Type/Strategy/Authority… (`POST …/check`, không chặn lưu); tự lưu nháp trình duyệt 10 giây + khôi phục; Ctrl/⌘+S |
| P2-6 cấu hình LLM | ✅ | `GET/PUT /settings/llm`, `POST /settings/llm/test` (chỉ admin); khóa mã hóa Fernet bằng `HD_SECRET_KEY`, chỉ hiện `••••1234`, không vào nhật ký; cấu hình trong hệ thống ưu tiên hơn `HD_LLM_*`; trang `/settings/llm` |
| P3-1 share link | ✅ | Bảng `share_links` (migration `0002`): token chỉ hiện một lần (lưu SHA-256), định dạng được phép, hết hạn 1–365 ngày, thu hồi, đếm lượt xem; nhật ký xem/tải |
| P3-2 trang `/r/[token]` | ✅ | SSR, mobile-first, `noindex`, `no-referrer`: thông tin + chỉ số + Infographic + đọc toàn bộ báo cáo + nút tải; không lộ cảnh báo nội bộ/giờ UTC. Link hết hạn/thu hồi → thông báo thân thiện (mã HTTP 410 ở API; trang Next trả 200) |
| P3-3 gửi email | ✖ bỏ | Theo quyết định của chủ dự án (24/9): không gửi email; chuyên viên tự gửi link qua Zalo/Messenger |
| P2-4 “AI biên tập phần này” | ✅ | Diff theo dòng (LCS), “Dùng bản này” / “Bỏ đề xuất”; proxy Next `proxyTimeout` 180 s |

### P0 — Nền móng backend (tuần 1–2)

| Mã | Việc | Ai | Ước lượng | Hoàn thành khi |
| --- | --- | --- | --- | --- |
| P0-1 | Khung `backend/api/` (FastAPI, settings qua `.env`, `/api/v1/health`), `deploy/ecosystem.config.cjs` (pm2), script `deploy/check.sh` chạy pytest trước khi deploy | BE | 1d | `pm2 start deploy/ecosystem.config.cjs` chạy được trên máy dev |
| P0-2 | SQLAlchemy models + Alembic migration theo mục 5 | BE | 2d | Migration up/down sạch |
| P0-3 | Auth: login/logout/me, Argon2, session cookie httpOnly + CSRF, RBAC dependency | BE | 2d | Test phân quyền admin/coach/ẩn danh |
| P0-4 | ✅ **Quy ước giờ sinh (mục 1.3)** — `tools/hd_time.py`, mọi entry point dùng chung, hiển thị giờ khai báo | BE | xong | 14 test `test_time_convention.py` xanh |
| P0-5 | **PDF theo chuẩn (B5):** `render_pdf(document)` dùng `ReportDocument` (thông tin + BodyGraph + sections theo content_mode), font DejaVu hỗ trợ tiếng Việt; giữ `build_pdf` cũ cho CLI | BE | 2d | PDF khớp nội dung Markdown; test snapshot |
| P0-6 | **DOCX (B6):** `render_docx(document)` bằng `python-docx` (tiêu đề, bảng thông tin, ảnh BodyGraph PNG, sections) | BE | 1,5d | Mở được trong Word/Google Docs, đúng dấu tiếng Việt |
| P0-7 | Worker arq: job `llm_edit`, `render_pdf`, `render_docx`; bảng `jobs`; retry + timeout | BE | 1,5d | Job LLM chạy nền, fallback template khi lỗi |
| P0-8 | CORS whitelist theo env (B10), rate limit (Redis) cho `/auth` và `/reports` | BE | 0,5d | Không còn `*` + credentials |
| P0-10 | Lưu artifact trên ổ đĩa VPS + endpoint tải có token ký tên (D5) | BE | 0,5d | Link hết hạn sau 5 phút |
| P0-9 | `GET /catalog` (B9) + OpenAPI v1 ổn định → sinh `web/src/api/types.ts` | BE | 0,5d | Frontend import type không lỗi |

### P1 — Admin MVP (tuần 3–5)

| Mã | Việc | Ai | Ước lượng | Hoàn thành khi |
| --- | --- | --- | --- | --- |
| P1-1 | Khung `web/` (Next.js, Tailwind, shadcn/ui, TanStack Query), layout, proxy `/api`, design tokens = theme tự sinh (D10) | FE | 2d | `npm run build` + lint + typecheck xanh trên máy dev |
| P1-2 | Đăng nhập, guard theo vai trò, trang 403/404 | FE | 1d | E2E đăng nhập/đăng xuất |
| P1-3 | API: CRUD `clients`, `reports` (template đồng bộ), `preview` | BE | 3d | Test contract |
| P1-4 | Màn Khách hàng: danh sách, hồ sơ, form ngày/giờ sinh (giờ Việt Nam) | FE | 2d | Hiển thị đúng giờ đã khai báo ở mọi màn |
| P1-5 | **Wizard tạo báo cáo 4 bước** + preview tức thì | FE | 4d | Nghiệm thu mục 7.1 |
| P1-6 | Xem báo cáo: tab Nội dung / Infographic / BodyGraph / Tệp xuất (MD, Infographic) | FE | 3d | Nghiệm thu mục 7.2 (trừ Lịch sử) |
| P1-7 | Tổng quan + nhật ký thao tác cơ bản | BE+FE | 1,5d | Ghi nhận tạo/xem/xuất |

**Mốc M1 (cuối tuần 5):** coach nội bộ tạo, xem, tải báo cáo template + infographic.

### P2 — Biên tập, LLM, đủ định dạng (tuần 6–7)

| Mã | Việc | Ai | Ước lượng |
| --- | --- | --- | --- |
| P2-1 | API sửa section + revision + restore + regenerate (B8) | BE | 2d |
| P2-2 | API LLM edit (cả báo cáo / từng section) + SSE tiến trình | BE | 1,5d |
| P2-3 | Trình biên tập (mục 7.3): editor, dữ liệu nguồn, cảnh báo, autosave | FE | 4d |
| P2-4 | "AI biên tập phần này" + diff + chấp nhận/bỏ | FE | 2d |
| P2-5 | Tab Tệp xuất: PDF/DOCX qua job, trạng thái, tải lại | FE | 1d |
| P2-6 | Cấu hình LLM (admin) + kiểm tra kết nối; key mã hóa (Fernet/KMS) | BE+FE | 1,5d |

**Mốc M2 (cuối tuần 7):** đủ 2 content mode, 4 định dạng xuất, biên tập có kiểm soát.

### P3 — Chia sẻ cho khách hàng (tuần 8)

| Mã | Việc | Ai | Ước lượng |
| --- | --- | --- | --- |
| P3-1 | Share link: tạo/thu hồi/hết hạn, định dạng được phép, đếm lượt xem | BE | 1,5d |
| P3-2 | Trang `/r/[token]` SSR, mobile-first, theme tự sinh, `noindex` | FE | 2d |
| P3-3 | ~~Gửi email kèm link (SMTP)~~ — **bỏ** theo quyết định chủ dự án | — | 0 |

> Màn **Thương hiệu** (logo/màu tổ chức áp vào Infographic/PDF/DOCX) chuyển vào **backlog sau go-live** theo D10.
> Kiến trúc đã sẵn: mọi renderer đọc `organizations.theme`, nên thay template mẫu bằng bộ nhận diện thật chỉ là cập nhật cấu hình.

### P4 — Hardening & go-live (tuần 9)

| Mã | Việc | Ai | Ước lượng |
| --- | --- | --- | --- |
| P4-1 | Bảo mật: header (CSP, HSTS), kiểm tra IDOR theo org/owner, khóa đăng nhập sai nhiều lần, quét dependency | BE | 1,5d |
| P4-2 | Giám sát: log JSON có request_id, `pm2-logrotate`, Sentry (tùy chọn), `pm2 monit` | BE | 0,5d |
| P4-3 | Sao lưu Postgres hằng ngày (`pg_dump` + cron, giữ 14 bản) + thử khôi phục; dọn artifact cũ | BE | 0,5d |
| P4-4 | E2E Playwright luồng chính chạy trên máy dev trước mỗi lần deploy + kiểm thử tải nhẹ | FE | 1,5d |
| P4-5 | Triển khai production: Nginx + certbot, `pm2 startup` + `pm2 save`, `deploy/deploy.sh`, runbook | BE | 1d |
| P4-6 | Chính sách dữ liệu: đồng ý xử lý dữ liệu, xuất/xóa dữ liệu theo yêu cầu | BE+FE | 1d |

**Mốc M3 (cuối tuần 9):** go-live.

---

## 9. Cấu trúc thư mục dự kiến

```text
human_design/
├── backend/
│   ├── reporting/            # GIỮ NGUYÊN — lõi nghiệp vụ thuần
│   │   └── renderers/        # MỚI: pdf.py, docx.py (render từ ReportDocument)
│   └── api/                  # MỚI — ứng dụng FastAPI cho frontend
│       ├── main.py  settings.py  deps.py  security.py
│       ├── models/  schemas/  routers/  services/
│       ├── workers/          # arq jobs: llm_edit, render_pdf, render_docx
│       └── migrations/       # Alembic
├── web/                      # MỚI — Next.js
│   ├── src/app/(admin)/…  src/app/r/[token]/…
│   ├── src/api/types.ts      # sinh từ OpenAPI — không sửa tay
│   └── src/components/…
├── mcp/                      # GIỮ NGUYÊN — MCP stdio + ChatGPT bridge
├── deploy/                   # MỚI — ecosystem.config.cjs (pm2), nginx.conf mẫu, deploy.sh, check.sh, backup.sh
└── tests/                    # + tests/api/ (pytest) ; web/e2e/ (Playwright)
```

---

## 10. Triển khai & vận hành (pm2 trên VPS riêng — đã chốt)

**Không dùng Docker, không dùng CI.** Mọi tiến trình chạy bằng **pm2**; kiểm thử chạy trên máy dev
bằng `deploy/check.sh` trước khi deploy.

### 10.1 Thành phần trên VPS

| Thành phần | Cách chạy | Cổng |
| --- | --- | --- |
| Nginx + certbot | systemd (apt) — TLS, reverse proxy, gzip, giới hạn body | 80/443 |
| `hd-web` (Next.js) | pm2: `npm run start` | 127.0.0.1:3000 |
| `hd-api` (FastAPI `/api/v1`) | pm2: `uvicorn backend.api.main:app --workers 2` | 127.0.0.1:8001 |
| `hd-worker` (arq) | pm2: `arq backend.api.workers.WorkerSettings` | — |
| `hd-gpt-bridge` (tùy chọn) | pm2: `uvicorn openapi_server:app` (ChatGPT Actions hiện có) | 127.0.0.1:8000 |
| PostgreSQL 16, Redis 7 | systemd (apt), chỉ lắng nghe localhost | 5432 / 6379 |

Nginx: `app.<domain>` → `hd-web`; `hd-web` proxy `/api/*` → `hd-api` (trình duyệt chỉ thấy một origin).

### 10.2 Cấu hình pm2 mẫu (`deploy/ecosystem.config.cjs`)

```js
// Biến môi trường do chính ứng dụng đọc từ /srv/human_design/.env (pydantic-settings / python-dotenv),
// nên cấu hình pm2 không phụ thuộc phiên bản pm2.
module.exports = {
  apps: [
    { name: "hd-api", cwd: "/srv/human_design",
      script: ".venv/bin/uvicorn", args: "backend.api.main:app --host 127.0.0.1 --port 8001 --workers 2",
      interpreter: "none", max_memory_restart: "600M" },
    { name: "hd-worker", cwd: "/srv/human_design",
      script: ".venv/bin/arq", args: "backend.api.workers.WorkerSettings",
      interpreter: "none", max_memory_restart: "600M" },
    { name: "hd-web", cwd: "/srv/human_design/web",
      script: "npm", args: "run start -- -p 3000 -H 127.0.0.1",
      interpreter: "none", env: { NODE_ENV: "production", API_INTERNAL_URL: "http://127.0.0.1:8001" } },
    { name: "hd-gpt-bridge", cwd: "/srv/human_design/mcp",
      script: "../.venv/bin/uvicorn", args: "openapi_server:app --host 127.0.0.1 --port 8000",
      interpreter: "none" },
  ],
};
```

### 10.3 Quy trình deploy (`deploy/deploy.sh`)

```bash
set -euo pipefail
cd /srv/human_design
git pull --ff-only origin main
.venv/bin/pip install -q -r requirements.txt
.venv/bin/alembic upgrade head
(cd web && npm ci && npm run build)
pm2 reload deploy/ecosystem.config.cjs --update-env
pm2 save
```

Lần đầu: `pm2 startup` (tự khởi động cùng VPS), `pm2 install pm2-logrotate`.
Hoàn tác: `git checkout <tag trước>` rồi chạy lại `deploy.sh` (migration luôn viết kèm `downgrade`).

### 10.4 Biến môi trường (`/srv/human_design/.env`, quyền 600)

`DATABASE_URL`, `REDIS_URL`, `ARTIFACT_DIR`, `SESSION_SECRET`, `ENCRYPTION_KEY` (mã hóa key LLM),
`CORS_ORIGINS`, `PUBLIC_BASE_URL`, `SMTP_*`, `SENTRY_DSN` (tùy chọn) và các `HD_LLM_*` hiện có (làm giá trị mặc định).

### 10.5 Chi phí hạ tầng ước tính

1 VPS 4 vCPU / 8 GB RAM là đủ cho giai đoạn đầu (tạo báo cáo chỉ 5–8 ms; PDF ~0,4 giây). Chi phí LLM
tính theo lượt, với `gpt-4o-mini` một báo cáo deep_core rất thấp — đo thực tế ở P2.

---

## 11. Dữ liệu cá nhân & tuân thủ

Ngày/giờ/nơi sinh gắn với họ tên là **dữ liệu cá nhân**. Khung pháp lý hiện hành: **Luật Bảo vệ
dữ liệu cá nhân 2025** (hiệu lực 01/01/2026) và **Nghị định 356/2025/NĐ-CP** hướng dẫn thi hành
(hiệu lực 01/01/2026) — **cần luật sư xác nhận nghĩa vụ cụ thể** (đồng ý, thông báo, nhân sự bảo
vệ dữ liệu, chuyển dữ liệu ra nước ngoài khi dùng LLM quốc tế). Kỹ thuật chuẩn bị sẵn:

- Ghi nhận **đồng ý** (`clients.consent_at`) trước khi lưu; hiển thị mục đích xử lý.
- **Xóa dữ liệu theo yêu cầu** (`POST /clients/{id}/erase`: xóa hồ sơ, báo cáo, artifact, thu hồi link).
- Mã hóa khi truyền (TLS) và khi lưu với bí mật (key LLM); sao lưu mã hóa.
- Nhật ký truy cập dữ liệu khách hàng (`audit_logs`).
- Khi dùng LLM bên ngoài: **chỉ gửi dữ liệu chart + tên hiển thị**; cân nhắc tùy chọn ẩn danh
  tên khách trong brief (thêm cờ ở P2).

---

## 12. Chiến lược kiểm thử

| Tầng | Công cụ | Phạm vi |
| --- | --- | --- |
| Lõi nghiệp vụ | pytest (48 test hiện có) | Giữ xanh; thêm test renderer PDF/DOCX |
| API v1 | pytest + httpx | Contract, phân quyền (ma trận vai trò × endpoint), IDOR, job |
| Contract FE/BE | OpenAPI snapshot trong `deploy/check.sh` | Phát hiện thay đổi phá vỡ type |
| Frontend | Vitest + Testing Library | Wizard, editor, cảnh báo |
| E2E | Playwright | Đăng nhập → tạo khách → tạo báo cáo → sửa → xuất → chia sẻ → mở link |
| Hình ảnh | Playwright screenshot | Infographic & trang chia sẻ (desktop + mobile) |
| Giờ sinh | pytest (`test_time_convention.py`) | Công thức −7 giờ, không áp lịch sử, mọi entry point cùng kết quả, hiển thị chỉ giờ khai báo |

---

## 13. Rủi ro & giảm thiểu

| Rủi ro | Mức | Giảm thiểu |
| --- | --- | --- |
| Người dùng khai báo giờ không theo chuẩn +07:00 (VD giờ đồng hồ miền Nam trước 1975 là UTC+8) | Thấp | Đã chốt: tính theo giờ khai báo; nếu cần, coach có thể truyền offset cố định khác qua API; ghi chú trong tài liệu hướng dẫn nhập liệu |
| Không có CI → lỗi lọt lên production | Trung bình | `deploy/check.sh` (pytest + build + typecheck) bắt buộc chạy trước `deploy.sh`; gắn tag git mỗi lần deploy để hoàn tác nhanh |
| LLM chậm/lỗi/đắt | Trung bình | Job nền, fallback template (đã có), giới hạn lượt theo tổ chức, cache theo phiên bản |
| LLM làm mất/sai sự kiện kỹ thuật | Trung bình | Validator đã có + diff bắt buộc duyệt trước khi chấp nhận |
| Lệch nội dung giữa các định dạng | Trung bình | Mọi renderer nhận **cùng một** `ReportDocument` (P0-5, P0-6) |
| Lộ dữ liệu khách hàng | **Cao** | RBAC theo org/owner, test IDOR, token chia sẻ băm + hết hạn, audit log |
| Phạm vi phình (billing, app mobile) | Trung bình | Giữ ngoài phạm vi; ghi vào backlog sau M3 |

---

## 14. Việc cần làm ngay (Sprint 0 — 3 ngày)

1. ✅ Đã chốt: giờ Việt Nam (D6b), pm2/VPS (D8), template tự sinh (D10). Các quyết định còn lại theo đề xuất mặc định.
2. ✅ **P0-4 quy ước giờ sinh** — đã xong, áp dụng cho mọi entry point hiện có.
3. ✅ Khung `backend/api/` + `deploy/ecosystem.config.cjs` + `deploy/check.sh` (P0-1).
4. Chuẩn bị VPS: Nginx, certbot, PostgreSQL 16, Redis 7, Node LTS + pm2, Python 3.11 + venv.
5. Wireframe 3 màn **Wizard**, **Xem báo cáo**, **Trình biên tập** (mục 7.1–7.3).

---

## Phụ lục A — Ánh xạ màn hình ↔ API ↔ module lõi

| Màn hình | API v1 | Module lõi dùng lại |
| --- | --- | --- |
| Wizard bước 1 | `/clients` | `contract.SubjectInput` (validator), `tools/hd_time.py` |
| Wizard bước 2–3 | `/catalog` | `catalog.py`, `contract` enums |
| Wizard bước 4 | `/reports/preview`, `POST /reports` | `service.generate_report`, `infographic` |
| Xem báo cáo | `/reports/{id}`, `/reports/{id}/artifacts/*` | `ReportDocument.to_markdown`, `export`, `infographic` |
| Trình biên tập | `PATCH …/sections/{id}`, `…/llm-edit`, `…/revisions` | `llm_editor.merge_llm_draft`, `validate_llm_draft`, `llm_client` |
| Cấu hình LLM | `/settings/llm`, `/settings/llm/test` | `llm_client.LLMConfig`, `call_llm` |
| Trang chia sẻ | `/public/r/{token}` | `infographic.render_infographic_html` |
