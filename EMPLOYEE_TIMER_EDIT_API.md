# Employee Timer Edit API - Complete Guide

## Overview
A new API endpoint allows employees to edit their task timer by adjusting the start time or end time. This is useful when employees need to correct time entries after the fact.

---

## Endpoint

### Edit Task Timer
**URL:** `PATCH /api/employee/timer/edit/`

**Authentication:** Required (Employee role)

**Description:** Allows employees to edit their task timer by adjusting start time and/or end time.

---

## Request

### Method
```
PATCH
```

### Headers
```http
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

### Request Body
```json
{
  "timer_id": 5,
  "start_time": "2025-11-20T09:30:00Z",
  "end_time": "2025-11-20T17:30:00Z"
}
```

### Parameters

| Parameter | Type | Required | Format | Description |
|-----------|------|----------|--------|-------------|
| `timer_id` | integer | Yes | Integer | ID of the timer to edit |
| `start_time` | string | No | ISO 8601 | New start time (e.g., 2025-11-20T09:30:00Z) |
| `end_time` | string | No | ISO 8601 | New end time (e.g., 2025-11-20T17:30:00Z) |

**At least one of `start_time` or `end_time` must be provided.**

### Example Requests

#### Edit Start Time Only
```bash
curl -X PATCH "http://localhost:8000/api/employee/timer/edit/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timer_id": 5,
    "start_time": "2025-11-20T09:30:00Z"
  }'
```

#### Edit End Time Only
```bash
curl -X PATCH "http://localhost:8000/api/employee/timer/edit/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timer_id": 5,
    "end_time": "2025-11-20T17:30:00Z"
  }'
```

#### Edit Both Start and End Times
```bash
curl -X PATCH "http://localhost:8000/api/employee/timer/edit/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timer_id": 5,
    "start_time": "2025-11-20T09:30:00Z",
    "end_time": "2025-11-20T17:30:00Z"
  }'
