# Estimates List API with Status Filter - Complete Guide

## 📡 Endpoint

**Base URL:** `http://10.10.13.27:8002/api/project-manager/estimates/`

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
| `q` | String | No | Search query | Any text (searches multiple fields) |
| `status` | String | No | Filter by status | `pending`, `sent`, `approved`, `rejected` |

---

## 🎯 Basic Request Examples

### Get All Estimates
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/estimates/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Approved
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/estimates/?status=approved \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Pending
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/estimates/?status=pending \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Sent
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/estimates/?status=sent \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Status - Rejected
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/estimates/?status=rejected \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Search Examples

### Search by Serial Number
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?q=EST-2025-001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search by Client Name
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?q=ABC%20Corporation" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search by Project Name
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?q=Renovation" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search by Estimate Number
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?q=001" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔗 Combined Filter & Search

### Approved Estimates from ABC Corporation
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?status=approved&q=ABC" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Pending Estimates with "Office" in name
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?status=pending&q=Office" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Sent Estimates from 2025
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/estimates/?status=sent&q=2025" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Success Response (200 OK)

```json
{
  "success": true,
  "message": "Retrieved 3 estimates",
  "data": {
    "total_count": 3,
    "filters_applied": {
      "q": null,
      "status": "approved"
    },
    "status_summary": {
      "pending": 2,
      "sent": 1,
      "approved": 3,
      "rejected": 0
    },
    "results": [
      {
        "id": 10,
        "serial_number": "EST-2025-001",
        "estimate_number": "001",
        "client_name": "ABC Corporation",
        "project_name": "Eagle Eye Office Renovation",
        "status": "approved",
        "total_with_tax": "50000.00",
        "created_at": "2025-11-15T10:30:00Z",
        "updated_at": "2025-11-20T14:00:00Z"
      },
      {
        "id": 11,
        "serial_number": "EST-2025-002",
        "estimate_number": "002",
        "client_name": "XYZ Ltd",
        "project_name": "Home Renovation",
        "status": "approved",
        "total_with_tax": "35000.00",
        "created_at": "2025-11-16T09:15:00Z",
        "updated_at": "2025-11-19T11:00:00Z"
      },
      {
        "id": 12,
        "serial_number": "EST-2025-003",
        "estimate_number": "003",
        "client_name": "DEF Industries",
        "project_name": "Factory Upgrade",
        "status": "approved",
        "total_with_tax": "120000.00",
        "created_at": "2025-11-17T13:45:00Z",
        "updated_at": "2025-11-18T16:30:00Z"
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
    "status_summary": object,  // Summary of all estimates by status
    "results": array           // Array of estimate objects
  }
}
```

### Status Summary
```json
{
  "status_summary": {
    "pending": 2,      // Total pending estimates (all records)
    "sent": 1,         // Total sent estimates (all records)
    "approved": 3,     // Total approved estimates (all records)
    "rejected": 0      // Total rejected estimates (all records)
  }
}
```

### Each Estimate Record
```json
{
  "id": 10,
  "serial_number": "EST-2025-001",
  "estimate_number": "001",
  "client_name": "ABC Corporation",
  "project_name": "Eagle Eye Office Renovation",
  "status": "approved",
  "total_with_tax": "50000.00",
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-20T14:00:00Z"
}
```

---

## 📋 Status Values Explained

| Status | Description | Use Case |
|--------|-------------|----------|
| `pending` | Estimate is created but not yet sent to client | Initial draft status |
| `sent` | Estimate has been sent to client awaiting response | Waiting for client decision |
| `approved` | Client has approved the estimate | Ready to create project |
| `rejected` | Client rejected the estimate | Not proceeding with this estimate |

---

## 🧪 Test Scenarios

### Scenario 1: Get All Approved Estimates
```bash
curl http://10.10.13.27:8002/api/project-manager/estimates/?status=approved \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns all estimates with `status: "approved"`

---

### Scenario 2: Get All Pending Estimates
```bash
curl http://10.10.13.27:8002/api/project-manager/estimates/?status=pending \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns all estimates with `status: "pending"`

---

### Scenario 3: Search for Specific Client
```bash
curl "http://10.10.13.27:8002/api/project-manager/estimates/?q=ABC%20Corporation" \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns all estimates with "ABC Corporation" in any searchable field

---

### Scenario 4: Approved + Search
```bash
curl "http://10.10.13.27:8002/api/project-manager/estimates/?status=approved&q=Renovation" \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns approved estimates containing "Renovation"

---

### Scenario 5: Get Status Summary Only
```bash
curl http://10.10.13.27:8002/api/project-manager/estimates/ \
  -H "Authorization: Bearer TOKEN"
```

**Expected:** Returns all estimates + status_summary showing counts of each status

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
**Example:** `?status=invalid` → Returns all estimates (status filter not applied)

---

## 💻 Frontend Integration Examples

