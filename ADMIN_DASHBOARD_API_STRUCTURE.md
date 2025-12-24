# Admin Dashboard Projects API - Structure Overview

## API Endpoints Map

```
/api/admin/
├── projects/
│   ├── GET - List all projects (with search/filter/sort)
│   │   ├── Query: search={text}
│   │   ├── Query: status={status}
│   │   ├── Query: sort_by={field}
│   │   └── Query: sort_order={order}
│   │
│   └── {project_id}/
│       └── GET - Get project details
│           ├── Project information
│           ├── Estimate details
│           ├── All tasks
│           └── Task statistics
│
├── materials/            (existing)
├── estimate-defaults/    (existing)
├── components/           (existing)
├── estimates/            (existing)
├── comprehensive-list/   (existing)
└── dashboard-overview/   (existing)
```

---

## Data Flow Diagram

```
Admin User
    ↓
[Authentication Check]
    ↓
[Company Verification]
    ↓
Get Projects from Database
    │
    ├─→ Filter by Company
    ├─→ Apply Search Query
    ├─→ Apply Status Filter
    ├─→ Apply Sorting
    │
    └─→ Return Results
        ├── Project List (with metadata)
        └── Project Details (with tasks)
```

---

## Response Structure for Projects List

```
{
  "success": boolean,
  "message": string,
  "data": {
    "total_count": integer,
    "filters_applied": {
      "search": string | null,
      "status": string | null,
      "sort_by": string,
      "sort_order": string
    },
    "results": [
      {
        "id": integer,
        "project_name": string,
        "client_name": string,
        "status": string,  // not_started | in_progress | completed | on_hold | cancelled
        "creating_date": date,
        "start_date": date,
        "end_date": date,
        "total_amount": decimal,
        "estimated_cost": decimal,
        "rooms": array,
        "tasks_count": integer,
        "assigned_employees_count": integer,
        "created_by_name": string,
        "assigned_to_name": string | null,
        "created_at": datetime
      },
      ...
    ]
  }
}
```

---

## Response Structure for Project Details

```
{
  "success": boolean,
  "message": string,
  "data": {
    "project": {
      "id": integer,
      "project_name": string,
      "client_name": string,
      "description": string,
      "status": string,
      "creating_date": date,
      "start_date": date,
      "end_date": date,
      "total_amount": decimal,
      "estimated_cost": decimal,
      "rooms": array,
      "created_by": integer,
      "assigned_to": integer | null,
      "created_at": datetime,
      "updated_at": datetime
    },
    "estimate": {
      "id": integer,
      "serial_number": string,
      "estimate_number": string,
      "client_name": string,
      "project_name": string,
      "status": string,
      "total_amount": decimal,
      "items": [
        {
          "id": integer,
          "description": string,
          "quantity": decimal,
          "unit_price": decimal,
          "total": decimal
        },
        ...
      ],
      "created_at": datetime
    },
    "tasks": [
      {
        "id": integer,
        "task_name": string,
        "description": string,
        "room": string,
        "status": string,  // not_started | in_progress | completed | blocked
        "priority": string,  // low | medium | high
        "phase": string,  // planning | design | procurement | construction | handover
        "start_date": date,
        "end_date": date,
        "assigned_employee_name": string | null,
        "assigned_employee": {
          "id": integer,
          "email": string,
          "first_name": string,
          "last_name": string,
          "role": string
        },
        "created_at": datetime
      },
      ...
    ],
    "task_summary": {
      "total_tasks": integer,
      "by_status": {
        "not_started": integer,
        "in_progress": integer,
        "completed": integer,
        "blocked": integer
      },
      "by_priority": {
        "low": integer,
        "medium": integer,
        "high": integer
      }
    }
  }
}
```

---

## Search and Filter Options

### Status Filters
- `not_started` - Project hasn't started yet
- `in_progress` - Project is currently active
- `completed` - Project is finished
- `on_hold` - Project is paused
- `cancelled` - Project is cancelled

