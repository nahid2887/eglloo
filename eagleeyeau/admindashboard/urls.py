from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaterialViewSet, EstimateDefaultsViewSet, ComponentViewSet, get_comprehensive_list

router = DefaultRouter()
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'estimate-defaults', EstimateDefaultsViewSet, basename='estimate-defaults')
router.register(r'components', ComponentViewSet, basename='component')

urlpatterns = [
    path('', include(router.urls)),
    path('comprehensive-list/', get_comprehensive_list, name='comprehensive-list'),
]

