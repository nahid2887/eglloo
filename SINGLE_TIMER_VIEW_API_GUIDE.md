# Single Timer View/Edit API - Complete Guide

## 📡 Endpoint

**Base URL:** `http://10.10.13.27:8002/api/employee/timer/edit/{timer_id}/`

**Methods:** `GET`, `PATCH`

---

## 🔐 Authentication

**Header Required:**
```
Authorization: Bearer YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Accessible to:** Employee role only (authenticated user)

---

## 📋 1. GET REQUEST - Retrieve Timer Details

### Endpoint
```
GET /api/employee/timer/edit/{timer_id}/
```

### Request Example
```bash
curl -X GET http://10.10.13.27:8002/api/employee/timer/edit/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Timer retrieved successfully for task 'Foundation Work'",
  "data": {
    "timer": {
      "id": 5,
      "task_id": 12,
      "employee_id": 3,
      "work_date": "2025-11-20",
      "start_time": "2025-11-20T09:00:00Z",
      "end_time": "2025-11-20T17:00:00Z",
      "duration_seconds": 28800,
      "is_active": false,
      "created_at": "2025-11-20T08:00:00Z",
      "updated_at": "2025-11-20T09:45:00Z"
    },
    "task_info": {
      "task_id": 12,
      "task_name": "Foundation Work",
      "project_id": 1,
      "project_name": "Eagle Eye Office Renovation"
    },
    "duration": {
      "seconds": 28800,
      "formatted": "08:00:00"
    },
    "total_time_today": {
      "seconds": 28800,
      "formatted": "08:00:00"
    },
    "work_date": "2025-11-20"
  }
}
```

---

## ✏️ 2. PATCH REQUEST - Update Timer

### Endpoint
```
PATCH /api/employee/timer/edit/{timer_id}/
```

### Request Body

**Minimal Payload (Update start time only):**
```json
{
  "start_time": "2025-11-20T09:30:00Z"
}
```

**Minimal Payload (Update end time only):**
```json
{
  "end_time": "2025-11-20T17:30:00Z"
}
```

**Full Payload (Update both):**
```json
{
  "start_time": "2025-11-20T09:30:00Z",
  "end_time": "2025-11-20T17:30:00Z"
}
```

### Field Descriptions

| Field | Type | Required | Description | Format |
|-------|------|----------|-------------|--------|
| `start_time` | String | No* | New start time | ISO 8601: `YYYY-MM-DDTHH:MM:SSZ` |
| `end_time` | String | No* | New end time | ISO 8601: `YYYY-MM-DDTHH:MM:SSZ` |

**\* At least one of `start_time` or `end_time` is required for PATCH**

---

## 💡 Common PATCH Examples

### Example 1: Fix Late Start Time
**Scenario:** Employee started at 9:30 AM (not 9:00 AM)

```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-11-20T09:30:00Z"
  }'
```

### Example 2: Fix Early End Time
**Scenario:** Employee finished at 5:30 PM (not 5:00 PM)

```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "end_time": "2025-11-20T17:30:00Z"
  }'
```

### Example 3: Fix Both Times
**Scenario:** Both start and end times are incorrect

```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-11-20T09:30:00Z",
    "end_time": "2025-11-20T17:30:00Z"
  }'
```

### Example 4: Different Timezone (UTC+5:30)

```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-11-20T09:30:00+05:30",
    "end_time": "2025-11-20T17:30:00+05:30"
  }'
```

### Example 5: Standard 8-Hour Day

```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/5/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-11-20T09:00:00Z",
    "end_time": "2025-11-20T17:00:00Z"
  }'
