# BÁO CÁO AUDIT BẢO MẬT — Human Design Analyzer v3.0

- **Ngày:** 2026-09-27
- **Phạm vi:** toàn bộ repository `cuongtv24h/human_design` — backend FastAPI (`backend/api`), frontend Next.js (`web`), MCP server (`mcp/`), scripts triển khai (`deploy/`), cấu hình nginx, dependencies.
- **Phương pháp:** đọc tĩnh toàn bộ bề mặt tấn công (auth, phân quyền, injection, XSS, CSRF, rate-limit, secrets, deploy), rà soát secret trong lịch sử Git, `npm audit` cho frontend, và **kiểm thử thực tế** trên server dev (uvicorn + SQLite tạm).

---

## 1. Tóm tắt điều hành

| Mức độ | Số lượng | Ghi chú |
|---|---|---|
| 🔴 Cao | 0 | Không phát hiện lỗ hổng critical kiểu RCE/nghịch dữ liệu trắng trợn |
| 🟠 Trung bình | 5 | Chủ yếu: token phiên trong URL, giả mạo IP vượt rate-limit, thiếu security header, GPT-bridge không auth, rate-limit in-memory với 2 worker |
| 🟡 Thấp | 6 | |
| 🔵 Thông tin | 5 | Khuyến nghị phòng ngừa |

**Điểm tổng thể: kiến trúc bảo mật tốt hơn mặt bằng chung** — Argon2, session token chỉ lưu hash, CSRF bằng header, signed link HMAC, multi-tenant scoping nhất quán, escape HTML/SVG/PDF, không có `eval/subprocess/pickle`, không commit secret. Các vấn đề chủ yếu là **hardening** và **vận hành** (log, header, rate-limit), không phải lỗi logic nghiệp vụ trầm trọng.

---

## 2. Những điểm đã kiểm chứng là TỐT ✅

1. **Mật khẩu:** Argon2id qua `argon2-cffi` (`backend/api/security.py`), `min_length=8` ở mọi điểm vào.
2. **Phiên đăng nhập:** token ngẫu nhiên 256-bit, DB chỉ lưu `SHA-256` (`new_session_token`/`hash_token`); cookie `HttpOnly` + `SameSite=lax`; ở production `Secure=True` (đã xác minh qua `Settings.from_env()` khi `HD_ENV=production`); logout xóa session record; đổi mật khẩu logout mọi phiên khác.
3. **CSRF:** mọi request `POST/PATCH/PUT/DELETE` dưới `/api/v1` bắt buộc header `X-HD-Request` — **đã kiểm thử thực tế: 403 khi thiếu header**, kể cả khi đính kèm token hợp lệ (form cross-site không thể thêm header custom → bị chặn ngay khi CORS không mở).
4. **Phân quyền nhiều tầng (multi-tenant):** mọi query dữ liệu đều lọc `org_id` + `owner_user_id` (`visible_clients`, `visible_reports`, `get_report_or_404`); endpoint admin dùng `require_admin` hoặc `_admin(user)` (game/leads); templates có luồng duyệt + kiểm tra quyền riêng; `rate_message` kiểm tra session thuộc về user/org.
5. **Link chia sẻ khách (P3):** token chỉ hiện 1 lần, lưu hash SHA-256, có hạn dùng/thu hồi, `formats` giới hạn `Literal["pdf","docx","markdown"]`, trang chia sẻ gắn `noindex` + `Referrer-Policy: no-referrer` + `Cache-Control: no-store`.
6. **Link tải trực tiếp (P0-10):** HMAC-SHA256 có purpose + TTL 5 phút — kiểm thử token rác → `410 Gone`.
7. **Chống XSS:**
   - Frontend: `react-markdown` mặc định **không render HTML thô**; không có `dangerouslySetInnerHTML`/`innerHTML` ở bất kỳ đâu trong `web/`.
   - Infographic HTML: escape bằng `html.escape` + CSP `default-src 'none'`.
   - BodyGraph SVG: `_esc()` escape `&<>` cho mọi chuỗi người dùng (tên, nơi sinh, type…).
   - PDF/DOCX: escape bằng `xml.sax.saxutils`/`html.escape`.
