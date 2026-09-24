# Tích hợp Human Design với ChatGPT Web

`server.py` là MCP stdio server. ChatGPT Custom GPT Actions không dùng trực tiếp file MCP config; hãy dùng `openapi_server.py` để expose cùng logic qua REST/OpenAPI.

> **Snapshot hiện tại:** API v3.0.0 · 36 route nghiệp vụ · 2 route hệ thống (`/`, `/health`) · OpenAPI spec tự sinh tại `/openapi.json`.

## 1. Chạy và kiểm tra API local

Từ root repository:

```bash
cd /home/user/human_design/mcp
../.venv/bin/python -m uvicorn openapi_server:app \
  --host 0.0.0.0 --port 8000
```

Kiểm tra:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/openapi.json
```

Swagger UI nằm ở `http://localhost:8000/docs`. Địa chỉ `localhost` chỉ dành cho máy chạy server; ChatGPT trên web cần một URL public có HTTPS.

## 2. Deploy public

Có thể deploy FastAPI app trên máy chủ/container hoặc nền tảng hỗ trợ ASGI. Lệnh production tối thiểu:

```bash
python -m uvicorn openapi_server:app --host 0.0.0.0 --port ${PORT:-8000}
```

Khi chạy từ thư mục `mcp`, cần bảo đảm `../tools` nằm trong repository đúng như import path của source. Không commit secret; nếu thêm authentication, cấu hình API key ở reverse proxy hoặc middleware và cập nhật schema tương ứng.

Sau khi deploy, kiểm tra các URL:

- `https://YOUR_HOST/health`
- `https://YOUR_HOST/docs`
- `https://YOUR_HOST/openapi.json`

## 3. Tạo Custom GPT Action

1. Mở trình tạo Custom GPT.
2. Tạo Action mới.
3. Import OpenAPI schema từ `https://YOUR_HOST/openapi.json`.
4. Chọn authentication phù hợp với deployment. Bản local/public test chỉ nên dùng `None` khi API đã được giới hạn truy cập.
5. Lưu và thử với ngày, giờ, timezone.

Các nhóm endpoint gồm:

- Foundation: `/calculation-method`, `/analyze-centers`, `/analyze-channels`, `/analyze-type-strategy-authority`, `/analyze-profile-definition`, `/analyze-practical-application`.
- Core: `/calculate-chart`, `/analyze-deep`, lookup Gate/Center/Channel/Profile, `/compare-charts`, `/generate-report`.
- Advanced: fear, love, incarnation cross, Manifestor.
- General/Money/Potential: consultation, money map, blind spots.
- v3.0: health, relationship, decision, deconditioning, purpose, team; mỗi domain có endpoint phân tích và endpoint report.

## 4. Quy trình gọi khuyến nghị

### Phân tích một người

1. Gọi `POST /calculate-chart` với `birth_date`, `birth_time`, `timezone` và thông tin tùy chọn.
2. Gọi `POST /analyze-deep` nếu cần phân tích nền tảng.
3. Gọi domain endpoint tương ứng với nhu cầu: `/analyze-health`, `/analyze-purpose`, `/analyze-money-map`, v.v.
4. Dùng `/generate-*-report` khi cần bản Markdown hoàn chỉnh.

### Tra cứu

- `GET /gate-info/{gate_number}`
- `GET /center-info/{center_name}`
- `GET /profile-info/{profile}`
- `GET /channel-info?gate1=10&gate2=20`

### Quan hệ

Gọi `/compare-charts` cho composite cơ bản hoặc `/analyze-relationship` cho phân tích quan hệ chuyên sâu có thông tin đối phương.

## 5. Nội dung hướng dẫn Custom GPT

Có thể copy `custom_gpt_instructions.txt`. Nguyên tắc chính:

- Luôn gọi API, không tự đoán Type/Authority/Profile/Gates.
- Với phân tích đầy đủ, gọi chart trước rồi gọi analyzer/domain phù hợp.
- Giải thích bằng tiếng Việt, ưu tiên Strategy + Authority và ví dụ thực tế.
- Nhắc rằng giờ sinh không chính xác làm giảm độ tin cậy.
- Không biến kết quả thành chẩn đoán y khoa, khuyến nghị đầu tư, pháp lý hoặc phán xét con người.

## 6. Xử lý lỗi thường gặp

| Hiện tượng | Cách kiểm tra |
|---|---|
| Action không import được | Mở `/openapi.json`, kiểm tra HTTPS và schema hợp lệ |
| API không gọi được | Kiểm tra public URL, port binding `0.0.0.0`, reverse proxy và firewall |
| Kết quả thiếu domain | Kiểm tra import path `tools/` và dependency trong `requirements.txt` |
| PNG/PDF BodyGraph lỗi | Cài Python `cairosvg` và system package `libcairo2` |
| Browser báo CORS | Kiểm tra cấu hình CORS/reverse proxy; không hard-code localhost trong client |

## File liên quan

- `openapi_server.py`: FastAPI app.
- `custom_gpt_instructions.txt`: hướng dẫn LLM.
- `../requirements.txt`: dependency chuẩn.
- `../README.md`: hướng dẫn vận hành tổng thể.
- `README.md`: MCP stdio và resource/tool contract.
