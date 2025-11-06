"""
Centralized API response messages for consistency across all endpoints
"""

# Authentication Messages
AUTH_MESSAGES = {
    # Registration
    'REGISTER_SUCCESS': 'User registered successfully',
    'REGISTER_ERROR': 'Registration failed',
    
    # Login
    'LOGIN_SUCCESS': 'Login successful',
    'LOGIN_ERROR': 'Invalid credentials',
    'EMAIL_NOT_VERIFIED': 'Email not verified. Please verify your email first',
    
    # Logout
    'LOGOUT_SUCCESS': 'Logged out successfully',
    
    # OTP/Email Verification
    'OTP_SENT': 'OTP sent successfully to your email',
    'OTP_RESENT': 'OTP resent successfully',
    'OTP_VERIFIED': 'OTP verified successfully',
    'OTP_INVALID': 'Invalid or expired OTP',
    'EMAIL_VERIFIED': 'Email verified successfully',
    
    # Password Reset
    'PASSWORD_RESET_SUCCESS': 'Password reset successfully',
    'PASSWORD_RESET_ERROR': 'Password reset failed',
    'PASSWORD_RESET_OTP_SENT': 'Password reset OTP sent to your email',
    
    # Profile
    'PROFILE_UPDATED': 'Profile updated successfully',
    'PROFILE_RETRIEVED': 'Profile retrieved successfully',
    'PROFILE_UPDATE_ERROR': 'Profile update failed',
    
    # Token
    'TOKEN_REFRESH_SUCCESS': 'Token refreshed successfully',
    'TOKEN_INVALID': 'Invalid or expired token',
    
    # Invitation
    'INVITATION_SENT': 'Invitation sent successfully',
    'INVITATION_ACCEPTED': 'Invitation accepted successfully',
    'INVITATION_INVALID': 'Invalid or expired invitation',
    'INVITATION_ERROR': 'Failed to send invitation',
}

# Employee/Timesheet Messages
EMPLOYEE_MESSAGES = {
    # Clock In/Out
    'CLOCK_IN_SUCCESS': 'Clocked in successfully',
    'CLOCK_OUT_SUCCESS': 'Clocked out successfully',
    'ALREADY_CLOCKED_IN': 'Already clocked in for today',
    'NOT_CLOCKED_IN': 'Not clocked in yet',
    'ALREADY_CLOCKED_OUT': 'Already clocked out for today',
    
    # Time Entries
    'TIME_ENTRY_CREATED': 'Time entry created successfully',
    'TIME_ENTRY_UPDATED': 'Time entry updated successfully',
    'TIME_ENTRY_RETRIEVED': 'Time entry retrieved successfully',
    'TIME_ENTRIES_RETRIEVED': 'Time entries retrieved successfully',
    'TIME_ENTRY_ERROR': 'Time entry operation failed',
    
    # Weekly Hours
    'WEEKLY_HOURS_RETRIEVED': 'Weekly hours retrieved successfully',
    
    # Dashboard
    'DASHBOARD_RETRIEVED': 'Dashboard data retrieved successfully',
    
    # Status
    'STATUS_RETRIEVED': 'Status retrieved successfully',
}

# Admin Dashboard Messages
ADMIN_MESSAGES = {
    # Materials
    'MATERIAL_CREATED': 'Material created successfully',
    'MATERIAL_UPDATED': 'Material updated successfully',
    'MATERIAL_DELETED': 'Material deleted successfully',
    'MATERIAL_RETRIEVED': 'Material retrieved successfully',
    'MATERIALS_RETRIEVED': 'Materials retrieved successfully',
    'MATERIAL_ERROR': 'Material operation failed',
    
    # Components
    'COMPONENT_CREATED': 'Component created successfully',
    'COMPONENT_UPDATED': 'Component updated successfully',
    'COMPONENT_DELETED': 'Component deleted successfully',
    'COMPONENT_RETRIEVED': 'Component retrieved successfully',
    'COMPONENTS_RETRIEVED': 'Components retrieved successfully',
    'COMPONENT_ERROR': 'Component operation failed',
    
    # Estimate Defaults
    'ESTIMATE_CREATED': 'Estimate template created successfully',
    'ESTIMATE_UPDATED': 'Estimate template updated successfully',
    'ESTIMATE_DELETED': 'Estimate template deleted successfully',
    'ESTIMATE_RETRIEVED': 'Estimate template retrieved successfully',
    'ESTIMATES_RETRIEVED': 'Estimate templates retrieved successfully',
    'ESTIMATE_ERROR': 'Estimate template operation failed',
    
    # User Management
    'USER_CREATED': 'User created successfully',
    'USER_UPDATED': 'User updated successfully',
    'USER_DELETED': 'User deleted successfully',
    'USER_RETRIEVED': 'User retrieved successfully',
    'USERS_RETRIEVED': 'Users retrieved successfully',
    'USER_ERROR': 'User operation failed',
    'USER_NOT_FOUND': 'User not found',
    'ROLE_UPDATED': 'User role updated successfully',
}

# Super Admin Messages
SUPERADMIN_MESSAGES = {
    # Privacy Policy
    'PRIVACY_POLICY_UPDATED': 'Privacy policy updated successfully',
    'PRIVACY_POLICY_RETRIEVED': 'Privacy policy retrieved successfully',
    'PRIVACY_POLICY_ERROR': 'Privacy policy operation failed',
    'PRIVACY_POLICY_NOT_FOUND': 'No active privacy policy found',
    
    # Terms and Conditions
    'TERMS_UPDATED': 'Terms and conditions updated successfully',
    'TERMS_RETRIEVED': 'Terms and conditions retrieved successfully',
    'TERMS_ERROR': 'Terms and conditions operation failed',
    'TERMS_NOT_FOUND': 'No active terms and conditions found',
}

# General Messages
GENERAL_MESSAGES = {
    'SUCCESS': 'Operation completed successfully',
    'ERROR': 'Operation failed',
    'NOT_FOUND': 'Resource not found',
    'UNAUTHORIZED': 'Authentication required',
    'FORBIDDEN': 'You do not have permission to perform this action',
    'BAD_REQUEST': 'Invalid request data',
    'VALIDATION_ERROR': 'Validation error',
    'SERVER_ERROR': 'Internal server error',
}

# Permission Messages
PERMISSION_MESSAGES = {
    'ADMIN_ONLY': 'Only Admin users can access this endpoint',
    'EMPLOYEE_ONLY': 'Only Employee users can access this endpoint',
    'SUPERADMIN_ONLY': 'Only Super Admin users can access this endpoint',
    'NOT_AUTHORIZED': 'You are not authorized to access this resource',
}