8. **Chống brute-force (ở mức logic):** 5 lỗi mật khẩu / 15 phút / (IP+email) → 429; chat trợ lý giới hạn 60 câu/giờ (đếm trong DB, chống được multi-worker); endpoint công khai (game chart/leads/scores/streak/events) đều có rate-limit theo IP.
9. **Không có sink nguy hiểm:** rà soát toàn bộ `backend/`, `tools/`, `mcp/` — không tìm thấy `subprocess`, `os.system`, `eval`, `exec`, `pickle.load`, `yaml.load` không an toàn.
10. **Secrets:** không có `.env`/key nào trong Git (chỉ `.env.example` với giá trị mẫu); `.env` + `var/` nằm trong `.gitignore`; `var/secret_key` tự sinh với quyền `0600`; `deploy/deploy.sh` từ chối deploy khi thiếu `HD_SECRET_KEY`/`HD_ENV=production`; `backup.sh` chạy `umask 077`.
11. **Khóa API LLM:** mã hóa Fernet bằng server secret, API chỉ trả về mask `••••1234`, audit log ghi `key=set/cleared` chứ không ghi khóa.
12. **SSRF-ish bề mặt Next.js:** chỉ fetch `API_INTERNAL_URL` (server-side, không expose cho browser) và Google Fonts URL cố định ở route OG.
13. **Job recovery nền:** claim nguyên tử `UPDATE … WHERE heartbeat` → không chiếm job lẫn nhau với `--workers 2`.
14. **Dependency Python:** ghim phiên bản chính xác từng package (`==`).
15. **API mặc định không public:** pm2 bind `127.0.0.1:8001`/`127.0.0.1:3000`, CORS rỗng theo mặc định, `AUTO_CREATE_TABLES=false` ở production.

---

## 3. Phát hiện chi tiết

### 🟠 M1 — Session token chấp nhận qua query string `?access_token=` (mọi GET)

- **Vị trí:** `backend/api/deps.py → session_token()` cho phép token từ query trên `GET/HEAD`; `web/lib/api.ts → fileUrl()` nối `&access_token=` vào link file.
- **Bằng chứng thực tế:** `GET /api/v1/auth/me?access_token=<token>` **trả 200** khi không có cookie/header. Log server ngay lập tức ghi:
  ```
  GET /api/v1/auth/me?access_token=4GJ0S1rT-OeePLNmV3l0Pcc8xTDcWuW1Ra-wmzsWrPU HTTP/1.1" 200 OK
  ```
- **Rủi ro:** token phiên rơi vào **access log nginx/uvicorn, lịch sử trình duyệt, header Referer** (Referer-Policy `same-origin` chỉ chặn leak ra origin khác, không chặn log). Bất kỳ ai đọc được log là chiếm được phiên (12h).
- **Khuyến nghị:**
  1. Tốt nhất: chỉ chấp nhận `access_token` cho **các route file cụ thể** (`/reports/{id}/…`), không phải mọi GET.
  2. Thay token phiên bằng **signed URL ngắn hạn** (giống `/files/{token}` 5 phút) cho `<img>`/download trong iframe.
  3. Bắt buộc: thêm log_format redaction truy vấn (`log_format … $uri` không lấy `$query_string`) trong nginx.

### 🟠 M2 — `client_ip()` tin giá trị đầu của `X-Forwarded-For` → bypass hoàn toàn rate-limit & làm giả audit log

- **Vị trí:** `backend/api/deps.py → client_ip()` lấy `x-forwarded-for.split(",")[0]`; nginx example dùng `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for` (nối giá trị client gửi lên **phía trước** IP thật).
- **Bằng chứng thực tế:**
  - Cùng `X-Forwarded-For: 10.9.9.9` → lần sai thứ 6 trả **429** (chốt bảo vệ hoạt động).
  - **Xoay `X-Forwarded-For: 10.1.1.1 … 10.1.1.7` → 7 lần sai liên tiếp toàn 401, không lần nào 429** → attacker brute-force không giới hạn chỉ bằng 1 header.
