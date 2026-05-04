from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

# Forward reference - will be implemented later
# from src.companies.models import Company


# Temporarily disabled - Company model not yet implemented
# class CompanyBriefSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Company
#         fields = ['id', 'name', 'tax_id', 'is_verified']


class UserSerializer(serializers.ModelSerializer):
    """Full user serializer"""
    # company = CompanyBriefSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'role_display', 'status', 'status_display',
            # 'company',
            'is_company_admin', 'job_title', 'department',
            'avatar', 'city', 'country', 'date_joined', 'last_login',
            'can_rent_equipment', 'is_active'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'can_rent_equipment']


class UserCreateSerializer(serializers.ModelSerializer):
    """User creation serializer with password"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'password', 'password_confirm', 'role'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update serializer"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'job_title',
            'department', 'address_line1', 'address_line2',
            'city', 'postal_code', 'country', 'avatar',
            'newsletter_subscribed', 'notification_email',
            'notification_sms', 'language', 'timezone'
        ]


class UserLoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserPasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return data


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """Admin serializer for updating user roles"""
    class Meta:
        model = User
        fields = ['role', 'is_company_admin', 'status']


class UserStatsSerializer(serializers.Serializer):
    """User statistics serializer"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    company_users = serializers.IntegerField()
    individual_users = serializers.IntegerField()
    pending_verification = serializers.IntegerField()
    users_by_role = serializers.DictField()
