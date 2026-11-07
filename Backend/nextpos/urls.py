from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [path('api/', include('core.urls'))]

# Admin hanya aktif jika DJANGO_ENABLE_ADMIN=1 (default: hanya saat DEBUG).
if settings.ENABLE_ADMIN:
    urlpatterns.insert(0, path('admin/', admin.site.urls))