- **Rủi ro:** đoán mật khẩu hàng loạt; nhật ký audit (`auth.login_failed`, IP…) bị đầu độc → điều tra sai hướng.
- **Khuyến nghị:**
  - Ưu tiên `X-Real-IP` (nginx set từ `$remote_addr`, không spoof được) hoặc lấy **giá trị cuối cùng** của XFF;
  - Thêm giới hạn đăng nhập cấp IP ở tầng nginx (`limit_req_zone … /api/v1/auth/login`) — độc lập với application;
  - Thêm rate-limit **toàn cục theo IP** (không chỉ `ip|email`) để chặn password-spray.

### 🟠 M3 — Rate-limit in-memory + uvicorn `--workers 2`

- **Vị trí:** `_FAILURES` (auth.py), `_HITS` (public.py) là `dict` trong process; `deploy/ecosystem.config.cjs` chạy `--workers 2`.
- **Rủi ro:** (a) counter chia đôi cho 2 worker → ngưỡng thực tế gấp đôi; (b) restart (deploy/pm2 memory) **xóa sạch** lịch sử lỗi; (c) `_HITS` phình bộ nhớ theo số (IP, endpoint) khác nhau — với endpoint công khai, dàn IP ảo có thể gây tốn RAM.
- **Khuyến nghị:** chuyển sang nginx `limit_req` (stateless, trước app) hoặc store chung (Redis/DB) nếu cần chính xác; dọn `_HITS` định kỳ theo tuổi (đã lọc theo window nhưng key không bao giờ bị xóa).

### 🟠 M4 — GPT bridge (`mcp/openapi_server.py`) không có authentication

- **Vị trí:** 44 route REST không hề có API key/Bearer check; `allow_origins=["*"]`; docstring khuyến nghị `uvicorn … --host 0.0.0.0` và “deploy lên public URL”.
- **Thực tế hiện tại:** pm2 chỉ chạy bridge khi `HD_GPT_BRIDGE=1` và bind `127.0.0.1` → **chưa bị phơi ra**. Nhưng rủi ro vận hành cao nếu ai đó bật theo hướng dẫn trong docstring.
- **Rủi ro:** lạm dụng tài nguyên tính thiên văn (DoS), quét API, trộn traffic với app chính nếu bị đưa ra Internet công khai.
- **Khuyến nghị:** thêm `Authorization: Bearer <HD_GPT_TOKEN>` bắt buộc; giữ bind `127.0.0.1` + forward có kiểm soát; sửa docstring khuyến nghị `0.0.0.0`; giới hạn CORS theo domain Custom GPT.

### 🟠 M5 — Thiếu security header cho trang HTML (Next.js)

- **Vị trí:** `web/next.config.ts` chỉ set `X-Content-Type-Options: nosniff` + `Referrer-Policy: same-origin`.
- **Thiếu:** CSP (toàn admin app), HSTS, `frame-ancestors` (clickjacking), `Permissions-Policy`.
- **Lưu ý:** trang admin *cố ý* nhúng trong iframe preview nên không đặt `X-Frame-Options: DENY` được — dùng allowlist.
- **Khuyến nghị (next.config.ts headers):**
  ```
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'self' *.e2b.app
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  ```
  (điều chỉnh `frame-ancestors`/`connect-src` theo domain preview thực tế). CSP đặc biệt quan trọng vì **token dự phòng nằm trong `sessionStorage`** — XSS trên origin sẽ đọc được ngay.

### 🟡 T1 — Swagger/OpenAPI của admin APIpublic không cần đăng nhập

- **Bằng chứng:** `GET /api/v1/docs` → 200, `GET /api/v1/openapi.json` → 200 (không cookie).
- **Rủi ro:** enumerate đầy đủ 44 route + schema cho attacker sau khi có bất kỳ foothold nào.
- **Khuyến nghị:** tắt ở production — `docs_url/openapi_url = None` khi `HD_ENV=production` (giữ ở dev).

### 🟡 T2 — Chính sách mật khẩu & các kênh brute-force còn lại

- Chỉ `min_length=8`, không kiểm tra độ phức tạp/danh sách mật khẩu phổ biến (HaveIBeenPwned k-anonymity).
- Chống brute-force theo `ip|email` → **password-spray 1 mật khẩu/1000 email từ cùng IP không bao giờ chạm ngưỡng** (mỗi email 1 bucket).
- Timing: khi email không tồn tại, không chạy Argon2 → khác biệt thời gian **leak user-enumeration**.
- **Khuyến nghị:** chạy Argon2 dummy khi user không tồn tại; bucket chống đăng nhập theo IP riêng (vd 20 lỗi/15 phút/IP); thêm option 2FA cho admin.

