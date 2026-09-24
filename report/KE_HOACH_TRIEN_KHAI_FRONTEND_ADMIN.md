# Kế hoạch triển khai Frontend / Admin — Human Design Analyzer

> Phiên bản 1.0 · 2026-09-24 · Trạng thái: **đề xuất, chờ chốt các quyết định ở mục 3**
> Nền tảng hiện có: branch `arena/01a0d215-human-design` @ `240d670` — 40 MCP tools, 44 REST routes, 48 test xanh.

---

## 0. Tóm tắt

Backend đã có đủ **lõi nghiệp vụ**: tính chart, báo cáo theo chuẩn (thông tin người được
phân tích + BodyGraph + nội dung template/LLM), infographic HTML, PDF, MCP/REST. Cái còn thiếu
để có sản phẩm Admin dùng được là **lớp ứng dụng**: lưu trữ, đăng nhập/phân quyền, hàng đợi
job cho LLM, API v1 riêng cho frontend, và chính giao diện.

Đề xuất triển khai **5 giai đoạn trong khoảng 9–10 tuần** với đội 1 Backend + 1 Frontend
(+ designer bán thời gian):

| Giai đoạn | Nội dung | Thời lượng |
| --- | --- | --- |
| **P0** | Nền móng backend: DB, API v1, auth, job queue, timezone, PDF theo chuẩn | 2 tuần |
| **P1** | Admin MVP: đăng nhập, khách hàng, wizard tạo báo cáo, xem/tải báo cáo | 3 tuần |
| **P2** | Trình biên tập báo cáo + LLM + đủ định dạng xuất (MD/PDF/DOCX/Infographic) | 2 tuần |
| **P3** | Chia sẻ cho khách hàng (link bảo mật / cổng khách hàng) | 1,5 tuần |
| **P4** | Hardening, bảo mật, quan sát hệ thống, triển khai production | 1 tuần |

Mốc quan trọng: **cuối P1 (tuần 5)** coach đã dùng được nội bộ với chế độ template;
**cuối P4 (tuần 10)** sẵn sàng go-live.

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
| B7 | **Múi giờ lịch sử** | Nhập offset cố định `+07:00` | **Sai chart** với người sinh ở nơi/thời kỳ có offset khác (VD miền Nam trước 1975 dùng UTC+8, giờ mùa hè ở nước ngoài) |
| B8 | **Sửa từng phần + kiểm tra lại** | Chỉ merge draft LLM | Coach sửa tay có thể làm mất sự kiện kỹ thuật mà không ai biết |
| B9 | **Catalog cho UI** | Nằm trong `catalog.py`, chưa có endpoint | Frontend phải hard-code tier/domain/section |
| B10 | **CORS** | `allow_origins=["*"]` + `allow_credentials=True` | Không hợp lệ cho app có cookie đăng nhập; rủi ro bảo mật |
| B11 | **Đóng gói/triển khai** | Không có Dockerfile, không có cấu hình môi trường | Không triển khai lặp lại được |

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
| D5 | Lưu file | **S3-compatible** (Cloudflare R2 / MinIO) | Rẻ, link ký tên có hạn | Ổ đĩa local (không scale) |
| D6 | Đăng nhập | **Email + mật khẩu, session cookie httpOnly do backend cấp**; magic link cho khách (P3) | Không phụ thuộc bên thứ ba, tuân thủ dữ liệu trong nước | Clerk/Auth0/Supabase Auth |
| D7 | Job nền | **Redis + arq** (async, nhẹ) | Hợp FastAPI async; chỉ cần cho LLM/PDF/DOCX | Celery (nặng hơn), RQ |
| D8 | Hosting | **1 VPS tại Việt Nam, Docker Compose** (web, api, worker, postgres, redis) | Dữ liệu cá nhân lưu trong nước, chi phí thấp | Vercel + Railway/Render |
| D9 | Nhà cung cấp LLM | **Endpoint OpenAI-compatible cấu hình qua Admin** (mặc định `gpt-4o-mini`) | Code đã hỗ trợ `HD_LLM_BASE_URL` | Cố định một nhà cung cấp |
| D10 | Thương hiệu trên báo cáo | **Logo + tên + màu của tổ chức**, cấu hình ở Settings | Coach cần báo cáo mang thương hiệu riêng | Không white-label |

