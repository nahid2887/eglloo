# Project Manager - All Projects API

## Overview
API endpoint for Project Managers to view all projects with progress tracking, statistics, and deadline information - matching the UI design shown in the image.

## Endpoint
```
GET /api/project-manager/all-projects/
```

## Authentication
- **Required**: Yes (Bearer Token)
- **Role**: Project Manager or Admin only

## Features
✅ View all projects in the system  
✅ Progress percentage calculation (based on completed tasks)  
✅ Total tasks and completed tasks count  
✅ Deadline status (days left to deliver)  
✅ Project statistics (total, completed, due, cancelled)  
✅ Filter by project status  
✅ Search by project name or client name  

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by project status: `not_started`, `in_progress`, `completed`, `on_hold`, `cancelled` |
| `search` | string | No | Search in project name or client name |

## Response Format

### Success Response (200 OK)
```json
{
    "success": true,
    "message": "Retrieved 5 projects",
    "data": {
        "statistics": {
            "total_projects": 5,
            "completed_projects": 2,
            "due_projects": 2,
            "cancelled_projects": 1
        },
        "projects": [
            {
                "id": 6,
                "project_name": "Home Renovation",
                "client_name": "John Doe",
                "description": "Design the layout of the kitchen, including the arrangement of cabinets.",
                "status": "in_progress",
                "progress": 35,
                "creating_date": "2025-04-20",
                "start_date": "2025-04-20",
                "end_date": "2025-05-23",
                "deadline_status": "20 days left to deliver",
                "total_amount": "50000.00",
                "estimated_cost": "45000.00",
                "rooms": ["Kitchen", "Living Room"],
                "total_tasks": 5,
                "completed_tasks": 1,
                "created_by_name": "Mostir Anderson",
                "created_at": "2025-04-20T10:30:00Z",
                "updated_at": "2025-05-01T14:20:00Z"
            },
            {
                "id": 7,
                "project_name": "Office renovation",
                "client_name": "ABC Corp",
                "description": "Design the layout of the kitchen, including the arrangement of cabinets.",
                "status": "in_progress",
                "progress": 35,
                "creating_date": "2025-04-20",
                "start_date": "2025-04-20",
                "end_date": "2025-05-23",
                "deadline_status": "20 days left to deliver",
                "total_amount": "75000.00",
                "estimated_cost": "70000.00",
                "rooms": ["Office", "Conference Room"],
                "total_tasks": 5,
                "completed_tasks": 1,
                "created_by_name": "Project Manager",
                "created_at": "2025-04-20T11:00:00Z",
                "updated_at": "2025-05-01T15:00:00Z"
            },
            {
                "id": 8,
                "project_name": "Retail store fit out",
                "client_name": "XYZ Ltd",
                "description": "Design the layout of the kitchen, including the arrangement of cabinets.",
                "status": "in_progress",
                "progress": 35,
                "creating_date": "2025-04-20",
                "start_date": "2025-04-20",
                "end_date": "2025-05-23",
                "deadline_status": "20 days left to deliver",
                "total_amount": "60000.00",
                "estimated_cost": "55000.00",
                "rooms": ["Store Front", "Back Office"],
                "total_tasks": 5,
                "completed_tasks": 1,
                "created_by_name": "Project Manager",
                "created_at": "2025-04-20T12:00:00Z",
                "updated_at": "2025-05-01T16:00:00Z"
            },
            {
                "id": 9,
                "project_name": "Warehouse Expansion",
                "client_name": "Logistics Co",
                "description": "Design the layout of the kitchen, including the arrangement of cabinets.",
                "status": "in_progress",
                "progress": 35,
                "creating_date": "2025-04-20",
                "start_date": "2025-04-20",
                "end_date": "2025-05-23",
                "deadline_status": "20 days left to deliver",
                "total_amount": "90000.00",
                "estimated_cost": "85000.00",
                "rooms": ["Warehouse", "Loading Bay"],
                "total_tasks": 0,
                "completed_tasks": 0,
                "created_by_name": "Project Manager",
                "created_at": "2025-04-20T13:00:00Z",
                "updated_at": "2025-05-01T17:00:00Z"
            }
        ]
    }
}
```

## Response Fields Explained

### Statistics Object
- **total_projects**: Total number of projects
- **completed_projects**: Number of projects with status "completed"
- **due_projects**: Number of overdue projects (past end_date and not completed)
- **cancelled_projects**: Number of cancelled projects