### 🟡 T3 — Cấu hình CORS (nếu bật) quá rộng cho cơ chế CSRF hiện tại

- `main.py`: khi `CORS_ORIGINS` được set → `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- Vì CSRF dựa hoàn toàn trên “header custom không gửi được cross-site”, **bất kỳ origin nào trong allowlist đều có toàn quyền gọi API đăng nhập/đổi mật khẩu** với cookie của nạn nhân.
- **Khuyến nghị:** enumerate method (`GET,POST,PATCH,PUT,DELETE`) và header (`Content-Type,X-HD-Request,Authorization,X-HD-Embedded`); tuyệt đối không đặt wildcard origin; validate từng origin.

### 🟡 T4 — `base_url` của LLM provider cho phép SSRF nội bộ (cần quyền admin)

- `LlmProviderIn.base_url` (max 300 ký tự, chỉ cần bắt đầu http/https) → `urllib.request.urlopen` phía server với khóa API của tổ chức.
- Admin đã xác thực mới đặt được → mức thấp, nhưng tài khoản admin bị chiếm có thể quét mạng nội bộ/metadata endpoint (`169.254.169.254`) từ VPS.
- **Khuyến nghị:** chỉ cho `https://`, chặn dải private/link-local (`127./10./172.16-31./192.168./169.254.`) trừ khi env cho phép.

### 🟡 T5 — Lỗ hổng dependency phía frontend (npm audit)

```
postcss <=8.5.22  (qua next@15.5.x)
- HIGH: XSS qua </style> chưa escape trong CSS stringify (GHSA-qx2v-qp2m-jg93)
- MODERATE/HIGH: đọc file .map tùy ý qua sourceMappingURL (GHSA-6g55…, GHSA-fxqj…, GHSA-r28c…)
```
- Chủ yếu ở **giai đoạn build** (không chạy trong trình duyệt người dùng), nhưng vẫn nên nâng.
- **Khuyến nghị:** lên kế hoạch nâng `next` lên bản vá ≥16.x khi tương thích; đưa `npm audit --omit=dev` + `pip-audit` vào `deploy/check.sh` (hiện `check.sh` mới có pytest/typecheck/build); bật Dependabot/Renovate.

### 🟡 T6 — Ví dụ nginx thiếu các lớp phòng thủ mặc định

`deploy/nginx.conf.example` chưa có: `limit_req` cho `/api/v1/auth/login` & `/api/v1/public/`, HSTS, header bảo mật, log redaction query string, `server_name` chặn Host lạ. Đây là file copy-paste theo docs nên sẽ thành cấu hình thật.

### 🔵 I1 — `_read_knowledge()` (MCP) dùng `os.path.join` không kiểm tra traversal
Hiện **chỉ được gọi với tên file hard-code** → chưa khai thác được, nhưng lần tái sử dụng sau là nguy hiểm. Nên chặn sớm:
```python
p = Path(KNOWLEDGE_DIR, filename).resolve()
if not p.is_relative_to(Path(KNOWLEDGE_DIR).resolve()): raise ValueError(...)
```

### 🔵 I2 — File `.env` không kiểm tra quyền
`load_dotenv()` đọc `.env` bất kể mode; nên cảnh báo/log khi file readable bởi group/other (so với `var/secret_key` đã 0600).

### 🔵 I3 — Timing/user-enumeration & chi tiết lỗi
Thông điệp lỗi nhất quán (tốt) nhưng timing khác (xem T2). Lỗi 422 trả `msg` gốc của Pydantic (tiếng Anh) — không rủi ro nhưng không đồng bộ tiếng Việt.

### 🔵 I4 — Dữ liệu cá nhân
- `GameLead` (tên, SĐT/Zalo, ngày sinh) lưu plaintext — chấp nhận được cho giai đoạn này nhưng nên có chính sách lưu giữ/xóa (GDPR-esque) và ограни chế xuất.
- `AuditLog` lưu email đăng nhập lỗi + IP — cần chính sách retention; tránh log query string (M1) để không cộng dồn token.

