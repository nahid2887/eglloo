from django.shortcuts import render
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import TermsAndConditions, PrivacyPolicy
from .serializers import (
    TermsAndConditionsSerializer,
    TermsAndConditionsPublicSerializer,
    PrivacyPolicySerializer,
    PrivacyPolicyPublicSerializer
)
from eagleeyeau.response_formatter import format_response
from eagleeyeau.api_messages import SUPERADMIN_MESSAGES, PERMISSION_MESSAGES


class IsSuperAdmin(permissions.BasePermission):
    """Custom permission to only allow superadmins to edit"""
    
    def has_permission(self, request, view):
        # Allow GET requests for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only Admin role can modify
        return request.user and request.user.is_authenticated and request.user.role == 'Admin'


class TermsAndConditionsView(APIView):
    """
    Single endpoint for Terms and Conditions (no ID required)
    - GET: Anyone can read (public access)
    - PATCH: Only Admin can modify
    """
    permission_classes = [IsSuperAdmin]
    
    @swagger_auto_schema(
        operation_description="Get the active Terms and Conditions (public access)",
        responses={
            200: TermsAndConditionsPublicSerializer(),
            404: "No active terms and conditions found"
        },
        tags=['Super Admin Dashboard']
    )
    def get(self, request):
        """Get the currently active terms and conditions"""
        terms = TermsAndConditions.objects.filter(is_active=True).first()
        if not terms:
            return Response(
                {"detail": "No active terms and conditions found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TermsAndConditionsPublicSerializer(terms)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Update the active Terms and Conditions (Admin only)",
        request_body=TermsAndConditionsSerializer,
        responses={
            200: TermsAndConditionsSerializer(),
            404: "No active terms and conditions found"
        },
        tags=['Super Admin Dashboard']
    )
    def patch(self, request):
        """Update the currently active terms and conditions"""
        terms = TermsAndConditions.objects.filter(is_active=True).first()
        if not terms:
            return Response(
                {"detail": "No active terms and conditions found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = TermsAndConditionsSerializer(terms, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)


class PrivacyPolicyView(APIView):
    """
    Single endpoint for Privacy Policy (no ID required)
    - GET: Anyone can read (public access)
    - PATCH: Only Admin can modify
    """
    permission_classes = [IsSuperAdmin]
    
    @swagger_auto_schema(
        operation_description="Get the active Privacy Policy (public access)",
        responses={
            200: PrivacyPolicyPublicSerializer(),
            404: "No active privacy policy found"
        },
        tags=['Super Admin Dashboard']
    )
    def get(self, request):
        """Get the currently active privacy policy"""
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if not policy:
            return Response(
                {"detail": "No active privacy policy found."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PrivacyPolicyPublicSerializer(policy)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Update the active Privacy Policy (Admin only)",
        request_body=PrivacyPolicySerializer,
        responses={
            200: PrivacyPolicySerializer(),
            404: "No active privacy policy found"
        },
        tags=['Super Admin Dashboard']
    )
    def patch(self, request):
        """Update the currently active privacy policy"""
        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if not policy:
            return Response(
                {"detail": "No active privacy policy found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = PrivacyPolicySerializer(policy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(serializer.data)
