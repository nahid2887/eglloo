from rest_framework import serializers
from .models import Material, Component

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure all decimal fields are properly serialized
        if 'unit_cost' in data and data['unit_cost'] is not None:
            data['unit_cost'] = float(data['unit_cost'])
        return data

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure all decimal fields are properly serialized
        if 'unit_cost' in data and data['unit_cost'] is not None:
            data['unit_cost'] = float(data['unit_cost'])
        return data