---

## 4. Kiến trúc đề xuất

```text
                         ┌──────────────────────────────┐
  Trình duyệt ──HTTPS──▶ │  web  (Next.js)               │
  (Admin/Coach/Khách)    │  - UI Admin/Coach             │
                         │  - Trang chia sẻ /r/[token]   │
                         │  - /api/* → proxy tới api     │  ← cùng origin, không lộ localhost
                         └──────────────┬───────────────┘
                                        │ HTTP nội bộ
                         ┌──────────────▼───────────────┐
                         │  api  (FastAPI /api/v1)       │
                         │  backend/api/                 │──▶ PostgreSQL (users, clients, reports…)
                         │  auth · RBAC · CRUD · catalog │──▶ S3/R2 (pdf, docx, html, svg)
                         │  gọi backend/reporting/*      │──▶ Redis (queue, rate limit)
                         └──────────────┬───────────────┘
                                        │ enqueue
                         ┌──────────────▼───────────────┐
                         │  worker (arq)                 │
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
| `organizations` | id, name, brand_logo_key, brand_color, llm_settings (JSONB, key mã hóa) | Chuẩn bị white-label (D10) |
| `users` | id, org_id, email, password_hash, role (`admin`/`coach`), is_active, last_login_at | Argon2 hash |
| `clients` | id, org_id, owner_user_id, full_name, email, phone, birth_date, birth_time, birth_time_known, birth_place, lat, lng, iana_tz, utc_offset_resolved, notes, consent_at, deleted_at | Dữ liệu cá nhân — xóa mềm + xóa cứng theo yêu cầu |
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
| Địa lý | `GET /geo/search?q=` → địa điểm + lat/lng; `POST /geo/resolve` {place/lat,lng, date, time} → `iana_tz`, `utc_offset` tại thời điểm sinh | ✔ | **mới (B7)** |
| Khách hàng | `GET/POST /clients`, `GET/PATCH/DELETE /clients/{id}`, `POST /clients/{id}/erase` | ✔ | — |
| Xem trước | `POST /reports/preview` → document + markdown + infographic (không lưu) | ✔ ≤ 50 ms | `service.generate_report` |
| Báo cáo | `POST /reports` (template → `ready` ngay; llm → `generating` + job_id), `GET /reports?client_id=&status=`, `GET /reports/{id}` | ✔ / job | `service`, `orchestrator` |
| Biên tập | `PATCH /reports/{id}/sections/{section_id}` {markdown} → lưu revision + **warnings kiểm tra sự kiện** | ✔ | `merge_llm_draft` (B8) |
| LLM | `POST /reports/{id}/llm-edit` {section_ids?} → job; `GET /reports/{id}/llm-brief` (cho coach xem prompt) | job | `llm_editor`, `llm_client` |
| Phiên bản | `GET /reports/{id}/revisions`, `POST /reports/{id}/revisions/{v}/restore`, `POST /reports/{id}/regenerate` | ✔ | — |
| Xuất file | `POST /reports/{id}/artifacts` {format} → nhanh thì trả link, chậm thì job; `GET /reports/{id}/artifacts/{format}` → link tải ký tên (5 phút) | ✔ / job | `export`, `infographic`, PDF/DOCX mới |
| Job | `GET /jobs/{id}` (poll) hoặc `GET /jobs/{id}/events` (SSE) | ✔ | — |
| Chia sẻ | `POST /reports/{id}/share` → token (hiện 1 lần), `DELETE /share/{id}`; công khai: `GET /public/r/{token}` | ✔ | `infographic` |
| Admin | `GET/POST/PATCH /users`, `GET/PUT /settings/llm` (+ `POST /settings/llm/test`), `GET/PUT /settings/brand`, `GET /audit` | ✔ | — |

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
/settings/brand           Thương hiệu             (admin)
/settings/users           Người dùng & vai trò    (admin)
/audit                    Nhật ký hệ thống        (admin)
/r/[token]                Trang báo cáo chia sẻ cho khách (công khai, SSR)
```

