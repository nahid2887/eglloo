# Admin Dashboard - Projects API Guide

## Overview
This guide documents the new Admin Dashboard Projects API endpoints that allow admins to view and manage all projects belonging to their company.

---

## Base URL
```
/api/admin/
```

---

## Endpoints

### 1. Get All Projects of Admin's Company
**Endpoint:** `GET /api/admin/projects/`

**Description:** Retrieve all projects belonging to the admin's company with search and filtering capabilities.

**Authentication:** Required (Admin role)

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search by project name or client name | `search=My House` |
| `status` | string | Filter by project status | `status=in_progress` |
| `sort_by` | string | Sort field (project_name, client_name, creating_date, start_date, status) | `sort_by=creating_date` |
| `sort_order` | string | Sort order - asc or desc (default: desc for dates) | `sort_order=asc` |

**Valid Status Values:**
- `not_started`
- `in_progress`
- `completed`
- `on_hold`
- `cancelled`

**Example Requests:**

```bash
# Get all projects
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search for specific project
curl -X GET "http://localhost:8000/api/admin/projects/?search=My%20House" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/admin/projects/?status=completed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search with multiple filters
curl -X GET "http://localhost:8000/api/admin/projects/?search=John&status=in_progress&sort_by=creating_date&sort_order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Example:**
```json
{
  "success": true,
  "message": "Projects retrieved successfully (Total: 2)",
  "data": {
    "total_count": 2,
    "filters_applied": {
      "search": null,
      "status": null,
      "sort_by": "creating_date",
      "sort_order": "desc"
    },
    "results": [
      {
        "id": 1,
        "project_name": "My House",
        "client_name": "John Smith",
        "status": "in_progress",
        "creating_date": "2025-02-25",
        "start_date": "2025-02-25",
        "end_date": "2025-03-25",
        "total_amount": "12000.00",
        "rooms": ["Living Room", "Bedroom", "Kitchen"],
        "tasks_count": 5,
        "assigned_employees_count": 2,
        "created_by_name": "Admin User",
        "assigned_to_name": "Project Manager Name",
        "created_at": "2025-02-25T10:30:00Z"
      },
      {
        "id": 2,
        "project_name": "My Office",
        "client_name": "Argentina Company",
        "status": "completed",
        "creating_date": "2025-02-25",
        "start_date": "2025-02-25",
        "end_date": "2025-02-25",
        "total_amount": "12000.00",
        "rooms": ["Office Space"],
        "tasks_count": 3,
        "assigned_employees_count": 1,
        "created_by_name": "Admin User",
        "assigned_to_name": null,
        "created_at": "2025-02-25T10:35:00Z"
      }
    ]
  }
}
```

---

### 2. Get Detailed Project Information
**Endpoint:** `GET /api/admin/projects/<project_id>/`

**Description:** Retrieve comprehensive details of a specific project including all tasks, estimate details, and task statistics.

**Authentication:** Required (Admin role)

**Path Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `project_id` | integer | ID of the project | `1` |

**Example Requests:**

```bash
# Get project details
curl -X GET "http://localhost:8000/api/admin/projects/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response Example:**
```json
{
  "success": true,
  "message": "Project details retrieved successfully",
  "data": {
    "project": {
      "id": 1,
      "estimate": 1,
      "project_name": "My House",
      "client_name": "John Smith",
      "description": "A beautiful house renovation project",
      "status": "in_progress",
      "creating_date": "2025-02-25",
      "start_date": "2025-02-25",
      "end_date": "2025-03-25",
      "total_amount": "12000.00",
      "estimated_cost": "10000.00",
      "rooms": ["Living Room", "Bedroom", "Kitchen"],
      "created_by": 1,
      "assigned_to": 2,
      "created_at": "2025-02-25T10:30:00Z",
      "updated_at": "2025-02-25T10:30:00Z"
    },
    "estimate": {
      "id": 1,
      "serial_number": "EST-001",
      "estimate_number": "2025-001",
      "client_name": "John Smith",
      "project_name": "My House",
      "status": "approved",
      "total_amount": "12000.00",
      "created_at": "2025-02-25T10:00:00Z",
      "created_by": 1,
      "items": [
        {
          "id": 1,
          "description": "Wood Flooring",
          "quantity": 100,
          "unit_price": "50.00",
          "total": "5000.00"
        }
      ]
    },
    "tasks": [
      {
        "id": 1,
        "project": 1,
        "task_name": "Foundation Work",
        "description": "Prepare foundation",
        "room": "Living Room",
        "status": "in_progress",
        "priority": "high",
        "phase": "construction",
        "start_date": "2025-02-25",
        "end_date": "2025-03-05",
        "assigned_employee_id": 3,
        "assigned_employee_name": "John Doe",
        "assigned_employee": {
          "id": 3,
          "email": "john@example.com",
          "first_name": "John",
          "last_name": "Doe",
          "role": "Employee"
        },
        "created_at": "2025-02-25T10:30:00Z",
        "updated_at": "2025-02-25T10:30:00Z"
      },
      {
        "id": 2,
        "project": 1,
        "task_name": "Wall Painting",
        "description": "Paint all walls",
        "room": "Kitchen",
        "status": "not_started",
        "priority": "medium",
        "phase": "construction",
        "start_date": "2025-03-05",
        "end_date": "2025-03-15",
        "assigned_employee_id": 4,
        "assigned_employee_name": "Jane Smith",
        "assigned_employee": {
          "id": 4,
          "email": "jane@example.com",
          "first_name": "Jane",
          "last_name": "Smith",
          "role": "Employee"
        },
        "created_at": "2025-02-25T10:32:00Z",
        "updated_at": "2025-02-25T10:32:00Z"
      }
    ],
    "task_summary": {
      "total_tasks": 5,
      "by_status": {
        "not_started": 2,
        "in_progress": 2,
        "completed": 1,
        "blocked": 0
      },
      "by_priority": {
        "low": 1,
        "medium": 2,
        "high": 2
      }
    }
  }
}
```

