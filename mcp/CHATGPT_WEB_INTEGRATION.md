# TÍCH HỢP HUMAN DESIGN VỚI CHATGPT BẢN WEB - HƯỚNG DẪN CHI TIẾT

> ChatGPT bản web (chat.openai.com) KHÔNG hỗ trợ MCP trực tiếp như Claude Desktop, nhưng có 3 cách tích hợp chính thức

---

## 🔍 TÌNH TRẠNG HIỆN TẠI (2026)

| Nền tảng | Hỗ trợ MCP trực tiếp? | Cách tích hợp |
|----------|----------------------|---------------|
| **Claude Desktop** | ✅ Có - Native MCP | Dùng `mcp_config.json` |
| **Claude Web** | ✅ Có (từ 2025) | MCP Connectors |
| **Cursor / Windsurf** | ✅ Có | MCP Config |
| **ChatGPT Web (Free)** | ❌ Không | Cần workaround qua Custom GPT Actions |
| **ChatGPT Plus / Pro** | ⚠️ Gián tiếp | Custom GPT + Actions (OpenAPI) |
| **ChatGPT Team/Enterprise** | ⚠️ Gián tiếp | Custom GPT + Actions + API |
| **OpenAI API** | ✅ Có (Function Calling) | Dùng API server như function |

**Kết luận:** ChatGPT bản web thường KHÔNG thể thêm MCP Server như Claude, nhưng **ChatGPT Plus** có thể tích hợp qua **Custom GPT Actions** - đây là cách chính thức và mạnh nhất.

---

## ✅ CÁCH 1: CUSTOM GPT + ACTIONS (KHUYÊN DÙNG - Cho ChatGPT Plus/Pro)

Đây là cách chính thức OpenAI khuyến nghị để tích hợp API bên ngoài vào ChatGPT web.

### Bước 1: Deploy API Server

Bạn đã có sẵn `openapi_server.py` - FastAPI server chuyển đổi MCP Tools thành REST API.

**Chạy local + ngrok:**

```bash
cd /home/user/human_design/mcp
pip install fastapi uvicorn
python openapi_server.py
# Server chạy tại http://localhost:8000

# Mở terminal khác, chạy ngrok để có public URL
ngrok http 8000
# -> https://abc123.ngrok.io
```

**Hoặc deploy lên cloud miễn phí:**
- Railway: `railway up`
- Render: `render.com`
- Fly.io: `fly deploy`
- Vercel: `vercel deploy`

Sau khi deploy, bạn sẽ có URL public, ví dụ: `https://human-design-api.yourdomain.com`

### Bước 2: Lấy OpenAPI Spec

Mở: `https://your-public-url.com/openapi.json`

Hoặc local: `http://localhost:8000/openapi.json`

Lưu file này lại.

### Bước 3: Tạo Custom GPT

1. Vào https://chat.openai.com/gpts/editor
2. Chọn **Create a GPT**
3. Tab **Configure**:
   - Name: `Human Design Analyzer`
   - Description: `Chuyên gia Human Design - Tính toán và phân tích BodyGraph chính xác bằng Swiss Ephemeris`
   - Instructions: Copy từ file `custom_gpt_instructions.txt` (bên dưới)
   - Conversation starters:
     - `Phân tích Human Design cho tôi sinh 1990-05-15 lúc 08:30 ở Hà Nội`
     - `Tra cứu Gate 10 là gì?`
     - `So sánh mối quan hệ 2 người`

4. Kéo xuống **Actions** -> **Create new action**
   - Chọn **Import from URL** -> dán URL `https://your-public-url.com/openapi.json`
   - Hoặc **Import** file `openapi.json` local
   - OpenAI sẽ tự parse thành các actions: calculate-chart, analyze-deep, gate-info, v.v.

5. Trong **Authentication**: Chọn **None** (hoặc API Key nếu bạn set)

6. **Privacy Policy**: Dán URL `https://your-public-url.com` hoặc để trống nếu test

7. Save -> Chọn **Only me** hoặc **Public**

### Bước 4: Sử dụng

Vào Custom GPT vừa tạo, chat:

```
Phân tích Human Design cho Nguyễn Văn A sinh 1990-05-15 lúc 08:30 ở Hà Nội
```

ChatGPT sẽ tự động gọi API `calculate-chart` và `analyze-deep` để lấy dữ liệu chính xác và phân tích!

### File hướng dẫn Custom GPT

Tạo file `custom_gpt_instructions.txt`:

```
Bạn là chuyên gia Human Design chuyên sâu 20 năm kinh nghiệm, được trang bị API tính toán chính xác bằng Swiss Ephemeris.

QUY TRÌNH BẮT BUỘC khi người dùng yêu cầu phân tích:

1. Khi có ngày giờ sinh:
   - Gọi calculate-chart để tính toán chính xác Type, Authority, Profile, Centers, Channels
   - Sau đó gọi analyze-deep với focus_area=full để có phân tích chuyên sâu
   - Tổng hợp thành báo cáo 7 phần chuẩn

2. Khi hỏi về Gate/Center/Channel/Profile:
   - Gọi gate-info, center-info, channel-info, profile-info tương ứng

3. Khi hỏi mối quan hệ:
   - Gọi compare-charts

4. Luôn:
   - Dùng tiếng Việt
   - Giải thích dễ hiểu, ví dụ thực tế
   - Nhấn mạnh Strategy + Authority
   - Không phán xét, không có chart xấu
   - Kết thúc bằng hành động thực hành

CẤU TRÚC BÁO CÁO CHUẨN:
- Tóm tắt nhanh (Type, Strategy, Authority, Profile)
- Type & Strategy (30%)
- Authority (20%)
- Centers (20%)
- Channels & Gates (15%)
- Profile & Definition (10%)
- Cross (5%)
- Lời khuyên thực hành

Bạn có API chính xác, đừng đoán, hãy gọi API.
```