### 7.1 Wizard tạo báo cáo — màn hình quan trọng nhất

| Bước | Nội dung | Chi tiết UX |
| --- | --- | --- |
| 1. Người được phân tích | Chọn khách có sẵn hoặc nhập mới: họ tên, ngày sinh, giờ sinh, nơi sinh | Ô nơi sinh có gợi ý địa điểm → tự điền múi giờ lịch sử (hiển thị "UTC+08:00 tại thời điểm sinh"); công tắc "Không rõ giờ sinh" → cảnh báo các phần phụ thuộc giờ |
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
| Thương hiệu | Logo, tên, màu chủ đạo → áp dụng cho PDF/DOCX/Infographic | Xem trước trực tiếp |
| Người dùng | Mời qua email, đổi vai trò, khóa | Chỉ admin |
| Nhật ký | Lọc theo người/hành động/thời gian | Ghi nhận xem/xuất/chia sẻ/xóa |
| Trang chia sẻ `/r/[token]` | Infographic + nút tải định dạng được phép, thương hiệu tổ chức | Token hết hạn/thu hồi → trang 410; không index (`noindex`) |

### 7.5 Nguyên tắc giao diện

- Toàn bộ nhãn tiếng Việt, **thuật ngữ song ngữ** lấy từ bảng chuẩn (`hd_language.py`) — endpoint
  `GET /catalog` trả kèm nhãn để frontend không tự dịch.
- Màu nhận diện Type dùng chung với infographic (`TYPE_ACCENT` trong `infographic.py`).
- Responsive: Admin tối ưu desktop ≥ 1280px, dùng được trên tablet; trang chia sẻ tối ưu **mobile trước**.
- Accessibility: WCAG 2.1 AA (tương phản, focus, nhãn form).

---

## 8. Lộ trình chi tiết

Ước lượng theo ngày công (d). BE = Backend, FE = Frontend.

### P0 — Nền móng backend (tuần 1–2)

| Mã | Việc | Ai | Ước lượng | Hoàn thành khi |
| --- | --- | --- | --- | --- |
| P0-1 | Khung `backend/api/` (FastAPI, settings qua env, `/api/v1/health`), Dockerfile, `docker-compose.yml` (api, worker, postgres, redis, minio) | BE | 2d | `docker compose up` chạy được, CI xanh |
| P0-2 | SQLAlchemy models + Alembic migration theo mục 5 | BE | 2d | Migration up/down sạch |
| P0-3 | Auth: login/logout/me, Argon2, session cookie httpOnly + CSRF, RBAC dependency | BE | 2d | Test phân quyền admin/coach/ẩn danh |
| P0-4 | **Timezone lịch sử (B7):** `timezonefinder` + `zoneinfo` + geocoding (Nominatim/OpenCage) → `/geo/search`, `/geo/resolve`; lưu `iana_tz` + offset đã giải | BE | 2d | Test: TP.HCM 1970 → +08:00, Hà Nội 1990 → +07:00, New York mùa hè → −04:00 |
| P0-5 | **PDF theo chuẩn (B5):** `render_pdf(document)` dùng `ReportDocument` (thông tin + BodyGraph + sections theo content_mode), font DejaVu hỗ trợ tiếng Việt; giữ `build_pdf` cũ cho CLI | BE | 2d | PDF khớp nội dung Markdown; test snapshot |
| P0-6 | **DOCX (B6):** `render_docx(document)` bằng `python-docx` (tiêu đề, bảng thông tin, ảnh BodyGraph PNG, sections) | BE | 1,5d | Mở được trong Word/Google Docs, đúng dấu tiếng Việt |
| P0-7 | Worker arq: job `llm_edit`, `render_pdf`, `render_docx`; bảng `jobs`; retry + timeout | BE | 1,5d | Job LLM chạy nền, fallback template khi lỗi |
| P0-8 | CORS whitelist theo env (B10), rate limit (Redis) cho `/auth` và `/reports` | BE | 0,5d | Không còn `*` + credentials |
| P0-9 | `GET /catalog` (B9) + OpenAPI v1 ổn định → sinh `web/src/api/types.ts` | BE | 0,5d | Frontend import type không lỗi |