```

---

## ✅ PATCH Response (200 OK)

```json
{
  "success": true,
  "message": "Timer updated successfully for task 'Foundation Work'",
  "data": {
    "timer": {
      "id": 5,
      "task_id": 12,
      "employee_id": 3,
      "work_date": "2025-11-20",
      "start_time": "2025-11-20T09:30:00Z",
      "end_time": "2025-11-20T17:30:00Z",
      "duration_seconds": 28800,
      "is_active": false,
      "created_at": "2025-11-20T08:00:00Z",
      "updated_at": "2025-11-20T10:00:00Z"
    },
    "old_values": {
      "start_time": "2025-11-20T09:00:00Z",
      "end_time": "2025-11-20T17:00:00Z",
      "duration_seconds": 28800,
      "duration_formatted": "08:00:00"
    },
    "new_values": {
      "start_time": "2025-11-20T09:30:00Z",
      "end_time": "2025-11-20T17:30:00Z",
      "duration_seconds": 28800,
      "duration_formatted": "08:00:00"
    },
    "total_time_today": {
      "seconds": 28800,
      "formatted": "08:00:00",
      "task_name": "Foundation Work",
      "work_date": "2025-11-20"
    }
  }
}
```

---

## ❌ Error Responses

### Error 1: Timer Not Found (404)
```json
{
  "success": false,
  "message": "Timer with ID 999 not found or not owned by you",
  "data": null
}
```
**Status:** `404 NOT FOUND`

---

### Error 2: Missing Both Times (400)
```json
{
  "success": false,
  "message": "At least one of start_time or end_time must be provided",
  "data": null
}
```
**Status:** `400 BAD REQUEST`

---

### Error 3: Invalid DateTime Format (400)
```json
{
  "success": false,
  "message": "Invalid datetime format. Use ISO 8601 format (e.g., 2025-11-20T09:30:00Z): ...",
  "data": null
}
```
**Status:** `400 BAD REQUEST`

**Valid Formats:**
- ✅ `2025-11-20T09:30:00Z` (UTC)
- ✅ `2025-11-20T09:30:00+00:00` (UTC)
- ✅ `2025-11-20T09:30:00+05:30` (IST)
- ❌ `2025-11-20 09:30:00` (space instead of T)
- ❌ `11/20/2025 09:30:00` (wrong format)

---

### Error 4: End Time Not After Start Time (400)
```json
{
  "success": false,
  "message": "End time must be after start time",
  "data": null
}
```
**Status:** `400 BAD REQUEST`

---

### Error 5: Cannot Edit Future Timer (400)
```json
{
  "success": false,
  "message": "Cannot edit timers for future dates",
  "data": null
}
```
**Status:** `400 BAD REQUEST`

---

### Error 6: Not Authenticated (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```
**Status:** `401 UNAUTHORIZED`

---

### Error 7: Not an Employee (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Status:** `403 FORBIDDEN`

---

## 🧪 Test Scenarios

### Test 1: Get Timer Details
```bash
curl -X GET http://10.10.13.27:8002/api/employee/timer/edit/1/ \
  -H "Authorization: Bearer TOKEN"
```

### Test 2: Update Start Time Only
```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_time": "2025-11-20T10:00:00Z"}'
```

### Test 3: Update End Time Only
```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"end_time": "2025-11-20T18:00:00Z"}'
```

### Test 4: Update Both Times
```bash
curl -X PATCH http://10.10.13.27:8002/api/employee/timer/edit/1/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-11-20T10:00:00Z",
    "end_time": "2025-11-20T18:00:00Z"
  }'
```

### Test 5: Invalid Timer ID
```bash
curl -X GET http://10.10.13.27:8002/api/employee/timer/edit/999/ \
  -H "Authorization: Bearer TOKEN"
```

---

## 🌍 DateTime Format Guide

### ISO 8601 Standard Format

```
YYYY-MM-DDTHH:MM:SSZ
    |   |   | |  |  | |
    |   |   | |  |  | └─ UTC indicator
    |   |   | |  |  └──── Seconds (00-59)
    |   |   | |  └─────── Minutes (00-59)
    |   |   | └────────── Hours (00-23)
    |   |   └──────────── Date-Time separator (literal 'T')
    |   └─────────────── Day (01-31)
    └────────────────── Month (01-12)
    └───────────────── Year (YYYY)
```

### Examples by Timezone

```
UTC (Recommended):
  "2025-11-20T09:30:00Z"
  "2025-11-20T09:30:00+00:00"

EST (UTC-5):
  "2025-11-20T09:30:00-05:00"

CST (UTC-6):
  "2025-11-20T09:30:00-06:00"

IST (UTC+5:30):
  "2025-11-20T09:30:00+05:30"

JST (UTC+9):
  "2025-11-20T09:30:00+09:00"
```

---

## 💻 Frontend Integration Examples

### JavaScript / Fetch API - GET
```javascript
async function getTimerDetails(timerId) {
  const response = await fetch(
    `http://10.10.13.27:8002/api/employee/timer/edit/${timerId}/`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    }
  );
  
  const result = await response.json();
  if (result.success) {
    console.log('Timer:', result.data.timer);
    console.log('Task:', result.data.task_info);
    console.log('Duration:', result.data.duration);
  }
}

getTimerDetails(5);
```

### JavaScript / Fetch API - PATCH
```javascript
async function updateTimer(timerId, updates) {
  const response = await fetch(
    `http://10.10.13.27:8002/api/employee/timer/edit/${timerId}/`,
    {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    }
  );
  
  const result = await response.json();
  if (result.success) {
    console.log('Timer updated:', result.data.timer);
    console.log('Old duration:', result.data.old_values.duration_formatted);
    console.log('New duration:', result.data.new_values.duration_formatted);
  }
}

