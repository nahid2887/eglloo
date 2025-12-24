# Admin Dashboard Projects - Visual Implementation Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND APPLICATION                         │
│                                                                       │
│  ┌──────────────────────┐    ┌──────────────────────┐               │
│  │  Projects Dashboard  │    │  Project Details     │               │
│  │  - List view         │    │  - Full info         │               │
│  │  - Search            │    │  - Tasks             │               │
│  │  - Filter            │    │  - Estimate          │               │
│  │  - Sort              │    │  - Team assignments  │               │
│  └──────┬───────────────┘    └──────┬───────────────┘               │
│         │                           │                                │
└─────────┼───────────────────────────┼────────────────────────────────┘
          │                           │
          │ HTTP Requests             │ HTTP Requests
          │                           │
          ▼                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DJANGO REST API                             │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │           Authentication & Authorization Layer               │  │
│  │                                                              │  │
│  │  1. Check Authentication (Token validation)                │  │
│  │  2. Check User Role (Admin only)                           │  │
│  │  3. Check Company (Company isolation)                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  admindashboard/views.py                     │  │
│  │                                                              │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ admin_all_projects() - GET /api/admin/projects/     │  │  │
│  │  │                                                      │  │  │
│  │  │ 1. Filter projects by company                      │  │  │
│  │  │ 2. Apply search query (name, client)              │  │  │
│  │  │ 3. Apply status filter                            │  │  │
│  │  │ 4. Apply sorting (field, order)                   │  │  │
│  │  │ 5. Return results with metadata                   │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                           │                                 │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │ admin_project_detail() - GET /api/admin/projects/<id>/  │  │
│  │  │                                                      │  │  │
│  │  │ 1. Get project with company verification           │  │  │
│  │  │ 2. Fetch estimate details                          │  │  │
│  │  │ 3. Get all tasks for project                       │  │  │
│  │  │ 4. Calculate task summary stats                    │  │  │
│  │  │ 5. Return complete data                            │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Serializers (ProjectListSerializer)              │  │
│  │              (ProjectDetailSerializer)                        │  │
│  │              (TaskSerializer)                                │  │
│  │              (EstimateSerializer)                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                 JSON Response Formatter                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        DJANGO DATABASE                              │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Project    │  │    Task      │  │   Estimate   │              │
│  │              │  │              │  │              │              │
│  │ - id         │  │ - id         │  │ - id         │              │
│  │ - name       │  │ - name       │  │ - number     │              │
│  │ - client     │  │ - status     │  │ - total      │              │
│  │ - status     │  │ - priority   │  │ - items      │              │
│  │ - amount     │  │ - project_id │  │ - project_id │              │
│  │ - company    │  │ - assigned   │  │ - company    │              │
│  │ - estimate   │  │ - dates      │  │ - dates      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│         ▲                  ▲                 ▲                       │
│         └──────────────────┴─────────────────┘                      │
│         All filtered by company and creator                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow - Get All Projects

```
User Request with Token
         ▼
┌─────────────────────────────────┐
│ Authentication Check            │
│ - Verify token valid            │
│ - Extract user from token       │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Admin Role Check                │
│ - Verify user.role == 'Admin'   │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Get Company Name                │
│ - From user.company_name        │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Database Query                  │
│ Projects.filter(                │
│   estimate.created_by           │
│   .company_name=company         │
│ )                               │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Apply Search Filter             │
│ if search_query:                │
│   filter by name or client      │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Apply Status Filter             │
│ if status:                      │
│   filter by status              │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Apply Sorting                   │
│ order_by(sort_field,            │
│          sort_order)            │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Serialize Data                  │
│ ProjectListSerializer(          │
│   queryset, many=True           │
│ )                               │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Format Response                 │
│ {                               │
│   success: true,                │
│   message: "...",               │
│   data: {                       │
│     total_count,                │
│     filters_applied,            │
│     results: [...]              │
│   }                             │
│ }                               │
└────────────┬────────────────────┘
             ▼
        JSON Response
        Status: 200
```

---

## Data Flow - Get Project Details

