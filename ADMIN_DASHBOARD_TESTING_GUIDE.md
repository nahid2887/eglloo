# Admin Dashboard Projects API - Testing Guide

## Testing Setup

### Prerequisites
- Admin user account with authentication token
- Projects in database linked to your company
- API running on `http://localhost:8000`

### Tools
- cURL (command line)
- Postman (GUI)
- Python requests library
- Frontend application

---

## Test Cases

### 1. Get All Projects (No Filters)

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK)**
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
    "results": [...]
  }
}
```

**Test Points**
- ✓ Returns 200 status code
- ✓ success field is true
- ✓ Results array contains projects
- ✓ total_count matches results length

---

### 2. Search by Project Name

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?search=My%20House" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK)**
```json
{
  "success": true,
  "message": "Projects retrieved successfully (Total: 1)",
  "data": {
    "total_count": 1,
    "filters_applied": {
      "search": "My House",
      "status": null,
      "sort_by": "creating_date",
      "sort_order": "desc"
    },
    "results": [
      {
        "project_name": "My House",
        "client_name": "John Smith",
        ...
      }
    ]
  }
}
```

**Test Points**
- ✓ Filter applied correctly
- ✓ Only matching projects returned
- ✓ total_count reduced to 1
- ✓ search field shows in filters_applied

---

### 3. Search by Client Name

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?search=John%20Smith" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**
- Results contain projects with client name "John Smith"
- Matches across all projects with that client

**Test Points**
- ✓ Search works for client names
- ✓ Case-insensitive matching
- ✓ Partial name matching works

---

### 4. Filter by Status

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?status=in_progress" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**
- All returned projects have status "in_progress"
- total_count shows only in_progress projects

**Test Points**
- ✓ Status filter applied
- ✓ Only matching status returned
- ✓ status field shows in filters_applied

---

### 5. Filter by Multiple Statuses (Test Each)

**Valid Status Values**
```bash
# Test each status
curl -X GET "http://localhost:8000/api/admin/projects/?status=not_started"
curl -X GET "http://localhost:8000/api/admin/projects/?status=in_progress"
curl -X GET "http://localhost:8000/api/admin/projects/?status=completed"
curl -X GET "http://localhost:8000/api/admin/projects/?status=on_hold"
curl -X GET "http://localhost:8000/api/admin/projects/?status=cancelled"
```

**Test Points**
- ✓ Each status returns correct projects
- ✓ Invalid status is ignored (returns all)
- ✓ Case-sensitive matching

---

### 6. Sort by Field (Ascending)

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?sort_by=project_name&sort_order=asc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**
- Projects sorted alphabetically by name (A-Z)

**Test Points**
- ✓ Results ordered A-Z
- ✓ sort_by field shows in response
- ✓ sort_order shows "asc"

---

### 7. Sort by Field (Descending)

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?sort_by=creating_date&sort_order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**
- Projects sorted by date (newest first)

**Test Points**
- ✓ Results ordered newest-oldest
- ✓ sort_order shows "desc"
- ✓ First project has most recent date

---

### 8. Complex Query (Multiple Filters)

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/?search=House&status=completed&sort_by=creating_date&sort_order=desc" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**
- Projects matching all criteria:
  - Name/client contains "House"
  - Status is "completed"
  - Sorted by date (newest first)

**Test Points**
- ✓ All filters applied together
- ✓ Results satisfy all conditions
- ✓ All filters show in filters_applied

---

### 9. Get Project Details

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/1/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (200 OK)**
```json
{
  "success": true,
  "message": "Project details retrieved successfully",
  "data": {
    "project": {...},
    "estimate": {...},
    "tasks": [...],
    "task_summary": {
      "total_tasks": 5,
      "by_status": {...},
      "by_priority": {...}
    }
  }
}
```

**Test Points**
- ✓ Returns status 200
- ✓ Project object is complete
- ✓ Estimate object is included
- ✓ Tasks array is populated
- ✓ task_summary is calculated

---

### 10. Get Project Details - Invalid ID

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/9999/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response (404 Not Found)**
```json
{
  "success": false,
  "message": "Project not found or access denied",
  "data": null
}
```

**Test Points**
- ✓ Returns 404 status
- ✓ success is false
- ✓ Appropriate error message

---

### 11. Test Without Authentication

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/"
```

**Expected Response (401 Unauthorized)**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Test Points**
- ✓ Returns 401 status
- ✓ Prevents access without token

---

