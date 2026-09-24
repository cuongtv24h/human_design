# Human Design MCP Server v3.0

MCP stdio server hiện tại của Human Design Analyzer. Server dùng `mcp/server.py`, nạp calculator/analyzer từ `tools/` và cung cấp dữ liệu qua tools + resources.

> **Runtime chuẩn (2026-09-24):** 40 tools · 22 resources · 0 MCP prompts · 25 skill Markdown · MCP SDK `mcp==1.30.0`.

## Kiến trúc

```text
LLM client (Claude Desktop / Cursor / Windsurf)
                 │ MCP stdio
                 ▼
          mcp/server.py
          ├── 40 tools
          ├── 22 resources
          └── import tools/hd_*.py
                 │
                 ▼
       hd_calculator.py + Swiss Ephemeris

ChatGPT Custom GPT / REST client
                 │ HTTP/OpenAPI
                 ▼
       mcp/openapi_server.py (FastAPI)
```

`mcp/skills/` là 19 file hướng dẫn Markdown cho LLM/client. Chúng không được đăng ký thành MCP prompts: `server.py` hiện có 0 decorator `@mcp.prompt()`.

## Cài đặt

Từ root repository:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Nếu cần xuất PNG hoặc nhúng BodyGraph vào PDF trên Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y libcairo2 fonts-dejavu
```

Dependency Python được quản lý tập trung ở `../requirements.txt`; không dùng các lệnh `pip install` rời rạc trong tài liệu cũ.

## Chạy MCP stdio

```bash
cd /home/user/human_design
.venv/bin/python mcp/server.py
```

Lệnh này giữ stdout cho MCP protocol. Không gửi log debug vào stdout khi tích hợp client.

Ví dụ cấu hình Claude Desktop: `mcp_config.json`. Hãy sửa đường dẫn tuyệt đối `command`/`args` theo vị trí checkout của bạn. Cấu hình mẫu hiện dùng:

```json
{
  "mcpServers": {
    "human-design-analyzer": {
      "command": "/home/user/human_design/.venv/bin/python",
      "args": ["/home/user/human_design/mcp/server.py"]
    }
  }
}
```

Smoke test logic trực tiếp, không mở transport:

```bash
PYTHONPATH=tools:mcp .venv/bin/python mcp/client_example.py
```

## 40 tools

### Foundation — 6

1. `explain_calculation_method`
2. `analyze_centers_deep`
3. `analyze_channels_deep`
4. `analyze_type_strategy_authority`
5. `analyze_profile_definition`
6. `analyze_practical_application`

### Core — 8

7. `calculate_human_design_chart`
8. `analyze_human_design_deep`
9. `get_gate_info`
10. `get_center_info`
11. `get_channel_info`
12. `get_profile_info`
13. `compare_charts`
14. `generate_full_report`

### Advanced — 4

15. `analyze_fear_gates`
16. `analyze_love_gates`
17. `get_incarnation_cross_details`
18. `analyze_manifestor_deep`

### General — 2

19. `analyze_consultation_general`
20. `generate_consultation_report`

### Money — 2

21. `analyze_money_map`
22. `generate_money_report`

### Potential — 2

23. `analyze_potential_blindspots`
24. `generate_potential_report`

### v3.0 domains — 12

25. `analyze_health`
26. `generate_health_report`
27. `analyze_relationship`
28. `generate_relationship_report`
29. `analyze_decision`
30. `generate_decision_report`
31. `analyze_deconditioning`
32. `generate_deconditioning_report`
33. `analyze_purpose`
34. `generate_purpose_report`
35. `analyze_team`
36. `generate_team_report`

### Report — 4 (chuẩn báo cáo: thông tin + BodyGraph + template/LLM; Infographic)

37. `generate_hd_report` — báo cáo hoàn chỉnh; `content_mode="template"` (mặc định) hoặc `"llm"`; `save_files` ghi `.md` + `_bodygraph.svg` vào `output/reports/`
38. `build_hd_report_brief` — brief biên tập (persona chuyên gia HD + nhà tư vấn tâm lý, quy tắc, dữ liệu nguồn, thuật ngữ chuẩn) để **chính AI host** tự biên tập, không cần API key
39. `apply_hd_report_draft` — ghép bản biên tập `{section_id: markdown}`, kiểm tra giữ nguyên sự kiện kỹ thuật (mất → `warnings`)
40. `generate_hd_infographic` — Infographic HTML tự chứa (CSS + BodyGraph nội tuyến, không JS/CDN): trực quan, ít chữ, điểm chính; ghi `output/reports/<slug>_infographic.html`

Chế độ LLM có hai cách chạy:

- **Server tự gọi LLM:** đặt `HD_LLM_API_KEY` (hoặc `OPENAI_API_KEY`), tuỳ chọn `HD_LLM_BASE_URL` (endpoint OpenAI-compatible bất kỳ), `HD_LLM_MODEL` (mặc định `gpt-4o-mini`), `HD_LLM_TIMEOUT`, `HD_LLM_TEMPERATURE` → gọi `generate_hd_report(content_mode="llm")`. Thiếu key hoặc LLM lỗi → fallback template, `editor="template (llm fallback)"` + cảnh báo.
- **AI host tự biên tập:** `build_hd_report_brief` → AI viết lại → `apply_hd_report_draft`.

Luồng phân tích chart nên bắt đầu bằng `calculate_human_design_chart`, sau đó dùng foundation analyzer hoặc domain tool phù hợp. Các tool nhận ngày/giờ local và timezone, rồi server chuyển sang UTC trước khi gọi calculator.

## 22 resources

| URI | Nội dung |
|---|---|
| `human-design://knowledge/gates` | 64 Gates và trung tâm |
| `human-design://knowledge/centers` | 9 Centers |
| `human-design://knowledge/types` | 5 Types |
| `human-design://knowledge/money-channels` | 6 Money Channels |
| `human-design://knowledge/money-gates` | 14 Money Gates |
| `human-design://knowledge/health-type` | Health theo Type |
| `human-design://knowledge/love-gates` | Love Gates |
| `human-design://knowledge/authorities` | 7 Authorities |
| `human-design://knowledge/notself` | Not-Self và Signature |
| `human-design://knowledge/purpose-quarters` | Quarters và Angles |
| `human-design://knowledge/team-roles` | Team roles |
| `human-design://knowledge/overview` | Tổng quan hệ thống |
| `human-design://knowledge/mandala` | Mandala và 64 Gates đầy đủ |
| `human-design://knowledge/channels` | 36 Channels |
| `human-design://knowledge/profile-definition` | Profile, Definition và Cross |
| `human-design://knowledge/calculation` | Phương pháp tính |
| `human-design://knowledge/applications` | Ứng dụng thực tiễn |
| `human-design://knowledge/incarnation-crosses` | 192 Incarnation Crosses |
| `human-design://knowledge/fear-gates` | Fear Gates và cơ chế trí óc |
| `human-design://knowledge/manifestor` | Manifestor và tham vấn |
| `human-design://knowledge/general-consultation` | Tham vấn tổng quát 60 biến thể |
| `human-design://knowledge/potential-blindspots` | Tiềm năng và điểm mù |

