from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Estimate(models.Model):
    """
    Main Estimate model with items stored as a JSON array.
    Single model handles complete estimate creation with all items.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic Info
    serial_number = models.CharField(max_length=100, unique=True)
    estimate_number = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Estimate number for tracking")
    client_name = models.CharField(max_length=200)
    project_name = models.CharField(max_length=300)
    
    # Fixed Fields - Status and Date
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    estimate_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True, help_text="End/completion date of the project")
    # Targeted rooms info (optional array)
    targeted_rooms = models.JSONField(default=list, blank=True, help_text="Array of targeted rooms for the estimate")
    targeted_rooms_updated = models.DateTimeField(null=True, blank=True, help_text="Timestamp when targeted_rooms was last updated")
    
    # Images (Reference URLs)
    image_1 = models.URLField(null=True, blank=True, help_text="First reference image URL")
    image_2 = models.URLField(null=True, blank=True, help_text="Second reference image URL")
    
    # Financial Details
    profit_margin = models.FloatField(default=20, validators=[MinValueValidator(0)])
    income_tax = models.FloatField(default=2, validators=[MinValueValidator(0)])
    notes = models.TextField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Items stored as JSON array
    items = models.JSONField(
        default=list,
        help_text="Array of items: [{item_type, item_id, quantity, unit_price}]"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.serial_number} - {self.client_name}"
    
    @property
    def total_cost(self):
        """Calculate total cost from all items"""
        if not self.items:
            return 0
        total = 0
        for item in self.items:
            qty = item.get('quantity', 0)
            unit_price = item.get('unit_price', 0)
            total += qty * unit_price
        return round(total, 2)
    
    @property
    def total_with_profit(self):
        """Calculate total with profit margin"""
        base_total = self.total_cost
        profit = (base_total * self.profit_margin) / 100
        return round(base_total + profit, 2)
    
    @property
    def total_with_tax(self):
        """Calculate final total with tax"""
        total_with_profit = self.total_with_profit
        tax = (total_with_profit * self.income_tax) / 100
        return round(total_with_profit + tax, 2)
