from django.urls import path
from .views import (
    EmployeeStartTimeView,
    EmployeeEndTimeView,
    EmployeeMyTimeEntriesView,
    EmployeeWeeklyHoursView,
    EmployeeTodayStatusView,
    EmployeeDashboardView,
)

urlpatterns = [
    # Employee time tracking endpoints (Employee role only)
    path('start/', EmployeeStartTimeView.as_view(), name='employee-start-time'),
    path('end/', EmployeeEndTimeView.as_view(), name='employee-end-time'),
    path('my-entries/', EmployeeMyTimeEntriesView.as_view(), name='employee-my-entries'),
    path('weekly-hours/', EmployeeWeeklyHoursView.as_view(), name='employee-weekly-hours'),
    path('today-status/', EmployeeTodayStatusView.as_view(), name='employee-today-status'),
    path('dashboard/', EmployeeDashboardView.as_view(), name='employee-dashboard'),
]