---

## Data Structure

### Project Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique project identifier |
| `project_name` | string | Name of the project |
| `client_name` | string | Client/customer name |
| `description` | string | Project description |
| `status` | string | Current project status |
| `creating_date` | date | Date project was created |
| `start_date` | date | Planned project start date |
| `end_date` | date | Planned project end date |
| `total_amount` | decimal | Total project budget/value |
| `estimated_cost` | decimal | Estimated cost |
| `rooms` | array | List of rooms involved in project |
| `tasks_count` | integer | Number of tasks in project |
| `assigned_employees_count` | integer | Number of unique employees assigned |
| `created_by_name` | string | Name of admin who created project |
| `assigned_to_name` | string | Name of assigned project manager |

### Task Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique task identifier |
| `task_name` | string | Name of the task |
| `description` | string | Task description |
| `room` | string | Room where task takes place |
| `status` | string | Task status (not_started, in_progress, completed, blocked) |
| `priority` | string | Task priority (low, medium, high) |
| `phase` | string | Project phase (planning, design, procurement, construction, handover) |
| `start_date` | date | Task start date |
| `end_date` | date | Task end date |
| `assigned_employee_name` | string | Name of assigned employee |
| `assigned_employee` | object | Full employee details |

---

## Error Responses

### 401 Unauthorized
```json
{
  "success": false,
  "message": "Authentication credentials were not provided.",
  "data": null
}
```

### 403 Forbidden
```json
{
  "success": false,
  "message": "Access denied",
  "data": null
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Project not found or access denied",
  "data": null
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Error retrieving project details: [error details]",
  "data": null
}
```

---

## Features

### 1. Company-Based Access Control
- Admins can only see projects from their own company
- Projects are filtered based on the estimate creator's company

### 2. Comprehensive Project Details
- Get complete project information including:
  - Project metadata (name, client, status, dates)
  - Estimate details and budget breakdown
  - All associated tasks with employee assignments
  - Task statistics (count by status and priority)

### 3. Flexible Search and Filtering
- Search across project names and client names
- Filter by project status
- Sort by various fields (name, client, date, status)
- Combine multiple filters for precise results

### 4. Task Management Insights
- View all tasks within a project
- See task status distribution
- Track priority levels
- Identify assigned employees

---

## Common Use Cases

### View All Projects Dashboard
```bash
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer TOKEN"
```

### Search for Project by Client Name
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?search=John%20Smith" \
  -H "Authorization: Bearer TOKEN"
```

### Get In-Progress Projects Only
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?status=in_progress" \
  -H "Authorization: Bearer TOKEN"
```

### Get Completed Projects Sorted by Date (Newest First)
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?status=completed&sort_by=creating_date&sort_order=desc" \
  -H "Authorization: Bearer TOKEN"
```

### View Full Details of Specific Project
```bash
curl -X GET "http://localhost:8000/api/admin/projects/1/" \
  -H "Authorization: Bearer TOKEN"
```

---

## Integration Notes

### Frontend Display
The API provides all necessary data to display:
- Projects table with filtering and sorting
- Project detail page with task breakdown
- Task status charts
- Employee assignment tracking
- Project timeline and progress

### Data Pagination
The current implementation returns all matching results. For large datasets, consider implementing pagination in your frontend or backend.

### Real-time Updates
For real-time project updates, consider implementing WebSocket connections alongside these REST endpoints.

---

## Security Considerations

1. **Company Isolation**: Projects are strictly filtered by the admin's company
2. **Authentication Required**: All endpoints require valid authentication
3. **Admin Role Required**: Only users with Admin role can access these endpoints
4. **Company Validation**: System verifies the requesting admin's company on each request

---

## Version History
- **v1.0** (2025-11-25): Initial release with project list and detail endpoints
  - Get all projects with search/filter
  - Get project details with tasks
  - Task summary statistics
