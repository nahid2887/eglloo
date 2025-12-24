# Estimator Dashboard API - Complete Guide

## 📡 Endpoint

**Base URL:** `http://10.10.13.27:8002/api/estimator/dashboard/`

**Method:** `GET`

---

## 🔐 Authentication

**Header Required:**
```
Authorization: Bearer YOUR_AUTH_TOKEN
Content-Type: application/json
```

**Accessible to:** Estimators (see their own estimates) and Admin (see all estimates)

---

## 📋 Overview

The Estimator Dashboard provides a comprehensive overview of all estimates with:

✅ **Overview Statistics** - Total counts by status  
✅ **Value Summary** - Total estimated value by status  
✅ **Due Soon** - Estimates with deadlines in next 30 days  
✅ **Recent Estimates** - Last 10 created estimates  
✅ **Completed Estimates** - All approved estimates  
✅ **Performance Metrics** - Approval/rejection rates and average value  

---

## 🎯 Request Example

### Get Estimator Dashboard
```bash
curl -X GET http://10.10.13.27:8002/api/estimator/dashboard/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✅ Success Response (200 OK)

```json
{
  "success": true,
  "message": "Estimator dashboard retrieved successfully",
  "data": {
    "overview": {
      "total_estimates": 15,
      "pending": 3,
      "sent": 4,
      "approved": 6,
      "rejected": 2
    },
    "value_summary": {
      "pending_value": 15000.00,
      "sent_value": 22500.00,
      "approved_value": 45000.00,
      "rejected_value": 8000.00,
      "total_value": 90500.00
    },
    "due_soon": [
      {
        "id": 5,
        "serial_number": "EST-2025-005",
        "estimate_number": "EST-2025-ABC-005",
        "project_name": "Kitchen Renovation",
        "client_name": "Tom Allen",
        "end_date": "2025-05-08",
        "days_remaining": 7,
        "status": "pending",
        "total_value": 5000.00
      },
      {
        "id": 8,
        "serial_number": "EST-2025-008",
        "estimate_number": "EST-2025-XYZ-008",
        "project_name": "Breeze Water Fitout",
        "client_name": "Aliki Joen",
        "end_date": "2025-05-18",
        "days_remaining": 17,
        "status": "sent",
        "total_value": 7500.00
      }
    ],
    "recent_estimates": [
      {
        "id": 15,
        "serial_number": "EST-2025-015",
        "estimate_number": "EST-2025-NEW-015",
        "project_name": "Office Renovation Phase 2",
        "client_name": "Acme Corp",
        "status": "pending",
        "created_at": "2025-05-01T14:30:00Z",
        "total_value": 12500.00,
        "estimate_date": "2025-05-01"
      },
      {
        "id": 14,
        "serial_number": "EST-2025-014",
        "estimate_number": "EST-2025-NEW-014",
        "project_name": "Home Renovation",
        "client_name": "Jane Doe",
        "status": "approved",
        "created_at": "2025-04-30T10:15:00Z",
        "total_value": 8500.00,
        "estimate_date": "2025-04-30"
      }
    ],
    "completed_estimates": [
      {
        "id": 1,
        "serial_number": "EST-2025-001",
        "estimate_number": "EST-2025-ABC-001",
        "project_name": "Staff Kitchen",
        "client_name": "Tom Allen",
        "status": "approved",
        "total_value": 7500.00,
        "estimate_date": "2025-04-15",
        "approved_date": "2025-04-28T11:00:00Z"
      },
      {
        "id": 2,
        "serial_number": "EST-2025-002",
        "estimate_number": "EST-2025-ABC-002",
        "project_name": "Breeze Water Fitout",
        "client_name": "Aliki Joen",
        "status": "approved",
        "total_value": 9200.00,
        "estimate_date": "2025-04-16",
        "approved_date": "2025-04-27T09:30:00Z"
      }
    ],
    "performance": {
      "approval_rate": 40.0,
      "rejection_rate": 13.33,
      "pending_rate": 20.0,
      "average_estimate_value": 6033.33
    }
  }
}
```

---

## 📊 Response Data Structure

### Overview Section
```json
{
  "overview": {
    "total_estimates": 15,           // Total number of estimates
    "pending": 3,                    // Pending estimates (not sent)
    "sent": 4,                       // Sent for approval
    "approved": 6,                   // Approved estimates
    "rejected": 2                    // Rejected estimates
  }
}
```

### Value Summary
```json
{
  "value_summary": {
    "pending_value": 15000.00,       // Total value of pending estimates
    "sent_value": 22500.00,          // Total value of sent estimates
    "approved_value": 45000.00,      // Total value of approved estimates
    "rejected_value": 8000.00,       // Total value of rejected estimates
    "total_value": 90500.00          // Total estimated value (all statuses)
  }
}
```

### Due Soon (Next 30 Days)
```json
{
  "due_soon": [
    {
      "id": 5,
      "serial_number": "EST-2025-005",
      "estimate_number": "EST-2025-ABC-005",
      "project_name": "Kitchen Renovation",
      "client_name": "Tom Allen",
      "end_date": "2025-05-08",          // Project end date
      "days_remaining": 7,                // Days until deadline
      "status": "pending",                // Current estimate status
      "total_value": 5000.00              // Estimated total value
    }
  ]
}
```

### Recent Estimates (Last 10 Created)
```json
{
  "recent_estimates": [
    {
      "id": 15,
      "serial_number": "EST-2025-015",
      "estimate_number": "EST-2025-NEW-015",
      "project_name": "Office Renovation Phase 2",
      "client_name": "Acme Corp",
      "status": "pending",
      "created_at": "2025-05-01T14:30:00Z",
      "total_value": 12500.00,
      "estimate_date": "2025-05-01"
    }
  ]
}
```

### Completed Estimates (Approved Status)
```json
{
  "completed_estimates": [
    {
      "id": 1,
      "serial_number": "EST-2025-001",
      "estimate_number": "EST-2025-ABC-001",
      "project_name": "Staff Kitchen",
      "client_name": "Tom Allen",
      "status": "approved",
      "total_value": 7500.00,
      "estimate_date": "2025-04-15",
      "approved_date": "2025-04-28T11:00:00Z"
    }
  ]
}
```

### Performance Metrics
```json
{
  "performance": {
    "approval_rate": 40.0,                    // % of approved estimates
    "rejection_rate": 13.33,                  // % of rejected estimates
    "pending_rate": 20.0,                     // % of pending estimates
    "average_estimate_value": 6033.33         // Average value per estimate
  }
}
```

---

## 📈 Key Metrics Explained

| Metric | Description | Formula |
|--------|-------------|---------|
| **Approval Rate** | Percentage of approved estimates | (Approved / Total) × 100 |
| **Rejection Rate** | Percentage of rejected estimates | (Rejected / Total) × 100 |
| **Pending Rate** | Percentage of pending estimates | (Pending / Total) × 100 |
| **Avg Value** | Average estimated value per estimate | Total Value / Total Estimates |
| **Days Remaining** | Days until project end_date | end_date - today |

---

## 🎯 Usage Examples

### Example 1: Monitor Due Estimates
Use the `due_soon` array to identify which estimates need attention:

```javascript
// From dashboard response
const dueSoon = response.data.data.due_soon;

