from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed


def token_is_expired(token):
    ttl = getattr(settings, 'TOKEN_TTL_DAYS', 0)
    if not ttl or ttl <= 0:
        return False
    return token.created < timezone.now() - timedelta(days=ttl)


class ExpiringTokenAuthentication(TokenAuthentication):
    """TokenAuthentication yang menolak token yang sudah lewat TOKEN_TTL_DAYS."""

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token_is_expired(token):
            token.delete()
            raise AuthenticationFailed('Sesi berakhir. Silakan masuk lagi.')
        return user, token


def issue_token(user):
    """Ambil token aktif milik user; jika sudah kedaluwarsa, buang dan terbitkan yang baru."""
    token = Token.objects.filter(user=user).first()
    if token and token_is_expired(token):
        token.delete()
        token = None
    if token is None:
        token, _ = Token.objects.get_or_create(user=user)  # aman bila dua login bersamaan
    return token
