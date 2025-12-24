# Project Manager - Task Assignment API Guide

## Overview
This guide shows the proper way to assign tasks to employees in a project using the Project Manager API.

---

## Task Assignment Workflow

### Step 1: Create a Project from an Approved Estimate

**Endpoint:** `POST /api/project-manager/projects/`

**Request Payload:**
```json
{
  "estimate": 1,
  "project_name": "Office Renovation",
  "client_name": "Acme Corporation",
  "description": "Complete office renovation project",
  "start_date": "2025-12-01",
  "end_date": "2026-03-31",
  "assigned_to": 5
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "project_name": "Office Renovation",
  "client_name": "Acme Corporation",
  "status": "not_started",
  "creating_date": "2025-11-13",
  "start_date": "2025-12-01",
  "end_date": "2026-03-31",
  "total_amount": "12500.50",
  "estimated_cost": "12000.00",
  "rooms": ["Kitchen", "Living Room", "Hallway"],
  "tasks_count": 0,
  "assigned_employees_count": 0,
  "created_by_name": "John Manager",
  "assigned_to_name": "Jane Supervisor",
  "created_at": "2025-11-13T10:30:00Z"
}
```

---

### Step 2: Add Tasks to the Project

**Endpoint:** `POST /api/project-manager/projects/{project_id}/tasks/`

#### Example 1: Assign Task to an Employee

**Request Payload:**
```json
{
  "task_name": "Kitchen Design",
  "description": "Design and plan kitchen layout and materials",
  "room": "Kitchen",
  "priority": "high",
  "status": "not_started",
  "start_date": "2025-12-01",
  "due_date": "2025-12-15",
  "assigned_employee": 7
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "project": 1,
  "task_name": "Kitchen Design",
  "description": "Design and plan kitchen layout and materials",
  "room": "Kitchen",
  "status": "not_started",
  "priority": "high",
  "start_date": "2025-12-01",
  "due_date": "2025-12-15",
  "assigned_employee": 7,
  "assigned_employee_name": "Smith Due",
  "created_by": 5,
  "created_by_name": "John Manager",
  "created_at": "2025-11-13T10:35:00Z",
  "updated_at": "2025-11-13T10:35:00Z"
}
```

#### Example 2: Create Unassigned Task (Assign Later)

**Request Payload:**
```json
{
  "task_name": "Kitchen Procurement",
  "description": "Order kitchen materials and equipment",
  "room": "Kitchen",
  "priority": "medium",
  "due_date": "2025-12-20"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "project": 1,
  "task_name": "Kitchen Procurement",
  "description": "Order kitchen materials and equipment",
  "room": "Kitchen",
  "status": "not_started",
  "priority": "medium",
  "start_date": null,
  "due_date": "2025-12-20",
  "assigned_employee": null,
  "assigned_employee_name": null,
  "created_by": 5,
  "created_by_name": "John Manager",
  "created_at": "2025-11-13T10:40:00Z",
  "updated_at": "2025-11-13T10:40:00Z"
}
```

#### Example 3: Multiple Tasks in Project

**Creating multiple tasks for different rooms:**

**Task 1 - Kitchen:**
```json
{
  "task_name": "Kitchen Design",
  "room": "Kitchen",
  "priority": "high",
  "due_date": "2025-12-15",
  "assigned_employee": 7
}
```

**Task 2 - Living Room:**
```json
{
  "task_name": "Living Room Painting",
  "room": "Living Room",
  "priority": "medium",
  "due_date": "2025-12-20",
  "assigned_employee": 8
}
```

**Task 3 - Hallway:**
```json
{
  "task_name": "Hallway Renovation",
  "room": "Hallway",
  "priority": "low",
  "due_date": "2026-01-10",
  "assigned_employee": 9
}
```

---

### Step 3: Retrieve Project with All Tasks

**Endpoint:** `GET /api/project-manager/projects/{project_id}/`

