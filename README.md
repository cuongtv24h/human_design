# Human Design Analyzer v3.0

Hệ thống tính toán và phân tích Human Design bằng tiếng Việt, dùng Swiss Ephemeris cho phần thiên văn và cung cấp cả MCP server lẫn REST/OpenAPI bridge.

> **Trạng thái chuẩn hiện tại:** v3.0.0 · 40 MCP tools · 22 MCP resources · 25 skill markdown · 44 REST routes (2026-09-24)

## Tính năng

- Tính BodyGraph từ ngày, giờ và múi giờ sinh: Personality, Design 88°, 64 Gates, 36 Channels, 9 Centers, Type, Strategy, Authority, Profile, Definition và Incarnation Cross.
- Phân tích cơ bản và 6 nhóm ứng dụng v3.0: Health, Relationship, Decision, Deconditioning, Purpose và Team.
- Các nhóm mở rộng: Fear Gates, Love Gates, 192 Incarnation Crosses, Manifestor, Consultation General, Money Map và Potential/Blind Spots.
- CLI, xuất BodyGraph SVG/PNG và báo cáo PDF tiếng Việt.
- MCP stdio cho Claude Desktop/Cursor/Windsurf và FastAPI/OpenAPI cho Custom GPT Actions hoặc client REST.

## Cấu trúc repository

```text
human_design/
├── requirements.txt             # dependency Python đã ghim phiên bản
├── tools/                       # calculator, analyzer, CLI, SVG, PDF và domain analyzers
├── backend/reporting/           # Report Contract, catalog và Admin/Coach orchestrator
├── mcp/
│   ├── server.py                # MCP entrypoint hiện tại: 40 tools, 22 resources
│   ├── openapi_server.py        # FastAPI bridge: 44 route decorator
│   ├── tools_manifest_latest.json
│   ├── mcp_config.json
│   └── skills/                  # 25 skill markdown; không phải MCP prompt decorator
├── knowledge/                   # 21 tài liệu kiến thức chuẩn hóa, đánh số 00–20
├── docs/                        # Wiki nguồn và catalog tài liệu cá nhân
└── report/                      # báo cáo lịch sử triển khai, giữ nguyên để tham chiếu
```

`README.md`, `docs/README.md` và `mcp/README.md` là tài liệu vận hành hiện tại. Các file có hậu tố hoặc tiêu đề v2.x trong `report/`, `README_v2.1.md` và `mcp/README_v2.1.md` là tài liệu lịch sử, không dùng làm số liệu runtime.

### Report layer cho Admin/Coach

`docs/REPORTING_ARCHITECTURE.md` mô tả `ReportRequest` → `ChartSnapshot` → `ReportPlan` → `ReportSection[]` → `ReportDocument`. Application layer hiện hỗ trợ `free_basic`/`deep_core` và 8 domain add-on; frontend, billing và payment chưa thuộc scope. Orchestrator gọi analyzer hiện có trong `tools/`, giữ raw structured output và provenance để renderer/LLM diễn giải sau này.

## Cài đặt

Yêu cầu Python 3.11+.

```bash
cd /home/user/human_design
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

`requirements.txt` bao gồm MCP SDK v1 tương thích với `FastMCP`, Swiss Ephemeris, FastAPI/Uvicorn, Pydantic, ReportLab, CairoSVG và pytest.

### Dependency hệ điều hành cho PNG/PDF BodyGraph

CairoSVG cần thư viện Cairo native. Trên Debian/Ubuntu cài thêm:

```bash
sudo apt-get update
sudo apt-get install -y libcairo2 fonts-dejavu
```

Phần tính chart, MCP, REST và PDF text không cần gọi CairoSVG cho đến khi render BodyGraph; `--png` và phần BodyGraph trong PDF cần dependency hệ điều hành này.

## Chạy nhanh

### CLI tính chart

```bash
PYTHONPATH=tools .venv/bin/python tools/hd_cli.py \
  --date 1990-05-15 --time 08:30 --timezone +07:00 \
  --name "Nguyen Van A"
```

### BodyGraph SVG/PNG

```bash
PYTHONPATH=tools .venv/bin/python tools/hd_bodygraph.py \
  --date 1990-05-15 --time 08:30 --tz +07:00 \
  --name "Nguyen Van A" --out output/chart.svg --png output/chart.png
