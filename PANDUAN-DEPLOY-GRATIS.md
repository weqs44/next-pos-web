# Panduan deploy gratis dari nol (tanpa domain)

Hasil akhir: aplikasi bisa dibuka di `https://<nama>.vercel.app`, API di `https://<nama>.onrender.com`, email verifikasi lewat Brevo, database MySQL gratis. Tidak perlu membeli domain.

Batasan paket gratis: backend Render tidur setelah 15 menit tanpa trafik (bangun ±1 menit). Cocok untuk uji coba/demo, kurang nyaman untuk kasir harian.

## 0. Persiapan
- Pasang **Git for Windows** (git-scm.com). Siapkan email aktif.
- Ganti rahasia lama: App Password Gmail yang pernah ada di `.env` lama dicabut (Akun Google → Keamanan → Sandi aplikasi). Jalur ini tidak memakainya lagi.

## 1. Repo GitHub (dipegang teman Anda)
Teman Anda yang meng-commit, jadi Anda tidak perlu push apa pun. Yang perlu disepakati:
1. Teman memasukkan perubahan di `perubahan-untuk-teman.patch` ke repo (`git apply perubahan-untuk-teman.patch`, lalu commit dan push). Isinya: `render.yaml`, `Frontend/vercel.json`, perbaikan `settings.py` dan `gunicorn.conf.py`, serta `.env.example`.
2. Teman memberi Anda akses ke repo (Settings → Collaborators → tambahkan akun GitHub Anda), supaya Render dan Vercel bisa membacanya.
3. Pastikan `.env` tidak pernah ikut ter-commit.

## 2. Database MySQL gratis (TiDB Cloud)
1. Daftar di tidbcloud.com, buat cluster tipe **Starter** (pastikan yang dipilih gratis).
2. Buka tombol **Connect**, catat: **host**, **port (4000)**, **user**, **password**.
3. Buat database di SQL editor: `CREATE DATABASE next_pos;`

## 3. Email (Brevo)
1. Daftar di brevo.com.
2. **Senders** → tambah dan verifikasi alamat pengirim (boleh Gmail Anda).
3. **Settings → SMTP & API → SMTP** → catat **login SMTP** dan buat **SMTP key**.

## 4. Backend di Render
1. Daftar di render.com dengan akun GitHub.
2. **New → Blueprint** → pilih repo `next-pos`. Isi kolom yang diminta:
   - `DB_HOST`, `DB_PORT` (4000), `DB_NAME` (`next_pos`), `DB_USER`, `DB_PASSWORD`
   - `EMAIL_HOST_USER` (login SMTP Brevo), `EMAIL_HOST_PASSWORD` (SMTP key)
   - `DEFAULT_FROM_EMAIL`: `NEXT POS <alamat-sender-brevo>`
   - `FRONTEND_BASE_URL` dan `CORS_ALLOWED_ORIGINS`: isi dulu `https://placeholder.vercel.app` (diperbaiki di langkah 6)
3. Tunggu deploy selesai, lalu buka `https://<layanan>.onrender.com/api/health/` → harus `{"status":"ok",...}`.

## 5. Frontend di Vercel
1. Daftar di vercel.com dengan akun GitHub → **Add New → Project** → pilih repo.
2. **Root Directory = `Frontend`**.
3. Environment Variables: `VITE_API_BASE_URL` = `https://<layanan>.onrender.com/api`
4. Deploy. Catat alamat `https://<app>.vercel.app`.

## 6. Hubungkan
Di Render → Environment, ubah `FRONTEND_BASE_URL` dan `CORS_ALLOWED_ORIGINS` menjadi alamat Vercel yang asli (tanpa garis miring di akhir). Simpan, tunggu redeploy.

## 7. Uji
1. Buka alamat Vercel → daftar manajer dengan email asli → buka link verifikasi di email (cek spam) → masuk.
2. Tambah menu, tambah kasir, login kasir, mulai shift, buat satu transaksi.
3. Setelah akun yang dibutuhkan ada, tutup pendaftaran: `ALLOW_REGISTRATION=0` di Render.

## Opsional: cegah backend tidur
Pasang monitor gratis (mis. UptimeRobot) yang memanggil `/api/health/` tiap 5 menit. Satu layanan menyala 24 jam masih muat di jatah 750 jam/bulan Render.

## Jika ada masalah
| Gejala | Cek |
|---|---|
| Build Render gagal "ImproperlyConfigured" | Ada variabel wajib yang kosong (lihat pesan di log) |
| Health check 503 | `DB_*` salah, `DB_PORT` bukan 4000, atau TLS: pastikan `DB_SSL=1` |
| Frontend "Tidak dapat terhubung ke server" | `VITE_API_BASE_URL` salah (build ulang di Vercel setelah mengubahnya) atau `CORS_ALLOWED_ORIGINS` tidak sama persis dengan alamat Vercel |
| Pertama dibuka lambat/error 503 | Backend sedang bangun, tunggu ±1 menit |
| Email tidak masuk | Cek spam; log Render: "Gagal mengirim email verifikasi"; sender Brevo belum terverifikasi |