### 12. Test with Invalid Token

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer INVALID_TOKEN"
```

**Expected Response (401 Unauthorized)**
- Token validation fails
- Access denied

**Test Points**
- ✓ Rejects invalid tokens
- ✓ Returns appropriate error

---

### 13. Test Company Isolation

**Setup**
- Create user with different company_name
- Login with that user
- Try to access projects

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer OTHER_COMPANY_TOKEN"
```

**Expected Response**
- Empty results or access denied
- Cannot see projects from other companies

**Test Points**
- ✓ Company isolation works
- ✓ Users can't cross-access companies
- ✓ Security enforced

---

### 14. Test with Non-Admin User

**Setup**
- Create user with role "Employee" or "Project Manager"
- Login with that user

**Request**
```bash
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer EMPLOYEE_TOKEN"
```

**Expected Response (403 Forbidden)**
```json
{
  "success": false,
  "message": "Access denied",
  "data": null
}
```

**Test Points**
- ✓ Only admins can access
- ✓ Role verification works
- ✓ Non-admins get denied

---

## Postman Collection Example

```json
{
  "info": {
    "name": "Admin Dashboard Projects API",
    "description": "Test collection for admin projects endpoints"
  },
  "item": [
    {
      "name": "Get All Projects",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/admin/projects/",
        "header": {
          "Authorization": "Bearer {{token}}",
          "Content-Type": "application/json"
        }
      }
    },
    {
      "name": "Search Projects",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/admin/projects/?search=My%20House",
        "header": {
          "Authorization": "Bearer {{token}}",
          "Content-Type": "application/json"
        }
      }
    },
    {
      "name": "Filter by Status",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/admin/projects/?status=in_progress",
        "header": {
          "Authorization": "Bearer {{token}}",
          "Content-Type": "application/json"
        }
      }
    },
    {
      "name": "Get Project Details",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/admin/projects/1/",
        "header": {
          "Authorization": "Bearer {{token}}",
          "Content-Type": "application/json"
        }
      }
    }
  ]
}
```

---

## Python Testing Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "YOUR_ADMIN_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test 1: Get all projects
response = requests.get(f"{BASE_URL}/api/admin/projects/", headers=headers)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Test 2: Search projects
response = requests.get(
    f"{BASE_URL}/api/admin/projects/?search=House",
    headers=headers
)
print(f"Search Results: {response.json()['data']['total_count']}")

# Test 3: Filter by status
response = requests.get(
    f"{BASE_URL}/api/admin/projects/?status=completed",
    headers=headers
)
print(f"Completed Projects: {response.json()['data']['total_count']}")

# Test 4: Get project details
response = requests.get(
    f"{BASE_URL}/api/admin/projects/1/",
    headers=headers
)
data = response.json()['data']
print(f"Project: {data['project']['project_name']}")
print(f"Tasks: {data['task_summary']['total_tasks']}")
```

---

## Browser Testing

### JavaScript Fetch Example
```javascript
const token = "YOUR_ADMIN_TOKEN";

// Get all projects
fetch("http://localhost:8000/api/admin/projects/", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Search projects
fetch("http://localhost:8000/api/admin/projects/?search=House", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  }
})
.then(response => response.json())
.then(data => console.log(data));

// Get project details
fetch("http://localhost:8000/api/admin/projects/1/", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Performance Testing

### Test with Large Dataset
```bash
# Test with many projects
curl -X GET "http://localhost:8000/api/admin/projects/" \
  -H "Authorization: Bearer TOKEN" \
  -w "\nTime: %{time_total}s\n"
```

**Performance Targets**
- Small dataset (< 100 projects): < 200ms
- Medium dataset (100-1000): < 500ms
- Large dataset (> 1000): < 1s with pagination

---

## Edge Cases to Test

1. ✓ Empty search results
2. ✓ Invalid sort field
3. ✓ Invalid status value
4. ✓ Missing query parameters
5. ✓ Special characters in search
6. ✓ SQL injection attempts (should fail safely)
7. ✓ Very long search strings
8. ✓ Unicode characters in search
9. ✓ Projects with no tasks
10. ✓ Projects with no assigned manager

---

## Success Criteria

All tests should pass:
- ✓ Authentication required
- ✓ Admin role required
- ✓ Company isolation enforced
- ✓ All search parameters work
- ✓ All filter options work
- ✓ All sort options work
- ✓ Project details complete
- ✓ Error handling correct
- ✓ Response format consistent
- ✓ Performance acceptable
