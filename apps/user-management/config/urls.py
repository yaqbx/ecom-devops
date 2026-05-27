"""
URL configuration for user_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView
from django.utils import timezone

@require_GET
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception:
        db_status = "error"
    return JsonResponse({
        'service': 'user-management',
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': db_status,
    })

def api_root(request):
    return JsonResponse({
        'service': 'User Management Service',
        'version': '1.0.0',
        'description': 'B2B user management (companies and rentals apps coming soon)',
        'endpoints': {
            'admin': '/admin/',
            'users': '/api/v1/users/',
            'token': '/api/v1/token/',
            'health': '/health/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('src.users.urls')),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('health/', health_check, name='health'),
]