### Sort Fields
- `project_name` - Alphabetical by project name
- `client_name` - Alphabetical by client name
- `creating_date` - By project creation date
- `start_date` - By project start date
- `status` - By project status

### Sort Order
- `asc` - Ascending (A-Z, oldest-newest)
- `desc` - Descending (Z-A, newest-oldest)

---

## Example Usage Scenarios

### Scenario 1: View All In-Progress Projects
```bash
GET /api/admin/projects/?status=in_progress
```
**Response**: List of all active projects

### Scenario 2: Search for a Specific Client's Projects
```bash
GET /api/admin/projects/?search=John%20Smith
```
**Response**: All projects for John Smith

### Scenario 3: View Recently Completed Projects
```bash
GET /api/admin/projects/?status=completed&sort_by=creating_date&sort_order=desc
```
**Response**: Completed projects sorted by date (newest first)

### Scenario 4: Get Full Details of a Project
```bash
GET /api/admin/projects/1/
```
**Response**: Complete project info including tasks and estimate

### Scenario 5: View Project Tasks and Assignment
```bash
GET /api/admin/projects/1/
```
**Response**: Includes task_summary showing:
- How many tasks are in each status
- How many tasks are in each priority level
- All task assignments

---

## Database Query Optimization

The API uses Django's `select_related()` and `prefetch_related()` for efficient database queries:

```python
# Projects are fetched with related data in one query
Project.objects.filter(...).select_related(
    'estimate',
    'created_by',
    'assigned_to'
).prefetch_related('tasks')
```

This ensures minimal database hits for optimal performance.

---

## Field Descriptions

### Project Fields
| Field | Type | Description |
|-------|------|-------------|
| `project_name` | String | Name of the project |
| `client_name` | String | Client or customer name |
| `status` | String | Current project status |
| `total_amount` | Decimal | Total project budget/value |
| `estimated_cost` | Decimal | Estimated project cost |
| `rooms` | Array | Rooms involved in project |
| `tasks_count` | Integer | Total number of tasks |

### Task Fields
| Field | Type | Description |
|-------|------|-------------|
| `task_name` | String | Name of the task |
| `status` | String | Task completion status |
| `priority` | String | Task importance level |
| `phase` | String | Project phase this task belongs to |
| `assigned_employee_name` | String | Employee assigned to task |

---

## Access Control Flow

```
Request Received
    ↓
[Check Authentication]
    └─ NO → Return 401 Unauthorized
    └─ YES ↓
[Check User Role]
    └─ NOT Admin → Return 403 Forbidden
    └─ IS Admin ↓
[Check Company]
    └─ Different Company → Return 404 Not Found
    └─ Same Company ↓
[Return Data]
```

---

## Error Response Examples

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
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

### 500 Server Error
```json
{
  "success": false,
  "message": "Error retrieving projects: [error details]",
  "data": null
}
```

---

## Frontend Implementation Checklist

- [ ] Create Projects List Page
  - [ ] Display projects in table format
  - [ ] Implement search input
  - [ ] Implement status filter dropdown
  - [ ] Implement sort options
  - [ ] Handle pagination (if needed)
  - [ ] Show total count

- [ ] Create Project Details Page
  - [ ] Display project information
  - [ ] Show estimate breakdown
  - [ ] Display tasks list
  - [ ] Show task status chart
  - [ ] Show task priority chart
  - [ ] Show employee assignments

- [ ] Implement Status Indicators
  - [ ] Color code by status
  - [ ] Show status badges
  - [ ] Show priority icons

- [ ] Add Loading States
  - [ ] Loading spinners
  - [ ] Error messages
  - [ ] Empty state handling

---

## Performance Notes

- All database queries are optimized with select_related/prefetch_related
- Results are filtered at the database level, not in Python
- Company isolation is enforced at query level
- No N+1 query problems

---

## Security Notes

✅ Company-level isolation
✅ Role-based access control
✅ Authentication required
✅ Input validation on all parameters
✅ SQL injection protection (Django ORM)
✅ CSRF protection on state-changing operations