dueSoon.forEach(estimate => {
  if (estimate.days_remaining <= 7) {
    console.log(`⚠️ URGENT: ${estimate.project_name} due in ${estimate.days_remaining} days`);
  } else if (estimate.days_remaining <= 14) {
    console.log(`📌 ${estimate.project_name} due in ${estimate.days_remaining} days`);
  }
});
```

### Example 2: Track Approval Performance
Use performance metrics to monitor how well estimates are being approved:

```javascript
const performance = response.data.data.performance;

console.log(`✅ Approval Rate: ${performance.approval_rate}%`);
console.log(`❌ Rejection Rate: ${performance.rejection_rate}%`);
console.log(`⏳ Pending Rate: ${performance.pending_rate}%`);

// Calculate sent rate
const sentRate = 100 - (performance.approval_rate + performance.rejection_rate + performance.pending_rate);
console.log(`📤 Sent Rate: ${sentRate}%`);
```

### Example 3: Calculate Revenue
Track estimated revenue by status:

```javascript
const valueSummary = response.data.data.value_summary;

console.log(`💰 Approved (Confirmed): $${valueSummary.approved_value}`);
console.log(`📤 Sent (Potential): $${valueSummary.sent_value}`);
console.log(`⏳ Pending (In Progress): $${valueSummary.pending_value}`);
console.log(`❌ Rejected (Lost): $${valueSummary.rejected_value}`);
console.log(`📊 Total Pipeline: $${valueSummary.total_value}`);
```

---

## 💻 Frontend Integration Examples

### JavaScript / Fetch API
```javascript
async function getEstimatorDashboard() {
  const response = await fetch(
    'http://10.10.13.27:8002/api/estimator/dashboard/',
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
    console.log('Overview:', result.data.overview);
    console.log('Due Soon:', result.data.due_soon);
    console.log('Recent:', result.data.recent_estimates);
    console.log('Completed:', result.data.completed_estimates);
    console.log('Performance:', result.data.performance);
    
    return result.data;
  }
}