### 🔵 I5 — Clickjacking UI redressing
Không có `frame-ancestors` → trang admin có thể bị overlay bởi trang khác (CSRF header vẫn chặn request, nhưng lừa người dùng bấm nút “Đổi mật khẩu/Chia sẻ” trong UI bị che vẫn khả thi kết hợp M5).

---

## 4. Ma trận ưu tiên khắc phục

| # | Việc cần làm | Effort | Ưu tiên |
|---|---|---|---|
| 1 | `client_ip()` dùng `X-Real-IP`/last-XFF + nginx `limit_req` cho `/auth/login` | S | **Cao** |
| 2 | Redaction query string trong access log + giới hạn `access_token` cho route file (M1) | S–M | **Cao** |
| 3 | Thêm CSP + HSTS + `frame-ancestors` allowlist cho Next (M5) | S | **Cao** |
| 4 | Tắt Swagger ở production (T1) | S | Trung bình |
| 5 | GPT-bridge: Bearer token + sửa docstring 0.0.0.0 (M4) | S | Trung bình |
| 6 | CORS enumerate methods/headers (T3) | S | Trung bình |
| 7 | Argon2 dummy khi user sai + bucket rate-limit theo IP (T2) | S | Trung bình |
| 8 | Nâng next/postcss; thêm `npm audit` + `pip-audit` vào `check.sh` (T5) | M | Trung bình |
| 9 | Validate `base_url` LLM chống SSRF (T4) | S | Thấp |
| 10 | Chuyển rate-limit sang nginx/Redis; dọn `_HITS` (M3) | M | Thấp |
| 11 | Path-check `_read_knowledge`, kiểm tra mode `.env` (I1, I2) | S | Thấp |

---

## 5. Kiểm thử đã thực hiện (repro)

```text
POST /api/v1/auth/login không có X-HD-Request        → 403  ✅ (CSRF chặn)
GET  /api/v1/docs, /openapi.json                      → 200  ⚠️ (T1)
POST /auth/login 5 lần sai, cùng XFF                 → 429  ✅ (chốt 401×5→429)
POST /auth/login 7 lần sai, XFF xoay 10.1.1.x         → 401×7 ✗ (M2 bypass)
GET  /auth/me?access_token=<token hợp lệ>             → 200  ✗ (M1 — token nằm trong log)
POST /reports?access_token=<token>, thiếu CSRF header → 403  ✅
GET  /files/<token rác>                               → 410  ✅ (HMAC hết hạn)
GET  /public/r/../../etc/passwd                       → 404  ✅ (không traversal)
TRACE/PUT không hợp lệ                               → 403  ✅
Cookie production (HD_ENV=production)                 → Secure=True, SameSite=lax ✅
npm audit (web)                                       → 2 vuln postcss/next ⚠️ (T5)
Git history secret scan                               → không phát hiện 🔐
```

*Lưu ý: phiên bản Python ghim trong `requirements.txt` chưa chạy được `pip-audit` trong môi trường sandbox (không truy cập PyPI API) — cần chạy ở CI.*

---
---
## 6. Cập nhật 2026-09-27 — đã xử lý Nhóm ưu tiên 1

Toàn bộ 5 việc ưu tiên 1 đã áp dụng và kiểm thử lại thành công (213/213 test, typecheck + build OK):

| # | Việc | File đã sửa | Kết quả kiểm thử |
|---|---|---|---|
| 1 | `client_ip()` ưu tiên `X-Real-IP`, fallback phần tử **cuối** XFF | `backend/api/deps.py` | Xoay XFF spoofed: `401×5 → 429` (trước: 7×401 không chặn) ✅ |
| 2 | `limit_req` cho `/api/v1/auth/login` + log không lưu query string | `deploy/nginx.conf.example` | Key là TCP peer thật, không giả mạo được; `?access_token=` không còn vào access log ✅ |
| 3 | `?access_token=` chỉ còn hiệu lực trên route xuất file (`/reports/{id}/markdown|infographic.html|bodygraph.svg|pdf|docx`) | `backend/api/deps.py` | `/auth/me?access_token=` → **401** (trước: 200); file route vẫn 200 ✅ |
| 4 | Tắt `/api/v1/docs` + `/openapi.json` khi `HD_ENV=production` | `backend/api/main.py` | Test production → 404, dev → 200, health luôn 200 ✅ |
| 5 | Thêm HSTS + Permissions-Policy + CSP `frame-ancestors 'self' *.e2b.app` | `web/next.config.ts` | Trang HTML trả đủ 3 header mới ✅ |

