"""
URL configuration for user_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'service': 'User Management Service',
        'version': '1.0.0',
        'description': 'B2B user management (companies and rentals apps coming soon)',
        'endpoints': {
            'admin': '/admin/',
            'users': '/api/v1/users/',
            # 'companies': '/api/v1/companies/',  # Coming soon
            # 'rentals': '/api/v1/rentals/',      # Coming soon
            'health': '/health/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/v1/users/', include('src.users.urls')),
    # path('api/v1/companies/', include('src.companies.urls')),  # Coming soon
    # path('api/v1/rentals/', include('src.rentals.urls')),      # Coming soon
]