```

### Báo cáo PDF

```bash
PYTHONPATH=tools .venv/bin/python tools/hd_report_pdf.py \
  --date 1990-05-15 --time 08:30 --tz +07:00 \
  --name "Nguyen Van A" --out output/report.pdf
```

Thư mục `output/` được `.gitignore` để tránh đưa artifact sinh ra vào Git.

## MCP server

Chạy từ thư mục repository:

```bash
.venv/bin/python mcp/server.py
```

Server dùng **stdio**, nên không mở HTTP port. Cấu hình mẫu nằm tại `mcp/mcp_config.json`; cần thay đường dẫn tuyệt đối nếu repository được đặt ở nơi khác. Client có thể gọi trực tiếp flow lõi bằng:

```bash
PYTHONPATH=tools:mcp .venv/bin/python mcp/client_example.py
```

MCP runtime hiện có:

- **39 tools:** 6 foundation, 8 core, 4 advanced, 2 general, 2 money, 2 potential, 12 domain v3.0 và 4 report tools (`generate_hd_report`, `build_hd_report_brief`, `apply_hd_report_draft`, `generate_hd_infographic`).
- **Báo cáo chuẩn:** thông tin người được phân tích + BodyGraph tự sinh + nội dung `content_mode` = `template` (mặc định) hoặc `llm` (cần `HD_LLM_API_KEY`, tự fallback về template). Chi tiết: `docs/REPORTING_ARCHITECTURE.md`.
- **Định dạng xuất:** Markdown, PDF (`tools/hd_report_pdf.py`) và **Infographic HTML** tự chứa — trực quan, ít chữ, tập trung điểm chính (`generate_hd_infographic`, `GET /reports/infographic.html`).
- **Foundation tools:** Centers, Channels, Type/Strategy/Authority, Profile/Definition, Calculation và Practical Application.
- **22 resources:** 11 resource tóm tắt runtime và 11 resource đọc toàn văn các knowledge topic còn lại.
- **0 MCP prompts:** 25 skill là các file Markdown trong `mcp/skills/`, được LLM/client đọc hoặc dùng làm hướng dẫn riêng; chúng chưa được đăng ký bằng `@mcp.prompt()` trong `server.py`.

Manifest máy đọc được: `mcp/tools_manifest_latest.json`.

## REST/OpenAPI server

Bridge cho ChatGPT Custom GPT Actions và REST client:

```bash
cd mcp
../.venv/bin/python -m uvicorn openapi_server:app --host 0.0.0.0 --port 8000
```

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI: `http://localhost:8000/openapi.json`
- Health check: `http://localhost:8000/health`
- 36 route nghiệp vụ tương ứng với 36 tool và 2 route hệ thống (`/`, `/health`).

Không hard-code `localhost` trong client chạy ở browser; khi deploy public, client phải gọi public base URL của API.

## Admin web (quản lý khách hàng & báo cáo)

Gồm **API `/api/v1`** (`backend/api/`, FastAPI + SQLAlchemy + Alembic) và **giao diện** (`web/`, Next.js 15 + Tailwind + TanStack Query). Trình duyệt chỉ gọi Next.js; Next.js proxy `/api/*` sang API nên cookie phiên (httpOnly) hoạt động trên cùng một origin.

Chạy trên máy dev (SQLite tự tạo ở `var/hd_dev.sqlite3`):

```bash
# 1) API
.venv/bin/python -m backend.api.cli create-admin --email admin@vidu.vn --name "Quản trị"   # hỏi mật khẩu
.venv/bin/uvicorn backend.api.main:app --host 127.0.0.1 --port 8001

# 2) Web (terminal khác)
cd web && npm install && npm run dev        # http://localhost:3000
```