// Usage
updateTimer(5, {
  start_time: '2025-11-20T09:30:00Z',
});
```

### Python / Requests Library
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

# GET request
response = requests.get(
    'http://10.10.13.27:8002/api/employee/timer/edit/5/',
    headers=headers,
)
result = response.json()
print(result['data']['timer'])

# PATCH request
updates = {
    'start_time': '2025-11-20T09:30:00Z',
}
response = requests.patch(
    'http://10.10.13.27:8002/api/employee/timer/edit/5/',
    json=updates,
    headers=headers,
)
result = response.json()
print(result['data']['timer'])
```

### Vue.js / Axios
```javascript
// Vue component
async getTimerDetails(timerId) {
  try {
    const response = await this.$axios.get(
      `/api/employee/timer/edit/${timerId}/`,
      {
        headers: {
          'Authorization': `Bearer ${this.$store.state.token}`,
        },
      }
    );
    
    if (response.data.success) {
      this.timer = response.data.data.timer;
      this.taskInfo = response.data.data.task_info;
      this.duration = response.data.data.duration;
    }
  } catch (error) {
    this.$notify.error(`Error: ${error.message}`);
  }
}

async updateTimer(timerId, updates) {
  try {
    const response = await this.$axios.patch(
      `/api/employee/timer/edit/${timerId}/`,
      updates,
      {
        headers: {
          'Authorization': `Bearer ${this.$store.state.token}`,
        },
      }
    );
    
    if (response.data.success) {
      this.timer = response.data.data.timer;
      this.$notify.success(response.data.message);
      console.log('Old:', response.data.data.old_values);
      console.log('New:', response.data.data.new_values);
    }
  } catch (error) {
    this.$notify.error(`Error: ${error.message}`);
  }
}
```

---

## 📊 Request/Response Flow Diagram

```
┌─────────────────────────────────┐
│  Client Application             │
│  (Web / Mobile)                 │
└────────────┬────────────────────┘
             │
             ├─── GET Request ──────────────┐
             │                              │
             │  /timer/edit/{timer_id}/     │
             │  Retrieve timer details      │
             │                              │
             ├─── PATCH Request ────────┐   │
             │                          │   │
             │  /timer/edit/{timer_id}/ │   │
             │  Update times            │   │
             │                          │   │
             └────────┬────────────────┘   │
                      │                    │
                      ▼                    │
         ┌──────────────────────────┐      │
         │  Employee Timer API      │      │
         │  Single View Endpoint    │      │
         └──────────┬───────────────┘      │
                    │                      │
                    │ Process Request      │
                    │ Authenticate         │
                    │ Get Timer            │
                    │ Validate (if PATCH)  │
                    │ Update (if PATCH)    │
                    │ Format Response      │
                    │                      │
                    ▼                      │
           ┌────────────────────┐          │
           │  Database          │          │
           │  Read/Write Timer  │          │
           └────────┬───────────┘          │
                    │                      │
                    │◄─────────────────────┘
                    │
                    │ Response (200 OK)
                    │ {
                    │   success: true,
                    │   data: {...}
                    │ }
                    │
                    ▼
        ┌─────────────────────────────┐
        │  Client Application         │
        │  Display Timer Details      │
        │  or Confirmation Message    │
        └─────────────────────────────┘
```

---

## ✨ Response Data Summary

### GET Response includes:
```
├─ timer: Complete timer record
├─ task_info: Task and project details
├─ duration: Formatted duration (HH:MM:SS)
├─ total_time_today: Total daily time
└─ work_date: Date worked
```

### PATCH Response includes:
```
├─ timer: Updated timer record
├─ old_values: Previous times and duration
├─ new_values: New times and duration
└─ total_time_today: Updated daily total
```

---

## 🎯 Summary Table

| Method | Endpoint | Purpose | Body |
|--------|----------|---------|------|
| **GET** | `/timer/edit/{id}/` | Retrieve timer details | N/A |
| **PATCH** | `/timer/edit/{id}/` | Update timer times | `{start_time?, end_time?}` |

---

## 📋 Validation Rules

```
✅ VALID:
├─ timer_id: Must be valid integer in URL
├─ GET: No body required
├─ PATCH: At least one of start_time/end_time
├─ DateTime: ISO 8601 format
├─ end_time > start_time
├─ Cannot edit future timers (work_date must be <= today)
└─ Only own timers can be accessed

❌ INVALID:
├─ Invalid timer_id (404)
├─ Missing both times in PATCH (400)
├─ Invalid datetime format (400)
├─ end_time <= start_time (400)
├─ Future date timer (400)
├─ Timer from another employee (404)
└─ Not authenticated (401)
```

---

## 🔄 URL Pattern Comparison

### Before (Multiple endpoints):
```
PATCH /api/employee/timer/edit/
Body: {"timer_id": 5, "start_time": "..."}
```

### After (Single view):
```
GET  /api/employee/timer/edit/5/
PATCH /api/employee/timer/edit/5/
Body: {"start_time": "..."}  (timer_id in URL)
```

---

Ready to use! 🚀
