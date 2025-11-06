from django.urls import path
from . import views

urlpatterns = [
    # Employee List APIs
    path('employees/', views.get_company_employees, name='get_company_employees'),
    path('employees/search/', views.get_company_employees_filtered, name='get_company_employees_filtered'),
]
