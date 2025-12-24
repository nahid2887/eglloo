from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstimateViewSet, estimator_dashboard

router = DefaultRouter()
router.register(r'estimates', EstimateViewSet, basename='estimate')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', estimator_dashboard, name='estimator-dashboard'),
]
