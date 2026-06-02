from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django.contrib.auth import get_user_model, authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    UserLoginSerializer, UserPasswordChangeSerializer, UserRoleUpdateSerializer,
    UserStatsSerializer
)
from .permissions import IsAdminOrSelf, IsCompanyAdmin

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset"""
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'company', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'last_login', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['list', 'destroy', 'update_role']:
            return [IsAdminUser()]
        elif self.action == 'me':
            return [IsAuthenticated()]
        return [IsAdminOrSelf()]
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """User login - returns JWT tokens + user data"""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, email=email, password=password)
        
        if user:
            if not user.is_active:
                return Response(
                    {'error': 'Account is inactive'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user.record_login(request.META.get('REMOTE_ADDR'))
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)
            return Response({
                'user': user_serializer.data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Login successful'
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Can only change own password'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UserPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdminUser])
    def update_role(self, request, pk=None):
        """Admin: Update user role"""
        user = self.get_object()
        serializer = UserRoleUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Get user statistics"""
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True, status='active').count(),
            'company_users': User.objects.filter(company__isnull=False).count(),
            'individual_users': User.objects.filter(company__isnull=True).count(),
            'pending_verification': User.objects.filter(status='pending_verification').count(),
            'users_by_role': dict(User.objects.values_list('role').annotate(
                count=models.Count('id')
            ))
        }
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse


class HealthCheckView(APIView):
    """Health check endpoint for Kubernetes"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Basic health check"""
        return JsonResponse({
            'service': 'user-management',
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected' if self.check_db() else 'error',
            'redis': 'connected' if self.check_redis() else 'error'
        })
    
    def check_db(self):
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            return False
    
    def check_redis(self):
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', timeout=5)
            return cache.get('health_check') == 'ok'
        except:
            return False


from django.utils import timezone
import django.db.models as models