### Project Object
- **id**: Project ID
- **project_name**: Name of the project
- **client_name**: Client name
- **description**: Project description
- **status**: Project status (not_started, in_progress, completed, on_hold, cancelled)
- **progress**: Progress percentage (0-100) based on completed tasks
- **creating_date**: Date when project was created
- **start_date**: Project start date
- **end_date**: Project deadline/end date
- **deadline_status**: Human-readable deadline status (e.g., "20 days left to deliver")
- **total_amount**: Total project amount
- **estimated_cost**: Estimated cost
- **rooms**: Array of room names
- **total_tasks**: Total number of tasks in the project
- **completed_tasks**: Number of completed tasks in the project
- **created_by_name**: Full name of project creator
- **created_at**: Project creation timestamp
- **updated_at**: Last update timestamp

## Progress Calculation
```
Progress % = (Completed Tasks / Total Tasks) × 100
```

Example:
- Total Tasks: 5
- Completed Tasks: 1
- Progress: (1 / 5) × 100 = 20%

If a project has 0 tasks, progress is 0%.

## Usage Examples

### 1. Get All Projects
```bash
GET /api/project-manager/all-projects/
Authorization: Bearer <your_token>
```

### 2. Filter by Status (In Progress)
```bash
GET /api/project-manager/all-projects/?status=in_progress
Authorization: Bearer <your_token>
```

### 3. Filter by Completed Projects
```bash
GET /api/project-manager/all-projects/?status=completed
Authorization: Bearer <your_token>
```

### 4. Search for Projects
```bash
GET /api/project-manager/all-projects/?search=renovation
Authorization: Bearer <your_token>
```

### 5. Combine Filters
```bash
GET /api/project-manager/all-projects/?status=in_progress&search=home
Authorization: Bearer <your_token>
```

## UI Integration (Matching the Image)

### Top Statistics Cards
Use the `statistics` object to display overview:
```javascript
// Total Projects Card
statistics.total_projects // 5

// Completed Projects Card
statistics.completed_projects // 2

// Due Projects Card (show in red/warning)
statistics.due_projects // 2

// Cancelled Card
statistics.cancelled_projects // 1
```

### Project Cards Layout
For each project in the `projects` array:

```javascript
// Project Header
project.project_name // "Home Renovation"
project.description // "Design the layout..."

// Progress Bar
project.progress // 35 (use for progress bar percentage)

// Left Side - Creation Date
project.creating_date // "20-04-2025"

// Right Side - Deadline
project.end_date // "23-05-2025"
project.deadline_status // "20 days left to deliver"

// Bottom Left - Tasks
project.total_tasks // "5 Tasks"

// Bottom Right - Completed
project.completed_tasks // "1 Completed" ✓

// View Details Button
// Link to: /projects/${project.id}/
```

### Progress Bar Styling
```javascript
// Progress bar color based on percentage
if (project.progress < 30) {
  color = 'red' // Behind schedule
} else if (project.progress < 70) {
  color = 'yellow' // On track
} else {
  color = 'green' // Ahead
}
```

### Deadline Status Colors
```javascript
// Color based on days left
const daysLeft = calculateDaysLeft(project.end_date)
if (daysLeft < 0) {
  color = 'red' // Overdue
} else if (daysLeft < 7) {
  color = 'orange' // Due soon
} else {
  color = 'green' // On track
}
```

## Error Responses

### 401 Unauthorized
```json
{
    "success": false,
    "message": "Authentication credentials were not provided.",
    "data": null
}
```

### 403 Forbidden (Not Project Manager Role)
```json
{
    "success": false,
    "message": "You do not have permission to perform this action.",
    "data": null
}
```

### 500 Internal Server Error
```json
{
    "success": false,
    "message": "Error retrieving projects: <error details>",
    "data": null
}
```

## Differences from Employee API

| Feature | Employee API | Project Manager API |
|---------|-------------|---------------------|
| Endpoint | `/api/employee/assigned-projects/` | `/api/project-manager/all-projects/` |
| Projects Shown | Only projects with assigned tasks | All projects |
| Permission | Employee role | Project Manager/Admin role |
| Additional Field | `assigned_tasks_count` | N/A (shows all tasks) |

## Related Endpoints
- `GET /api/project-manager/projects/` - Basic project list (without progress)
- `GET /api/project-manager/projects/{id}/` - Single project details
- `GET /api/project-manager/projects/{id}/tasks/` - Tasks in a project

## Notes
- Projects are ordered by creation date (newest first)
- Progress is calculated based on ALL tasks in the project
- Deadline status is dynamic based on current date
- All date/time fields use ISO 8601 format
- Empty projects (0 tasks) show 0% progress

## Testing
Use the Swagger documentation at:
```
http://your-domain:8002/swagger/
```
Look for the **"Project Manager - Projects"** section.
