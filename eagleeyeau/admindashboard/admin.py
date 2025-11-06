from django.contrib import admin
from .models import Material, EstimateDefaults, Component


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """Admin configuration for Material model"""
    
    list_display = ['material_name', 'supplier', 'category', 'unit', 'cost_per_unit', 'created_at', 'created_by']
    list_filter = ['category', 'supplier', 'created_at']
    search_fields = ['material_name', 'supplier', 'category']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Material Information', {
            'fields': ('material_name', 'supplier', 'category', 'unit', 'cost_per_unit')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EstimateDefaults)
class EstimateDefaultsAdmin(admin.ModelAdmin):
    """Admin configuration for EstimateDefaults model"""
    
    list_display = ['name', 'category', 'cost', 'created_at', 'created_by']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['-created_at']
    filter_horizontal = ['current_materials']
    
    fieldsets = (
        ('Estimate Information', {
            'fields': ('name', 'description', 'cost', 'category')
        }),
        ('Associated Materials', {
            'fields': ('current_materials',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Admin configuration for Component model"""
    
    list_display = ['component_name', 'base_price', 'labor_hours', 'created_at', 'created_by']
    list_filter = ['created_at']
    search_fields = ['component_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['-created_at']
    filter_horizontal = ['material_used']
    
    fieldsets = (
        ('Component Information', {
            'fields': ('component_name', 'description', 'base_price', 'labor_hours')
        }),
        ('Associated Materials', {
            'fields': ('material_used',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )