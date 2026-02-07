from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'projects', views.ProjectViewSet, basename='project')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Download project as PDF
    path('projects/<int:pk>/download-documents/', views.ProjectViewSet.as_view({'get': 'download_documents'}), name='project-download-documents'),
    
    # Nested URL for tasks within a project
    path('projects/<int:project_id>/tasks/', views.TaskViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='project-tasks-list'),
    path('projects/<int:project_id>/tasks/<int:pk>/', views.TaskViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='project-task-detail'),
    
    # Employee List APIs
    path('employees/', views.get_company_employees, name='get_company_employees'),
    path('employees/search/', views.get_company_employees_filtered, name='get_company_employees_filtered'),
    
    # Gantt Chart API
    path('projects/<int:pk>/gantt-chart/', views.ProjectViewSet.as_view({'get': 'gantt_chart'}), name='project-gantt-chart'),
    
    # Project Manager - All Projects View
    path('all-projects/', views.get_all_projects_with_progress, name='get_all_projects_with_progress'),
    
    # Company Dashboard
    path('company-dashboard/', views.company_dashboard, name='company_dashboard'),
    
    # Employee Timesheet Management
    path('employee-timesheets/', views.view_company_timesheets, name='view_company_timesheets'),
    
    # Estimate APIs
    path('estimates/', views.get_estimates_list, name='get_estimates_list'),
    path('estimates/<int:estimate_id>/', views.get_estimate_detail, name='get_estimate_detail'),
]
