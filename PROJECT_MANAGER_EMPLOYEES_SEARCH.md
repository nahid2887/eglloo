# Project Manager Employee Search API

## Endpoint
```
GET /api/project-manager/employees/
```

## Authentication
- **Required:** Yes (JWT Bearer token)
- **Role:** Project Manager or Admin only

## Description
Retrieve all employees from the same company as the logged-in Project Manager, with optional search functionality.

---

## Query Parameters

### `q` (String - Optional)
Single search box that searches across:
- `first_name` (case-insensitive, partial match)
- `last_name` (case-insensitive, partial match)
- `email` (case-insensitive, partial match)
- `username` (case-insensitive, partial match)

**Examples:**
```bash
GET /api/project-manager/employees/?q=john
GET /api/project-manager/employees/?q=smith
GET /api/project-manager/employees/?q=john.doe@example.com
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Retrieved X employees from Company Name",
  "data": {
    "company": "Company Name",
    "total_employees": X,
    "filters_applied": {
      "q": "search_term"
    },
    "employees": [
      {
        "id": 1,
        "username": "john.doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "company_name": "Acme Corp",
        "role": "Employee",
        "profile_image": "http://example.com/image.jpg",
        "country": "USA",
        "is_email_verified": true,
        "created_at": "2025-11-08T10:30:00Z"
      },
      // ... more employees
    ]
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

---

## Usage Examples

### Example 1: Get All Employees (No Search)
```bash
curl -X GET "http://localhost:8002/api/project-manager/employees/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 5 employees from Acme Corp",
  "data": {
    "company": "Acme Corp",
    "total_employees": 5,
    "filters_applied": {
      "q": null
    },
    "employees": [...]
  }
}
```

### Example 2: Search by First Name
```bash
curl -X GET "http://localhost:8002/api/project-manager/employees/?q=john" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 2 employees from Acme Corp",
  "data": {
    "company": "Acme Corp",
    "total_employees": 2,
    "filters_applied": {
      "q": "john"
    },
    "employees": [
      {
        "id": 1,
        "username": "john.doe",
        "email": "john.doe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "company_name": "Acme Corp",
        "role": "Employee",
        "profile_image": null,
        "country": "USA",
        "is_email_verified": true,
        "created_at": "2025-11-08T10:30:00Z"
      },
      {
        "id": 3,
        "username": "john.smith",
        "email": "john.smith@example.com",
        "first_name": "John",
        "last_name": "Smith",
        "full_name": "John Smith",
        "company_name": "Acme Corp",
        "role": "Employee",
        "profile_image": null,
        "country": "USA",
        "is_email_verified": false,
        "created_at": "2025-11-08T11:00:00Z"
      }
    ]
  }
}
```

### Example 3: Search by Last Name
```bash
curl -X GET "http://localhost:8002/api/project-manager/employees/?q=smith" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Example 4: Search by Email
```bash
curl -X GET "http://localhost:8002/api/project-manager/employees/?q=jane@example.com" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

### Example 5: Search by Username
```bash
curl -X GET "http://localhost:8002/api/project-manager/employees/?q=jane.doe" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

---

## Employee Data Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique user identifier |
| username | string | Unique username |
| email | string | User email address |
| first_name | string | Employee's first name |
| last_name | string | Employee's last name |
| full_name | string | Computed (first_name + last_name) |
| company_name | string | Company name |
| role | string | User role (always "Employee") |
| profile_image | string or null | URL to profile image |
| country | string or null | Country of residence |
| is_email_verified | boolean | Email verification status |
| created_at | datetime | Account creation timestamp |

---

## Frontend Integration

### JavaScript/Fetch
```javascript
async function searchEmployees(searchTerm = '') {
  const params = new URLSearchParams();
  if (searchTerm) params.append('q', searchTerm);
  
  const response = await fetch(`/api/project-manager/employees/?${params}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
  
  return await response.json();
}

