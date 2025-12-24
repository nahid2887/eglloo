from django.db import models
from authentication.models import User


class Material(models.Model):
    """Material Model for Admin Dashboard"""
    
    material_name = models.CharField(max_length=255, help_text="Name of the material")
    supplier = models.CharField(max_length=255, help_text="Supplier name")
    category = models.CharField(max_length=255, help_text="Material category")
    unit = models.CharField(max_length=50, help_text="Unit of measurement (e.g., kg, liter, piece)")
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per unit")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='materials_created')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Material"
        verbose_name_plural = "Materials"

    def __str__(self):
        return f"{self.material_name} - {self.supplier}"


class EstimateDefaults(models.Model):
    """Estimate Defaults Model for Admin Dashboard"""
    
    name = models.CharField(max_length=255, help_text="Name of the estimate default")
    description = models.TextField(help_text="Description of the estimate default", blank=True, null=True)
    category = models.CharField(max_length=255, help_text="Category of the estimate")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='estimate_defaults_created')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Estimate Default"
        verbose_name_plural = "Estimate Defaults"

    def __str__(self):
        return f"{self.name} - {self.category}"


class Component(models.Model):
    """Component Model for Admin Dashboard"""
    
    component_name = models.CharField(max_length=255, help_text="Name of the component")
    description = models.TextField(help_text="Description of the component", blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price of the component")
    material_used = models.ManyToManyField(
        Material,
        related_name='components',
        blank=True,
        help_text="Materials used in this component",
        through='ComponentMaterialQuantity'
    )
    estimate_defaults = models.ManyToManyField(
        EstimateDefaults,
        related_name='components',
        blank=True,
        help_text="Estimate defaults associated with this component",
        through='ComponentEstimateQuantity'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='components_created')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Component"
        verbose_name_plural = "Components"

    def __str__(self):
        return f"{self.component_name}"


class ComponentMaterialQuantity(models.Model):
    """Through model to track material quantities in components"""
    
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name='material_quantities'
    )
    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name='component_quantities'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity of material needed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('component', 'material')
        verbose_name = "Component Material Quantity"
        verbose_name_plural = "Component Material Quantities"

    def __str__(self):
        return f"{self.component.component_name} - {self.material.material_name} ({self.quantity})"


class ComponentEstimateQuantity(models.Model):
    """Through model to track estimate default quantities in components"""
    
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name='estimate_quantities'
    )
    estimate_default = models.ForeignKey(
        EstimateDefaults,
        on_delete=models.CASCADE,
        related_name='component_quantities'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Quantity of estimate default needed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('component', 'estimate_default')
        verbose_name = "Component Estimate Quantity"
        verbose_name_plural = "Component Estimate Quantities"

    def __str__(self):
        return f"{self.component.component_name} - {self.estimate_default.name} ({self.quantity})"
    
    