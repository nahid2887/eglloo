# Lignaflow Authentication API

A complete Django REST Framework authentication system with JWT tokens, OTP verification, and Swagger documentation.

## Features

- ✅ User Registration with email verification
- ✅ Login with JWT tokens (access & refresh tokens)
- ✅ OTP-based email verification
- ✅ Password reset with OTP
- ✅ User profile management
- ✅ Swagger API documentation
- ✅ Email notifications

## Technologies

- Django 5.2.7
- Django REST Framework
- Simple JWT (JWT authentication)
- drf-yasg (Swagger documentation)
- python-decouple (environment variables)
- django-cors-headers (CORS support)

## Setup Instructions

### 1. Install Dependencies

All dependencies are already installed in the virtual environment at `env/`.

### 2. Environment Variables

The `.env` file is already configured in `eagleeyeau/.env` with:
```
EMAIL_HOST=smtp.strato.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@wiiz.ai
EMAIL_HOST_PASSWORD=Genovate_2025!
```

### 3. Database

Migrations have been applied. The SQLite database is ready at `eagleeyeau/db.sqlite3`.

### 4. Run Server

```bash
cd eagleeyeau
python manage.py runserver 8001
```

## API Endpoints

### Base URL
`http://127.0.0.1:8001/api/auth/`

### Swagger Documentation
- **Swagger UI**: http://127.0.0.1:8001/swagger/
- **ReDoc**: http://127.0.0.1:8001/redoc/

---

### 1. Register (Sign-Up)
**POST** `/api/auth/register/`

Register a new user and receive an OTP via email.

**Request Body:**
```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Lignaflow Inc",
  "country": "USA",
  "password": "SecurePassword123!",
  "confirm_password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully. Please check your email for OTP verification.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Lignaflow Inc",
    "country": "USA",
    "is_email_verified": false,
    "created_at": "2025-10-15T14:30:00Z"
  }
}
```

---

### 2. Verify OTP
**POST** `/api/auth/verify-otp/`

Verify the OTP sent to email and get access/refresh tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "8693"
}
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Lignaflow Inc",
    "country": "USA",
    "is_email_verified": true,
    "created_at": "2025-10-15T14:30:00Z"
  }
}
```

---

### 3. Resend OTP
**POST** `/api/auth/resend-otp/`

Resend OTP to email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent successfully to your email"
}
```

---

### 4. Login
**POST** `/api/auth/login/`

Login with email and password to get access/refresh tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Lignaflow Inc",
    "country": "USA",
    "is_email_verified": true,
    "created_at": "2025-10-15T14:30:00Z"
  }
}
```

---

### 5. Forgot Password
**POST** `/api/auth/forgot-password/`

Send OTP to email for password reset.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent successfully to your email"
}
```

---

### 6. Reset Password
**POST** `/api/auth/reset-password/`

Reset password with OTP verification.

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "8693",
  "new_password": "NewSecurePassword123!",
  "confirm_password": "NewSecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

---

### 7. Token Refresh
**POST** `/api/auth/token/refresh/`

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 8. User Profile
**GET** `/api/auth/profile/`

Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Lignaflow Inc",
  "country": "USA",
  "is_email_verified": true,
  "created_at": "2025-10-15T14:30:00Z"
}
```

---

**PUT/PATCH** `/api/auth/profile/`

Update user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "company_name": "New Company",
  "country": "Canada"
}
```

## Authentication Flow

### Registration Flow:
1. User registers → `POST /api/auth/register/`
2. User receives OTP via email (4-digit code)
3. User verifies OTP → `POST /api/auth/verify-otp/`
4. User receives access and refresh tokens
5. User can now access protected endpoints

### Login Flow:
1. User logs in → `POST /api/auth/login/`
2. System checks email verification
3. User receives access and refresh tokens
4. User can access protected endpoints

### Password Reset Flow:
1. User requests password reset → `POST /api/auth/forgot-password/`
2. User receives OTP via email
3. User resets password with OTP → `POST /api/auth/reset-password/`
4. User can log in with new password

## JWT Token Configuration

- **Access Token Lifetime**: 1 day
- **Refresh Token Lifetime**: 7 days
- **Token Type**: Bearer
- **Header Format**: `Authorization: Bearer <token>`

## Using Protected Endpoints

To access protected endpoints (like user profile), include the access token in the Authorization header:

```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     http://127.0.0.1:8001/api/auth/profile/
```

## Testing with Swagger

1. Open Swagger UI: http://127.0.0.1:8001/swagger/
2. Register a new user or login
3. Copy the access token from the response
4. Click the "Authorize" button (top right)
5. Enter: `Bearer <your_access_token>`
6. Now you can test all protected endpoints

## Email Configuration

The system uses the following email configuration:
- **Provider**: Strato SMTP
- **Host**: smtp.strato.com
- **Port**: 587
- **TLS**: Enabled
- **From**: noreply@wiiz.ai

## Database Models

### User Model
- Email (unique, used for login)
- Username (auto-generated from email)
- First Name
- Last Name
- Company Name (optional)
- Country (optional)
- Email Verified Status
- Timestamps

### OTP Model
- Email
- OTP Code (4-digit)
- Purpose (email_verification or password_reset)
- Expiry (10 minutes)
- Used Status
- Timestamps

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Email not verified
- `404 Not Found` - Resource not found

Error response format:
```json
{
  "error": "Error message here"
}
```

Or for validation errors:
```json
{
  "field_name": ["Error message for this field"]
}
```

## Admin Panel

Access the Django admin panel at: http://127.0.0.1:8001/admin/

To create a superuser:
```bash
python manage.py createsuperuser
```

## Development Notes

- The system uses SQLite database for development
- CORS is enabled for all origins (development only)
- Debug mode is enabled
- OTP expires after 10 minutes
- Tokens are rotated on refresh
- Email backend is configured for SMTP

## Security Features

- Password validation (minimum length, complexity)
- Email verification required for login
- JWT token authentication
- OTP expiration (10 minutes)
- One-time use OTPs
- Secure password hashing
- CSRF protection

## Project Structure

```
eagleeyeau/
├── authentication/
│   ├── models.py          # User and OTP models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── urls.py            # Authentication URLs
│   ├── utils.py           # Email utilities
│   └── admin.py           # Admin configuration
├── eagleeyeau/
│   ├── settings.py        # Django settings
│   ├── urls.py            # Main URLs with Swagger
│   └── .env               # Environment variables
├── manage.py
└── db.sqlite3
```

## Next Steps

1. **Test the APIs** using Swagger UI
2. **Create a superuser** to access admin panel
3. **Configure production email** settings when deploying
4. **Add frontend** to consume these APIs
5. **Deploy** to production with proper security settings

## Support

For any issues or questions, please contact support@lignaflow.com
