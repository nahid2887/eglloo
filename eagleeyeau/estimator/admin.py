from django.contrib import admin
from django.utils.html import format_html
from .models import Estimate


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = [
        'serial_number',
        'client_name',
        'project_name',
        'status_badge',
        'items_count',
        'total_cost_display',
        'estimate_date',
        'created_at',
    ]
    
    list_filter = ['status', 'estimate_date', 'created_at']
    search_fields = ['serial_number', 'client_name', 'project_name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('serial_number', 'client_name', 'project_name')
        }),
        ('Status & Dates', {
            'fields': ('status', 'estimate_date')
        }),
        ('Reference Images', {
            'fields': ('image_1', 'image_2'),
            'classes': ('collapse',)
        }),
        ('Financial Details', {
            'fields': ('profit_margin', 'income_tax', 'notes')
        }),
        ('Items', {
            'fields': ('items',),
            'description': 'Array of items with quantities and prices'
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    def status_badge(self, obj):
        """Display status with color"""
        colors = {
            'pending': '#FFA500',
            'sent': '#0066CC',
            'approved': '#00AA00',
            'rejected': '#CC0000',
        }
        color = colors.get(obj.status, '#808080')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def items_count(self, obj):
        """Display number of items"""
        return len(obj.items) if obj.items else 0
    items_count.short_description = 'Items'
    
    def total_cost_display(self, obj):
        """Display total cost"""
        return f'${obj.total_cost:.2f}'
    total_cost_display.short_description = 'Total Cost'