**Response:**
```json
{
  "id": 1,
  "project_name": "Office Renovation",
  "client_name": "Acme Corporation",
  "status": "in_progress",
  "creating_date": "2025-11-13",
  "start_date": "2025-12-01",
  "end_date": "2026-03-31",
  "total_amount": "12500.50",
  "rooms": ["Kitchen", "Living Room", "Hallway"],
  "tasks_count": 3,
  "assigned_employees_count": 3,
  "tasks": [
    {
      "id": 1,
      "task_name": "Kitchen Design",
      "room": "Kitchen",
      "status": "not_started",
      "priority": "high",
      "due_date": "2025-12-15",
      "assigned_employee": 7,
      "assigned_employee_name": "Smith Due"
    },
    {
      "id": 2,
      "task_name": "Living Room Painting",
      "room": "Living Room",
      "status": "not_started",
      "priority": "medium",
      "due_date": "2025-12-20",
      "assigned_employee": 8,
      "assigned_employee_name": "Abri Mathwe"
    },
    {
      "id": 3,
      "task_name": "Hallway Renovation",
      "room": "Hallway",
      "status": "not_started",
      "priority": "low",
      "due_date": "2026-01-10",
      "assigned_employee": 9,
      "assigned_employee_name": "Hilan Mack"
    }
  ]
}
```

---

## Task Assignment Payload Fields

### Required Fields:
- **task_name** (string): Name/title of the task
- **priority** (enum): Task priority level
  - `'low'` - Low priority
  - `'medium'` - Medium priority (default)
  - `'high'` - High priority
- **due_date** (date): Task completion deadline (format: YYYY-MM-DD)

### Optional Fields:
- **description** (string): Detailed description of the task
- **room** (string): Target room/location (e.g., "Kitchen", "Living Room")
- **status** (enum): Current task status
  - `'not_started'` - Not started yet (default)
  - `'in_progress'` - Currently being worked on
  - `'completed'` - Task is finished
  - `'blocked'` - Task is blocked/delayed
- **start_date** (date): When task should start (format: YYYY-MM-DD)
- **assigned_employee** (integer): User ID of employee to assign the task to

### Auto-Generated Fields (Read-Only):
- **id**: Task ID
- **project**: Project ID (auto-set to the parent project)
- **assigned_employee_name**: Full name of assigned employee
- **created_by**: User ID of who created the task
- **created_by_name**: Full name of who created the task
- **created_at**: Creation timestamp
- **updated_at**: Last update timestamp

---

## Priority Levels & Best Practices

### Priority Levels:

| Level | Usage | Examples |
|-------|-------|----------|
| **High** | Critical tasks, blocking dependencies | Design phase, foundational work |
| **Medium** | Standard tasks | Material ordering, regular work |
| **Low** | Non-critical, nice-to-have | Final touches, documentation |

### Task Status Workflow:

```
not_started → in_progress → completed
                ↓
              blocked (if issues arise)
```

---

## Assignment Best Practices

### 1. Assign During Creation (Recommended)
```json
{
  "task_name": "Kitchen Design",
  "assigned_employee": 7
}
```
**Pros:** Employee knows immediately, clear ownership
**Cons:** Need to know employee ID

### 2. Create Unassigned, Assign Later
```json
{
  "task_name": "Kitchen Design"
}
```
Then update with:
```
PATCH /api/project-manager/projects/{project_id}/tasks/{task_id}/
{
  "assigned_employee": 7
}
```
**Pros:** Flexible, can batch create tasks
**Cons:** Tasks sit unassigned initially

### 3. Reassign If Needed
```
PATCH /api/project-manager/projects/{project_id}/tasks/{task_id}/
{
  "assigned_employee": 8
}
```
**Pros:** Can handle changes easily
**Cons:** Original assignee loses context

---

## Common Scenarios

### Scenario 1: Large Project with Multiple Teams

```json
// Create 3 kitchen tasks for the kitchen team
POST /api/project-manager/projects/1/tasks/
{
  "task_name": "Kitchen Design",
  "room": "Kitchen",
  "priority": "high",
  "assigned_employee": 7,
  "due_date": "2025-12-15"
}

// Create 2 painting tasks for the painting team
POST /api/project-manager/projects/1/tasks/
{
  "task_name": "Living Room Painting",
  "room": "Living Room",
  "priority": "medium",
  "assigned_employee": 8,
  "due_date": "2025-12-20"
}
```