Tất cả 22 resource hiện đã có decorator trong `server.py`; 11 resource mới đọc trực tiếp toàn văn file knowledge.

## Skill Markdown

Có 25 file skill tại `mcp/skills/`: `01`–`18` và `20`–`26`. Sáu skill `21`–`26` là nhóm foundation mới. Đây là template tài liệu để LLM tham khảo, không phải MCP prompt runtime. Manifest hiện tại vì vậy tách rõ:

- `resources`: 22 runtime resources.
- `prompts`: `[]`.
- `skills_path`: `./skills/`, 25 Markdown skill files.

## REST/OpenAPI bridge

`openapi_server.py` cung cấp 44 route decorator: 42 route nghiệp vụ, `/` và `/health`. Report routes: `POST /reports/generate` (`?include_bodygraph_svg=true` để kèm SVG), `POST /reports/llm-brief`, `POST /reports/apply-draft`, `POST /reports/bodygraph.svg`, `POST|GET /reports/infographic.html` (GET nhận query `birth_date`, `birth_time`, `timezone`, `name`, `birth_location`, `tier` — mở thẳng trên trình duyệt) — body là `ReportRequest` (`subject`, `tier`, `template`, `content_mode`, `domains`...).

```bash
cd /home/user/human_design/mcp
../.venv/bin/python -m uvicorn openapi_server:app --host 0.0.0.0 --port 8000
```

- `/docs`: Swagger UI
- `/openapi.json`: OpenAPI spec cho Custom GPT Actions
- `/health`: health check

Hướng dẫn tích hợp riêng: `CHATGPT_WEB_INTEGRATION.md`. Không dùng MCP stdio config cho ChatGPT Web; ChatGPT Web cần REST server public và OpenAPI spec.

## Manifest

`tools_manifest_latest.json` là manifest canonical cho việc phân phối tool/resource. Các file `tools_manifest.json`, `tools_manifest_v2.json`, … `tools_manifest_v6.json` là snapshot lịch sử.

## Kiểm tra

```bash
cd /home/user/human_design
.venv/bin/python -m compileall -q tools mcp
PYTHONPATH=tools .venv/bin/python tools/test_calculator.py
PYTHONPATH=tools .venv/bin/python tools/test_manifestor_profiles.py
PYTHONPATH=tools:mcp .venv/bin/python - <<'PY'
import server
import openapi_server
print("server import OK")
print("OpenAPI decorator/runtime routes:", len(openapi_server.app.routes))
PY
```

Repository có `tests/test_runtime_contract.py` cho các invariant runtime/count/manifest; hai file trong `tools/` vẫn là smoke script lịch sử. Chạy `PYTHONPATH=tools:mcp .venv/bin/pytest -q` để kiểm tra contract hiện tại.
