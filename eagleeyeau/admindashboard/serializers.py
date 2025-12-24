from rest_framework import serializers
from .models import Material, EstimateDefaults, Component, ComponentMaterialQuantity, ComponentEstimateQuantity


class MaterialSerializer(serializers.ModelSerializer):
    """Serializer for Material model"""
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Material
        fields = [
            'id',
            'material_name',
            'supplier',
            'category',
            'unit',
            'cost_per_unit',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_email']
    
    def validate_cost_per_unit(self, value):
        """Validate that cost per unit is positive"""
        if value <= 0:
            raise serializers.ValidationError("Cost per unit must be greater than zero.")
        return value
    
    def validate_material_name(self, value):
        """Validate that material name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Material name cannot be empty.")
        return value.strip()
    
    def validate_supplier(self, value):
        """Validate that supplier name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Supplier name cannot be empty.")
        return value.strip()
    
    def validate_category(self, value):
        """Validate that category is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Category cannot be empty.")
        return value.strip()
    
    def validate_unit(self, value):
        """Validate that unit is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Unit cannot be empty.")
        return value.strip()


class EstimateDefaultsSerializer(serializers.ModelSerializer):
    """Serializer for EstimateDefaults model"""
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = EstimateDefaults
        fields = [
            'id',
            'name',
            'description',
            'category',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_email']
    
    def validate_name(self, value):
        """Validate that name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value.strip()
    
    def validate_category(self, value):
        """Validate that category is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Category cannot be empty.")
        return value.strip()


class ComponentMaterialQuantitySerializer(serializers.ModelSerializer):
    """Serializer for material quantities in components"""
    
    class Meta:
        model = ComponentMaterialQuantity
        fields = ['id', 'material', 'quantity']


class ComponentEstimateQuantitySerializer(serializers.ModelSerializer):
    """Serializer for estimate quantities in components"""
    
    class Meta:
        model = ComponentEstimateQuantity
        fields = ['id', 'estimate_default', 'quantity']


class ComponentSerializer(serializers.ModelSerializer):
    """Serializer for Component model with quantities"""
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    material_quantities = serializers.SerializerMethodField(read_only=True)
    estimate_quantities = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Component
        fields = [
            'id',
            'component_name',
            'description',
            'base_price',
            'material_quantities',
            'estimate_quantities',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_email', 'material_quantities', 'estimate_quantities']
    
    def get_material_quantities(self, obj):
        """Get material quantities for the component"""
        quantities = obj.material_quantities.all()
        return [
            {
                'id': q.material.id,
                'material_id': q.material.id,
                'material_name': q.material.material_name,
                'quantity': float(q.quantity),
                'unit': q.material.unit,
                'cost_per_unit': float(q.material.cost_per_unit),
                'total_cost': float(q.material.cost_per_unit * q.quantity)
            }
            for q in quantities
        ]
    
    def get_estimate_quantities(self, obj):
        """Get estimate quantities for the component"""
        quantities = obj.estimate_quantities.all()
        return [
            {
                'id': q.estimate_default.id,
                'estimate_id': q.estimate_default.id,
                'estimate_name': q.estimate_default.name,
                'quantity': float(q.quantity)
            }
            for q in quantities
        ]
    
    def validate_base_price(self, value):
        """Validate that base price is positive or zero"""
        if value < 0:
            raise serializers.ValidationError("Base price must be zero or greater.")
        return value
    
    def validate_component_name(self, value):
        """Validate that component name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Component name cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """Create Component with quantities"""
        component = Component.objects.create(**validated_data)
        
        # Handle material quantities from request
        material_quantities = self.context.get('request').data.get('material_quantities', [])
        for mat_qty in material_quantities:
            material_id = mat_qty.get('id') or mat_qty.get('material_id')
            quantity = mat_qty.get('quantity')
            if material_id and quantity:
                ComponentMaterialQuantity.objects.create(
                    component=component,
                    material_id=material_id,
                    quantity=quantity
                )
        
        # Handle estimate quantities from request
        estimate_quantities = self.context.get('request').data.get('estimate_quantities', [])
        for est_qty in estimate_quantities:
            estimate_id = est_qty.get('id') or est_qty.get('estimate_id')
            quantity = est_qty.get('quantity')
            if estimate_id and quantity:
                ComponentEstimateQuantity.objects.create(
                    component=component,
                    estimate_default_id=estimate_id,
                    quantity=quantity
                )
        
        return component
    
    def update(self, instance, validated_data):
        """Update Component with quantities"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle material quantities from request
        material_quantities = self.context.get('request').data.get('material_quantities')
        if material_quantities is not None:
            instance.material_quantities.all().delete()
            for mat_qty in material_quantities:
                material_id = mat_qty.get('id') or mat_qty.get('material_id')
                quantity = mat_qty.get('quantity')
                if material_id and quantity:
                    ComponentMaterialQuantity.objects.create(
                        component=instance,
                        material_id=material_id,
                        quantity=quantity
                    )
        
        # Handle estimate quantities from request
        estimate_quantities = self.context.get('request').data.get('estimate_quantities')
        if estimate_quantities is not None:
            instance.estimate_quantities.all().delete()
            for est_qty in estimate_quantities:
                estimate_id = est_qty.get('id') or est_qty.get('estimate_id')
                quantity = est_qty.get('quantity')
                if estimate_id and quantity:
                    ComponentEstimateQuantity.objects.create(
                        component=instance,
                        estimate_default_id=estimate_id,
                        quantity=quantity
                    )
        
        return instance