// Usage
const dashboard = await getEstimatorDashboard();
```

---

### Python / Requests
```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
}

response = requests.get(
    'http://10.10.13.27:8002/api/estimator/dashboard/',
    headers=headers,
)

if response.status_code == 200:
    data = response.json()
    
    print(f"Total Estimates: {data['data']['overview']['total_estimates']}")
    print(f"Approval Rate: {data['data']['performance']['approval_rate']}%")
    print(f"Total Value: ${data['data']['value_summary']['total_value']}")
    
    # Process due soon estimates
    for estimate in data['data']['due_soon']:
        print(f"  - {estimate['project_name']} ({estimate['days_remaining']} days)")
```

---

### Vue.js / Axios
```javascript
// Vue component
export default {
  data() {
    return {
      dashboard: null,
      loading: true,
    }
  },
  mounted() {
    this.loadDashboard();
  },
  methods: {
    async loadDashboard() {
      try {
        const response = await this.$axios.get('/api/estimator/dashboard/');
        
        if (response.data.success) {
          this.dashboard = response.data.data;
        }
      } catch (error) {
        this.$notify.error(`Error: ${error.message}`);
      } finally {
        this.loading = false;
      }
    },
    
    getStatusColor(status) {
      const colors = {
        pending: '#FFA500',
        sent: '#3498DB',
        approved: '#27AE60',
        rejected: '#E74C3C',
      };
      return colors[status] || '#95A5A6';
    },
  }
}
```

**Template:**
```vue
<div v-if="dashboard" class="dashboard">
  <!-- Overview Stats -->
  <div class="stats-grid">
    <div class="stat-card">
      <h3>Total Estimates</h3>
      <p class="big-number">{{ dashboard.overview.total_estimates }}</p>
    </div>
    <div class="stat-card">
      <h3>Approved</h3>
      <p class="big-number success">{{ dashboard.overview.approved }}</p>
    </div>
    <div class="stat-card">
      <h3>Pending</h3>
      <p class="big-number warning">{{ dashboard.overview.pending }}</p>
    </div>
    <div class="stat-card">
      <h3>Total Value</h3>
      <p class="big-number">${{ dashboard.value_summary.total_value }}</p>
    </div>
  </div>

  <!-- Due Soon Section -->
  <div class="due-soon">
    <h2>📌 Due Soon (Next 30 Days)</h2>
    <table v-if="dashboard.due_soon.length > 0">
      <thead>
        <tr>
          <th>Quote Name</th>
          <th>Client</th>
          <th>Due Date</th>
          <th>Days Left</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="estimate in dashboard.due_soon" :key="estimate.id">
          <td>{{ estimate.project_name }}</td>
          <td>{{ estimate.client_name }}</td>
          <td>{{ estimate.end_date }}</td>
          <td :style="{ color: estimate.days_remaining <= 7 ? 'red' : 'orange' }">
            {{ estimate.days_remaining }} days
          </td>
          <td>${{ estimate.total_value }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>No estimates due in the next 30 days</p>
  </div>

  <!-- Recent Estimates Section -->
  <div class="recent">
    <h2>📅 Recent Quotes</h2>
    <div class="cards">
      <div v-for="estimate in dashboard.recent_estimates" :key="estimate.id" class="card">
        <h4>{{ estimate.project_name }}</h4>
        <p>Client: {{ estimate.client_name }}</p>
        <p>Status: <span :style="{ color: getStatusColor(estimate.status) }">{{ estimate.status }}</span></p>
        <p class="value">${{ estimate.total_value }}</p>
      </div>
    </div>
  </div>

  <!-- Completed Section -->
  <div class="completed">
    <h2>✅ Quotes Won</h2>
    <div class="chart">
      <!-- Chart visualization of completed estimates -->
    </div>
  </div>
</div>
```

---

## 🔄 Request/Response Flow

```
┌──────────────────────────────┐
│  Frontend Application        │
│  (Estimator Dashboard)       │
└────────────┬─────────────────┘
             │
             │ GET Request
             │ /api/estimator/dashboard/
             │ Authorization: Bearer TOKEN
             │
             ▼
┌──────────────────────────────┐
│  API Endpoint                │
│  /estimator/dashboard/       │
└────────────┬─────────────────┘
             │
             │ Process
             │ ├─ Authenticate user
             │ ├─ Get user's estimates
             │ ├─ Calculate statistics
             │ ├─ Find due soon (30 days)
             │ ├─ Get recent (last 10)
             │ ├─ Get completed (approved)
             │ ├─ Calculate performance
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
             │   overview: {...},
             │   value_summary: {...},
             │   due_soon: [...],
             │   recent_estimates: [...],
             │   completed_estimates: [...],
             │   performance: {...}
             │ }
             │
             ▼
