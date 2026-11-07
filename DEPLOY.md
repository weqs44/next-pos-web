# Panduan Deploy NEXT-POS

Arsitektur yang disarankan: **nginx** (HTTPS, menyajikan frontend statis, meneruskan `/api/`) → **gunicorn** (Django) → **MySQL 8**. Contoh nginx: `deploy/nginx.conf.example`.

## 1. Backend

```bash
cd Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # lalu isi (lihat di bawah)
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn nextpos.wsgi:application --config gunicorn.conf.py
```

`.env` produksi minimal:

```env
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_ALLOWED_HOSTS=pos.example.com
CSRF_TRUSTED_ORIGINS=https://pos.example.com
DB_ENGINE=mysql
DB_NAME=next_pos
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
```

Verifikasi email manajer (aktif secara default) butuh server SMTP, jadi tambahkan juga ke `.env`:

```env
FRONTEND_BASE_URL=https://pos.example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=NEXT POS <noreply@pos.example.com>
```

Catatan:
- Aplikasi **menolak start** jika `DJANGO_DEBUG=0` dan `DJANGO_SECRET_KEY` kosong/lemah.
- Di belakang nginx: `DJANGO_NUM_PROXIES=1` (bawaan di produksi) supaya rate limit membaca IP klien yang benar; nginx harus mengirim `X-Forwarded-For` dan `X-Forwarded-Proto` (sudah ada di contoh).
- Gunicorn bawaan: 1 worker dengan 4 thread (`GUNICORN_THREADS`) bila `CACHE_DB_TABLE` kosong, supaya hitungan rate limit tidak terpecah per worker. Untuk memakai lebih dari 1 worker (`WEB_CONCURRENCY`, bawaan 3 bila `CACHE_DB_TABLE` diisi): isi `CACHE_DB_TABLE=nextpos_cache` lalu jalankan `python manage.py createcachetable` agar hitungan dibagi antar worker.
- Admin Django mati secara default di produksi (`DJANGO_ENABLE_ADMIN=1` untuk menyalakan; buat superuser dengan `python manage.py createsuperuser`).
- **Verifikasi email:** manajer baru menerima tautan (berlaku 48 jam) dan baru bisa masuk setelah membukanya; kasir tidak perlu karena dibuat oleh manajer. Aplikasi menolak start jika verifikasi aktif tetapi `EMAIL_HOST`, `DEFAULT_FROM_EMAIL`, atau `FRONTEND_BASE_URL` kosong. Set `REQUIRE_EMAIL_VERIFICATION=0` untuk mematikannya. Akun yang sudah ada sebelum fitur ini otomatis dianggap terverifikasi (migrasi 0009). Agar email tidak masuk spam, pasang SPF/DKIM di domain pengirim sesuai petunjuk penyedia SMTP.
- Untuk menutup pendaftaran manajer baru setelah akun yang dibutuhkan dibuat: `ALLOW_REGISTRATION=0`.
- Healthcheck: `GET /api/health/` (200 jika DB terhubung, 503 jika tidak).

Docker (opsional): `docker build -t next-pos-api Backend` lalu jalankan dengan `--env-file Backend/.env`; jalankan `python manage.py migrate` sebagai perintah terpisah.

## 2. Frontend

```bash
cd Frontend
cp .env.example .env     # VITE_API_BASE_URL=/api bila satu domain dengan API
npm ci
npm run typecheck
npm run build            # hasil di Frontend/dist
```

Salin isi `Frontend/dist` ke root web nginx. `VITE_API_BASE_URL` tertanam saat build: ubah nilainya = build ulang.

## 3. Setelah deploy

1. Buka `https://<domain>/api/health/` → `{"status":"ok"}`.
2. Daftar manajer memakai email asli, buka tautan verifikasi di email, lalu masuk (ini sekaligus menguji SMTP).
3. Tambah menu, tambah kasir, login kasir, buat satu transaksi uji.
4. Jadwalkan **backup MySQL** harian dan uji pemulihannya.
5. Pantau log gunicorn (stdout) dan pasang monitoring uptime pada `/api/health/`.

## Yang belum ada (sengaja di luar perbaikan ini)

- CAPTCHA pada pendaftaran (saat ini dibatasi rate limit, diverifikasi lewat email, dan bisa ditutup dengan `ALLOW_REGISTRATION=0`).
- Lupa kata sandi lewat email (saat ini manajer mengatur ulang sandi kasir; belum ada reset sandi untuk manajer).
- Pajak per-restoran (saat ini satu tarif global `POS_TAX_RATE`).
- Struk/laporan per menu (data baris pesanan sudah tersimpan di tabel `TransactionItem`, belum ditampilkan di UI).
- Mode offline untuk pembayaran.

## Alternatif gratis: Vercel + Render + Brevo

Berkas siap pakai: `render.yaml` (backend) dan `Frontend/vercel.json`. Batasan paket gratis Render: layanan tidur setelah 15 menit tanpa trafik (bangun ±1 menit), dan port SMTP 25/465/587 diblokir — karena itu email memakai Brevo di port 2525.

1. **Database MySQL** (gratis dari penyedia terkelola, mis. TiDB Cloud): buat database `next_pos`, catat host, port, user, password. Bila port-nya bukan 3306, ubah `DB_PORT` di Render. `DB_SSL=1` sudah diset di `render.yaml`.
2. **Backend (Render):** New → Blueprint → pilih repo ini. Isi variabel bertanda `sync: false` di dashboard. `DJANGO_ALLOWED_HOSTS` tidak perlu diisi (hostname Render diizinkan otomatis).
3. **Frontend (Vercel):** import repo, **Root Directory = `Frontend`**, tambahkan env `VITE_API_BASE_URL=https://<nama-layanan>.onrender.com/api`, lalu Deploy.
4. Kembali ke Render: isi `CORS_ALLOWED_ORIGINS` dan `FRONTEND_BASE_URL` dengan alamat Vercel (`https://<app>.vercel.app`), simpan (redeploy otomatis).
5. Email: buat SMTP key di Brevo (Settings → SMTP & API), isi `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` (alamat sender yang sudah diverifikasi di Brevo).
6. Tes: `https://<nama-layanan>.onrender.com/api/health/`, lalu daftar manajer dan buka link verifikasi.
