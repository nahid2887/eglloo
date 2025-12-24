# Employee Task Timers API - Complete Guide

## 📡 Endpoint

**Base URL:** `http://10.10.13.27:8002/api/project-manager/employee-timesheets/`

**Method:** `GET`

---

## 🔐 Authentication

**Header Required:**
```
Authorization: Bearer YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Accessible to:** Project Manager, Admin only

**Data Source:** Employee task timers from **emopye app** (employee timesheet module)

---

## 📋 Overview

The Employee Task Timers endpoint shows work time tracking data from the emopye app. It tracks:

✅ **Employee work time** on assigned tasks  
✅ **Task and project assignment** details  
✅ **Timer status** (active/completed)  
✅ **Duration worked** in seconds and formatted  
✅ **Work dates and weeks**  
✅ **Start/end times** for each timer session  

---

## 🎯 Request Examples

### Get All Company Employee Timers
```bash
curl -X GET http://10.10.13.27:8002/api/project-manager/employee-timesheets/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Employee
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?employee_id=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Task
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?task_id=12" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Project
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?project_id=3" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Date
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?date=2025-12-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Date Range
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Week
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?week=2025-W48" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Timer Status (Active Only)
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?is_active=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Combined Filters
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?employee_id=5&project_id=3&start_date=2025-11-01" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Success Response (200 OK)

```json
{
  "success": true,
  "message": "Retrieved 15 timesheet records for 3 employees",
  "data": {
    "total_records": 15,
    "total_employees": 3,
    "total_working_hours": "45 hours 30 minutes",
    "timer_summary": {
      "active": 2,
      "completed": 13
    },
    "timesheets": [
      {
        "id": 127,
        "employee_id": 5,
        "employee_name": "John Smith",
        "employee_email": "john.smith@company.com",
        "task_id": 12,
        "task_name": "Kitchen Design",
        "project_id": 3,
        "project_name": "Office Renovation",
        "client_name": "ABC Corporation",
        "work_date": "2025-12-01",
        "week": "01/12/2025 - 07/12/2025",
        "start_time": "2025-12-01T09:00:00Z",
        "end_time": "2025-12-01T17:00:00Z",
        "duration_seconds": 28800,
        "duration_formatted": "8 hours 0 minutes 0 seconds",
        "current_duration_formatted": "8 hours 0 minutes 0 seconds",
        "is_active": false,
        "created_at": "2025-12-01T09:00:15Z",
        "updated_at": "2025-12-01T17:00:30Z"
      },
      {
        "id": 128,
        "employee_id": 5,
        "employee_name": "John Smith",
        "employee_email": "john.smith@company.com",
        "task_id": 15,
        "task_name": "Plumbing Work",
        "project_id": 3,
        "project_name": "Office Renovation",
        "client_name": "ABC Corporation",
        "work_date": "2025-12-01",
        "week": "01/12/2025 - 07/12/2025",
        "start_time": "2025-12-01T17:30:00Z",
        "end_time": null,
        "duration_seconds": 5400,
        "duration_formatted": "1 hours 30 minutes 0 seconds",
        "current_duration_formatted": "2 hours 15 minutes 45 seconds",
        "is_active": true,
        "created_at": "2025-12-01T17:30:00Z",
        "updated_at": "2025-12-01T19:45:45Z"
      },
      {
        "id": 129,
        "employee_id": 6,
        "employee_name": "Jane Doe",
        "employee_email": "jane.doe@company.com",
        "task_id": 18,
        "task_name": "Electrical Installation",
        "project_id": 4,
        "project_name": "Home Renovation Phase 2",
        "client_name": "XYZ Ltd",
        "work_date": "2025-11-30",
        "week": "24/11/2025 - 30/11/2025",
        "start_time": "2025-11-30T08:00:00Z",
        "end_time": "2025-11-30T16:30:00Z",
        "duration_seconds": 30600,
        "duration_formatted": "8 hours 30 minutes 0 seconds",
        "current_duration_formatted": "8 hours 30 minutes 0 seconds",
        "is_active": false,
        "created_at": "2025-11-30T08:00:20Z",
        "updated_at": "2025-11-30T16:30:45Z"
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
  "success": boolean,              // API call status
  "message": string,               // Human-readable message
  "data": {
    "total_records": integer,      // Total number of timer records
    "total_employees": integer,    // Number of unique employees
    "total_working_hours": string, // Total hours formatted
    "timer_summary": object,       // Active vs completed count
    "timesheets": array            // Array of timer records
  }
}
```

