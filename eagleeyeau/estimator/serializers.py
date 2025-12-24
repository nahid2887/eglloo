from rest_framework import serializers
from django.utils import timezone
from .models import Estimate
from admindashboard.models import Material, Component, EstimateDefaults


class EstimateItemSerializer(serializers.Serializer):
    """
    Serializer for individual items within the items array.
    Includes item cost calculation and full item details.
    """
    item_type = serializers.ChoiceField(choices=['material', 'component', 'estimate_default'])
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, coerce_to_string=False)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    def to_representation(self, instance):
        """Add calculated total_price and full item details when serializing"""
        data = super().to_representation(instance)
        qty = instance.get('quantity', 0)
        price = float(instance.get('unit_price', 0))
        item_total = round(qty * price, 2)
        data['item_total_cost'] = item_total  # Individual item total
        
        # Convert unit_price to float for JSON serialization
        data['unit_price'] = float(data['unit_price'])
        
        # Fetch and include full item details based on item_type
        item_type = instance.get('item_type')
        item_id = instance.get('item_id')
        item_details = None
        
        try:
            if item_type == 'material':
                material = Material.objects.get(id=item_id)
                item_details = {
                    'id': material.id,
                    'material_name': material.material_name,
                    'supplier': material.supplier,
                    'category': material.category,
                    'unit': material.unit,
                    'cost_per_unit': float(material.cost_per_unit),
                    'created_at': material.created_at.isoformat(),
                    'created_by_email': material.created_by.email if material.created_by else None,
                }
            
            elif item_type == 'component':
                component = Component.objects.get(id=item_id)
                materials_list = [
                    {
                        'id': m.id,
                        'material_name': m.material_name,
                        'supplier': m.supplier,
                        'category': m.category,
                        'unit': m.unit,
                        'cost_per_unit': float(m.cost_per_unit),
                    }
                    for m in component.material_used.all()
                ]
                estimate_defaults_list = [
                    {
                        'id': ed.id,
                        'name': ed.name,
                        'description': ed.description,
                        'category': ed.category,
                    }
                    for ed in component.estimate_defaults.all()
                ]
                item_details = {
                    'id': component.id,
                    'component_name': component.component_name,
                    'description': component.description,
                    'base_price': float(component.base_price),
                    'labor_hours': float(component.labor_hours),
                    'material_used': materials_list,
                    'estimate_defaults': estimate_defaults_list,
                    'created_at': component.created_at.isoformat(),
                    'created_by_email': component.created_by.email if component.created_by else None,
                }
            
            elif item_type == 'estimate_default':
                estimate_default = EstimateDefaults.objects.get(id=item_id)
                item_details = {
                    'id': estimate_default.id,
                    'name': estimate_default.name,
                    'description': estimate_default.description,
                    'category': estimate_default.category,
                    'created_at': estimate_default.created_at.isoformat(),
                    'created_by_email': estimate_default.created_by.email if estimate_default.created_by else None,
                }
        
        except (Material.DoesNotExist, Component.DoesNotExist, EstimateDefaults.DoesNotExist):
            item_details = {'error': f'{item_type} with id {item_id} not found'}
        
        data['item_details'] = item_details
        return data


