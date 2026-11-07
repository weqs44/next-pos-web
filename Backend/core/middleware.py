from ipaddress import ip_address
from urllib.parse import urlsplit


class InternalHealthProbeHostMiddleware:
    """Normalize private-IP Host headers used by the platform's internal health probes only."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/health/":
            raw_host = request.META.get("HTTP_HOST", "")
            try:
                host = urlsplit("//" + raw_host).hostname
                address = ip_address(host) if host else None
            except ValueError:
                address = None

            if address is not None and address.is_private:
                # localhost is explicitly included in ALLOWED_HOSTS.
                request.META["HTTP_HOST"] = "localhost"

        return self.get_response(request)