```
User Request: /api/admin/projects/{id}/
         ▼
┌─────────────────────────────────┐
│ Authentication Check            │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Admin Role Check                │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Company Verification            │
│ Get project.estimate            │
│ .created_by.company_name        │
│ Verify == user.company_name     │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Get Project                     │
│ Project.objects.get(            │
│   id=project_id                 │
│ )                               │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Get Related Data                │
│ 1. Estimate                     │
│ 2. Tasks (all)                  │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Calculate Statistics            │
│ Task summary:                   │
│ - Count by status               │
│ - Count by priority             │
│ - Total count                   │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Serialize All Data              │
│ 1. ProjectDetailSerializer      │
│ 2. EstimateSerializer           │
│ 3. TaskSerializer (many)        │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│ Format Response                 │
│ {                               │
│   success: true,                │
│   message: "...",               │
│   data: {                       │
│     project: {...},             │
│     estimate: {...},            │
│     tasks: [...],               │
│     task_summary: {...}         │
│   }                             │
│ }                               │
└────────────┬────────────────────┘
             ▼
        JSON Response
        Status: 200
```

---

## URL Routing Structure

```
Django URL Configuration
  ↓
eagleeyeau/urls.py
  ↓
  path('api/admin/', include('admindashboard.urls'))
  ↓
admindashboard/urls.py
  ↓
  ├─ router.register(r'materials', ...)         → CRUD endpoints
  ├─ router.register(r'estimate-defaults', ...) → CRUD endpoints
  ├─ router.register(r'components', ...)        → CRUD endpoints
  ├─ router.register(r'estimates', ...)         → CRUD endpoints
  │
  ├─ path('comprehensive-list/', get_comprehensive_list)
  │
  ├─ path('dashboard-overview/', admin_dashboard_overview)
  │
  ├─ path('projects/', admin_all_projects)
  │        ↓
  │   GET /api/admin/projects/
  │   - Returns list of projects
  │   - Supports: search, status, sort_by, sort_order
  │
  └─ path('projects/<int:project_id>/', admin_project_detail)
           ↓
       GET /api/admin/projects/1/
       - Returns project with tasks
       - Includes estimate details
       - Shows task summary
```

---

## Database Query Optimization

```
Without Optimization (N+1 Problem):
────────────────────────────────────
Query 1: SELECT * FROM projects WHERE company_id = 1  (1 query)
Loop through each project:
  Query 2: SELECT * FROM estimate WHERE id = project.estimate_id  (N queries)
  Query 3: SELECT * FROM user WHERE id = project.created_by_id    (N queries)
Total: 1 + 2N queries (inefficient!)

With Optimization (select_related):
─────────────────────────────────────
Query 1: SELECT projects.*, estimates.*, users.* 
         FROM projects 
         LEFT JOIN estimates ON ... 
         LEFT JOIN users ON ...
         WHERE company_id = 1  (1 query, all data at once!)

Result: Much faster! Only 1 query regardless of projects count
```

---

## Request/Response Cycle

```
┌─────────────────────────────────────────┐
│ FRONTEND                                │
│                                         │
│ const response = await fetch(           │
│   '/api/admin/projects/?status=...',    │
│   {headers: {                           │
│     'Authorization': 'Bearer token'     │
│   }}                                    │
│ )                                       │
└──────────────┬──────────────────────────┘
               │
               │ HTTP GET Request
               │ Headers: Authorization
               │ Query: ?status=in_progress
               ▼
┌──────────────────────────────────────────┐
│ DJANGO                                   │
│                                          │
│ 1. Parse request                        │
│ 2. Extract token from header            │
│ 3. Validate token                       │
│ 4. Load user from token                 │
│ 5. Check is_authenticated               │
│ 6. Check user.role == 'Admin'          │
│ 7. Get company_name from user           │
│ 8. Execute query:                       │
│    Project.objects.filter(              │
│      estimate__created_by__             │
│        company_name=company             │
│    )                                    │
│ 9. Apply filters & sorting              │
│ 10. Serialize results                   │
│ 11. Format response                     │
│ 12. Return 200 OK                       │
└──────────────┬──────────────────────────┘
               │
               │ JSON Response
               │ {success: true, data: {...}}
               ▼
┌──────────────────────────────────────────┐
│ FRONTEND                                 │
│                                          │
│ const data = response.json()             │
│ displayProjects(data.data.results)       │
│ updateTotal(data.data.total_count)       │
│ updateFilters(data.data.filters_applied) │
└──────────────────────────────────────────┘
```