### Timer Summary
```json
{
  "timer_summary": {
    "active": 2,        // Currently running timers
    "completed": 13     // Stopped timers
  }
}
```

### Each Timer Record
```json
{
  "id": 127,
  "employee_id": 5,
  "employee_name": "John Smith",
  "employee_email": "john.smith@company.com",
  "task_id": 12,
  "task_name": "Kitchen Design",
  "project_id": 3,
  "project_name": "Office Renovation",
  "client_name": "ABC Corporation",
  "work_date": "2025-12-01",           // Date of work
  "week": "01/12/2025 - 07/12/2025",   // Week range
  "start_time": "2025-12-01T09:00:00Z",
  "end_time": "2025-12-01T17:00:00Z",  // Null if still active
  "duration_seconds": 28800,            // Total seconds worked
  "duration_formatted": "8 hours 0 minutes 0 seconds",
  "current_duration_formatted": "8 hours 0 minutes 0 seconds",  // For active timers, auto-updated
  "is_active": false,                   // True if timer is running
  "created_at": "2025-12-01T09:00:15Z",
  "updated_at": "2025-12-01T17:00:30Z"
}
```

---

## 📋 Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `employee_id` | Integer | No | Filter by specific employee | `?employee_id=5` |
| `task_id` | Integer | No | Filter by specific task | `?task_id=12` |
| `project_id` | Integer | No | Filter by specific project | `?project_id=3` |
| `date` | String (YYYY-MM-DD) | No | Filter by specific date | `?date=2025-12-01` |
| `start_date` | String (YYYY-MM-DD) | No | Filter from date onwards | `?start_date=2025-11-01` |
| `end_date` | String (YYYY-MM-DD) | No | Filter until date | `?end_date=2025-11-30` |
| `week` | String (YYYY-W##) | No | Filter by ISO week | `?week=2025-W48` |
| `is_active` | String | No | Filter by timer status | `?is_active=true` or `?is_active=false` |

---

## 🎯 Common Use Cases

### 1. Track Daily Work for Specific Employee
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?employee_id=5&date=2025-12-01" \
  -H "Authorization: Bearer TOKEN"
```

Response shows: John Smith's work on 2025-12-01 with all tasks and times

---

### 2. Monitor Active Timers (Running Now)
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?is_active=true" \
  -H "Authorization: Bearer TOKEN"
```

Response shows: All currently running timers with `current_duration_formatted` auto-calculated

---

### 3. Get Weekly Timesheet
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?week=2025-W48" \
  -H "Authorization: Bearer TOKEN"
```

Response shows: All work done in week 48 of 2025 (Nov 24 - Nov 30)

---

### 4. Track Project Work Hours
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?project_id=3&start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer TOKEN"
```

Response shows: Total work on project 3 during November with `total_working_hours`

---

### 5. Employee Monthly Report
```bash
curl "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?employee_id=5&start_date=2025-12-01&end_date=2025-12-31" \
  -H "Authorization: Bearer TOKEN"
```

Response shows: John Smith's complete December work history

---

## 💻 Frontend Integration Examples

### JavaScript / Fetch API
```javascript
async function getEmployeeTimesheets(filters = {}) {
  let url = 'http://10.10.13.27:8002/api/project-manager/employee-timesheets/';
  
  const params = new URLSearchParams();
  if (filters.employee_id) params.append('employee_id', filters.employee_id);
  if (filters.task_id) params.append('task_id', filters.task_id);
  if (filters.project_id) params.append('project_id', filters.project_id);
  if (filters.date) params.append('date', filters.date);
  if (filters.start_date) params.append('start_date', filters.start_date);
  if (filters.end_date) params.append('end_date', filters.end_date);
  if (filters.week) params.append('week', filters.week);
  if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
  
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
    return result.data;
  }
}

// Usage:
// Get all timers for employee 5 on 2025-12-01
const daily = await getEmployeeTimesheets({ 
  employee_id: 5, 
  date: '2025-12-01' 
});
console.log(`${daily.total_employees} employee(s) worked ${daily.total_working_hours}`);

// Get active timers only
const active = await getEmployeeTimesheets({ is_active: true });
console.log(`${active.timer_summary.active} active timer(s) running right now`);

// Get weekly report for week 48
const weekly = await getEmployeeTimesheets({ week: '2025-W48' });
console.log(`Week data: ${weekly.timesheets.length} records`);
```

---

### Python / Requests
```python
import requests

def get_employee_timesheets(**filters):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    
    params = {}
    if 'employee_id' in filters:
        params['employee_id'] = filters['employee_id']
    if 'task_id' in filters:
        params['task_id'] = filters['task_id']
    if 'project_id' in filters:
        params['project_id'] = filters['project_id']
    if 'date' in filters:
        params['date'] = filters['date']
    if 'start_date' in filters:
        params['start_date'] = filters['start_date']
    if 'end_date' in filters:
        params['end_date'] = filters['end_date']
    if 'week' in filters:
        params['week'] = filters['week']
    if 'is_active' in filters:
        params['is_active'] = str(filters['is_active']).lower()
    
    response = requests.get(
        'http://10.10.13.27:8002/api/project-manager/employee-timesheets/',
        params=params,
        headers=headers,
    )
    
    if response.status_code == 200:
        return response.json()['data']
    return None

# Usage:
# Get timers for employee 5 on specific date
data = get_employee_timesheets(employee_id=5, date='2025-12-01')
print(f"Total hours: {data['total_working_hours']}")

# Get active timers
active = get_employee_timesheets(is_active=True)
print(f"Active timers: {active['timer_summary']['active']}")

# Get weekly data
weekly = get_employee_timesheets(week='2025-W48')
for record in weekly['timesheets']:
    print(f"{record['employee_name']} - {record['task_name']}: {record['duration_formatted']}")
```

---

### Vue.js / Axios
```javascript
export default {
  data() {
    return {
      timesheets: [],
      filters: {
        employee_id: null,
        project_id: null,
        date: null,
        is_active: null,
      },
      stats: {},
      loading: false,
    }
  },
  methods: {
    async loadTimesheets() {
      this.loading = true;
      try {
        const params = {};
        if (this.filters.employee_id) params.employee_id = this.filters.employee_id;
        if (this.filters.project_id) params.project_id = this.filters.project_id;
        if (this.filters.date) params.date = this.filters.date;
        if (this.filters.is_active !== null) params.is_active = this.filters.is_active;
        
        const response = await this.$axios.get(
          '/api/project-manager/employee-timesheets/',
          { params }
        );
        
        if (response.data.success) {
          this.timesheets = response.data.data.timesheets;
          this.stats = {
            total_hours: response.data.data.total_working_hours,
            total_employees: response.data.data.total_employees,
            active_timers: response.data.data.timer_summary.active,
            completed_timers: response.data.data.timer_summary.completed,
          };
        }
      } catch (error) {
        this.$notify.error(`Error: ${error.message}`);
      } finally {
        this.loading = false;
      }
    },
    
    getStatusColor(isActive) {
      return isActive ? '#FF6B6B' : '#51CF66';
    },
    
    getStatusLabel(isActive) {
      return isActive ? '🔴 Running' : '✅ Completed';
    },
  },
  watch: {
    filters: {
      handler() {
        this.loadTimesheets();
      },
      deep: true,
    }
  }
}
```

**Template:**
```vue
<div class="timesheets-container">
  <!-- Filters -->
  <div class="filters">
    <div class="filter-group">
      <label>Employee:</label>
      <input v-model="filters.employee_id" type="number" placeholder="Employee ID">
    </div>
    <div class="filter-group">
      <label>Project:</label>
      <input v-model="filters.project_id" type="number" placeholder="Project ID">
    </div>
    <div class="filter-group">
      <label>Date:</label>
      <input v-model="filters.date" type="date">
    </div>
    <div class="filter-group">
      <label>Status:</label>
      <select v-model="filters.is_active">
        <option :value="null">All</option>
        <option :value="true">Active Only</option>
        <option :value="false">Completed Only</option>
      </select>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats" v-if="timesheets.length">
    <div class="stat-card">
      <h4>Total Hours</h4>
      <p>{{ stats.total_hours }}</p>
    </div>
    <div class="stat-card">
      <h4>Active Timers</h4>
      <p>{{ stats.active_timers }}</p>
    </div>
    <div class="stat-card">
      <h4>Completed</h4>
      <p>{{ stats.completed_timers }}</p>
    </div>
  </div>

  <!-- Timers Table -->
  <table v-if="timesheets.length" class="timesheets-table">
    <thead>
      <tr>
        <th>Employee</th>
        <th>Task</th>
        <th>Project</th>
        <th>Work Date</th>
        <th>Duration</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="timer in timesheets" :key="timer.id">
        <td>{{ timer.employee_name }}</td>
        <td>{{ timer.task_name }}</td>
        <td>{{ timer.project_name }}</td>
        <td>{{ timer.work_date }}</td>
        <td>{{ timer.duration_formatted }}</td>
        <td :style="{ color: getStatusColor(timer.is_active) }">
          {{ getStatusLabel(timer.is_active) }}
        </td>
      </tr>
    </tbody>
  </table>
  
  <div v-else class="no-data">No timers found</div>
</div>
```

---

## 📌 Key Fields Explained

| Field | Description | Example |
|-------|-------------|---------|
| **duration_seconds** | Total seconds worked | `28800` |
| **duration_formatted** | Human-readable format | `8 hours 0 minutes 0 seconds` |
| **current_duration_formatted** | Auto-updated for active timers | Updates in real-time |
| **is_active** | True if timer still running | `false` |
| **work_date** | Date employee worked on this task | `2025-12-01` |
| **week** | Week range for the date | `01/12/2025 - 07/12/2025` |

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

### Error 2: Permission Denied (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Status:** `403 FORBIDDEN`  
**Reason:** Only Project Manager and Admin roles can access  
**Fix:** Use Project Manager or Admin account

---

### Error 3: Server Error (500)
```json
{
  "success": false,
  "message": "Error retrieving employee timesheets: {error_details}",
  "data": null
}
```

**Status:** `500 INTERNAL_SERVER_ERROR`  
**Fix:** Check server logs

---

## 🎯 Quick Reference

### URL Patterns
```
/api/project-manager/employee-timesheets/
  ├─ ?employee_id=5
  ├─ ?task_id=12
  ├─ ?project_id=3
  ├─ ?date=2025-12-01
  ├─ ?start_date=2025-11-01&end_date=2025-11-30
  ├─ ?week=2025-W48
  ├─ ?is_active=true
  └─ ?employee_id=5&project_id=3&start_date=2025-11-01
```

### Common Scenarios
```
1. View all timers
   GET /api/project-manager/employee-timesheets/

2. See active timers (running now)
   GET /api/project-manager/employee-timesheets/?is_active=true

3. Get specific employee's daily work
   GET /api/project-manager/employee-timesheets/?employee_id=5&date=2025-12-01

4. Get project work summary
   GET /api/project-manager/employee-timesheets/?project_id=3&start_date=2025-11-01&end_date=2025-11-30

5. Get weekly report
   GET /api/project-manager/employee-timesheets/?week=2025-W48

6. Track specific task
   GET /api/project-manager/employee-timesheets/?task_id=12
```

---

## ✨ Key Features

✅ **From emopye app** - Real task timer data from employee tracking system  
✅ **Active timers** - Shows currently running timers with auto-updated duration  
✅ **Flexible filtering** - By employee, task, project, date, week, or status  
✅ **Detailed tracking** - Start/end times, duration, work dates  
✅ **Company-scoped** - Project managers see only their company's employees  
✅ **Total calculations** - Automatic sum of total hours worked  

---

Ready to use! 🚀
