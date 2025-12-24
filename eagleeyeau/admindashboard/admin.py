from django.contrib import admin
from .models import Material, EstimateDefaults, Component, ComponentMaterialQuantity, ComponentEstimateQuantity


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
    
    list_display = ['name', 'category', 'created_at', 'created_by']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Estimate Information', {
            'fields': ('name', 'description', 'category')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ComponentMaterialQuantityInline(admin.TabularInline):
    """Inline admin for component material quantities"""
    model = ComponentMaterialQuantity
    extra = 1


class ComponentEstimateQuantityInline(admin.TabularInline):
    """Inline admin for component estimate quantities"""
    model = ComponentEstimateQuantity
    extra = 1


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Admin configuration for Component model"""
    
    list_display = ['component_name', 'base_price', 'created_at', 'created_by']
    list_filter = ['created_at']
    search_fields = ['component_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['-created_at']
    inlines = [ComponentMaterialQuantityInline, ComponentEstimateQuantityInline]
    
    fieldsets = (
        ('Component Information', {
            'fields': ('component_name', 'description', 'base_price')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComponentMaterialQuantity)
class ComponentMaterialQuantityAdmin(admin.ModelAdmin):
    """Admin configuration for ComponentMaterialQuantity model"""
    
    list_display = ['component', 'material', 'quantity', 'created_at']
    list_filter = ['created_at', 'component']
    search_fields = ['component__component_name', 'material__material_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComponentEstimateQuantity)
class ComponentEstimateQuantityAdmin(admin.ModelAdmin):
    """Admin configuration for ComponentEstimateQuantity model"""
    
    list_display = ['component', 'estimate_default', 'quantity', 'created_at']
    list_filter = ['created_at', 'component']
    search_fields = ['component__component_name', 'estimate_default__name']
    readonly_fields = ['created_at', 'updated_at']