┌──────────────────────────────┐
│  Frontend Application        │
│  Display Dashboard:          │
│  - Overview Cards            │
│  - Due Soon Table            │
│  - Recent Quotes Cards       │
│  - Completed Chart           │
│  - Performance Metrics       │
└──────────────────────────────┘
```

---

## 📌 Key Features

✅ **Estimator Specific** - Estimators see only their estimates (Admins see all)  
✅ **Due Soon Tracking** - Auto-filter estimates expiring within 30 days  
✅ **Value Tracking** - See total estimated value by status  
✅ **Performance Metrics** - Monitor approval/rejection rates  
✅ **Recent Activity** - Last 10 created estimates  
✅ **Completed Tracking** - See all approved estimates  
✅ **Days Remaining** - Automatically calculated for deadline tracking  

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

### Error 2: Server Error (500)
```json
{
  "success": false,
  "message": "Error retrieving dashboard: {error_details}",
  "data": null
}
```

**Status:** `500 INTERNAL_SERVER_ERROR`  
**Fix:** Check server logs and contact support

---

## 🎯 Quick Reference

### URL Pattern
```
/api/estimator/dashboard/
```

### Common Use Cases
```
1. Get dashboard overview
   GET /api/estimator/dashboard/

2. Monitor due estimates
   Use: data.due_soon array
   Filter: days_remaining <= 7 (URGENT)

3. Track performance
   Use: data.performance object
   Monitor: approval_rate, rejection_rate

4. Revenue tracking
   Use: data.value_summary
   Sum: approved_value (confirmed revenue)

5. View completed projects
   Use: data.completed_estimates
   Filter: approved estimates for success stories
```

---

## 📊 Status Values

| Status | Description | Color | Count Field |
|--------|-------------|-------|-------------|
| `pending` | Created but not sent | 🔴 Orange | pending |
| `sent` | Sent for approval | 🔵 Blue | sent |
| `approved` | Approved by client | 🟢 Green | approved |
| `rejected` | Rejected by client | 🔴 Red | rejected |

---

## ✨ Dashboard Sections

| Section | Purpose | Items | Sort Order |
|---------|---------|-------|-----------|
| **Overview** | Quick stats by status | 5 counts | - |
| **Value Summary** | Track money by status | 5 values | - |
| **Due Soon** | Urgent deadlines | Up to 10 | By end_date (closest first) |
| **Recent** | Latest activity | Up to 10 | By created_at (newest) |
| **Completed** | Success tracking | All approved | By updated_at (newest) |
| **Performance** | KPIs | 4 metrics | - |

---

Ready to use! 🚀
