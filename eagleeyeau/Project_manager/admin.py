from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model"""
    list_display = [
        'id', 
        'project_name', 
        'client_name', 
        'status', 
        'creating_date', 
        'end_date', 
        'total_amount',
        'created_by',
        'tasks_count'
    ]
    list_filter = ['status', 'creating_date', 'created_by']
    search_fields = ['project_name', 'client_name', 'description']
    readonly_fields = ['creating_date', 'created_at', 'updated_at']
    date_hierarchy = 'creating_date'
    ordering = ['-creating_date']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('project_name', 'client_name', 'description', 'estimate')
        }),
        ('Status & Dates', {
            'fields': ('status', 'creating_date', 'start_date', 'end_date')
        }),
        ('Financial Information', {
            'fields': ('total_amount', 'estimated_cost')
        }),
        ('Project Details', {
            'fields': ('rooms',)
        }),
        ('Management', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tasks_count(self, obj):
        """Display number of tasks in the project"""
        return obj.tasks.count()
    tasks_count.short_description = 'Tasks'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model"""
    list_display = [
        'id',
        'task_name',
        'project',
        'status',
        'priority',
        'phase',
        'assigned_employee',
        'due_date',
        'created_by'
    ]
    list_filter = ['status', 'priority', 'phase', 'project', 'due_date', 'created_by']
    search_fields = ['task_name', 'description', 'room', 'project__project_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    ordering = ['priority', 'due_date']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('task_name', 'description', 'project', 'room')
        }),
        ('Status, Priority & Phase', {
            'fields': ('status', 'priority', 'phase')
        }),
        ('Dates', {
            'fields': ('start_date', 'due_date')
        }),
        ('Assignment', {
            'fields': ('assigned_employee', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('project', 'assigned_employee', 'created_by')
