from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import OTP, Invitation
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    OTPVerificationSerializer,
    SendOTPSerializer,
    PasswordResetSerializer,
    UserSerializer,
    TokenSerializer,
    SendInvitationSerializer,
    AcceptInvitationSerializer,
    InvitationSerializer,
    AdminUserSerializer,
    AdminUserRoleUpdateSerializer,
    UserProfileUpdateSerializer
)
from .utils import send_otp_email, send_invitation_email
from eagleeyeau.response_formatter import format_response, extract_error_message
from eagleeyeau.api_messages import AUTH_MESSAGES, GENERAL_MESSAGES

User = get_user_model()


class RegisterView(APIView):
    """
    API endpoint for user registration.
    Registers a new user and returns access and refresh tokens.
    """
    permission_classes = [AllowAny]
    # Do not run any authentication on this view — ignore any Authorization header
    authentication_classes = []

    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=TokenSerializer
            ),
            400: "Bad Request"
        },
        operation_description="Register a new user and return access and refresh tokens"
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Mark email as verified (no email verification required)
            user.is_email_verified = True
            user.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response(
                format_response(
                    data={
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data
                    },
                    message=AUTH_MESSAGES['REGISTER_SUCCESS'],
                    status_code=status.HTTP_201_CREATED
                ),
                status=status.HTTP_201_CREATED
            )
        
        # Extract first error message for the message field
        error_message = AUTH_MESSAGES['REGISTER_ERROR']
        if serializer.errors:
            # Get the first field's first error message
            first_field = next(iter(serializer.errors))
            first_error = serializer.errors[first_field]
            if isinstance(first_error, list) and first_error:
                error_message = f"{first_field}: {first_error[0]}"
            else:
                error_message = str(first_error)
        
        # Return validation errors in standard format
        return Response({
            'success': False,
            'message': error_message,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for user login.
    Returns access and refresh tokens upon successful authentication.
    """
    permission_classes = [AllowAny]
    # Bypass authentication for login endpoint to avoid token validation interfering
    authentication_classes = []

    @swagger_auto_schema(
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=TokenSerializer
            ),
            401: "Invalid credentials",
            403: "Email not verified"
        },
        operation_description="Login with email and password to get access and refresh tokens"
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Authenticate user
            user = authenticate(username=email, password=password)
            
            if user is None:
                return Response(
                    format_response(
                        data=None,
                        message=AUTH_MESSAGES['LOGIN_ERROR'],
                        success=False
                    ),
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response(
                format_response(
                    data={
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data
                    },
                    message=AUTH_MESSAGES['LOGIN_SUCCESS'],
                ),
                status=status.HTTP_200_OK
            )
        
        # Extract first error message for the message field
        error_message = AUTH_MESSAGES['LOGIN_ERROR']
        if serializer.errors:
            # Get the first field's first error message
            first_field = next(iter(serializer.errors))
            first_error = serializer.errors[first_field]
            if isinstance(first_error, list) and first_error:
                error_message = f"{first_field}: {first_error[0]}"
            else:
                error_message = str(first_error)
        
        # Return validation errors in standard format
        return Response({
            'success': False,
            'message': error_message,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    API endpoint for OTP verification (for password reset).
    Verifies the OTP for password reset flow.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=OTPVerificationSerializer,
        responses={
            200: openapi.Response(
                description="OTP verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Invalid or expired OTP"
        },
        operation_description="Verify OTP for password reset (use this before reset-password endpoint)"
    )
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found',
                    'error': {'email': ['User not found']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Find valid OTP for password reset
            otp = OTP.objects.filter(
                email=email,
                otp=otp_code,
                purpose='password_reset',
                is_used=False
            ).first()
            
            if not otp or not otp.is_valid():
                return Response({
                    'success': False,
                    'message': AUTH_MESSAGES.get('OTP_INVALID', 'Invalid or expired OTP'),
                    'error': {'otp': ['Invalid or expired OTP']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as verified (but not used yet)
            otp.is_verified = True
            otp.save()
            
            return Response(
                format_response(
                    data={'email': email},
                    message=AUTH_MESSAGES.get('OTP_VERIFIED', 'OTP verified successfully'),
                    success=True
                ),
                status=status.HTTP_200_OK
            )
        
        # Validation errors: extract concise message and return standardized envelope
        error_message = extract_error_message(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'message': error_message,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class ResendOTPView(APIView):
    """
    API endpoint for resending OTP (for password reset).
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=SendOTPSerializer,
        responses={
            200: "OTP sent successfully",
            400: "Bad Request"
        },
        operation_description="Resend OTP for password reset"
    )
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create and send new OTP for password reset
            otp = OTP.create_otp(email, 'password_reset')
            send_otp_email(email, otp.otp, 'password_reset')
            
            return Response({
                'message': 'OTP sent successfully to your email'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    """
    API endpoint for forgot password.
    Sends OTP to email for password reset.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=SendOTPSerializer,
        responses={
            200: "OTP sent successfully",
            404: "User not found"
        },
        operation_description="Send OTP for password reset"
    )
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Return standardized not-found error
                return Response({
                    'success': False,
                    'message': 'No user found with this email address.',
                    'error': {'email': ['No user found with this email address.']}
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create and send OTP
            otp = OTP.create_otp(email, 'password_reset')
            send_otp_email(email, otp.otp, 'password_reset')
            
            return Response(
                format_response(
                    data=None,
                    message=AUTH_MESSAGES.get('PASSWORD_RESET_OTP_SENT', 'OTP sent successfully to your email'),
                    success=True
                ),
                status=status.HTTP_200_OK
            )
        
        # Validation errors: extract a concise message and return standardized error envelope
        error_message = extract_error_message(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'message': error_message,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """
    API endpoint for resetting password.
    User must verify OTP first using /verify-otp/ endpoint before calling this.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        request_body=PasswordResetSerializer,
        responses={
            200: "Password reset successfully",
            400: "OTP not verified or expired"
        },
        operation_description="Reset password after OTP verification (call /verify-otp/ first)"
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found',
                    'error': {'email': ['User not found']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if there's a verified OTP for password reset
            otp = OTP.objects.filter(
                email=email,
                purpose='password_reset',
                is_verified=True,
                is_used=False
            ).first()
            
            if not otp or not otp.is_valid():
                return Response({
                    'success': False,
                    'message': AUTH_MESSAGES.get('OTP_INVALID', 'OTP not verified or expired. Please verify OTP first.'),
                    'error': {'otp': ['OTP not verified or expired. Please verify OTP first.']}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mark OTP as used and reset password
            otp.is_used = True
            otp.save()
            
            user.set_password(new_password)
            user.save()
            
            return Response(
                format_response(
                    data=None,
                    message=AUTH_MESSAGES.get('PASSWORD_RESET_SUCCESS', 'Password reset successfully'),
                    success=True
                ),
                status=status.HTTP_200_OK
            )
        
        # Validation errors: extract concise message and return standardized envelope
        error_message = extract_error_message(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'message': error_message,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    Supports profile image upload using multipart/form-data.
    Users cannot update their own role.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        responses={
            200: UserSerializer
        },
        operation_description="Get current user profile with role and profile image"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: UserSerializer
        },
        operation_description="Update current user profile (use multipart/form-data for image upload). Fields: first_name, last_name, company_name, country, profile_image (file). Role cannot be changed."
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            200: UserSerializer
        },
        operation_description="Partially update current user profile (use multipart/form-data for image upload). Fields: first_name, last_name, company_name, country, profile_image (file). Role cannot be changed."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


# ========== ADMIN INVITATION SYSTEM ==========

class SendInvitationView(APIView):
    """
    API endpoint for admin to send invitation link to user.
    Only accessible by admin users.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=SendInvitationSerializer,
        responses={
            201: openapi.Response(
                description="Invitation sent successfully",
                schema=InvitationSerializer
            ),
            400: "Bad Request",
            403: "Not authorized"
        },
        operation_description="Send invitation link to user's email (Admin only)"
    )
    def post(self, request):
        # Check if user is admin
        if request.user.role != 'Admin':
            return Response({
                'error': 'Only admins can send invitations'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SendInvitationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            role = serializer.validated_data['role']
            
            # Create invitation
            invitation = Invitation.create_invitation(
                email=email,
                role=role,
                invited_by=request.user
            )
            
            # Send invitation email with admin's company name
            base_url = request.build_absolute_uri('/').rstrip('/')
            company_name = request.user.company_name or 'Not specified'
            send_invitation_email(email, role, invitation.token, company_name, base_url)
            
            return Response({
                'message': 'Invitation sent successfully',
                'invitation': InvitationSerializer(invitation).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AcceptInvitationView(APIView):
    """
    API endpoint for user to accept invitation and set password.
    """
    permission_classes = [AllowAny]
    # Ignore any Authorization header for invitation acceptance
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Verify invitation token and get pre-filled information (email, role, company name)",
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_PATH,
                description="Invitation token (UUID format)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Invitation details",
                examples={
                    'application/json': {
                        'success': True,
                        'message': 'Invitation is valid',
                        'data': {
                            'email': 'user@example.com',
                            'role': 'Estimator',
                            'company_name': 'ABC Company',
                            'expires_at': '2025-11-08T10:00:00Z',
                            'invited_by': 'Admin Name'
                        }
                    }
                }
            ),
            400: "Invalid or expired invitation"
        }
    )
    def get(self, request, token):
        """Get invitation details (verify token and show pre-filled info)"""
        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid invitation token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not invitation.is_valid():
            return Response({
                'success': False,
                'error': 'Invitation has expired or already been used'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': 'Invitation is valid',
            'data': {
                'email': invitation.email,
                'role': invitation.role,
                'company_name': invitation.company_name,
                'expires_at': invitation.expires_at,
                'invited_by': invitation.invited_by.get_full_name() if invitation.invited_by else None
            }
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['password', 'confirm_password', 'first_name', 'last_name'],
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password (min 8 characters)'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm password'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country (optional)'),
            },
            example={
                'password': 'SecurePassword123!',
                'confirm_password': 'SecurePassword123!',
                'first_name': 'John',
                'last_name': 'Doe',
                'country': 'USA'
            }
        ),
        responses={
            201: openapi.Response(
                description="Invitation accepted successfully. Email, role, and company name are auto-filled from invitation.",
                schema=TokenSerializer
            ),
            400: "Bad Request or invalid/expired invitation"
        },
        operation_description="""Accept invitation and create account. 
        
Token must be in URL path (UUID format).

Email, role, and company name are automatically taken from the invitation - DO NOT include them in request body.

Required fields:
- password
- confirm_password  
- first_name
- last_name

Optional fields:
- country""",
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_PATH,
                description="Invitation token (UUID format)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def post(self, request, token):
        serializer = AcceptInvitationSerializer(data=request.data)
        if serializer.is_valid():
            # Token comes from URL now, not from body
            
            # Find valid invitation
            try:
                invitation = Invitation.objects.get(token=token)
            except Invitation.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid invitation token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not invitation.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invitation has expired or already been used'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user with pre-filled data from invitation
            user_data = {
                'email': invitation.email,  # From invitation, cannot change
                'username': invitation.email.split('@')[0],
                'first_name': serializer.validated_data['first_name'],
                'last_name': serializer.validated_data['last_name'],
                'company_name': invitation.company_name or '',  # From admin's company, cannot change
                'country': serializer.validated_data.get('country', ''),
                'role': invitation.role,  # From invitation, cannot change
                'invited_by': invitation.invited_by,  # Track who invited this user
                'is_email_verified': True,  # Email already verified through invitation
            }
            
            user = User.objects.create_user(
                **user_data,
                password=serializer.validated_data['password']
            )
            
            # Mark invitation as used
            invitation.is_used = True
            invitation.accepted_at = timezone.now()
            invitation.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Account created successfully',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========== ADMIN USER MANAGEMENT ==========

class AdminUserListView(generics.ListAPIView):
    """
    API endpoint for admin to view users invited by them.
    Excludes other admins and shows only invited users.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        # Check if user is admin
        if self.request.user.role != 'Admin':
            return User.objects.none()
        
        # Return only users invited by this admin (exclude admins)
        return User.objects.filter(
            invited_by=self.request.user
        ).exclude(
            role='Admin'
        ).order_by('-created_at')

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="List of users invited by this admin",
                schema=AdminUserSerializer(many=True)
            ),
            403: "Not authorized"
        },
        operation_description="Get list of users invited by this admin (excludes other admins)"
    )
    def get(self, request, *args, **kwargs):
        if request.user.role != 'Admin':
            return Response({
                'error': 'Only admins can view user list'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for admin to view, update role, or delete users they invited.
    Admin can only manage users they invited.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        # Return only users invited by this admin (exclude admins)
        return User.objects.filter(
            invited_by=self.request.user
        ).exclude(
            role='Admin'
        )

    def get_serializer_class(self):
        if self.request.method == 'PATCH' and 'role' in self.request.data:
            return AdminUserRoleUpdateSerializer
        return AdminUserSerializer

    def check_admin_permission(self):
        """Check if user is admin"""
    def check_admin_permission(self):
        """Check if user is admin"""
        if self.request.user.role != 'Admin':
            return False
        return True
    
    def check_user_ownership(self):
        """Check if the target user was invited by current admin"""
        user = self.get_object()
        return user.invited_by == self.request.user

    @swagger_auto_schema(
        responses={
            200: AdminUserSerializer,
            403: "Not authorized",
            404: "User not found or not invited by you"
        },
        operation_description="Get user details by ID (only for users you invited)"
    )
    def get(self, request, *args, **kwargs):
        if not self.check_admin_permission():
            return Response({
                'error': 'Only admins can view user details'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=AdminUserRoleUpdateSerializer,
        responses={
            200: AdminUserSerializer,
            403: "Not authorized",
            404: "User not found or not invited by you"
        },
        operation_description="Update user role (only for users you invited)"
    )
    def patch(self, request, *args, **kwargs):
        if not self.check_admin_permission():
            return Response({
                'error': 'Only admins can update user roles'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            204: "User deleted successfully",
            403: "Not authorized",
            404: "User not found or not invited by you"
        },
        operation_description="Delete user account (only for users you invited)"
    )
    def delete(self, request, *args, **kwargs):
        if not self.check_admin_permission():
            return Response({
                'error': 'Only admins can delete users'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        
        user.delete()
        return Response({
            'message': 'User deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
