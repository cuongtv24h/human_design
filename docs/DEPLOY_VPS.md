# Hướng dẫn đưa Human Design Admin lên VPS

Tài liệu cho **lần cài đặt đầu tiên** trên VPS riêng (pm2, không Docker). Các lần cập nhật sau chỉ cần
mục 13. Ước tính 45–60 phút.

```
Trình duyệt ──HTTPS──▶ Nginx :443 ──▶ hd-web (Next.js) 127.0.0.1:3000
                                         │  /api/*
                                         ▼
                                      hd-api (FastAPI, 2 worker) 127.0.0.1:8001 ──▶ PostgreSQL
```

Chỉ Nginx mở ra Internet. `hd-web` và `hd-api` chỉ nghe trên `127.0.0.1`.

> Quy ước trong tài liệu: thay `admin.example.com` bằng tên miền thật, còn `hd` là user Linux chạy ứng dụng.
> Lệnh có `sudo` chạy bằng tài khoản quản trị. Lệnh sau `sudo -iu hd` chạy bằng user `hd`.

---

## 0. Chuẩn bị

| Hạng mục | Yêu cầu |
| --- | --- |
| VPS | **Ubuntu 24.04 LTS** (22.04 cũng được), tối thiểu **2 GB RAM**, 20 GB ổ cứng |
| Tên miền | Bản ghi **A** `admin.example.com` trỏ về IP của VPS. Nên tạo trước ~30 phút để DNS kịp cập nhật |
| Mã nguồn | Repo `https://github.com/cuongtv24h/human_design` (công khai). Code mới nhất nằm ở nhánh `main` sau khi merge PR |
| Khóa AI (tùy chọn) | Nhập sau trong giao diện: **Cài đặt → AI / LLM** |

> VPS chỉ có 1 GB RAM thì bước build giao diện dễ hết bộ nhớ. Khi đó tạo swap trước:
> `sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab`

## 1. Cài gói hệ thống

```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install git curl build-essential python3 python3-venv python3-dev \
                    postgresql nginx certbot python3-certbot-nginx fonts-dejavu-core ufw
sudo timedatectl set-timezone Asia/Ho_Chi_Minh

# Node.js 22 LTS + pm2
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt -y install nodejs
sudo npm install -g pm2
node -v    # v22.x
python3 --version   # 3.10 trở lên
```

Vì sao cần các gói này:
- `build-essential`, `python3-dev`: thư viện tính toán thiên văn `pyswisseph` không có bản dựng sẵn, phải biên dịch khi cài.
- `fonts-dejavu-core`: font tiếng Việt cho PDF và Word. Thiếu font này thì xuất PDF sẽ báo lỗi.

## 2. Tường lửa

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'      # cổng 80 + 443
sudo ufw enable
sudo ufw status
```

## 3. User chạy ứng dụng và thư mục

```bash
sudo adduser --system --group --shell /bin/bash --home /home/hd hd
sudo mkdir -p /srv/human_design /srv/backups/human_design
sudo chown -R hd:hd /srv/human_design /srv/backups/human_design
```

## 4. PostgreSQL

```bash
DB_PASS=$(openssl rand -hex 16); echo "Mật khẩu CSDL: $DB_PASS"   # ghi lại để dùng ở bước 6
sudo -u postgres psql -c "CREATE USER hd WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "CREATE DATABASE human_design OWNER hd ENCODING 'UTF8' TEMPLATE template0;"
```

Mật khẩu dạng hex chỉ gồm chữ và số nên đưa thẳng vào URL được, không cần mã hóa ký tự đặc biệt.

## 5. Lấy mã nguồn và cài thư viện

```bash
sudo -iu hd
cd /srv/human_design
git clone https://github.com/cuongtv24h/human_design.git .
git checkout main

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt       # 2–5 phút (biên dịch pyswisseph)

