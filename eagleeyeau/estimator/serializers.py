from rest_framework import serializers
from .models import Estimate


class EstimateItemSerializer(serializers.Serializer):
    """
    Serializer for individual items within the items array.
    Includes item cost calculation.
    """
    item_type = serializers.ChoiceField(choices=['material', 'component', 'estimate_default'])
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    
    def to_representation(self, instance):
        """Add calculated total_price when serializing"""
        data = super().to_representation(instance)
        qty = instance.get('quantity', 0)
        price = float(instance.get('unit_price', 0))
        item_total = round(qty * price, 2)
        data['item_total_cost'] = item_total  # Individual item total
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
            'client_name',
            'project_name',
            'status',
            'estimate_date',
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
        return obj.total_cost
    
    def get_total_cost(self, obj):
        """Get base total cost"""
        return obj.total_cost
    
    def get_profit_amount(self, obj):
        """Calculate profit amount"""
        base_total = obj.total_cost
        profit = (base_total * obj.profit_margin) / 100
        return round(profit, 2)
    
    def get_total_with_profit(self, obj):
        """Get total with profit margin"""
        return obj.total_with_profit
    
    def get_tax_amount(self, obj):
        """Calculate tax amount"""
        total_with_profit = obj.total_with_profit
        tax = (total_with_profit * obj.income_tax) / 100
        return round(tax, 2)
    
    def get_total_with_tax(self, obj):
        """Get final total with tax"""
        return obj.total_with_tax
    
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
        
        base_total = obj.total_cost
        profit = (base_total * obj.profit_margin) / 100
        total_with_profit = base_total + profit
        tax = (total_with_profit * obj.income_tax) / 100
        final_total = total_with_profit + tax
        
        return {
            'items': items_cost_list,
            'summary': {
                'total_items_cost': round(total_items_sum, 2),
                'profit_margin_percent': obj.profit_margin,
                'profit_amount': round(profit, 2),
                'subtotal_with_profit': round(total_with_profit, 2),
                'tax_percent': obj.income_tax,
                'tax_amount': round(tax, 2),
                'final_total': round(final_total, 2)
            }
        }
    
    def create(self, validated_data):
        """Create estimate with items array"""
        items = validated_data.pop('items', [])
        
        # Calculate item totals
        for item in items:
            item['item_total_cost'] = item['quantity'] * float(item['unit_price'])
        
        estimate = Estimate.objects.create(items=items, **validated_data)
        return estimate
    
    def update(self, instance, validated_data):
        """Update estimate and items"""
        items = validated_data.pop('items', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update items if provided
        if items is not None:
            for item in items:
                item['item_total_cost'] = item['quantity'] * float(item['unit_price'])
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
            'client_name',
            'project_name',
            'status',
            'estimate_date',
            'items_count',
            'total_cost',
            'created_at',
        ]
    
    def get_items_count(self, obj):
        return len(obj.items) if obj.items else 0
    
    def get_total_cost(self, obj):
        return obj.total_cost
