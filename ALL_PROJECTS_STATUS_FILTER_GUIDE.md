# All Projects List API with Status Filter - Complete Guide

## 📡 Endpoint

**Base URL:** `http://10.10.13.27:8002/api/project-manager/all-projects/`

**Method:** `GET`

---

## 🔐 Authentication

**Header Required:**
```
Authorization: Bearer YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Accessible to:** Project Manager, Admin only

---

## 📋 Query Parameters

| Parameter | Type | Required | Description | Values |
|-----------|------|----------|-------------|--------|
| `status` | String | No | Filter by project status | `not_started`, `in_progress`, `completed`, `on_hold`, `cancelled` |
| `search` | String | No | Search by project or client name | Any text |

---

## 🎯 Basic Request Examples

### Get All Projects
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/all-projects/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - In Progress
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/all-projects/?status=in_progress \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Completed
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/all-projects/?status=completed \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Not Started
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/all-projects/?status=not_started \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - On Hold
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/all-projects/?status=on_hold \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Cancelled
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/all-projects/?status=cancelled \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Search Examples

### Search by Project Name
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?search=Renovation" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search by Client Name
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?search=ABC%20Corporation" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search for "Office"
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?search=Office" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔗 Combined Filter & Search

### Active Projects from ABC Corporation
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?status=in_progress&search=ABC" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Completed Projects with "Renovation"
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?status=completed&search=Renovation" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Pending Projects for specific client
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?status=not_started&search=Office" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Success Response (200 OK)

```json
{
  "success": true,
  "message": "Retrieved 8 projects",
  "data": {
    "total_count": 8,
    "filters_applied": {
      "status": "in_progress",
      "search": null
    },
    "status_summary": {
      "not_started": 3,
      "in_progress": 8,
      "completed": 5,
      "on_hold": 2,
      "cancelled": 1
    },
    "statistics": {
      "total_projects": 8,
      "completed_projects": 0,
      "in_progress_projects": 8,
      "due_projects": 2,
      "cancelled_projects": 0
    },
    "projects": [
      {
        "id": 1,
        "project_name": "Eagle Eye Office Renovation",
        "client_name": "ABC Corporation",
        "status": "in_progress",
        "start_date": "2025-11-16",
        "end_date": "2025-12-15",
        "total_amount": "50000.00",
        "estimated_cost": "45000.00",
        "tasks_count": 12,
        "completed_tasks": 4,
        "in_progress_tasks": 6,
        "not_started_tasks": 2,
        "created_at": "2025-11-15T10:30:00Z",
        "updated_at": "2025-11-20T14:00:00Z"
      },
      {
        "id": 2,
        "project_name": "Home Renovation Phase 2",
        "client_name": "XYZ Ltd",
        "status": "in_progress",
        "start_date": "2025-11-16",
        "end_date": "2025-12-10",
        "total_amount": "35000.00",
        "estimated_cost": "32000.00",
        "tasks_count": 8,
        "completed_tasks": 2,
        "in_progress_tasks": 4,
        "not_started_tasks": 2,
        "created_at": "2025-11-16T09:15:00Z",
        "updated_at": "2025-11-19T11:00:00Z"
      }
    ]
  }
}
```

---

## 📊 Response Data Structure

### Top Level
```json
{
  "success": boolean,          // API call status
  "message": string,           // Human-readable message
  "data": {
    "total_count": integer,    // Number of results returned
    "filters_applied": object, // Which filters were used
    "status_summary": object,  // Summary of all projects by status
    "statistics": object,      // Statistics for filtered results
    "projects": array          // Array of project objects
  }
}
```

### Status Summary (All Projects)
```json
{
  "status_summary": {
    "not_started": 3,     // Total not_started projects
    "in_progress": 8,     // Total in_progress projects
    "completed": 5,       // Total completed projects
    "on_hold": 2,         // Total on_hold projects
    "cancelled": 1        // Total cancelled projects
  }
}
```

### Statistics (Filtered Results)
```json
{
  "statistics": {
    "total_projects": 8,           // Number of results
    "completed_projects": 0,       // Completed in results
    "in_progress_projects": 8,     // In progress in results
    "due_projects": 2,             // Overdue in results
    "cancelled_projects": 0        // Cancelled in results
  }
}
```

### Each Project Record
```json
{
  "id": 1,
  "project_name": "Eagle Eye Office Renovation",
  "client_name": "ABC Corporation",
  "status": "in_progress",
  "start_date": "2025-11-16",
  "end_date": "2025-12-15",
  "total_amount": "50000.00",
  "estimated_cost": "45000.00",
  "tasks_count": 12,
  "completed_tasks": 4,
  "in_progress_tasks": 6,
  "not_started_tasks": 2,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-20T14:00:00Z"
}
```

---

## 📋 Status Values Explained

| Status | Description | Color | Use Case |
|--------|-------------|-------|----------|
| `not_started` | Project created but not started | Gray | Not yet begun |
| `in_progress` | Project is actively being worked on | Blue | Currently active |
| `completed` | Project is finished | Green | ✅ Done |
| `on_hold` | Project is paused/suspended | Orange | Temporarily stopped |
| `cancelled` | Project is cancelled | Red | ❌ Won't proceed |

---

## 🧪 Test Scenarios

### Scenario 1: Get All In-Progress Projects
```bash
curl http://10.10.13.27:8002/api/project-manager/all-projects/?status=in_progress \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns only projects with `status: "in_progress"`

