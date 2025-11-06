from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTP, Invitation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'is_email_verified', 'is_staff', 'created_at']
    list_filter = ['role', 'is_email_verified', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('company_name', 'country', 'role', 'profile_image', 'is_email_verified')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'first_name', 'last_name', 'company_name', 'country', 'role')}),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'purpose', 'is_used', 'created_at', 'expires_at']
    list_filter = ['purpose', 'is_used', 'created_at']
    search_fields = ['email', 'otp']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'invited_by', 'is_used', 'created_at', 'expires_at']
    list_filter = ['role', 'is_used', 'created_at']
    search_fields = ['email']
    ordering = ['-created_at']
    readonly_fields = ['token', 'created_at', 'accepted_at']