### P1 — Admin MVP (tuần 3–5)

| Mã | Việc | Ai | Ước lượng | Hoàn thành khi |
| --- | --- | --- | --- | --- |
| P1-1 | Khung `web/` (Next.js, Tailwind, shadcn/ui, TanStack Query), layout, proxy `/api`, design tokens | FE | 2d | Build/lint/typecheck xanh |
| P1-2 | Đăng nhập, guard theo vai trò, trang 403/404 | FE | 1d | E2E đăng nhập/đăng xuất |
| P1-3 | API: CRUD `clients`, `reports` (template đồng bộ), `preview` | BE | 3d | Test contract |
| P1-4 | Màn Khách hàng: danh sách, hồ sơ, form có gợi ý địa điểm + múi giờ | FE | 3d | Tạo khách với nơi sinh → offset hiển thị đúng |
| P1-5 | **Wizard tạo báo cáo 4 bước** + preview tức thì | FE | 4d | Nghiệm thu mục 7.1 |
| P1-6 | Xem báo cáo: tab Nội dung / Infographic / BodyGraph / Tệp xuất (MD, Infographic) | FE | 3d | Nghiệm thu mục 7.2 (trừ Lịch sử) |
| P1-7 | Tổng quan + nhật ký thao tác cơ bản | BE+FE | 1,5d | Ghi nhận tạo/xem/xuất |
| P1-8 | Lưu artifact lên S3/MinIO, link tải ký tên | BE | 1d | Link hết hạn sau 5 phút |

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

### P3 — Chia sẻ cho khách hàng (tuần 8 – giữa tuần 9)

| Mã | Việc | Ai | Ước lượng |
| --- | --- | --- | --- |
| P3-1 | Share link: tạo/thu hồi/hết hạn, định dạng được phép, đếm lượt xem | BE | 1,5d |
| P3-2 | Trang `/r/[token]` SSR, mobile-first, thương hiệu tổ chức, `noindex` | FE | 2d |
| P3-3 | Gửi email kèm link (SMTP/SES) + mẫu email tiếng Việt | BE | 1d |
| P3-4 | Thương hiệu (logo/màu) áp dụng vào Infographic/PDF/DOCX | BE+FE | 2d |

### P4 — Hardening & go-live (nửa sau tuần 9 – tuần 10)

| Mã | Việc | Ai | Ước lượng |
| --- | --- | --- | --- |
| P4-1 | Bảo mật: header (CSP, HSTS), kiểm tra IDOR theo org/owner, khóa đăng nhập sai nhiều lần, quét dependency | BE | 1,5d |
| P4-2 | Quan sát: log JSON có request_id, Sentry (web + api + worker), metrics job | BE | 1d |
| P4-3 | Sao lưu Postgres hằng ngày + thử khôi phục; lưu artifact có vòng đời | BE | 0,5d |
| P4-4 | E2E Playwright luồng chính + kiểm thử tải nhẹ (50 người dùng đồng thời) | FE | 1,5d |
| P4-5 | Triển khai production (VPS, Caddy/Traefik TLS), runbook vận hành | BE | 1d |
| P4-6 | Chính sách dữ liệu: đồng ý xử lý dữ liệu, xuất/xóa dữ liệu theo yêu cầu | BE+FE | 1d |

