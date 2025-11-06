from rest_framework import serializers
from .models import Material, EstimateDefaults, Component


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
    current_materials_details = MaterialSerializer(source='current_materials', many=True, read_only=True)
    current_materials = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Material.objects.all(),
        required=False
    )
    
    class Meta:
        model = EstimateDefaults
        fields = [
            'id',
            'name',
            'description',
            'cost',
            'category',
            'current_materials',
            'current_materials_details',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_email', 'current_materials_details']
    
    def validate_cost(self, value):
        """Validate that cost is positive"""
        if value < 0:
            raise serializers.ValidationError("Cost must be zero or greater.")
        return value
    
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
    
    def create(self, validated_data):
        """Create EstimateDefaults with many-to-many relationships"""
        materials = validated_data.pop('current_materials', [])
        estimate_default = EstimateDefaults.objects.create(**validated_data)
        estimate_default.current_materials.set(materials)
        return estimate_default
    
    def update(self, instance, validated_data):
        """Update EstimateDefaults with many-to-many relationships"""
        materials = validated_data.pop('current_materials', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if materials is not None:
            instance.current_materials.set(materials)
        
        return instance


class ComponentSerializer(serializers.ModelSerializer):
    """Serializer for Component model"""
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    material_used_details = MaterialSerializer(source='material_used', many=True, read_only=True)
    material_used = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Material.objects.all(),
        required=False
    )
    
    class Meta:
        model = Component
        fields = [
            'id',
            'component_name',
            'description',
            'base_price',
            'labor_hours',
            'material_used',
            'material_used_details',
            'created_at',
            'updated_at',
            'created_by',
            'created_by_email'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'created_by_email', 'material_used_details']
    
    def validate_base_price(self, value):
        """Validate that base price is positive or zero"""
        if value < 0:
            raise serializers.ValidationError("Base price must be zero or greater.")
        return value
    
    def validate_labor_hours(self, value):
        """Validate that labor hours is positive or zero"""
        if value < 0:
            raise serializers.ValidationError("Labor hours must be zero or greater.")
        return value
    
    def validate_component_name(self, value):
        """Validate that component name is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Component name cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """Create Component with many-to-many relationships"""
        materials = validated_data.pop('material_used', [])
        component = Component.objects.create(**validated_data)
        component.material_used.set(materials)
        return component
    
    def update(self, instance, validated_data):
        """Update Component with many-to-many relationships"""
        materials = validated_data.pop('material_used', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if materials is not None:
            instance.material_used.set(materials)
        
        return instance