cd web && npm ci && cd ..
```

## 6. File cấu hình `.env`

Vẫn đang là user `hd`, trong `/srv/human_design`:

```bash
SECRET=$(python3 -c "import secrets;print(secrets.token_urlsafe(48))")
cat > .env <<EOF
HD_ENV=production
DATABASE_URL=postgresql+psycopg://hd:DAN_MAT_KHAU_CSDL_O_BUOC_4@127.0.0.1:5432/human_design
HD_SECRET_KEY=$SECRET
SESSION_HOURS=12
ARTIFACT_DIR=/srv/human_design/var/artifacts
EOF
chmod 600 .env
nano .env     # thay DAN_MAT_KHAU_CSDL_O_BUOC_4 bằng mật khẩu thật
```

Giải thích từng dòng:

| Biến | Ý nghĩa |
| --- | --- |
| `HD_ENV=production` | Cookie đăng nhập chỉ gửi qua HTTPS. Không tự tạo bảng: bảng chỉ được tạo bằng migration |
| `DATABASE_URL` | Kết nối PostgreSQL |
| `HD_SECRET_KEY` | Dùng để ký link tải/chia sẻ và **mã hóa khóa AI**. **Không đổi và không làm mất** (xem mục 12) |
| `ARTIFACT_DIR` | Nơi lưu PDF/Word đã tạo sẵn. Đây chỉ là bộ nhớ đệm, có thể xóa |

Không cần `COOKIE_SAMESITE`, vì biến này chỉ dùng cho bản xem trước nhúng iframe.

## 7. Tạo bảng dữ liệu và tài khoản quản trị

```bash
.venv/bin/alembic upgrade head
# → Running upgrade -> 0001 … 0002 … 0003

.venv/bin/python -m backend.api.cli create-admin --email ban@studio.vn --name "Tên của bạn" --org "Tên studio"
# nhập mật khẩu (≥ 8 ký tự) khi được hỏi
```

Phải chạy `alembic upgrade head` **trước**. Nếu chạy `create-admin` trước, lệnh sẽ báo
*“Chưa có bảng dữ liệu…”* và không làm gì.

## 8. Build giao diện và chạy bằng pm2

```bash
cd web && npm run build && cd ..
pm2 start deploy/ecosystem.config.cjs
pm2 save
pm2 install pm2-logrotate    # tự xoay vòng log, tránh đầy ổ cứng
pm2 status          # hd-api và hd-web ở trạng thái "online"
curl -s http://127.0.0.1:3000/api/v1/health    # {"status":"ok","environment":"production"}
exit                # quay về tài khoản quản trị
```

Cho pm2 tự chạy lại sau khi VPS khởi động lại (chạy bằng tài khoản quản trị):

```bash
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u hd --hp /home/hd
sudo -iu hd pm2 save
```

> Tiến trình `hd-gpt-bridge` (kết nối ChatGPT Custom GPT) mặc định **không chạy**. Muốn bật thì chạy
> `HD_GPT_BRIDGE=1 pm2 start deploy/ecosystem.config.cjs` rồi `pm2 save`.

## 9. Nginx và HTTPS

```bash
sudo cp /srv/human_design/deploy/nginx.conf.example /etc/nginx/sites-available/human_design
sudo sed -i 's/admin.example.com/TEN-MIEN-CUA-BAN/g' /etc/nginx/sites-available/human_design
sudo ln -s /etc/nginx/sites-available/human_design /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d TEN-MIEN-CUA-BAN --redirect -m email-cua-ban@vidu.com --agree-tos -n
```

`certbot` tự thêm chứng chỉ HTTPS, tự chuyển hướng từ `http` sang `https`, và tự gia hạn chứng chỉ.
Kiểm tra việc gia hạn bằng lệnh `sudo certbot renew --dry-run`.

## 10. Kiểm tra sau khi cài

Mở `https://TEN-MIEN-CUA-BAN` và làm lần lượt:

1. Đăng nhập bằng tài khoản ở bước 7.
2. **Khách hàng → Thêm khách hàng**: nhập ngày giờ sinh theo giờ Việt Nam.
3. **Tạo báo cáo**: báo cáo ở chế độ nội dung chuẩn phải xong ngay.
4. Tab **Xuất file**: tải PDF và Word, rồi mở ra kiểm tra dấu tiếng Việt.
5. Tab **Chia sẻ**: tạo link, rồi mở link đó bằng **điện thoại** (dùng 4G, không đăng nhập).
6. (Nếu dùng AI) **Cài đặt → AI / LLM**: nhập khóa, bấm **Kiểm tra kết nối**, rồi tạo thử một báo cáo ở chế độ “AI biên tập”.
7. **Tài khoản**: tạo tài khoản cho chuyên viên tư vấn (vai trò coach).

## 11. Sao lưu tự động

