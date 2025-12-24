from django.contrib import admin
from .models import TaskTimer


@admin.register(TaskTimer)
class TaskTimerAdmin(admin.ModelAdmin):
    """Admin for TaskTimer model"""
    
    list_display = ['employee', 'task', 'work_date', 'start_time', 'end_time', 'duration_formatted', 'is_active']
    list_filter = ['work_date', 'is_active', 'employee']
    search_fields = ['employee__username', 'employee__email', 'task__task_name']
    readonly_fields = ['duration_seconds', 'created_at', 'updated_at']
    ordering = ['-work_date', '-start_time']
    
    fieldsets = (
        ('Timer Information', {
            'fields': ('employee', 'task', 'work_date')
        }),
        ('Time Tracking', {
            'fields': ('start_time', 'end_time', 'duration_seconds', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_formatted(self, obj):
        """Display formatted duration"""
        return obj.get_duration_formatted()
    duration_formatted.short_description = 'Duration'
