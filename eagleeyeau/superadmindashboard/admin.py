from django.contrib import admin
from .models import TermsAndConditions, PrivacyPolicy


@admin.register(TermsAndConditions)
class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'effective_date', 'is_active', 'updated_at']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['title', 'content', 'version']
    readonly_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'version', 'effective_date', 'is_active')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'effective_date', 'is_active', 'updated_at']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['title', 'content', 'version']
    readonly_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'version', 'effective_date', 'is_active')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Tracking', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