```

---

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Timer updated successfully for task 'Foundation Work'",
  "data": {
    "timer": {
      "id": 5,
      "employee": 3,
      "task": 1,
      "work_date": "2025-11-20",
      "start_time": "2025-11-20T09:30:00Z",
      "end_time": "2025-11-20T17:30:00Z",
      "duration_seconds": 28800,
      "is_active": false,
      "created_at": "2025-11-20T08:00:00Z",
      "updated_at": "2025-11-20T18:00:00Z"
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

### Error Responses

#### 400 Bad Request - Missing timer_id
```json
{
  "success": false,
  "message": "timer_id is required",
  "data": null
}
```

#### 400 Bad Request - No times provided
```json
{
  "success": false,
  "message": "At least one of start_time or end_time must be provided",
  "data": null
}
```

#### 400 Bad Request - Invalid datetime format
```json
{
  "success": false,
  "message": "Invalid datetime format. Use ISO 8601 format (e.g., 2025-11-20T09:30:00Z): [error details]",
  "data": null
}
```

#### 400 Bad Request - End time not after start time
```json
{
  "success": false,
  "message": "End time must be after start time",
  "data": null
}
```

#### 400 Bad Request - Cannot edit future timer
```json
{
  "success": false,
  "message": "Cannot edit timers for future dates",
  "data": null
}
```

#### 404 Not Found - Timer not found
```json
{
  "success": false,
  "message": "Timer not found or not owned by you",
  "data": null
}
```

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden (Non-employee user)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Rules & Validations

### 1. Required Fields
- `timer_id` is **always required**
- At least one of `start_time` or `end_time` must be provided

### 2. Time Validations
- `end_time` must be **after** `start_time`
- If updating only `start_time`, existing `end_time` must be after the new `start_time`
- If updating only `end_time`, the new `end_time` must be after existing `start_time`

### 3. Date Restrictions
- Cannot edit timers for **future dates** (after today)
- Can only edit **own timers** (current user)

### 4. Duration Calculation
- Duration is automatically recalculated: `end_time - start_time`
- Duration is stored in **seconds**

### 5. DateTime Format
- Must use **ISO 8601 format**
- Timezone must be included (Z for UTC or ±HH:MM)
- Valid examples:
  - `2025-11-20T09:30:00Z`
  - `2025-11-20T09:30:00+00:00`
  - `2025-11-20T09:30:00-05:00`

---

## Use Cases

### Case 1: Adjust Start Time (Late Clock-in)
Employee forgot to clock in at the correct time.

**Request:**
```json
{
  "timer_id": 5,
  "start_time": "2025-11-20T09:30:00Z"
}
```

**Result:** Start time is updated, end time remains the same, duration is recalculated.

---

### Case 2: Adjust End Time (Late Clock-out)
Employee worked longer than initially recorded.

**Request:**
```json
{
  "timer_id": 5,
  "end_time": "2025-11-20T18:00:00Z"
}
```

**Result:** End time is updated, start time remains the same, duration is recalculated.

---

### Case 3: Correct Both Times
Employee realizes both times were wrong.

**Request:**
```json
{
  "timer_id": 5,
  "start_time": "2025-11-20T09:00:00Z",
  "end_time": "2025-11-20T18:00:00Z"
}
```

**Result:** Both times are updated, new duration is calculated (9 hours = 32400 seconds).

---

### Case 4: Convert Active Timer to Fixed Time
Employee was working with an active timer but wants to set exact times.

**Request:**
```json
{
  "timer_id": 5,
  "start_time": "2025-11-20T08:00:00Z",
  "end_time": "2025-11-20T17:00:00Z"
}
```

**Result:** Timer is now fixed with exact times and duration calculated.

---

## Duration Calculation Examples

### Example 1: 8 Hours
- Start: `2025-11-20T09:00:00Z`
- End: `2025-11-20T17:00:00Z`
- Duration: `28800 seconds` = `08:00:00`

### Example 2: 8.5 Hours
- Start: `2025-11-20T09:00:00Z`
- End: `2025-11-20T17:30:00Z`
- Duration: `30600 seconds` = `08:30:00`

### Example 3: 8 Hours 45 Minutes
- Start: `2025-11-20T09:00:00Z`
- End: `2025-11-20T17:45:00Z`
- Duration: `31500 seconds` = `08:45:00`

---

## Response Fields

### timer Object
| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Timer ID |
| `employee` | integer | Employee user ID |
| `task` | integer | Task ID |
| `work_date` | date | Date of work |
| `start_time` | string | Start time (ISO 8601) |
| `end_time` | string | End time (ISO 8601) |
| `duration_seconds` | integer | Duration in seconds |
| `is_active` | boolean | Whether timer is currently running |
| `created_at` | string | Creation timestamp |
| `updated_at` | string | Last update timestamp |

### old_values Object
Shows the values **before** the edit for comparison.

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | string | Previous start time |
| `end_time` | string | Previous end time |
| `duration_seconds` | integer | Previous duration in seconds |
| `duration_formatted` | string | Previous duration formatted (HH:MM:SS) |

### new_values Object
Shows the values **after** the edit.

| Field | Type | Description |
|-------|------|-------------|
| `start_time` | string | New start time |
| `end_time` | string | New end time |
| `duration_seconds` | integer | New duration in seconds |
| `duration_formatted` | string | New duration formatted (HH:MM:SS) |

### total_time_today Object
Shows the total time worked on this task for the entire day.

| Field | Type | Description |
|-------|------|-------------|
| `seconds` | integer | Total seconds for the day |
| `formatted` | string | Total formatted (HH:MM:SS) |
| `task_name` | string | Name of the task |
| `work_date` | string | Work date (YYYY-MM-DD) |

---

## Integration Examples

### JavaScript / Fetch
```javascript
const editTimer = async (timerId, startTime, endTime) => {
  const response = await fetch('/api/employee/timer/edit/', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      timer_id: timerId,
      start_time: startTime,
      end_time: endTime,
    })
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Timer updated:', data.data.timer);
    console.log('Old duration:', data.data.old_values.duration_formatted);
    console.log('New duration:', data.data.new_values.duration_formatted);
  } else {
    console.error('Error:', data.message);
  }
};

