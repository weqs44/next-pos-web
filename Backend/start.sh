#!/bin/sh
# Jalankan migrasi hanya jika memang ada yang belum diterapkan.
#
# `migrate` biasa selalu memicu sinyal post_migrate (membuat ulang content type + permission untuk
# semua model), yaitu ratusan query setiap start. Di hosting dengan cold start (mis. Render gratis
# yang tidur setelah 15 menit idle) itu berulang setiap kali service bangun dan menghabiskan
# Request Unit TiDB Cloud. `migrate --check` hanya membaca tabel django_migrations (1 query) dan
# keluar dengan kode != 0 bila ada migrasi tertunda.
set -e

if python manage.py migrate --check >/dev/null 2>&1; then
    echo "Migrasi sudah terbaru, dilewati."
else
    echo "Ada migrasi tertunda, menjalankan migrate..."
    python manage.py migrate --noinput
fi

exec gunicorn nextpos.wsgi:application --config gunicorn.conf.py
