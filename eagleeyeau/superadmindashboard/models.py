from django.db import models
from django.utils import timezone
from authentication.models import User


class TermsAndConditions(models.Model):
    """Model for Terms and Conditions - Only one active record"""
    
    title = models.CharField(max_length=255, default="Terms and Conditions")
    content = models.TextField(help_text="HTML content for terms and conditions")
    version = models.CharField(max_length=50, default="1.0", help_text="Version number")
    effective_date = models.DateField(default=timezone.now, help_text="When these terms become effective")
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='terms_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='terms_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True, help_text="Only one can be active at a time")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Terms and Conditions'
        verbose_name_plural = 'Terms and Conditions'
    
    def __str__(self):
        return f"{self.title} - v{self.version}"
    
    def save(self, *args, **kwargs):
        """Ensure only one active record exists"""
        if self.is_active:
            # Deactivate all other records
            TermsAndConditions.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class PrivacyPolicy(models.Model):
    """Model for Privacy Policy - Only one active record"""
    
    title = models.CharField(max_length=255, default="Privacy Policy")
    content = models.TextField(help_text="HTML content for privacy policy")
    version = models.CharField(max_length=50, default="1.0", help_text="Version number")
    effective_date = models.DateField(default=timezone.now, help_text="When this policy becomes effective")
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='privacy_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='privacy_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True, help_text="Only one can be active at a time")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Privacy Policy'
        verbose_name_plural = 'Privacy Policies'
    
    def __str__(self):
        return f"{self.title} - v{self.version}"
    
    def save(self, *args, **kwargs):
        """Ensure only one active record exists"""
        if self.is_active:
            # Deactivate all other records
            PrivacyPolicy.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