```bash
sudo apt -y install postgresql-client     # đã có sẵn nếu cài postgresql trên cùng máy
sudo -iu hd
/srv/human_design/deploy/backup.sh        # chạy thử một lần
crontab -e
# thêm dòng này (2:15 sáng mỗi ngày, giữ 14 ngày):
15 2 * * * /srv/human_design/deploy/backup.sh >> /srv/human_design/var/backup.log 2>&1
```

Mỗi ngày script tạo ra trong `/srv/backups/human_design/`:
- `db-YYYYMMDD-HHMM.dump`: toàn bộ CSDL (khách hàng, báo cáo, lịch sử phiên bản, link chia sẻ, nhật ký).
- `config-…tgz`: file `.env` (chứa `HD_SECRET_KEY` và mật khẩu CSDL).

Nên chép thư mục này ra **ngoài VPS** định kỳ, ví dụ về máy tính của bạn:
`rsync -a hd@IP-VPS:/srv/backups/human_design/ ~/hd-backups/`.

**Khôi phục CSDL** từ một bản sao lưu:

```bash
sudo -iu hd
pm2 stop hd-api
pg_restore --clean --if-exists --no-owner -d "postgresql://hd:MAT_KHAU@127.0.0.1:5432/human_design" /srv/backups/human_design/db-YYYYMMDD-HHMM.dump
pm2 start hd-api
```

## 12. Những điều không được làm

- **Không đổi và không làm mất `HD_SECRET_KEY`.** Nếu đổi, mọi link chia sẻ và link tải đang có sẽ hết hiệu lực, khóa AI đã lưu không đọc được nữa và phải nhập lại, còn đăng nhập thì không bị ảnh hưởng.
- Không commit hay gửi file `.env` cho người khác.
- Không mở cổng 3000, 8001 hay 5432 ra Internet. Tường lửa ở bước 2 đã chặn sẵn.
- Không chạy ứng dụng bằng `root`.

## 13. Cập nhật phiên bản mới

### Lệnh tắt `git up` (cài một lần, dùng mãi)

Trên VPS, chạy **một lần duy nhất** bằng user `hd` để tạo lệnh tắt:

```bash
sudo -iu hd
cd /srv/human_design
git config --global alias.up '!f() { bash deploy/deploy.sh "${1:-$(git rev-parse --abbrev-ref HEAD)}"; }; f'
```

Từ đó về sau, mỗi lần cập nhật chỉ cần **đúng 1 lệnh**:

```bash
sudo -iu hd
cd /srv/human_design
git up            # deploy nhánh hiện tại: pull code → cài lib → migrate → build → restart → kiểm tra
```

Muốn deploy nhánh khác thì thêm tên nhánh: `git up main`.

> `git up` dừng an toàn nếu `.env` thiếu/chưa đúng, hoặc code trên VPS có sửa đổi chưa commit
> (do `git pull --ff-only`). Sửa xong chạy lại `git up` là tiếp tục.

### Thử nhánh test trên VPS rồi gộp vào main

Khi có tính năng mới cần thử trên VPS trước:

```bash
sudo -iu hd
cd /srv/human_design
git up ten-nhanh-test        # VPS chuyển sang chạy nhánh test
git up                       # mỗi khi có code test mới, chạy lại để cập nhật
```

Thử xong, gộp vào `main` (nên tạo Pull Request trên GitHub để có lịch sử), rồi cho VPS về lại nhánh ổn định:

```bash
git up main
```

> File `.env` không nằm trong git nên chuyển nhánh không mất cấu hình (khóa AI, chuỗi kết nối CSDL…).
> Nếu nhánh test có migration mới thì nó sẽ áp vào CSDL chung và không tự gỡ khi quay về `main`
> (thường vô hại — code cũ bỏ qua bảng/cột thừa), nên đừng thử migration nguy hiểm trên CSDL thật.

### Chi tiết các bước (để tham khảo)

Trên máy phát triển, nếu có thể, kiểm tra trước khi đưa lên:

```bash
deploy/check.sh      # chạy test + kiểm tra migration + build giao diện
```

Sau đó trên VPS:

```bash
sudo -iu hd
/srv/human_design/deploy/deploy.sh          # nhánh main; hoặc: deploy.sh ten-nhanh
```

Script làm lần lượt (bước nào không đổi so với lần deploy **thành công** trước sẽ tự bỏ qua):

