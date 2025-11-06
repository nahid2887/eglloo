from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Invitation

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'company_name', 'country', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Generate username from email
        validated_data['username'] = validated_data['email'].split('@')[0]
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class OTPVerificationSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP"""
    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset after OTP verification"""
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    profile_image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'company_name', 'country', 'role', 'profile_image', 'is_email_verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'username', 'is_email_verified', 'created_at', 'updated_at']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user profile update - role is read-only"""
    profile_image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'company_name', 'country', 'profile_image']


class AdminUserSerializer(serializers.ModelSerializer):
    """Serializer for admin to view and manage users"""
    profile_image = serializers.ImageField(required=False, allow_null=True)
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'company_name', 'country', 'role', 'profile_image', 'invited_by_email', 'is_email_verified', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'username', 'invited_by_email', 'is_email_verified', 'created_at', 'updated_at']


class AdminUserRoleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin to update user role"""
    
    class Meta:
        model = User
        fields = ['role']
    
    def validate_role(self, value):
        """Validate role - allow predefined roles or any custom text, but not Admin"""
        allowed_roles = ['Employee', 'Estimator', 'Project Manager']
        
        # Don't allow changing to Admin role
        if value == 'Admin':
            raise serializers.ValidationError("Cannot change user role to Admin")
        
        # Allow predefined roles or any custom role text
        return value


class SendInvitationSerializer(serializers.Serializer):
    """Serializer for sending invitation"""
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True, max_length=100)

    def validate_email(self, value):
        """Check if user already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value
    
    def validate_role(self, value):
        """Validate role - allow predefined roles or any custom text"""
        # Define allowed predefined roles (excluding Admin)
        allowed_roles = ['Employee', 'Estimator', 'Project Manager']
        
        # If it's a predefined role, validate it
        if value in allowed_roles:
            return value
        
        # If it's not a predefined role, allow it as custom role (for "Other" option)
        # But don't allow setting role as 'Admin' via invitation
        if value == 'Admin':
            raise serializers.ValidationError("Cannot invite users with Admin role")
        
        # Allow any other custom role text
        return value


class AcceptInvitationSerializer(serializers.Serializer):
    """Serializer for accepting invitation and setting password (token is in URL)"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    company_name = serializers.CharField(required=False, max_length=255, allow_blank=True)
    country = serializers.CharField(required=False, max_length=100, allow_blank=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs


class InvitationSerializer(serializers.ModelSerializer):
    """Serializer for invitation details"""
    invited_by_email = serializers.EmailField(source='invited_by.email', read_only=True)
    
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'role', 'company_name', 'token', 'invited_by_email', 'created_at', 'expires_at', 'is_used', 'accepted_at']
        read_only_fields = ['id', 'token', 'company_name', 'invited_by_email', 'created_at', 'expires_at', 'is_used', 'accepted_at']


class TokenSerializer(serializers.Serializer):
    """Serializer for token response"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
