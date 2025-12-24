# Employee Timer Edit API - Quick Reference

## 🎯 What's New

A new API endpoint allows employees to edit their task timer by adjusting start time and/or end time.

---

## 📍 Endpoint

```
PATCH /api/employee/timer/edit/
```

---

## 🔐 Authentication
- Required: Yes
- Role: Employee only

---

## 📝 Request Example

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

## 📨 Request Body

```json
{
  "timer_id": 5,                              // Required
  "start_time": "2025-11-20T09:30:00Z",      // Optional - ISO 8601
  "end_time": "2025-11-20T17:30:00Z"         // Optional - ISO 8601
}
```

**Rules:**
- `timer_id` is required
- At least one of `start_time` or `end_time` must be provided
- End time must be after start time
- Cannot edit timers for future dates

---

## ✅ Success Response (200)

```json
{
  "success": true,
  "message": "Timer updated successfully for task 'Foundation Work'",
  "data": {
    "timer": { /* Updated timer object */ },
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

## ❌ Common Errors

| Error | Status | Solution |
|-------|--------|----------|
| Missing timer_id | 400 | Provide timer_id |
| No times provided | 400 | Provide start_time or end_time |
| Invalid datetime format | 400 | Use ISO 8601 (2025-11-20T09:30:00Z) |
| End before start | 400 | Ensure end_time > start_time |
| Timer not found | 404 | Check timer_id is correct |
| Future timer | 400 | Cannot edit future timers |
| Not authenticated | 401 | Add Authorization header |

---

## 💡 Use Cases

### Edit Start Time Only
```bash
curl -X PATCH "http://localhost:8000/api/employee/timer/edit/" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"timer_id": 5, "start_time": "2025-11-20T09:30:00Z"}'
```

### Edit End Time Only
```bash
curl -X PATCH "http://localhost:8000/api/employee/timer/edit/" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"timer_id": 5, "end_time": "2025-11-20T17:30:00Z"}'
```

### Correct Both Times
```bash
curl -X PATCH "http://localhost:8000/api/employee/timer/edit/" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "timer_id": 5,
    "start_time": "2025-11-20T09:00:00Z",
    "end_time": "2025-11-20T18:00:00Z"
  }'
```

---

## ⏱️ Duration Examples

| Start | End | Duration |
|-------|-----|----------|
| 09:00 | 17:00 | 08:00:00 (8 hours) |
| 09:00 | 17:30 | 08:30:00 (8.5 hours) |
| 09:00 | 17:45 | 08:45:00 (8 hours 45 min) |
| 09:30 | 17:30 | 08:00:00 (8 hours) |

---

## 🔗 DateTime Format

Must use **ISO 8601 format with timezone**:
- ✅ `2025-11-20T09:30:00Z` (UTC)
- ✅ `2025-11-20T09:30:00+00:00` (UTC)
- ✅ `2025-11-20T09:30:00-05:00` (EST)
- ❌ `2025-11-20 09:30:00` (Invalid)
- ❌ `11/20/2025 09:30 AM` (Invalid)

---

## 🎯 Key Features

✅ Edit start time, end time, or both
✅ Automatic duration recalculation
✅ Compare old vs new values
✅ See total daily time worked
✅ Can only edit own timers
✅ Cannot edit future timers
✅ Full datetime validation
✅ Employee role required

---

## 📋 Response Fields

### old_values
Previous timer values before edit:
- `start_time`
- `end_time`
- `duration_seconds`
- `duration_formatted` (HH:MM:SS)

### new_values
Updated timer values after edit:
- `start_time`
- `end_time`
- `duration_seconds`
- `duration_formatted` (HH:MM:SS)

### total_time_today
Total work time on this task for the day:
- `seconds` - Total in seconds
- `formatted` - Formatted as HH:MM:SS
- `task_name` - Name of the task
- `work_date` - Date (YYYY-MM-DD)

---

## 🚀 Frontend Integration

### JavaScript
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
  
  return await response.json();
};
```

### Python
```python
import requests

def edit_timer(token, timer_id, start_time=None, end_time=None):
    response = requests.patch(
        'http://localhost:8000/api/employee/timer/edit/',
        json={
            'timer_id': timer_id,
            'start_time': start_time,
            'end_time': end_time,
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()
```

---

## 🧪 Test Cases

1. ✓ Edit start time only
2. ✓ Edit end time only
3. ✓ Edit both times
4. ✓ Invalid datetime format
5. ✓ End time before start time
6. ✓ Timer not found
7. ✓ Future timer
8. ✓ No authentication
9. ✓ Duration recalculates
10. ✓ Total daily time updates

---

## 📖 Related Endpoints

- `POST /api/employee/timer/toggle/` - Start/stop timer
- `GET /api/employee/timer/daily-summary/` - Daily summary
- `GET /api/employee/timesheet/entries/` - Timesheet entries

---

## 📄 Full Documentation

See `EMPLOYEE_TIMER_EDIT_API.md` for complete documentation with:
- Detailed examples
- All validation rules
- Integration code samples
- Error handling
- Use cases
- Testing checklist