- Tài liệu API: `http://localhost:8001/api/v1/docs`.
- Production dùng PostgreSQL: `DATABASE_URL=postgresql+psycopg://…` trong `.env` (xem `.env.example`), rồi `.venv/bin/alembic upgrade head`.
- Triển khai pm2 trên VPS: `deploy/ecosystem.config.cjs`, `deploy/deploy.sh`; trước khi deploy chạy `deploy/check.sh` (pytest + migration + typecheck + build).
- Xuất **PDF/Word** từ cùng một `ReportDocument` (`backend/reporting/render_pdf.py`, `render_docx.py`). Cần font DejaVu (`sudo apt install fonts-dejavu-core`, hoặc đặt `HD_FONT_DIR`); hình BodyGraph PNG dùng `resvg-py`, không cần libcairo. File được render sẵn sau khi tạo báo cáo và lưu theo phiên bản ở `ARTIFACT_DIR` (mặc định `var/artifacts`).
- Giờ sinh nhập và hiển thị theo **giờ Việt Nam khai báo**, tính theo UTC+07:00 cố định (`tools/hd_time.py`).
- **Biên tập báo cáo** (`/reports/{id}/edit`): sửa từng phần bằng Markdown, “Lưu phiên bản” (Ctrl/⌘+S) tạo phiên bản mới, xem/khôi phục lịch sử, cảnh báo vàng khi nội dung mất thông tin kỹ thuật gốc (Type, Strategy, Authority…), bản nháp tự lưu trong trình duyệt mỗi 10 giây. Nút “AI biên tập phần này” trả về đề xuất kèm so sánh để chấp nhận hoặc bỏ.
- **Chia sẻ cho khách**: tab “Chia sẻ” của báo cáo tạo link `/r/…` (chọn định dạng được tải, hạn 7 ngày–1 năm, thu hồi bất cứ lúc nào, đếm lượt xem). Tab “Xuất file” có nút “Link 5 phút” — link tải trực tiếp không cần đăng nhập.
- **AI / LLM** (admin, `/settings/llm`): nhập base URL, mô hình, khóa API (mã hóa khi lưu) và bấm “Kiểm tra kết nối”; nếu không lưu khóa, hệ thống dùng `HD_LLM_API_KEY`.
- **`HD_SECRET_KEY`** ký link và mã hóa khóa AI. Production nên đặt trong `.env` (chuỗi ngẫu nhiên dài, ví dụ `python -c "import secrets;print(secrets.token_urlsafe(48))"`); nếu bỏ trống, hệ thống tự tạo `var/secret_key`. Đổi khóa này làm link cũ mất hiệu lực và phải nhập lại khóa AI.
- Nâng cấp CSDL: `.venv/bin/alembic upgrade head` (migration `0002`: bảng `share_links`, cột `organizations.llm_settings`).
- Preview nhúng trong iframe khác site: đặt `COOKIE_SAMESITE=none` (cookie `Secure; Partitioned`). Nếu trình duyệt vẫn chặn cookie trong iframe (Safari, Chrome ẩn danh…), trang admin tự nhận biết đang bị nhúng và giữ phiên trong `sessionStorage` của tab (gửi `Authorization: Bearer`). Chạy trực tiếp trên domain riêng thì chỉ dùng cookie httpOnly; production giữ mặc định `lax`.
- Chế độ nội dung LLM cần `HD_LLM_API_KEY`; hiện chạy nền bằng FastAPI background task (worker arq/Redis thuộc P2).

## Kiểm tra

```bash
# Syntax toàn bộ Python source
.venv/bin/python -m compileall -q tools mcp

# Pytest runtime contract
PYTHONPATH=tools:mcp .venv/bin/pytest -q

# Smoke scripts nghiệp vụ lịch sử
PYTHONPATH=tools .venv/bin/python tools/test_calculator.py
PYTHONPATH=tools .venv/bin/python tools/test_manifestor_profiles.py

# Kiểm tra import MCP và OpenAPI
PYTHONPATH=tools:mcp .venv/bin/python - <<'PY'
import server
import openapi_server
print("MCP import OK")
print("OpenAPI routes:", len(openapi_server.app.routes))
PY
```

## Lưu ý nghiệp vụ

- Input cần ngày, giờ và múi giờ; giờ sinh không chính xác làm giảm độ tin cậy của Gate/Profile.
- Engine dùng Tropical Zodiac và chuyển giờ địa phương sang UTC trước khi tính.
- Kết quả Human Design nên được dùng như công cụ tự quan sát/thử nghiệm, không thay thế tư vấn y tế, pháp lý hoặc tài chính.
- `server_final.py`, các manifest `v1`–`v6`, README v2.x và các file trong `report/` được giữ lại để truy vết lịch sử; entrypoint hiện tại là `mcp/server.py`.