**Result:** 
- tasks_count: 2
- assigned_employees_count: 2 (two different employees)

---

### Scenario 2: Batch Task Creation

Create all tasks first, then assign:

```json
// Create unassigned tasks
POST /api/project-manager/projects/1/tasks/
{
  "task_name": "Demolition",
  "due_date": "2025-12-10"
}

POST /api/project-manager/projects/1/tasks/
{
  "task_name": "Framing",
  "due_date": "2025-12-25"
}

POST /api/project-manager/projects/1/tasks/
{
  "task_name": "Finishing",
  "due_date": "2026-01-15"
}

// Then assign as team capacity becomes clear
PATCH /api/project-manager/projects/1/tasks/1/
{ "assigned_employee": 7 }

PATCH /api/project-manager/projects/1/tasks/2/
{ "assigned_employee": 8 }

PATCH /api/project-manager/projects/1/tasks/3/
{ "assigned_employee": 9 }
```

---

## Metrics Explained

### tasks_count
**What it means:** Total number of tasks in the project
**Example:** If tasks_count = 6, there are 6 tasks total

### assigned_employees_count
**What it means:** Number of UNIQUE employees assigned to tasks
**Example:** If assigned_employees_count = 3, then 3 different employees are working on the project

**Important:** Multiple tasks can be assigned to the same employee!
- 6 tasks assigned to 2 employees → assigned_employees_count = 2
- 6 tasks assigned to 3 employees → assigned_employees_count = 3

---

## Error Handling

### Common Errors and Solutions

#### 1. Employee Not Found
```
Error: "assigned_employee": ["Invalid pk \"999\" - object does not exist."]
```
**Solution:** Use a valid employee ID from your system

#### 2. Project Not Found
```
Error: {"detail": "Project not found"}
```
**Solution:** Verify project ID exists: `GET /api/project-manager/projects/`

#### 3. Missing Required Field
```
Error: "task_name": ["This field is required."]
```
**Solution:** Include all required fields (task_name, priority, due_date)

#### 4. Invalid Priority
```
Error: "priority": ["\"urgent\" is not a valid choice. Expected one of: low, medium, high"]
```
**Solution:** Use only: 'low', 'medium', 'high'

---

## API Endpoints Summary

```
# Project Management
POST   /api/project-manager/projects/                          - Create project
GET    /api/project-manager/projects/                          - List projects
GET    /api/project-manager/projects/{id}/                     - Get project details
PATCH  /api/project-manager/projects/{id}/                     - Update project

# Task Management
POST   /api/project-manager/projects/{project_id}/tasks/       - Create task
GET    /api/project-manager/projects/{project_id}/tasks/       - List tasks
GET    /api/project-manager/projects/{project_id}/tasks/{id}/  - Get task details
PATCH  /api/project-manager/projects/{project_id}/tasks/{id}/  - Update task
DELETE /api/project-manager/projects/{project_id}/tasks/{id}/  - Delete task
```

---

## Full Example: From Estimate to Project with Tasks

```bash
# 1. Admin approves estimate (already done)
# Estimate ID: 1, Status: approved

# 2. Project Manager creates project
curl -X POST http://10.10.13.27:8002/api/project-manager/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "estimate": 1,
    "project_name": "Office Renovation",
    "client_name": "Acme Corporation",
    "start_date": "2025-12-01",
    "end_date": "2026-03-31",
    "assigned_to": 5
  }'
# Response: Project ID: 1

# 3. Project Manager adds tasks
curl -X POST http://10.10.13.27:8002/api/project-manager/projects/1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "task_name": "Kitchen Design",
    "room": "Kitchen",
    "priority": "high",
    "due_date": "2025-12-15",
    "assigned_employee": 7
  }'

# 4. View project with all tasks
curl http://10.10.13.27:8002/api/project-manager/projects/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Support

For issues or questions:
- Check the payload format matches examples
- Verify all required fields are present
- Ensure Employee IDs are valid
- Check estimate is approved before creating project
