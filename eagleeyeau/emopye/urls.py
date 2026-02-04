from django.urls import path
from .views import (
    get_employee_assigned_tasks,
    get_single_assigned_task,
    update_employee_task_status,
    get_employee_assigned_projects,
    get_single_assigned_project,
    get_employee_project_tasks,
    update_task_status,
    get_employee_task_schedule,
    toggle_task_timer,
    edit_task_timer,
    get_daily_timer_summary,
    get_employee_info,
    get_employee_timesheet_entries,
)

urlpatterns = [
    # Employee Profile
    path('info/', get_employee_info, name='employee-info'),
    
    # Employee Assigned Tasks
    path('assigned-tasks/', get_employee_assigned_tasks, name='employee-assigned-tasks'),
    path('assigned-tasks/<int:task_id>/', get_single_assigned_task, name='employee-single-task'),
    path('update-task-status/', update_employee_task_status, name='update-task-status'),
    
    # Employee Task Schedule (sorted by dates)
    path('task-schedule/', get_employee_task_schedule, name='employee-task-schedule'),
    
    # Employee Task Timer
    path('timer/toggle/', toggle_task_timer, name='toggle-task-timer'),
    path('timer/edit/<int:timer_id>/', edit_task_timer, name='edit-task-timer'),
    path('timer/daily-summary/', get_daily_timer_summary, name='daily-timer-summary'),
    
    # Employee Timesheet Entries
    path('timesheet/entries/', get_employee_timesheet_entries, name='employee-timesheet-entries'),
    
    # Employee Assigned Projects
    path('assigned-projects/', get_employee_assigned_projects, name='employee-assigned-projects'),
    path('assigned-projects/<int:project_id>/', get_single_assigned_project, name='employee-single-project'),
    path('projects/<int:project_id>/tasks/', get_employee_project_tasks, name='employee-project-tasks'),
    
    # RESTful Task Status Update
    path('tasks/<int:task_id>/status/', update_task_status, name='update-task-status-restful'),
]
#