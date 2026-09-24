# Dùng database Supabase (PostgreSQL) cho Human Design Admin

App đọc kết nối CSDL từ biến `DATABASE_URL` trong file `.env` (`backend/api/settings.py`).
Mặc định là SQLite (`var/hd_dev.sqlite3`). Muốn dùng Supabase thì trỏ `DATABASE_URL` sang Postgres của Supabase.

## 1. Chuỗi kết nối đúng cho project này

Supabase cho bạn chuỗi dạng (pooler):

```text
postgresql://postgres.anfqnmwmojmsrgjbvxul:[YOUR-PASSWORD]@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

**Không paste nguyên xi.** Project dùng driver `psycopg` (v3) qua SQLAlchemy, nên phải sửa 3 chỗ:

1. Thêm `+psycopg` sau `postgresql` → `postgresql+psycopg://...`
2. Thay `[YOUR-PASSWORD]` bằng mật khẩu database thật (Supabase Dashboard → Project Settings → Database → Database password, nút Reveal/Reset nếu quên)
3. Thêm `?sslmode=require` ở cuối (Supabase bắt buộc SSL)

Kết quả:

```text
DATABASE_URL=postgresql+psycopg://postgres.anfqnmwmojmsrgjbvxul:MAT-KHAU-THAT@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require
```

> Giữ cổng `5432` (Session mode) cho `alembic` và app. Cổng `6543` (Transaction mode) không chạy được DDL/migration ổn định, chỉ dùng khi bạn đã hiểu rõ pooler.

### Mật khẩu có ký tự đặc biệt?

Nếu mật khẩu chứa `@ : / # % ? &` thì phải URL-encode, nếu không sẽ báo lỗi xác thực. Chạy:

```bash
python3 -c "import urllib.parse; print(urllib.parse.quote_plus(input('password: ')))"
```

rồi paste kết quả vào vị trí mật khẩu. Ví dụ `ab@c:d` → `ab%40c%3Ad`.

## 2. Tạo file `.env`

Trong thư mục repo:

```bash
cp .env.example .env
nano .env
```

Nội dung tối thiểu khi dev với Supabase:

```dotenv
HD_ENV=development
DATABASE_URL=postgresql+psycopg://postgres.anfqnmwmojmsrgjbvxul:MAT-KHAU-THAT@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres?sslmode=require
SESSION_HOURS=12
HD_SECRET_KEY=
```

Giải thích:

| Biến | Để gì khi dùng Supabase |
| --- | --- |
| `HD_ENV` | `development` khi chạy máy cá nhân; `production` khi chạy VPS thật (cookie chỉ gửi qua HTTPS, không tự tạo bảng) |
| `DATABASE_URL` | Chuỗi ở mục 1 |
| `HD_SECRET_KEY` | Chuỗi ngẫu nhiên dài ở production (`python3 -c "import secrets;print(secrets.token_urlsafe(48))"`). Dev có thể để trống (app tự tạo `var/secret_key`) |
| `SESSION_HOURS` | Thời gian phiên đăng nhập, mặc định 12 |

> Không commit `.env`. File này đã có trong `.gitignore`.

## 3. Cài thư viện và tạo bảng

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# Tạo bảng trên Supabase (bắt buộc, chạy trước mọi thứ khác)
.venv/bin/alembic upgrade head
# Kỳ vọng: Running upgrade -> 0001 ... 0002 ... 0003
```

Vào Supabase Dashboard → **Table Editor** sẽ thấy các bảng mới: `organizations`, `users`, `clients`, `reports`, `report_versions`, `share_links`, ...

## 4. Tạo tài khoản admin

```bash
.venv/bin/python -m backend.api.cli create-admin --email ban@studio.vn --name "Tên của bạn" --org "Tên studio"
# nhập mật khẩu ≥ 8 ký tự khi được hỏi
```

Phải chạy `alembic upgrade head` **trước**. Nếu chạy `create-admin` trước sẽ báo *“Chưa có bảng dữ liệu…”*.

Đặt lại mật khẩu admin sau này thì chạy lại đúng lệnh trên với cùng email.

## 5. Chạy app

```bash
# Terminal 1: API
.venv/bin/uvicorn backend.api.main:app --host 127.0.0.1 --port 8001

# Terminal 2: Web
cd web && npm install && npm run dev
# mở http://localhost:3000
```

Kiểm tra nhanh:

```bash
curl -s http://127.0.0.1:8001/api/v1/health
# {"status":"ok","environment":"development"}
```

Tài liệu API: `http://127.0.0.1:8001/api/v1/docs`.

## 6. Test kết nối nhanh (không cần chạy app)

```bash
.venv/bin/python - <<'PY'
from sqlalchemy import create_engine, text
from backend.api.settings import Settings
url = Settings.from_env().database_url
print("đang kết nối tới:", url.split("@")[-1])
engine = create_engine(url)
with engine.connect() as conn:
    print("server_version:", conn.execute(text("show server_version")).scalar())
    print("bảng hiện có:", conn.execute(text(
        "select count(*) from information_schema.tables where table_schema='public'"
    )).scalar())
PY
```

## 7. Chuyển đổi qua lại SQLite ↔ Supabase

- Dùng Supabase: mở `.env`, bật dòng `DATABASE_URL=postgresql+psycopg://...`
- Về SQLite dev: comment dòng đó lại (`# DATABASE_URL=...`), app tự dùng `var/hd_dev.sqlite3`
- Mỗi lần đổi CSDL nhớ chạy lại `alembic upgrade head` + `create-admin` trên CSDL đó

## 8. Lỗi thường gặp

| Lỗi | Nguyên nhân / cách sửa |
| --- | --- |
| `No module named 'psycopg2'` hoặc `Can't load plugin: sqlalchemy.dialects:driver` | Quên `+psycopg`. Chuỗi phải bắt đầu bằng `postgresql+psycopg://` |
| `password authentication failed` | Sai mật khẩu, hoặc mật khẩu có ký tự đặc biệt chưa URL-encode (xem mục 1). Kiểm tra lại trong Supabase → Database settings |
| `SSL connection is required` / `sslmode` | Thiếu `?sslmode=require` ở cuối URL |
| `connection timed out` / lỗi IPv6 | Đừng dùng `db.xxxxx.supabase.co` (Direct, hay cần IPv6). Dùng host `....pooler.supabase.com` như chuỗi Supabase cấp |
| `alembic` treo/lỗi trên cổng `6543` | Đổi sang cổng `5432` (Session mode) để chạy migration |
| `Chưa có bảng dữ liệu` khi `create-admin` | Chưa chạy `.venv/bin/alembic upgrade head` |
| Supabase báo hết connection | App dev chỉ chạy 1 worker uvicorn; đừng mở quá nhiều process cùng lúc vào gói free |

## 9. Lưu ý production

- Đặt `HD_ENV=production` + `HD_SECRET_KEY` dài ngẫu nhiên, `chmod 600 .env`
- Sao lưu: Supabase đã tự backup theo gói, nhưng trước khi deploy bản lớn vẫn nên dump tay: `pg_dump "$DATABASE_URL" -Fc -f backup.dump` (cần `postgresql-client`)
- Không chia sẻ `.env` / mật khẩu database; mỗi người nên có user riêng trong Supabase nếu cần