### JavaScript / Fetch API
```javascript
async function getEstimates(statusFilter = null, searchQuery = null) {
  let url = 'http://10.10.13.27:8002/api/project-manager/estimates/';
  
  const params = new URLSearchParams();
  if (statusFilter) params.append('status', statusFilter);
  if (searchQuery) params.append('q', searchQuery);
  
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
    console.log('Estimates:', result.data.results);
    console.log('Status Summary:', result.data.status_summary);
    return result.data;
  } else {
    console.error('Error:', result.message);
  }
}

// Usage examples:
getEstimates('approved');                          // Get approved estimates
getEstimates('pending');                           // Get pending estimates
getEstimates('approved', 'ABC');                   // Approved + search
getEstimates();                                    // Get all estimates
```

---

### Python / Requests Library
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

# Get all approved estimates
params = {'status': 'approved'}
response = requests.get(
    'http://10.10.13.27:8002/api/project-manager/estimates/',
    params=params,
    headers=headers,
)
result = response.json()
print(result['data']['results'])

# Get approved estimates with search
params = {'status': 'approved', 'q': 'ABC'}
response = requests.get(
    'http://10.10.13.27:8002/api/project-manager/estimates/',
    params=params,
    headers=headers,
)
result = response.json()
print(f"Found {result['data']['total_count']} estimates")
```

---

### Vue.js / Axios
```javascript
// Vue component
async getEstimates(status = null, search = null) {
  try {
    const params = {};
    if (status) params.status = status;
    if (search) params.q = search;
    
    const response = await this.$axios.get(
      '/api/project-manager/estimates/',
      { params }
    );
    
    if (response.data.success) {
      this.estimates = response.data.data.results;
      this.statusSummary = response.data.data.status_summary;
      this.filtersApplied = response.data.data.filters_applied;
    }
  } catch (error) {
    this.$notify.error(`Error: ${error.message}`);
  }
}

// Usage:
this.getEstimates('approved');              // Approved only
this.getEstimates('pending');               // Pending only
this.getEstimates('approved', 'ABC');       // Approved + search
this.getEstimates();                        // All estimates
```

---

## 📊 Searching Fields

The `q` parameter searches in these fields (case-insensitive):
- `serial_number` - e.g., "EST-2025-001"
- `estimate_number` - e.g., "001"
- `client_name` - e.g., "ABC Corporation"
- `project_name` - e.g., "Eagle Eye Office Renovation"

---

## 🔄 Request/Response Flow

```
┌──────────────────────────────┐
│  Client Application          │
│  (Web / Mobile)              │
└────────────┬─────────────────┘
             │
             │ GET Request
             │ ?status=approved&q=ABC
             │
             ▼
┌──────────────────────────────┐
│  API Endpoint                │
│  /api/project-manager/       │
│  estimates/                  │
└────────────┬─────────────────┘
             │
             │ Process Query
             │ ├─ Authenticate
             │ ├─ Parse filters
             │ ├─ Query database
             │ ├─ Count by status
             │ ├─ Serialize results
             │ └─ Format response
             │
             ▼
        ┌────────────────┐
        │  Database      │
        │  Estimate      │
        │  Table         │
        └────────────────┘
             │
             │ Response
             │ {
             │   total_count: 2,
             │   status_summary: {...},
             │   results: [...]
             │ }
             │
             ▼
┌──────────────────────────────┐
│  Client Application          │
│  Display Results             │
│  Show Status Summary         │
└──────────────────────────────┘
```

---

## 🎯 Quick Reference

### URL Patterns
```
/api/project-manager/estimates/
  ├─ ?status=pending
  ├─ ?status=sent
  ├─ ?status=approved
  ├─ ?status=rejected
  ├─ ?q=search_term
  └─ ?status=approved&q=search_term
```

### Common Use Cases
```
1. View all estimates
   GET /api/project-manager/estimates/

2. View only approved (ready to create projects)
   GET /api/project-manager/estimates/?status=approved

3. View pending (need client action)
   GET /api/project-manager/estimates/?status=pending

4. Search for specific client
   GET /api/project-manager/estimates/?q=client_name

5. Find approved estimates for specific client
   GET /api/project-manager/estimates/?status=approved&q=client_name
```

---

## 📈 Data Insights from Response

```json
"status_summary": {
  "pending": 2,    // These need client approval
  "sent": 1,       // These are waiting for response
  "approved": 3,   // These are ready for project creation
  "rejected": 0    // These won't proceed
}
```

Use `status_summary` to show:
- Total estimates waiting for approval
- Total estimates ready to convert to projects
- Total rejected estimates (for analysis)

---

## ✨ Key Features

✅ **Status Filtering** - See estimates by status: pending, sent, approved, rejected  
✅ **Full Text Search** - Search across serial_number, estimate_number, client_name, project_name  
✅ **Combined Filters** - Use status AND search together  
✅ **Status Summary** - Get count of all statuses in one response  
✅ **Clean Response** - Shows filters applied and total count  
✅ **Sorted Results** - Newest estimates first (by created_at descending)

---

Ready to use! 🚀