**Mốc M3 (cuối tuần 10):** go-live.

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
├── deploy/                   # MỚI — docker-compose.prod.yml, Caddyfile, backup.sh
└── tests/                    # + tests/api/ (pytest) ; web/e2e/ (Playwright)
```

---

## 10. Triển khai & vận hành

**Biến môi trường chính:** `DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT`/`S3_BUCKET`/`S3_KEY`/`S3_SECRET`,
`SESSION_SECRET`, `ENCRYPTION_KEY` (mã hóa key LLM), `CORS_ORIGINS`, `PUBLIC_BASE_URL`,
`SMTP_*`, `GEOCODER_API_KEY`, `SENTRY_DSN`, và các `HD_LLM_*` hiện có (làm giá trị mặc định).

**Môi trường:** `local` (docker compose) → `staging` (bản sao production, dữ liệu giả) → `production`.
CI (GitHub Actions): lint + typecheck + pytest + build web + Playwright trên staging; deploy khi merge `main`.

**Chi phí hạ tầng ước tính (giai đoạn đầu):** 1 VPS 4 vCPU/8 GB (~15–25 USD/tháng) + R2 (gần như
miễn phí ở quy mô nhỏ) + chi phí LLM theo lượt (với `gpt-4o-mini`, một báo cáo deep_core cỡ vài
nghìn token — rất thấp; cần đo thực tế ở P2).

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
| Contract FE/BE | OpenAPI snapshot trong CI | Phát hiện thay đổi phá vỡ type |
| Frontend | Vitest + Testing Library | Wizard, editor, cảnh báo |
| E2E | Playwright | Đăng nhập → tạo khách → tạo báo cáo → sửa → xuất → chia sẻ → mở link |
| Hình ảnh | Playwright screenshot | Infographic & trang chia sẻ (desktop + mobile) |
| Múi giờ | pytest bảng dữ liệu | Các mốc lịch sử VN + DST quốc tế |

---

## 13. Rủi ro & giảm thiểu

| Rủi ro | Mức | Giảm thiểu |
| --- | --- | --- |
| Sai múi giờ lịch sử → sai chart | **Cao** | P0-4 làm đầu tiên, bộ test mốc lịch sử, luôn hiển thị offset đã dùng để coach xác nhận |
| LLM chậm/lỗi/đắt | Trung bình | Job nền, fallback template (đã có), giới hạn lượt theo tổ chức, cache theo phiên bản |
| LLM làm mất/sai sự kiện kỹ thuật | Trung bình | Validator đã có + diff bắt buộc duyệt trước khi chấp nhận |
| Lệch nội dung giữa các định dạng | Trung bình | Mọi renderer nhận **cùng một** `ReportDocument` (P0-5, P0-6) |
| Lộ dữ liệu khách hàng | **Cao** | RBAC theo org/owner, test IDOR, token chia sẻ băm + hết hạn, audit log |
| Phạm vi phình (billing, app mobile) | Trung bình | Giữ ngoài phạm vi; ghi vào backlog sau M3 |

---

## 14. Việc cần làm ngay (Sprint 0 — 3 ngày)

1. Chốt các quyết định **D1–D10** (mục 3).
2. Tạo khung `backend/api/` + `docker-compose.yml` + CI (P0-1).
3. Làm **P0-4 múi giờ lịch sử** trước tiên — rủi ro cao nhất về độ chính xác.
4. Designer: wireframe 3 màn **Wizard**, **Xem báo cáo**, **Trình biên tập** (mục 7.1–7.3).
5. Tạo backlog issue trên GitHub theo mã việc P0-x … P4-x.

---

## Phụ lục A — Ánh xạ màn hình ↔ API ↔ module lõi

| Màn hình | API v1 | Module lõi dùng lại |
| --- | --- | --- |
| Wizard bước 1 | `/geo/search`, `/geo/resolve`, `/clients` | `contract.SubjectInput` (validator) |
| Wizard bước 2–3 | `/catalog` | `catalog.py`, `contract` enums |
| Wizard bước 4 | `/reports/preview`, `POST /reports` | `service.generate_report`, `infographic` |
| Xem báo cáo | `/reports/{id}`, `/reports/{id}/artifacts/*` | `ReportDocument.to_markdown`, `export`, `infographic` |
| Trình biên tập | `PATCH …/sections/{id}`, `…/llm-edit`, `…/revisions` | `llm_editor.merge_llm_draft`, `validate_llm_draft`, `llm_client` |
| Cấu hình LLM | `/settings/llm`, `/settings/llm/test` | `llm_client.LLMConfig`, `call_llm` |
| Trang chia sẻ | `/public/r/{token}` | `infographic.render_infographic_html` |
