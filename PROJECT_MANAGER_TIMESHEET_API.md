# Project Manager - Employee Timesheet Management API

## API Overview
Project Managers can view detailed timesheet records for all employees in their company with comprehensive filtering and reporting options.

## Endpoint
```
GET /api/project-manager/employee-timesheets/
```

## Access Requirements
- **Authentication**: JWT Token (Bearer Token)
- **Permission**: Project Manager or Admin role
- **Company Scope**: Shows data only for employees in the manager's company

## Request Example
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/employee-timesheets/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

## Query Parameters

### 1. Filter by Employee
```bash
?employee_id=5
```
Shows timesheet records for a specific employee only.

### 2. Filter by Specific Date
```bash
?date=2025-02-05
```
Shows all timesheet entries for a specific date (YYYY-MM-DD format).

### 3. Filter by Date Range
```bash
?start_date=2025-02-01&end_date=2025-02-28
```
Shows timesheet entries within a date range (both dates are YYYY-MM-DD format, inclusive).

### 4. Filter by Week (ISO Week Format)
```bash
?week=2025-W06
```
Shows all timesheet entries for a specific week. Format: `YYYY-W##` (e.g., 2025-W06 for week 6 of 2025).

### 5. Filter by Attendance Status
```bash
?status=Present
```
Shows records with specific attendance status:
- `Present` - 6+ hours worked
- `Half Day` - 4-6 hours worked  
- `Absent` - less than 4 hours worked

### 6. Combine Multiple Filters
```bash
?start_date=2025-02-01&end_date=2025-02-28&status=Present
```

## Response Structure

### Complete Response Example
```json
{
  "success": true,
  "message": "Retrieved 45 timesheet records for 12 employees",
  "data": {
    "total_records": 45,
    "total_employees": 12,
    "total_working_hours": "360 hours 30 minutes",
    "attendance_summary": {
      "present": 40,
      "absent": 2,
      "half_day": 3
    },
    "timesheets": [
      {
        "id": 245813,
        "employee_id": 15,
        "employee_name": "Jane Smith",
        "employee_email": "jane.smith@company.com",
        "date": "2025-02-05",
        "week": "05/02/2025 - 12/02/2025",
        "entry_time": "10:00:00",
        "exit_time": "18:00:00",
        "total_working_time": "8 hours 0 minutes",
        "attendance": "Present",
        "created_at": "2025-02-05T10:00:00Z",
        "updated_at": "2025-02-05T18:00:00Z"
      },
      {
        "id": 245814,
        "employee_id": 15,
        "employee_name": "Jane Smith",
        "employee_email": "jane.smith@company.com",
        "date": "2025-02-06",
        "week": "05/02/2025 - 12/02/2025",
        "entry_time": "10:00:00",
        "exit_time": "14:00:00",
        "total_working_time": "4 hours 0 minutes",
        "attendance": "Half Day",
        "created_at": "2025-02-06T10:00:00Z",
        "updated_at": "2025-02-06T14:00:00Z"
      },
      {
        "id": 245815,
        "employee_id": 16,
        "employee_name": "John Johnson",
        "employee_email": "john.johnson@company.com",
        "date": "2025-02-05",
        "week": "05/02/2025 - 12/02/2025",
        "entry_time": null,
        "exit_time": null,
        "total_working_time": "0 hours 0 minutes",
        "attendance": "Absent",
        "created_at": "2025-02-05T08:00:00Z",
        "updated_at": "2025-02-05T08:00:00Z"
      }
    ]
  }
}
```

## Response Fields Explained

### Summary Statistics
- **total_records**: Total number of timesheet entries returned
- **total_employees**: Number of unique employees in the results
- **total_working_hours**: Combined total working hours across all entries
- **attendance_summary**: Count breakdown by attendance status

### Individual Timesheet Entry Fields
- **id**: Unique timesheet record ID
- **employee_id**: Employee's user ID
- **employee_name**: Employee's full name
- **employee_email**: Employee's email address
- **date**: Date of the timesheet entry (YYYY-MM-DD)
- **week**: Human-readable week range (DD/MM/YYYY - DD/MM/YYYY)
- **entry_time**: Clock-in time (HH:MM:SS format, null if not clocked in)
- **exit_time**: Clock-out time (HH:MM:SS format, null if not clocked out)
- **total_working_time**: Calculated total working time (human-readable format)
- **attendance**: Attendance status (Present, Absent, or Half Day)
- **created_at**: When the record was created (ISO 8601 format)
- **updated_at**: When the record was last updated (ISO 8601 format)

## Usage Examples

### Example 1: View All Company Timesheets
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/employee-timesheets/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 2: View Specific Employee's February Timesheet
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?employee_id=15&start_date=2025-02-01&end_date=2025-02-28" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 3: View All Present Attendance Records This Week
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?week=2025-W06&status=Present" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example 4: View Specific Date Across All Employees
```bash
curl -X GET "http://10.10.13.27:8002/api/project-manager/employee-timesheets/?date=2025-02-05" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing in Swagger

1. Open: `http://10.10.13.27:8002/swagger/`
2. Find: **GET /api/project-manager/employee-timesheets/**
3. Click **"Try it out"**
4. Enter query parameters as needed
5. Click **"Execute"**

## Attendance Status Logic
- **Present**: Employee worked 6 or more hours
- **Half Day**: Employee worked 4-6 hours
- **Absent**: Employee worked less than 4 hours (or no clock in/out)

## Key Features

✅ **Flexible Filtering**
- By employee, date, date range, week, or attendance status
- Combine multiple filters for precise results

✅ **Detailed Statistics**
- Total working hours across all entries
- Attendance breakdown (Present, Absent, Half Day)
- Unique employee count

✅ **Week Range Display**
- Automatic calculation of week boundaries
- Human-readable week format (DD/MM/YYYY - DD/MM/YYYY)

✅ **Comprehensive Employee Info**
- Employee name and email included
- Easy employee identification

✅ **Time Tracking Details**
- Clock-in and clock-out times
- Calculated working duration
- Formatted time display

## Error Handling

### Invalid Date Format
If you provide an invalid date format, it will be ignored and the filter will be skipped.

```bash
?date=2025/02/05  # Invalid - will be ignored
?date=2025-02-05  # Correct format
```

### Invalid Week Format
If you provide invalid week format, it will be ignored.

```bash
?week=W06  # Invalid - will be ignored
?week=2025-W06  # Correct format
```

### Non-existent Employee ID
Returns empty timesheet array if the employee ID doesn't exist or isn't in the manager's company.

## Company Scope
- Project Managers can ONLY see timesheets for employees in their company
- Data is automatically filtered by the manager's company
- No cross-company data leakage

## File Modifications
1. **Project_manager/views.py**: Added `view_company_timesheets()` function
2. **Project_manager/urls.py**: Added route `path('employee-timesheets/', ...)`

## Integration Notes
- Uses TimeEntry model from timesheet app
- Automatic week calculation (Monday-Sunday)
- Queries optimized with select_related for employee data
- Returns empty array if no matches found (not an error)