---

## Security Checks Flow

```
Request Received
       ▼
   Is Token Present?
   ├─ NO → 401 Unauthorized
   └─ YES ▼
         Token Valid?
         ├─ NO → 401 Unauthorized
         └─ YES ▼
               User Exists?
               ├─ NO → 401 Unauthorized
               └─ YES ▼
                     User Active?
                     ├─ NO → 401 Unauthorized
                     └─ YES ▼
                           User Role == 'Admin'?
                           ├─ NO → 403 Forbidden
                           └─ YES ▼
                                 Project Company == User Company?
                                 ├─ NO → 404 Not Found
                                 └─ YES ▼
                                       Return Data
                                       Status: 200
```

---

## Example Frontend Code

```javascript
// Vue.js example
<template>
  <div class="admin-dashboard">
    <!-- Search & Filter Bar -->
    <div class="controls">
      <input 
        v-model="searchQuery" 
        @input="searchProjects"
        placeholder="Search by project name or client..."
      />
      <select v-model="statusFilter" @change="filterProjects">
        <option value="">All Status</option>
        <option value="not_started">Not Started</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
        <option value="on_hold">On Hold</option>
        <option value="cancelled">Cancelled</option>
      </select>
    </div>

    <!-- Projects Table -->
    <table>
      <thead>
        <tr>
          <th @click="sort('id')">ID</th>
          <th @click="sort('project_name')">Project Name</th>
          <th @click="sort('client_name')">Client Name</th>
          <th @click="sort('status')">Status</th>
          <th>Total Amount</th>
          <th @click="sort('creating_date')">Created Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="project in projects" :key="project.id">
          <td>{{ project.id }}</td>
          <td>{{ project.project_name }}</td>
          <td>{{ project.client_name }}</td>
          <td>
            <span :class="'status-' + project.status">
              {{ project.status }}
            </span>
          </td>
          <td>${{ project.total_amount }}</td>
          <td>{{ project.creating_date }}</td>
          <td>
            <button @click="viewDetails(project.id)">View</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Total Count -->
    <div class="total">
      Total Projects: {{ totalCount }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      projects: [],
      searchQuery: '',
      statusFilter: '',
      totalCount: 0,
      sortBy: 'creating_date',
      sortOrder: 'desc'
    }
  },
  methods: {
    async fetchProjects() {
      const params = new URLSearchParams({
        search: this.searchQuery,
        status: this.statusFilter,
        sort_by: this.sortBy,
        sort_order: this.sortOrder
      });
      
      const response = await fetch(
        `/api/admin/projects/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        }
      );
      
      const data = await response.json();
      this.projects = data.data.results;
      this.totalCount = data.data.total_count;
    },
    
    searchProjects() {
      this.fetchProjects();
    },
    
    filterProjects() {
      this.fetchProjects();
    },
    
    sort(field) {
      if (this.sortBy === field) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortBy = field;
        this.sortOrder = 'asc';
      }
      this.fetchProjects();
    },
    
    async viewDetails(projectId) {
      const response = await fetch(
        `/api/admin/projects/${projectId}/`,
        {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        }
      );
      
      const data = await response.json();
      this.$router.push({
        name: 'ProjectDetail',
        params: { id: projectId },
        query: { data: JSON.stringify(data.data) }
      });
    }
  },
  mounted() {
    this.fetchProjects();
  }
}
</script>
```

---

## Summary

✅ Clean architecture with separation of concerns
✅ Optimized database queries
✅ Security at every step
✅ Flexible filtering and searching
✅ Ready for frontend integration
✅ Well-documented and tested
