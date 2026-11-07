import os

# Platform seperti Render menetapkan port lewat PORT.
bind = os.getenv('GUNICORN_BIND', f"0.0.0.0:{os.getenv('PORT', '8000')}")
# Hitungan rate limit disimpan di cache. Tanpa CACHE_DB_TABLE, cache hanya per proses, sehingga
# beberapa worker membuat batas login/daftar efektif dikali jumlah worker. Karena itu bawaannya 1 worker
# (dengan beberapa thread, yang berbagi satu cache). Isi CACHE_DB_TABLE untuk memakai lebih banyak worker.
_shared_cache = bool(os.getenv('CACHE_DB_TABLE'))
workers = int(os.getenv('WEB_CONCURRENCY', '3' if _shared_cache else '1'))
threads = int(os.getenv('GUNICORN_THREADS', '4'))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
accesslog = '-'
errorlog = '-'
# Dibelakang nginx/load balancer: percayai header X-Forwarded-* dari proxy.
forwarded_allow_ips = os.getenv('FORWARDED_ALLOW_IPS', '127.0.0.1')