// Usage
const allEmployees = await searchEmployees();
const johnEmployees = await searchEmployees('john');
const emailResults = await searchEmployees('john.doe@example.com');
```

### React Component
```jsx
import { useState, useEffect } from 'react';

function EmployeeSearch() {
  const [query, setQuery] = useState('');
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [company, setCompany] = useState('');

  useEffect(() => {
    // Load all employees on component mount
    handleSearch();
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    
    try {
      const params = new URLSearchParams();
      if (query) params.append('q', query);
      
      const response = await fetch(`/api/project-manager/employees/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      const data = await response.json();
      setEmployees(data.data.employees);
      setCompany(data.data.company);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="employee-search">
      <h2>Team Members - {company}</h2>
      
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Search by name, email, or username..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="search-input"
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>
      
      <div className="results">
        <p>Found: {employees.length} employees</p>
        <div className="employee-grid">
          {employees.map(emp => (
            <div key={emp.id} className="employee-card">
              {emp.profile_image && (
                <img src={emp.profile_image} alt={emp.full_name} />
              )}
              <h3>{emp.full_name}</h3>
              <p>{emp.email}</p>
              <p className="username">@{emp.username}</p>
              {emp.is_email_verified && <span className="verified">✓ Verified</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default EmployeeSearch;
```

### Vue.js Component
```vue
<template>
  <div class="employee-search">
    <h2>Team Members - {{ company }}</h2>
    
    <form @submit.prevent="handleSearch">
      <input
        v-model="query"
        type="text"
        placeholder="Search by name, email, or username..."
        class="search-input"
      />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Searching...' : 'Search' }}
      </button>
    </form>
    
    <div class="results">
      <p>Found: {{ employees.length }} employees</p>
      <div class="employee-grid">
        <div v-for="emp in employees" :key="emp.id" class="employee-card">
          <img v-if="emp.profile_image" :src="emp.profile_image" :alt="emp.full_name" />
          <h3>{{ emp.full_name }}</h3>
          <p>{{ emp.email }}</p>
          <p class="username">@{{ emp.username }}</p>
          <span v-if="emp.is_email_verified" class="verified">✓ Verified</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      query: '',
      employees: [],
      loading: false,
      company: ''
    };
  },
  mounted() {
    this.handleSearch();
  },
  methods: {
    async handleSearch() {
      this.loading = true;
      try {
        const params = new URLSearchParams();
        if (this.query) params.append('q', this.query);
        
        const response = await fetch(`/api/project-manager/employees/?${params}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        this.employees = data.data.employees;
        this.company = data.data.company;
      } catch (error) {
        console.error('Search error:', error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
```

---

## Search Behavior

| Search Field | Type | Match Type | Example |
|--------------|------|-----------|---------|
| first_name | String | Partial, Case-insensitive | "joh" matches "John" |
| last_name | String | Partial, Case-insensitive | "doe" matches "Doe" |
| email | String | Partial, Case-insensitive | "john.d" matches "john.doe@example.com" |
| username | String | Partial, Case-insensitive | "john" matches "john.doe" |

---

## Response Structure

```json
{
  "success": true/false,
  "message": "Description",
  "data": {
    "company": "Company Name",
    "total_employees": X,
    "filters_applied": {
      "q": "search_term or null"
    },
    "employees": [...]
  }
}
```

---

## Error Cases

### User has no company assigned
```json
{
  "success": false,
  "message": "Your user account doesn't have a company assigned",
  "data": null
}
```

### Server error
```json
{
  "success": false,
  "message": "Error retrieving employees: error details",
  "data": null
}
```

---

## Access Control

Only **Project Manager** and **Admin** users can access this endpoint. Other roles will receive a 403 Forbidden response.

---

## Notes

- All searches are **optional** — omit `q` to get all employees
- Searches are **case-insensitive**
- Searches use **partial matching** (substring search)
- Results are sorted by first_name, then last_name
- Only shows employees from the same company as the logged-in Project Manager
- Response includes `total_employees` for tracking
- `filters_applied` shows which filters were used

Enjoy employee search! 🚀