class EstimateSerializer(serializers.ModelSerializer):
    """
    Main serializer for Estimate with items as array field.
    Handles complete estimate creation in single API call.
    Returns comprehensive cost breakdown.
    """
    items = EstimateItemSerializer(many=True)
    items_count = serializers.SerializerMethodField()
    total_items_cost = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    profit_amount = serializers.SerializerMethodField()
    total_with_profit = serializers.SerializerMethodField()
    tax_amount = serializers.SerializerMethodField()
    total_with_tax = serializers.SerializerMethodField()
    cost_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Estimate
        fields = [
            'id',
            'serial_number',
            'estimate_number',
            'client_name',
            'project_name',
            'status',
            'estimate_date',
            'end_date',
            'targeted_rooms',
            'targeted_rooms_updated',
            'profit_margin',
            'income_tax',
            'notes',
            'items',
            'items_count',
            'total_items_cost',
            'total_cost',
            'profit_amount',
            'total_with_profit',
            'tax_amount',
            'total_with_tax',
            'cost_breakdown',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'estimate_date']
    
    def get_items_count(self, obj):
        """Get total number of items"""
        return len(obj.items) if obj.items else 0
    
    def get_total_items_cost(self, obj):
        """Get sum of all item costs"""
        return float(obj.total_cost)
    
    def get_total_cost(self, obj):
        """Get base total cost"""
        return float(obj.total_cost)
    
    def get_profit_amount(self, obj):
        """Calculate profit amount"""
        base_total = float(obj.total_cost)
        profit = (base_total * float(obj.profit_margin)) / 100
        return round(profit, 2)
    
    def get_total_with_profit(self, obj):
        """Get total with profit margin"""
        return float(obj.total_with_profit)
    
    def get_tax_amount(self, obj):
        """Calculate tax amount"""
        total_with_profit = float(obj.total_with_profit)
        tax = (total_with_profit * float(obj.income_tax)) / 100
        return round(tax, 2)
    
    def get_total_with_tax(self, obj):
        """Get final total with tax"""
        return float(obj.total_with_tax)
    
    def get_cost_breakdown(self, obj):
        """Get detailed cost breakdown"""
        if not obj.items:
            return None
        
        items_cost_list = []
        total_items_sum = 0
        
        for item in obj.items:
            qty = item.get('quantity', 0)
            unit_price = float(item.get('unit_price', 0))
            item_total = qty * unit_price
            total_items_sum += item_total
            
            items_cost_list.append({
                'item_type': item.get('item_type'),
                'item_id': item.get('item_id'),
                'quantity': qty,
                'unit_price': round(unit_price, 2),
                'item_cost': round(item_total, 2)
            })
        
        base_total = float(obj.total_cost)
        profit = (base_total * float(obj.profit_margin)) / 100
        total_with_profit = base_total + profit
        tax = (total_with_profit * float(obj.income_tax)) / 100
        final_total = total_with_profit + tax
        
        return {
            'items': items_cost_list,
            'summary': {
                'total_items_cost': round(total_items_sum, 2),
                'profit_margin_percent': float(obj.profit_margin),
                'profit_amount': round(profit, 2),
                'subtotal_with_profit': round(total_with_profit, 2),
                'tax_percent': float(obj.income_tax),
                'tax_amount': round(tax, 2),
                'final_total': round(final_total, 2)
            }
        }
    
    def create(self, validated_data):
        """Create estimate with items array"""
        items = validated_data.pop('items', [])
        # If targeted_rooms is provided, stamp the update time
        if 'targeted_rooms' in validated_data and validated_data.get('targeted_rooms'):
            validated_data['targeted_rooms_updated'] = timezone.now()
        
        # Convert Decimal to float for JSON storage and calculate item totals
        for item in items:
            item['unit_price'] = float(item['unit_price'])  # Convert Decimal to float
            item['item_total_cost'] = item['quantity'] * item['unit_price']
        
        estimate = Estimate.objects.create(items=items, **validated_data)
        return estimate
    
    def update(self, instance, validated_data):
        """Update estimate and items"""
        items = validated_data.pop('items', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # If targeted_rooms was updated in the payload, update its timestamp
        if 'targeted_rooms' in validated_data:
            instance.targeted_rooms_updated = timezone.now()
        
        # Update items if provided
        if items is not None:
            for item in items:
                item['unit_price'] = float(item['unit_price'])  # Convert Decimal to float
                item['item_total_cost'] = item['quantity'] * item['unit_price']
            instance.items = items
        
        instance.save()
        return instance


class EstimateListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list view with summary.
    """
    items_count = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    
    class Meta:
        model = Estimate
        fields = [
            'id',
            'serial_number',
            'targeted_rooms',
            'targeted_rooms_updated',
            'estimate_number',
            'client_name',
            'project_name',
            'status',
            'estimate_date',
            'end_date',
            'items_count',
            'total_cost',
            'created_at',
        ]
    
    def get_items_count(self, obj):
        return len(obj.items) if obj.items else 0
    
    def get_total_cost(self, obj):
        return float(obj.total_cost)


class AdminEstimateListSerializer(serializers.ModelSerializer):
    """
    Serializer for admin view with creator information.
    Includes creator name and email.
    """
    items_count = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_by_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Estimate
        fields = [
            'id',
            'serial_number',
            'targeted_rooms',
            'targeted_rooms_updated',
            'estimate_number',
            'client_name',
            'project_name',
            'status',
            'estimate_date',
            'end_date',
            'items_count',
            'total_cost',
            'created_by_name',
            'created_by_email',
            'created_at',
        ]
    
    def get_items_count(self, obj):
        return len(obj.items) if obj.items else 0
    
    def get_total_cost(self, obj):
        return float(obj.total_cost)
    
    def get_created_by_name(self, obj):
        """Get creator's full name"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return None
    
    def get_created_by_email(self, obj):
        """Get creator's email"""
        if obj.created_by:
            return obj.created_by.email
        return None
