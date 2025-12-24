"""
URL configuration for eagleeyeau project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Lignaflow Authentication API",
        default_version='v1',
        description="""
        Complete authentication system with JWT tokens and OTP verification.
        
        ## Features:
        - User Registration with email verification
        - Login with JWT tokens (access & refresh)
        - OTP-based email verification
        - Password reset with OTP
        - User profile management
        
        ## Authentication:
        Most endpoints require JWT authentication. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your_access_token>
        ```
        """,
        terms_of_service="https://www.lignaflow.com/terms/",
        contact=openapi.Contact(email="support@lignaflow.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('api/auth/', include('authentication.urls')),
    
    # Timesheet URLs
    path('api/timesheet/', include('timesheet.urls')),
    
    # Super Admin Dashboard URLs
    path('api/superadmin/', include('superadmindashboard.urls')),
    
    # Admin Dashboard URLs
    path('api/admin/', include('admindashboard.urls')),
    
    # Estimator URLs (Single API for complete estimate creation)
    path('api/estimator/', include('estimator.urls')),
    
    # Project Manager URLs
    path('api/project-manager/', include('Project_manager.urls')),
    
    # Employee URLs
    path('api/employee/', include('emopye.urls')),
    
    # Swagger Documentation URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-root'),  # Default to Swagger UI
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
