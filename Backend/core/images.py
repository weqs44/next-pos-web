"""Penyajian gambar menu sebagai URL ber-cache, bukan data URL di dalam JSON.

Gambar menu tetap disimpan apa adanya di kolom Product.image. Yang berubah hanya cara mengirimnya:
JSON (bootstrap/produk) memuat URL pendek bertanda tangan, dan browser mengunduh gambarnya terpisah
sekali saja (Cache-Control immutable). Tanda tangan ikut berubah saat gambar diganti, jadi URL baru
otomatis memutus cache lama. Tanda tangan juga mencegah orang menebak URL dari ID produk yang berurutan.

Modul ini hanya memakai pustaka standar supaya mudah diuji.
"""
import base64
import binascii
import hashlib
import hmac
import re

# Hanya tipe raster yang aman disajikan langsung. SVG sengaja tidak termasuk (bisa memuat skrip).
SAFE_MIME_TYPES = frozenset({'image/jpeg', 'image/png', 'image/webp', 'image/gif'})

_DATA_URL_RE = re.compile(r'^data:(image/[a-z0-9.+-]+);base64,', re.IGNORECASE)

# URL gambar buatan kita sendiri. Dipakai untuk mengabaikan URL itu bila klien mengirimnya balik saat edit.
OWN_IMAGE_URL_RE = re.compile(r'/api/products/\d{1,18}/image/[0-9a-f]{32}/?(?:[?#].*)?$')


def servable_prefix(value):
    """True bila nilai berupa data URL base64 bertipe raster aman. Hanya memeriksa awalan (murah, tanpa decode)."""
    if not isinstance(value, str):
        return False
    match = _DATA_URL_RE.match(value)
    return bool(match) and match.group(1).lower() in SAFE_MIME_TYPES


def parse_data_image(value):
    """Kembalikan (mime, bytes) untuk data URL raster yang valid, atau None bila tidak bisa disajikan."""
    if not servable_prefix(value):
        return None
    match = _DATA_URL_RE.match(value)
    try:
        raw = base64.b64decode(value[match.end():], validate=True)
    except (binascii.Error, ValueError):
        return None
    if not raw:
        return None
    return match.group(1).lower(), raw


def signature(secret, product_id, image):
    """Tanda tangan 32 hex yang terikat pada ID produk DAN isi gambar saat ini."""
    digest = hashlib.sha256(image.encode('utf-8')).hexdigest()
    message = f'product-image:{int(product_id)}:{digest}'.encode('utf-8')
    return hmac.new(secret.encode('utf-8'), message, hashlib.sha256).hexdigest()[:32]


def signature_matches(secret, product_id, image, candidate):
    return hmac.compare_digest(signature(secret, product_id, image), candidate)