Kèm theo: forward thêm `X-Real-IP` ở 2 đường proxy nội bộ Next (SSE route + SSR share page); sửa lỗi typecheck có sẵn ở `web/app/admin/reports/new/page.tsx` (chặn `npm run build`); bổ sung 3 test hồi quy trong `tests/test_api_v1.py`.

**Ghi chú vận hành:**
- Cấu hình nginx production thật (`/etc/nginx/sites-available/human_design`) cần được cập nhật tương tự `deploy/nginx.conf.example` rồi `nginx -t && systemctl reload nginx`.
- CSP đầy đủ (`script-src` nonce cho App Router) để làm riêng — Next cần middleware nonce, làm vội sẽ vỡ hydration.
- 2 lỗi có sẵn trên nhánh (ngoài phạm vi bảo mật): `alembic check` fail trên SQLite (reflection 2 unique constraint), và dependency postcss/next (T5).

## 7. Cập nhật 2026-09-27 — xử lý Nhóm ưu tiên 2 (bước 6→10)

Toàn bộ 5 việc + cơ chế allowlist LLM đã triển khai. Test: **233/233 pass** (thêm 20 test mới), typecheck + build OK.

| # | Việc | File | Chi tiết |
|---|---|---|---|
| 6 | **CORS enumerate** | `backend/api/main.py` | Bỏ `allow_methods/headers ["*"]`; chỉ giữ `GET,POST,PATCH,PUT,DELETE,OPTIONS` + `Accept,Content-Type,Authorization,X-HD-Request,X-HD-Embedded`, `max_age=600`. Test: preflight header lạ → 400, origin lạ → không ACAO ✅ |
| 7 | **GPT-bridge bắt buộc token** | `mcp/openapi_server.py` | Đăng ký bằng `add_middleware(BaseHTTPMiddleware)` (không decorator → không phá test contract 44 route): có `HD_GPT_TOKEN` → yêu cầu `Bearer` (`compare_digest`); **production thiếu token → 503 fail-closed**; CORS bỏ wildcard, chỉ bật khi set `HD_GPT_CORS_ORIGINS`; bind `127.0.0.1` + sửa docstring/banner. 4 test mới ✅ |
| 8 | **Chống timing + spray** | `backend/api/routers/auth.py` | `_DUMMY_HASH` Argon2 giả → email không tồn tại vẫn tốn cùng chi phí verify; bucket **IP thuần 20 lỗi/15 phút** bên cạnh `ip\|email`; reset IP bucket khi đăng nhập thành công. Test: 20 email khác nhau → 401, lần 21 → 429 ✅ |
| 9 | **SSRF guard `base_url` (allowlist)** | `backend/reporting/llm_client.py`, `backend/api/schemas.py`, `backend/api/routers/admin_settings.py` | `validate_llm_base_url()`: https bắt buộc + chặn IP không global (127/8, 10/8, 192.168/16, ::1…) + **link-local 169.254 luôn chặn kể cả whitelist**; whitelist `HD_LLM_ALLOWED_PRIVATE_HOSTS=host[:port]` cho 9router/Ollama (http được qua trong whitelist). Áp ở **2 tầng**: Pydantic validator (422 tiếng Việt) + trước `urlopen` (LLMError). Audit log ghi `base_url` cũ→mới. 12 test unit/API ✅ |
| 10 | **npm audit vào check.sh + lịch nâng next** | `deploy/check.sh`, GitHub issue | Chế độ **CẢNH BÁO** hiện tại (next@15 còn dính HIGH → bật fail ngay sẽ tự chặn deploy); dòng sẵn để chuyển fail-on-high sau khi nâng. Issue: **[#4 — Nâng next 15.5 → 16.x](https://github.com/cuongtv24h/human_design/issues/4)** với checklist + điều kiện bật gate ✅ |

**Kèm theo:** `tests/conftest.py` dọn bucket rate-limit in-memory giữa các test (chống flaky); `.env.example` ghi chú 3 biến mới (`HD_LLM_ALLOWED_PRIVATE_HOSTS`, `HD_GPT_TOKEN`, `HD_GPT_CORS_ORIGINS`).

**Lưu ý vận hành:**
- Provider `base_url` http/IP nội bộ tồn tại từ trước: sau deploy sẽ **fail sang provider kế tiếp** (fallback chain) tới khi thêm host vào `HD_LLM_ALLOWED_PRIVATE_HOSTS`.
- Bật `HD_GPT_TOKEN` bất cứ khi nào bật `HD_GPT_BRIDGE=1` ở production (thiếu → 503 fail-closed là chủ đích).
- Bucket rate-limit in-memory vẫn reset khi restart (đã có `limit_req` nginx ở mục 2 bù); nâng `_MAX_IP_FAILURES` nếu đứng sau NAT lớn.
- `alembic check` trong `check.sh` vẫn fail **có sẵn từ trước** (SQLite reflection 2 unique constraint) — xử lý riêng, không thuộc nhóm này.

*Báo cáo do Agent Mode (Arena.ai) lập ngày 2026-09-27 trên nhánh `arena/01a0e48f-human-design`.*

## 8. Cập nhật 2026-09-27 — T5 (nâng next), 2 mục 🔵 và fix `alembic check`

**`deploy/check.sh` chạy trọn vẹn lần đầu: `check.sh: OK` (exit 0)** — pytest toàn bộ pass + `alembic check` xanh + typecheck + build + `npm audit --audit-level=high` = 0 lỗ hổng.

| Hạng mục | Việc đã làm | Kết quả |
|---|---|---|
| **T5 — nâng next** (issue #4) | `next 15.5.26 → 16.3.6` (`package.json` `^16.3.6`) | typecheck ✅ · build đủ route ✅ · smoke `next start` (trang admin, game, proxy /api, login, SSR /r, headers 3/3, SSE 401) ✅ · `npm audit --omit=dev` → **0 vulnerabilities** ✅ |
| **Gate audit** | `check.sh` chuyển từ CẢNH BÁO → **fail-on-high** (`--audit-level=high`), dòng hướng dẫn rollback nếu npm báo high trở lại | kích hoạt ngay khi còn 0 vuln ✅ |
| **🔵 I1 — `_read_knowledge`** (`mcp/server.py`) | Sau `realpath`, file phải nằm **trực tiếp** trong `knowledge/` → chặn `../`, đường dẫn tuyệt đối, symlink trỏ ra ngoài; nhánh OSError giữ nguyên | 1 test: 5 payload traversal (`../../.env`, `/etc/passwd`…) bị từ chối ✅ |
| **🔵 I2 — quyền `.env`** (`backend/api/settings.py`) | `load_dotenv` cảnh báo `chmod 600` khi file group/other đọc được (POSIX); không chặn khởi động | 2 test: 0644 → có warning, 0600 → im ✅ |
| **`alembic check`** (drift có sẵn) | **Nguyên nhân gốc:** migration 0009/0012 tạo `UNIQUE (template_id, version_no)` và `UNIQUE (session_id, day)` nhưng `models.py` **không khai báo** `__table_args__` → autogenerate muốn drop constraint khỏi DB. Thêm `UniqueConstraint` vào 2 model cho khớp migration | `alembic check` → **"No new upgrade operations detected" exit 0** ✅ |
| **Kèm theo** | `mcp/openapi_server.py` giờ nạp `.env` ở repo root (nhờ đó `HD_GPT_TOKEN`/`HD_ENV` trong `.env` có hiệu lực với bridge; pm2 env vẫn thắng) | nhất quán với backend ✅ |

**Ghi chú:**
- Issue [#4](https://github.com/cuongtv24h/human_design/issues/4): bot tạo được issue nhưng **không có quyền comment/close** ("Resource not accessible by integration") — cần đóng/cập nhật tay sau khi duyệt.
- Lợi ích ẩn của fix models: trước đây dev/test (`db.create_all()`) tạo bảng **thiếu 2 unique constraint** mà production có → dev không phản ánh đúng hành vi prod (chèn trùng streak/style version chỉ prod bắt lỗi).
