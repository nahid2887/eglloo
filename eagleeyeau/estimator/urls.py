from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstimateViewSet

router = DefaultRouter()
router.register(r'estimates', EstimateViewSet, basename='estimate')

urlpatterns = [
    path('', include(router.urls)),
]
