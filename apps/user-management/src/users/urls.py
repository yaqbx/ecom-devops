from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, HealthCheckView

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health'),
]
