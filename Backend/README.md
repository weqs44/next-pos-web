# NEXT-POS Backend

Backend untuk aplikasi **NEXT-POS**, sistem Point of Sale (POS) berbasis Django yang menyediakan API untuk kebutuhan autentikasi, manajemen karyawan, shift, produk, dan transaksi.

## Tech Stack

- Python 3.15
- Django 5.2.18
- Django REST Framework
- MySQL
- Django CORS Headers

## Project Structure

```text
Backend/
├── core/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── apps.py
│
├── nextpos/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── .env.example
├── .gitignore
├── manage.py
└── requirements.txt
```

## Requirements

Pastikan perangkat sudah memiliki:

- Python
- MySQL Server
- Git

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/willfredsh-star/next-pos-web.git
```

Masuk ke folder Backend:

```bash
cd next-pos-web/Backend
```

### 2. Create Virtual Environment

```bash
py -m venv .venv
```

Aktifkan virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Buat file `.env` berdasarkan template yang tersedia:

```powershell
Copy-Item .env.example .env
```

Buka file `.env`, kemudian sesuaikan konfigurasi dengan lingkungan lokal, termasuk kredensial database.

**Jangan mengunggah file `.env` ke repository.**

### 5. Setup Database

Buat database MySQL sesuai nama database yang dikonfigurasi di `.env`.

Contoh:

```sql
CREATE DATABASE next_pos;
```

Pastikan MySQL Server sedang berjalan dan konfigurasi koneksi database sudah benar.

### 6. Run Database Migrations

```bash
python manage.py migrate
```

### 7. Start Development Server

```bash
python manage.py runserver
```

Backend akan berjalan secara default di:

```text
http://127.0.0.1:8000/
```

## Development Notes

- Gunakan virtual environment untuk mengelola dependencies.
- Jangan commit `.env`, `.venv`, atau file database lokal.
- Jika terdapat perubahan pada Django models, buat migration menggunakan:

```bash
python manage.py makemigrations
python manage.py migrate
```

- Setelah melakukan pull perubahan dari repository, periksa apakah ada dependencies atau migrations baru.

## License

This project is developed for the NEXT-POS application.