---

### Scenario 2: Get All Completed Projects
```bash
curl http://10.10.13.27:8002/api/project-manager/all-projects/?status=completed \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns only completed projects

---

### Scenario 3: Search for ABC Projects
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?search=ABC" \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns projects with "ABC" in name or client name

---

### Scenario 4: Active ABC Corporation Projects
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?status=in_progress&search=ABC" \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns active projects for ABC Corporation

---

### Scenario 5: Projects on Hold
```bash
curl "http://10.10.13.27:8002/api/project-manager/all-projects/?status=on_hold" \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns paused/on_hold projects

---

### Scenario 6: Get Status Summary
```bash
curl http://10.10.13.27:8002/api/project-manager/all-projects/ \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Shows `status_summary` with all project counts

---

## ❌ Error Responses

### Error 1: Not Authenticated (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Status:** `401 UNAUTHORIZED`  
**Fix:** Add valid `Authorization` header with bearer token

---

### Error 2: Not Project Manager (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Status:** `403 FORBIDDEN`  
**Reason:** Only Project Manager and Admin roles can access this endpoint

---

### Error 3: Invalid Status Value
**What happens:** Status parameter is silently ignored if invalid  
**Example:** `?status=invalid` → Returns all projects (status filter not applied)

---

## 💻 Frontend Integration Examples

### JavaScript / Fetch API
```javascript
async function getProjects(statusFilter = null, searchQuery = null) {
  let url = 'http://10.10.13.27:8002/api/project-manager/all-projects/';
  
  const params = new URLSearchParams();
  if (statusFilter) params.append('status', statusFilter);
  if (searchQuery) params.append('search', searchQuery);
  
  if (params.toString()) {
    url += '?' + params.toString();
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  const result = await response.json();
  if (result.success) {
    console.log('Projects:', result.data.projects);
    console.log('Status Summary:', result.data.status_summary);
    console.log('Statistics:', result.data.statistics);
    return result.data;
  }
}

// Usage:
getProjects('in_progress');                    // Get active projects
getProjects('completed');                      // Get completed
getProjects('in_progress', 'ABC');             // Active + search
getProjects();                                 // Get all projects
```

---

### Python / Requests Library
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
}

# Get all in-progress projects
params = {'status': 'in_progress'}
response = requests.get(
    'http://10.10.13.27:8002/api/project-manager/all-projects/',
    params=params,
    headers=headers,
)
result = response.json()
print(result['data']['projects'])
print(f"Status summary: {result['data']['status_summary']}")

# Get active projects from ABC
params = {'status': 'in_progress', 'search': 'ABC'}
response = requests.get(
    'http://10.10.13.27:8002/api/project-manager/all-projects/',
    params=params,
    headers=headers,
)
result = response.json()
print(f"Found {result['data']['total_count']} projects")
```

---

### Vue.js / Axios
```javascript
// Vue component
async getProjects(status = null, search = null) {
  try {
    const params = {};
    if (status) params.status = status;
    if (search) params.search = search;
    
    const response = await this.$axios.get(
      '/api/project-manager/all-projects/',
      { params }
    );
    
    if (response.data.success) {
      this.projects = response.data.data.projects;
      this.statusSummary = response.data.data.status_summary;
      this.statistics = response.data.data.statistics;
      this.filtersApplied = response.data.data.filters_applied;
    }
  } catch (error) {
    this.$notify.error(`Error: ${error.message}`);
  }
}

// Usage in component:
// Get all active projects
this.getProjects('in_progress');

// Get projects for specific client
this.getProjects(null, 'ABC');

// Get active projects for ABC
this.getProjects('in_progress', 'ABC');
```

---

## 📊 Searching Fields

The `search` parameter searches in these fields (case-insensitive):
- `project_name` - e.g., "Eagle Eye Office Renovation"
- `client_name` - e.g., "ABC Corporation"

---

## 🔄 Request/Response Flow

```
┌──────────────────────────────┐
│  Client Application          │
│  (Web / Mobile)              │
└────────────┬─────────────────┘
             │
             │ GET Request
             │ ?status=in_progress&search=ABC
             │
             ▼
┌──────────────────────────────┐
│  API Endpoint                │
│  /api/project-manager/       │
│  all-projects/               │
└────────────┬─────────────────┘
             │
             │ Process Query
             │ ├─ Authenticate
             │ ├─ Parse filters
             │ ├─ Query database
             │ ├─ Calculate summary
             │ ├─ Calculate stats
             │ ├─ Serialize results
             │ └─ Format response
             │
             ▼
        ┌────────────────┐
        │  Database      │
        │  Project       │
        │  Table         │
        └────────────────┘
             │
             │ Response
             │ {
             │   total_count: 5,
             │   status_summary: {...},
             │   statistics: {...},
             │   projects: [...]
             │ }
             │
             ▼
┌──────────────────────────────┐
│  Client Application          │
│  Display Results             │
│  Show Status Summary         │
│  Show Statistics             │
└──────────────────────────────┘
```

---

## 🎯 Quick Reference

### URL Patterns
```
/api/project-manager/all-projects/
  ├─ ?status=not_started
  ├─ ?status=in_progress
  ├─ ?status=completed
  ├─ ?status=on_hold
  ├─ ?status=cancelled
  ├─ ?search=search_term
  └─ ?status=in_progress&search=search_term
```

### Common Use Cases
```
1. View all projects
   GET /api/project-manager/all-projects/

2. View only active projects
   GET /api/project-manager/all-projects/?status=in_progress

3. View completed projects
   GET /api/project-manager/all-projects/?status=completed

4. Search for specific client
   GET /api/project-manager/all-projects/?search=client_name

5. Find active projects for specific client
   GET /api/project-manager/all-projects/?status=in_progress&search=client_name

6. View overdue/on hold projects
   GET /api/project-manager/all-projects/?status=on_hold
```

---

## 📈 Data Insights from Response

```json
"status_summary": {
  "not_started": 3,
  "in_progress": 8,
  "completed": 5,
  "on_hold": 2,
  "cancelled": 1
}
```

Use `status_summary` to create:
- Status distribution pie charts
- Progress dashboards
- Summary cards showing project counts
- Filter buttons/tabs

---

## ✨ Key Features

✅ **Status Filtering** - See projects by status (5 types)  
✅ **Full Text Search** - Search project and client names  
✅ **Combined Filters** - Use status AND search together  
✅ **Status Summary** - Get count of all statuses in one response  
✅ **Project Statistics** - Task counts and progress info  
✅ **Clean Response** - Shows filters applied and total count  
✅ **Sorted Results** - Newest projects first (by creating_date descending)  
✅ **Task Progress** - See completed/in-progress/not-started task counts per project

---

## 📌 Key Differences from Other APIs

| Feature | All Projects | Single Project |
|---------|--------------|---|
| **Endpoint** | `/all-projects/` | `/projects/{id}/` |
| **Status Filter** | ✅ Yes | N/A |
| **Search** | ✅ Yes | N/A |
| **Status Summary** | ✅ Yes (all projects) | N/A |
| **Task Details** | ✅ Summary counts | ✅ Full details |
| **Pagination** | ❌ No (returns all) | N/A |

---

Ready to use! 🚀
