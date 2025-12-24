# Project Manager Company Dashboard API

## API Overview
A comprehensive dashboard API for Project Managers to view all company information including weekly progress, completed progress rates, and employee performance metrics.

## Endpoint
```
GET /api/project-manager/company-dashboard/
```

## Access Requirements
- **Authentication**: JWT Token (Bearer Token)
- **Permission**: Project Manager or Admin role
- **Company Scope**: Shows data for the user's company only

## Request Example
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/company-dashboard/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

## Response Structure

### Overall Statistics
```json
{
  "overall_stats": {
    "total_projects": 30,
    "active_projects": 15,
    "completed_projects": 10,
    "on_hold_projects": 2,
    "cancelled_projects": 3
  }
}
```

### Task Statistics
```json
{
  "task_stats": {
    "total_tasks": 90,
    "completed_tasks": 45,
    "in_progress_tasks": 30,
    "not_started_tasks": 15,
    "blocked_tasks": 0
  }
}
```

### Progress Rates (Percentages)
```json
{
  "progress_rate": {
    "overall_progress": 50.0,
    "project_completion_rate": 33.33,
    "task_completion_rate": 50.0
  }
}
```

### Weekly Progress
```json
{
  "weekly_progress": {
    "week_start": "2025-11-17",
    "week_end": "2025-11-23",
    "tasks_completed_this_week": 8,
    "projects_completed_this_week": 2,
    "new_tasks_created_this_week": 12
  }
}
```

### Upcoming Deadlines (Next 30 Days)
```json
{
  "upcoming_deadlines": [
    {
      "project_id": 5,
      "project_name": "Office Renovation",
      "deadline": "2025-11-25",
      "status": "in_progress",
      "tasks_completed": 5,
      "total_tasks": 10
    }
  ]
}
```

### Employee Summary & Performance
```json
{
  "employee_summary": {
    "total_employees": 15,
    "active_employees": 12,
    "top_performers": [
      {
        "employee_name": "John Smith",
        "tasks_completed": 25,
        "active_tasks": 3
      },
      {
        "employee_name": "Sarah Johnson",
        "tasks_completed": 22,
        "active_tasks": 5
      }
    ]
  }
}
```

## Complete Response Example
```json
{
  "success": true,
  "message": "Company dashboard data retrieved successfully",
  "data": {
    "overall_stats": {
      "total_projects": 30,
      "active_projects": 15,
      "completed_projects": 10,
      "on_hold_projects": 2,
      "cancelled_projects": 3
    },
    "task_stats": {
      "total_tasks": 90,
      "completed_tasks": 45,
      "in_progress_tasks": 30,
      "not_started_tasks": 15,
      "blocked_tasks": 0
    },
    "progress_rate": {
      "overall_progress": 50.0,
      "project_completion_rate": 33.33,
      "task_completion_rate": 50.0
    },
    "weekly_progress": {
      "week_start": "2025-11-17",
      "week_end": "2025-11-23",
      "tasks_completed_this_week": 8,
      "projects_completed_this_week": 2,
      "new_tasks_created_this_week": 12
    },
    "upcoming_deadlines": [
      {
        "project_id": 5,
        "project_name": "Office Renovation",
        "deadline": "2025-11-25",
        "status": "in_progress",
        "tasks_completed": 5,
        "total_tasks": 10
      }
    ],
    "employee_summary": {
      "total_employees": 15,
      "active_employees": 12,
      "top_performers": [
        {
          "employee_name": "John Smith",
          "tasks_completed": 25,
          "active_tasks": 3
        },
        {
          "employee_name": "Sarah Johnson",
          "tasks_completed": 22,
          "active_tasks": 5
        }
      ]
    }
  }
}
```

## Features

### Overall Statistics
- Total number of projects in the company
- Count by project status (Active, Completed, On Hold, Cancelled)

### Task Statistics
- Total tasks across all projects
- Breakdown by task status (Completed, In Progress, Not Started, Blocked)

### Progress Metrics
- **Overall Progress**: Percentage of completed tasks
- **Project Completion Rate**: Percentage of completed projects
- **Task Completion Rate**: Percentage of completed tasks

### Weekly Performance
- Week start and end dates (Monday-Sunday)
- Number of tasks completed this week
- Number of projects completed this week
- Number of new tasks created this week

### Upcoming Deadlines
- Projects with deadlines in next 30 days
- Shows project status and task progress for each deadline
- Sorted by deadline date

### Employee Performance
- Total active employees in company
- Top 5 performers with most completed tasks
- Shows active tasks for each top performer

## Testing in Swagger

1. Open: `http://10.10.13.27:8002/swagger/`
2. Find: **GET /api/project-manager/company-dashboard/**
3. Click **"Try it out"**
4. Click **"Execute"** (no parameters required)

## Integration Notes

### File Modifications
1. **Project_manager/views.py**: Added `company_dashboard()` function
2. **Project_manager/urls.py**: Added route `path('company-dashboard/', ...)`

### Dependencies
- Django ORM for database queries
- DRF-YASG for Swagger documentation
- Custom `format_response()` from response_formatter

### Filters & Queries
- Automatic weekly calculation (Monday-Sunday)
- 30-day upcoming deadline window
- Filters by company (request.user.company)
- Only counts active tasks (status='in_progress', 'not_started', or 'completed')

## Error Handling
Returns HTTP 500 with error message if any database query fails.

## Performance Considerations
- Uses Django ORM aggregation for efficient counting
- Limits top performers to 5 employees
- Limits upcoming deadlines to 10 projects
- All queries filtered by company scope