---

## ✅ CÁCH 2: OPENAI API + FUNCTION CALLING (Cho Developer)

Nếu bạn dùng OpenAI API (không phải ChatGPT web), bạn có thể tích hợp trực tiếp MCP Tools như Functions.

**Ví dụ Python:**

```python
import openai

# Định nghĩa functions từ MCP Tools
tools = [
  {
    "type": "function",
    "function": {
      "name": "calculate_human_design_chart",
      "description": "Tính toán Human Design chart chính xác...",
      "parameters": {
        "type": "object",
        "properties": {
          "birth_date": {"type": "string", "description": "YYYY-MM-DD"},
          "birth_time": {"type": "string", "description": "HH:MM"},
          "timezone": {"type": "string", "default": "+07:00"},
          "name": {"type": "string"}
        },
        "required": ["birth_date", "birth_time"]
      }
    }
  }
  # ... thêm các tools khác
]

# Gọi ChatGPT với tools
response = openai.chat.completions.create(
  model="gpt-4o",
  messages=[{"role": "user", "content": "Phân tích Human Design cho 1990-05-15 08:30"}],
  tools=tools
)

# Xử lý function call -> gọi hd_calculator.py
# ...
```

File ví dụ: `openai_function_calling_example.py` (sẽ tạo)

---

## ⚠️ CÁCH 3: CHATGPT WEB FREE (Workaround - Không chính thức)

ChatGPT Free không có Custom GPT Actions, nhưng bạn có thể:

### 3a. Dùng ChatGPT với Browser Tool + API

1. Deploy API server public
2. Trong ChatGPT Free, bật **Browsing** hoặc **Code Interpreter**
3. Nói: "Gọi API https://your-url.com/calculate-chart với birth_date=1990-05-15..."
4. ChatGPT sẽ dùng browsing để gọi API (không ổn định)

### 3b. Copy-Paste

1. Chạy `hd_cli.py` local để tính chart
2. Copy kết quả JSON
3. Paste vào ChatGPT web và nói: "Phân tích JSON này theo Human Design"
4. ChatGPT sẽ phân tích dựa trên JSON (không tự tính được)

**Nhược điểm:** Không tự động, phải làm thủ công.

---

## 🚀 KHUYÊN NGHỊ CHO BẠN

| Bạn đang dùng | Cách tốt nhất |
|---------------|---------------|
| **ChatGPT Plus/Pro ($20/tháng)** | **Cách 1: Custom GPT + Actions** - Mạnh nhất, tự động, chính xác |
| **ChatGPT Free** | Cách 3b: Copy-Paste hoặc nâng cấp lên Plus |
| **Developer (dùng API)** | Cách 2: OpenAI Function Calling |
| **Claude** | Dùng MCP trực tiếp với `mcp_config.json` - Native, tốt nhất |

**Nếu bạn dùng ChatGPT Plus:** Tôi khuyên dùng Cách 1, tôi đã chuẩn bị sẵn:
- `openapi_server.py` - API server
- OpenAPI spec tự động tại `/openapi.json`
- Hướng dẫn Custom GPT

Chỉ cần deploy server lên public URL (ngrok miễn phí 5 phút là xong) và tạo Custom GPT!

---

## 📋 CHECKLIST TÍCH HỢP CHATGPT WEB

- [ ] Deploy `openapi_server.py` lên public URL (ngrok/Railway/Render)
- [ ] Kiểm tra `https://your-url.com/docs` hoạt động
- [ ] Lấy `https://your-url.com/openapi.json`
- [ ] Tạo Custom GPT tại https://chat.openai.com/gpts/editor
- [ ] Thêm Action với openapi.json
- [ ] Test với câu: "Phân tích Human Design cho 1990-05-15 08:30"
- [ ] Nếu thành công, ChatGPT sẽ gọi API và trả về báo cáo chính xác!

---

## 🆘 HỖ TRỢ

Nếu gặp lỗi:
- **Action không gọi được:** Kiểm tra CORS (đã thêm trong openapi_server.py), kiểm tra public URL có truy cập được không
- **ChatGPT Free:** Không có Actions, phải dùng Plus hoặc copy-paste
- **Ngrok URL hết hạn:** Ngrok free URL đổi mỗi lần chạy, cần update lại trong Custom GPT

---

## 📁 FILE LIÊN QUAN

- `openapi_server.py` - FastAPI server cho ChatGPT Actions
- `mcp_config.json` - Cho Claude Desktop (không dùng cho ChatGPT)
- `server.py` - MCP Server gốc (cho Claude)
- `CHATGPT_WEB_INTEGRATION.md` - File này

---

*Human Design MCP - ChatGPT Web Integration Guide - 2026-09-23*
