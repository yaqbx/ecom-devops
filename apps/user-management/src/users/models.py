from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
# from django.utils import timezone
from django.utils import timezone as django_timezone 
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for B2B heavy equipment platform"""
    
    ROLE_CHOICES = [
        ('admin', 'Platform Administrator'),
        ('company_admin', 'Company Administrator'),
        ('company_manager', 'Company Manager'),
        ('company_operator', 'Equipment Operator'),
        ('customer', 'Individual Customer'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending_verification', 'Pending Verification'),
    ]
    
    email = models.EmailField(unique=True, verbose_name='Email Address')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20, blank=True)
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_verification')
    
    # Company association - temporarily disabled (Company app not yet implemented)
    # company = models.ForeignKey(
    #     'companies.Company',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='employees'
    # )
    company = None  # Placeholder
    is_company_admin = models.BooleanField(default=False)
    
    # Profile
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Address
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Poland')
    
    # Preferences
    newsletter_subscribed = models.BooleanField(default=False)
    notification_email = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='Europe/Warsaw')
    
    # Verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    identity_verified = models.BooleanField(default=False)
    
    # Security
    login_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=django_timezone.now)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Django admin fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=django_timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'
    ordering = ['-date_joined']
    indexes = [
        models.Index(fields=['email']),
        # models.Index(fields=['company']),  # Removed - Company app not implemented yet
        models.Index(fields=['role']),
        models.Index(fields=['status']),
    ]
    
    def __str__(self):
        return f"{self.email} ({self.get_full_name()})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_company_user(self):
        return False  # Company app not implemented yet
    
    @property
    def can_rent_equipment(self):
        return self.status == 'active' and self.email_verified
    
    def record_login(self, ip_address=None):
        self.last_login = django_timezone.now()
        self.login_attempts = 0
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=['last_login', 'login_attempts', 'last_login_ip'])
