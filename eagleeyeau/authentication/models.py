from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
import string
import uuid


class User(AbstractUser):
    """Custom User Model"""
    
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
        ('Estimator', 'Estimator'),
        ('Project Manager', 'Project Manager'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default='Admin')
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_users')
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email


class OTP(models.Model):
    """OTP Model for email verification and password reset"""
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=50, choices=[
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.otp} - {self.purpose}"

    @staticmethod
    def generate_otp():
        """Generate a 4-digit OTP"""
        return ''.join(random.choices(string.digits, k=4))

    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_otp(cls, email, purpose):
        """Create a new OTP"""
        otp_code = cls.generate_otp()
        expires_at = timezone.now() + timezone.timedelta(minutes=10)
        return cls.objects.create(
            email=email,
            otp=otp_code,
            purpose=purpose,
            expires_at=expires_at
        )


class Invitation(models.Model):
    """Model for user invitations sent by admin"""
    email = models.EmailField()
    role = models.CharField(max_length=100)  # Allow custom roles, no choices constraint
    company_name = models.CharField(max_length=255, blank=True, null=True)  # Admin's company name
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invitation for {self.email} as {self.role}"

    def is_valid(self):
        """Check if invitation is still valid"""
        return not self.is_used and timezone.now() < self.expires_at

    @classmethod
    def create_invitation(cls, email, role, invited_by):
        """Create a new invitation"""
        expires_at = timezone.now() + timezone.timedelta(days=7)  # 7 days validity
        # Automatically use admin's company name
        company_name = invited_by.company_name if invited_by else ''
        return cls.objects.create(
            email=email,
            role=role,
            company_name=company_name,
            invited_by=invited_by,
            expires_at=expires_at
        )
