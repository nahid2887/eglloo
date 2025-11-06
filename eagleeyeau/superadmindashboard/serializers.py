from rest_framework import serializers
from .models import TermsAndConditions, PrivacyPolicy


class TermsAndConditionsSerializer(serializers.ModelSerializer):
    """Serializer for Terms and Conditions"""
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TermsAndConditions
        fields = [
            'id', 'title', 'content', 'version', 'effective_date',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
        return None


class TermsAndConditionsPublicSerializer(serializers.ModelSerializer):
    """Public serializer for Terms and Conditions (read-only)"""
    
    class Meta:
        model = TermsAndConditions
        fields = ['id', 'title', 'content', 'version', 'effective_date', 'updated_at']
        read_only_fields = fields


class PrivacyPolicySerializer(serializers.ModelSerializer):
    """Serializer for Privacy Policy"""
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = PrivacyPolicy
        fields = [
            'id', 'title', 'content', 'version', 'effective_date',
            'created_by', 'created_by_name', 'updated_by', 'updated_by_name',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'updated_by', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None
    
    def get_updated_by_name(self, obj):
        if obj.updated_by:
            return f"{obj.updated_by.first_name} {obj.updated_by.last_name}"
        return None


class PrivacyPolicyPublicSerializer(serializers.ModelSerializer):
    """Public serializer for Privacy Policy (read-only)"""
    
    class Meta:
        model = PrivacyPolicy
        fields = ['id', 'title', 'content', 'version', 'effective_date', 'updated_at']
        read_only_fields = fields
