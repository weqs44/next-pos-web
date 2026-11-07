from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Samakan format error 429 dengan error lain ({'error': ...}) dan berikan pesan berbahasa Indonesia."""
    response = exception_handler(exc, context)
    if response is not None and response.status_code == 429:
        response.data = {'error': 'Terlalu banyak percobaan. Coba lagi beberapa saat lagi.'}
    return response
