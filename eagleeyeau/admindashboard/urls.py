from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MaterialViewSet, 
    EstimateDefaultsViewSet, 
    ComponentViewSet, 
    AdminEstimateViewSet, 
    get_comprehensive_list, 
    admin_dashboard_overview,
    admin_all_projects,
    admin_project_detail,
)

router = DefaultRouter()
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'estimate-defaults', EstimateDefaultsViewSet, basename='estimate-defaults')
router.register(r'components', ComponentViewSet, basename='component')
router.register(r'estimates', AdminEstimateViewSet, basename='admin-estimate')

urlpatterns = [
    path('', include(router.urls)),
    path('comprehensive-list/', get_comprehensive_list, name='comprehensive-list'),
    path('dashboard-overview/', admin_dashboard_overview, name='admin-dashboard-overview'),
    path('projects/', admin_all_projects, name='admin-all-projects'),
    path('projects/<int:project_id>/', admin_project_detail, name='admin-project-detail'),
]

