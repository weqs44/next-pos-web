# NEXT-POS Backend

Backend aplikasi **NEXT-POS** (Point of Sale): Django + Django REST Framework + MySQL. Menyediakan API untuk autentikasi, karyawan, shift, menu, dan transaksi.

## Tech Stack

- Python 3.12 – 3.13
- Django 5.2 LTS, Django REST Framework
- MySQL 8 (SQLite didukung untuk pengembangan/tes)
- gunicorn + WhiteNoise untuk produksi

## Pengembangan lokal

```bash
cd Backend
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1      Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env        # Windows: Copy-Item .env.example .env
```

Edit `.env` untuk lokal:

```env
DJANGO_DEBUG=1
DB_ENGINE=sqlite            # atau isi kredensial MySQL
```

```bash
python manage.py migrate
python manage.py runserver      # http://127.0.0.1:8000/
```

Jika memakai MySQL: buat database dulu (`CREATE DATABASE next_pos CHARACTER SET utf8mb4;`) dan isi `DB_*` di `.env`.

## Tes

```bash
DJANGO_DEBUG=1 DB_ENGINE=sqlite python manage.py test
```

(PowerShell: `$env:DJANGO_DEBUG="1"; $env:DB_ENGINE="sqlite"; python manage.py test`)

## Aturan penting API

- Nominal transaksi (harga, diskon, pajak, total) **dihitung server** dari harga menu di database. Klien hanya mengirim `lines: [{productId, qty}]`, `discount: {type: "percent"|"amount", value}`, `orderType`, `guestCount`.
- Token kedaluwarsa setelah `TOKEN_TTL_DAYS` (30 hari); token kasir dicabut saat dinonaktifkan atau kata sandinya direset.
- Login dan pendaftaran dibatasi lajunya (rate limit). Kata sandi minimal 8 karakter dan tidak boleh umum/angka saja.

## Produksi

Lihat [`../DEPLOY.md`](../DEPLOY.md). Ringkasnya: `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` acak (aplikasi menolak start tanpa itu), HTTPS di depan aplikasi, `migrate`, `collectstatic`, jalankan dengan gunicorn.

## Struktur

```text
Backend/
├── core/            # models, serializers, views, authentication, tests, migrations
├── nextpos/         # settings, urls, wsgi/asgi
├── Dockerfile
├── gunicorn.conf.py
├── .env.example
├── manage.py
└── requirements.txt
```