1. Kiểm tra `.env`.
2. Lấy code mới. Nếu code không đổi gì → chỉ kiểm tra app có đang chạy không rồi xong trong vài giây (không restart).
3. Cài thư viện — chỉ khi `requirements.txt` đổi (hoặc `.venv` bị hỏng).
4. `alembic upgrade head` — chỉ khi có migration mới trong `backend/api/migrations/`.
5. Build giao diện — chỉ khi `web/` đổi; `npm ci` chỉ khi `package-lock.json`/`package.json` đổi.
6. `pm2 startOrReload`.
7. Kiểm tra `/api/v1/health`. Nếu có lỗi, script báo ngay.

Nếu có báo cáo AI đang tạo dở đúng lúc khởi động lại, hệ thống sẽ **tự chạy tiếp** trong khoảng 1–2 phút,
nên không cần chọn giờ vắng người để cập nhật.

Nên sao lưu trước những lần cập nhật lớn: `deploy/backup.sh && deploy/deploy.sh`.

## 14. Xử lý sự cố

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
| --- | --- | --- |
| Trang báo **502 Bad Gateway** | `hd-web` hoặc `hd-api` chưa chạy | `pm2 status`, `pm2 logs hd-api --lines 80`, `pm2 logs hd-web --lines 80` |
| Đăng nhập xong lại bị đẩy về trang đăng nhập | Đang truy cập bằng `http://` hoặc qua IP, trong khi cookie production chỉ gửi qua HTTPS | Dùng đúng `https://tên-miền`, và làm xong bước 9 |
| `pip install` lỗi khi cài `pyswisseph` | Thiếu công cụ biên dịch | `sudo apt install build-essential python3-dev`, rồi cài lại |
| Tải PDF báo lỗi font | Thiếu DejaVu | `sudo apt install fonts-dejavu-core`, rồi `pm2 restart hd-api` |
| `npm run build` bị “Killed” | Hết RAM | Tạo swap (xem mục 0) |
| `alembic upgrade` lỗi xác thực | Sai `DATABASE_URL` | Kiểm tra lại mật khẩu, user và tên CSDL trong `.env` |
| `git up` báo `set: Illegal option -o pipefail` | Alias cũ dùng `sh` (trên Ubuntu là `dash`) | Cài lại alias ở mục 13 (dùng `bash`), rồi chạy lại `git up` |
| Nút “AI biên tập phần này” báo quá thời gian | Nginx cắt kết nối sớm | Giữ `proxy_read_timeout 180s` trong cấu hình Nginx |
| Báo cáo AI “Thất bại: Máy chủ khởi động lại… đã thử 3 lần” | AI lỗi liên tục, hoặc VPS khởi động lại nhiều lần | Kiểm tra **Cài đặt → AI / LLM → Kiểm tra kết nối**, rồi bấm “Tạo lại với cùng tùy chọn” |
| Quên mật khẩu admin | — | `sudo -iu hd; cd /srv/human_design; .venv/bin/python -m backend.api.cli create-admin --email <email cũ>` để đặt lại mật khẩu |

Các lệnh hay dùng:

```bash
pm2 status | pm2 logs | pm2 restart hd-api | pm2 restart hd-web | pm2 monit
sudo tail -f /var/log/nginx/error.log
sudo -u postgres psql human_design -c "select status, count(*) from reports group by 1;"
```

## Danh sách kiểm tra

- [ ] Bản ghi DNS A trỏ đúng IP
- [ ] Gói hệ thống, Node 22 và pm2 đã cài (mục 1)
- [ ] Tường lửa chỉ mở SSH, 80 và 443 (mục 2)
- [ ] Đã tạo CSDL `human_design` với user `hd` (mục 4)
- [ ] `.env` có `HD_ENV=production`, `DATABASE_URL`, `HD_SECRET_KEY`, và `chmod 600` (mục 6)
- [ ] `alembic upgrade head` chạy xong, đã tạo admin (mục 7)
- [ ] `pm2 status` báo online, đã chạy `pm2 startup` và `pm2 save` (mục 8)
- [ ] HTTPS hoạt động, `certbot renew --dry-run` chạy được (mục 9)
- [ ] Đã làm đủ 7 bước kiểm tra ở mục 10
- [ ] Cron sao lưu đã chạy thử, và có bản sao ở ngoài VPS (mục 11)
