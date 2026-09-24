# Human Design MCP Server v3.0

MCP stdio server hiện tại của Human Design Analyzer. Server dùng `mcp/server.py`, nạp calculator/analyzer từ `tools/` và cung cấp dữ liệu qua tools + resources.

> **Runtime chuẩn (2026-09-24):** 30 tools · 11 resources · 0 MCP prompts · 19 skill Markdown · MCP SDK `mcp==1.30.0`.

## Kiến trúc

```text
LLM client (Claude Desktop / Cursor / Windsurf)
                 │ MCP stdio
                 ▼
          mcp/server.py
          ├── 30 tools
          ├── 11 resources
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

## 30 tools

### Core — 8

1. `calculate_human_design_chart`
2. `analyze_human_design_deep`
3. `get_gate_info`
4. `get_center_info`
5. `get_channel_info`
6. `get_profile_info`
7. `compare_charts`
8. `generate_full_report`

### Advanced — 4

9. `analyze_fear_gates`
10. `analyze_love_gates`
11. `get_incarnation_cross_details`
12. `analyze_manifestor_deep`

### General — 2

13. `analyze_consultation_general`
14. `generate_consultation_report`

### Money — 2

15. `analyze_money_map`
16. `generate_money_report`

### Potential — 2

17. `analyze_potential_blindspots`
18. `generate_potential_report`

### v3.0 domains — 12

19. `analyze_health`
20. `generate_health_report`
21. `analyze_relationship`
22. `generate_relationship_report`
23. `analyze_decision`
24. `generate_decision_report`
25. `analyze_deconditioning`
26. `generate_deconditioning_report`
27. `analyze_purpose`
28. `generate_purpose_report`
29. `analyze_team`
30. `generate_team_report`

Luồng phân tích chart nên bắt đầu bằng `calculate_human_design_chart`, sau đó dùng analyzer/domain tool phù hợp. Các tool nhận ngày/giờ local và timezone, rồi server chuyển sang UTC trước khi gọi calculator.

## 11 resources

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

Resource `channels`, `mandala/order`, `fear-gates`, `incarnation-crosses`, `manifestor`, `general-consultation` và `potential-blindspots` từng xuất hiện trong manifest lịch sử nhưng **không** có decorator resource trong server hiện tại; không liệt kê chúng là runtime resource.

## Skill Markdown

Có 19 file tại `mcp/skills/`: `01`–`18` và `20`. Đây là prompt/template tài liệu để LLM tham khảo, không phải MCP prompt runtime. Manifest hiện tại vì vậy tách rõ:

- `resources`: 11 runtime resources.
- `prompts`: `[]`.
- `skills_path`: `./skills/`, 19 Markdown files.

## REST/OpenAPI bridge

`openapi_server.py` cung cấp 32 route decorator: 30 route nghiệp vụ, `/` và `/health`.

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
