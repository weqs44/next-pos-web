"""Verifikasi email manajer: token bertanda tangan (tanpa tabel baru) dan pengiriman email."""
import logging
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.models import User
from django.core import signing
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
SALT = 'nextpos.email-verification'


def make_token(user):
    return signing.dumps({'u': user.pk, 'e': user.email}, salt=SALT)


def user_for_token(token):
    """User untuk token yang valid dan belum kedaluwarsa; selain itu None."""
    if not isinstance(token, str) or not token or len(token) > 500:
        return None
    try:
        data = signing.loads(token, salt=SALT, max_age=settings.EMAIL_VERIFY_TTL_HOURS * 3600)
    except signing.BadSignature:  # termasuk SignatureExpired
        return None
    if not isinstance(data, dict):
        return None
    user = User.objects.filter(pk=data.get('u')).first()
    # Token hanya berlaku untuk alamat email yang sama dengan saat token dibuat.
    if user is None or user.email != data.get('e'):
        return None
    return user


def verification_link(user):
    base = settings.FRONTEND_BASE_URL.rstrip('/')
    return f"{base}/?verify={quote(make_token(user), safe='')}"


def send_verification_email(user):
    """Kirim email verifikasi. True bila terkirim; kegagalan dicatat di log dan tidak melempar error."""
    message = (
        f"Halo {user.first_name or 'Manajer'},\n\n"
        "Terima kasih telah mendaftar di NEXT POS. Buka tautan berikut untuk memverifikasi email Anda:\n\n"
        f"{verification_link(user)}\n\n"
        f"Tautan berlaku {settings.EMAIL_VERIFY_TTL_HOURS} jam. "
        "Jika Anda tidak merasa mendaftar, abaikan email ini.\n\n"
        "NEXT POS"
    )
    try:
        send_mail('Verifikasi email NEXT POS', message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception:
        logger.exception('Gagal mengirim email verifikasi (user id=%s)', user.pk)
        return False
    return True