// Usage
await editTimer(
  5,
  '2025-11-20T09:30:00Z',
  '2025-11-20T17:30:00Z'
);
```

### Python / Requests
```python
import requests
from datetime import datetime

def edit_timer(token, timer_id, start_time=None, end_time=None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
    
    payload = {'timer_id': timer_id}
    if start_time:
        payload['start_time'] = start_time.isoformat()
    if end_time:
        payload['end_time'] = end_time.isoformat()
    
    response = requests.patch(
        'http://localhost:8000/api/employee/timer/edit/',
        json=payload,
        headers=headers
    )
    
    return response.json()

# Usage
result = edit_timer(
    token='YOUR_TOKEN',
    timer_id=5,
    start_time=datetime(2025, 11, 20, 9, 30),
    end_time=datetime(2025, 11, 20, 17, 30)
)

if result['success']:
    print(f"Timer updated: {result['message']}")
    print(f"New duration: {result['data']['new_values']['duration_formatted']}")
```

### Vue.js Component
```vue
<template>
  <div class="edit-timer">
    <form @submit.prevent="submitEdit">
      <div class="form-group">
        <label>Start Time</label>
        <input 
          v-model="form.start_time" 
          type="datetime-local"
          placeholder="2025-11-20T09:30"
        />
      </div>
      
      <div class="form-group">
        <label>End Time</label>
        <input 
          v-model="form.end_time" 
          type="datetime-local"
          placeholder="2025-11-20T17:30"
        />
      </div>
      
      <button type="submit">Update Timer</button>
    </form>
    
    <div v-if="result" class="result">
      <p v-if="result.success" class="success">
        {{ result.message }}
      </p>
      <p v-else class="error">
        {{ result.message }}
      </p>
      
      <div v-if="result.data" class="details">
        <p>Old duration: {{ result.data.old_values.duration_formatted }}</p>
        <p>New duration: {{ result.data.new_values.duration_formatted }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        timer_id: null,
        start_time: '',
        end_time: '',
      },
      result: null,
    }
  },
  methods: {
    async submitEdit() {
      const response = await fetch('/api/employee/timer/edit/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${this.$store.state.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          timer_id: this.form.timer_id,
          start_time: new Date(this.form.start_time).toISOString(),
          end_time: new Date(this.form.end_time).toISOString(),
        })
      });
      
      this.result = await response.json();
    }
  }
}
</script>
```

---

## Testing Checklist

- [ ] Edit start time only
- [ ] Edit end time only
- [ ] Edit both start and end times
- [ ] Verify duration recalculates correctly
- [ ] Verify total daily time updates
- [ ] Try with invalid datetime format
- [ ] Try with end time before start time
- [ ] Try to edit non-existent timer
- [ ] Try to edit someone else's timer
- [ ] Try to edit future timer
- [ ] Verify response includes old and new values
- [ ] Verify comparison data is accurate

---

## Error Handling Best Practices

### Always Check Success Flag
```javascript
if (response.data.success) {
  // Handle success
} else {
  // Handle error - message field has details
  showErrorMessage(response.data.message);
}
```

### Handle Specific Errors
```javascript
if (response.status === 404) {
  // Timer not found
} else if (response.status === 400) {
  // Validation error - check message
} else if (response.status === 401) {
  // Authentication error
}
```

### Display Changes to User
```javascript
const result = response.data.data;
console.log(`Duration changed from ${result.old_values.duration_formatted} to ${result.new_values.duration_formatted}`);
```

---

## Security Notes

✅ Authentication required
✅ Only employee can edit own timers
✅ Cannot edit timers from future dates
✅ All input validated
✅ Timezone-aware operations

---

## Related Endpoints

- `POST /api/employee/timer/toggle/` - Start/stop timer
- `GET /api/employee/timer/daily-summary/` - View daily timer summary
- `GET /api/employee/timesheet/entries/` - View all timesheet entries

---

## Version History

- **v1.0** (2025-11-29): Initial release
  - Edit start time
  - Edit end time
  - Edit both times
  - Automatic duration recalculation
