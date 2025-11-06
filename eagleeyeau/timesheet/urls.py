from django.urls import path
from .views import (
    StartTimeView,
    EndTimeView,
    UpdateTimeEntryView,
    MyTimeEntriesView,
    WeeklyHoursView,
    TodayStatusView,
    AllEmployeeTimeEntriesView,
)

urlpatterns = [
    # Employee time tracking endpoints
    path('start/', StartTimeView.as_view(), name='start-time'),
    path('end/', EndTimeView.as_view(), name='end-time'),
    path('update/<int:entry_id>/', UpdateTimeEntryView.as_view(), name='update-time-entry'),
    path('my-entries/', MyTimeEntriesView.as_view(), name='my-time-entries'),
    path('weekly-hours/', WeeklyHoursView.as_view(), name='weekly-hours'),
    path('today-status/', TodayStatusView.as_view(), name='today-status'),
    
    # Admin endpoints
    path('admin/all-entries/', AllEmployeeTimeEntriesView.as_view(), name='all-time-entries'),
]
