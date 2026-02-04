# 🐳 Docker Run & Deployment Guide

This guide covers how to run the **EagleEyeAU** application using Docker and Docker Compose, including the updated **Employee Assigned Tasks API** with pagination and enhanced search.

---

## 📋 Prerequisites

- Docker installed (`docker --version`)
- Docker Compose installed (`docker-compose --version`)
- SSL certificates in `./certs/` directory (for HTTPS)
  - `fullchain.pem` - SSL certificate
  - `privkey.pem` - SSL private key
- `.env` file configured (optional, uses defaults if not present)

---

## 🚀 Quick Start

### 1. **Build and Start Services**

```bash
# Navigate to project directory
cd /path/to/eagleeyeau

# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

**Expected Output:**
```
CONTAINER ID  IMAGE                    STATUS
abc123...     eagleeyeau-db           Up 2 minutes
def456...     eagleeyeau-app          Up 1 minute
ghi789...     eagleeyeau-nginx        Up 1 minute
```

### 2. **Access Application**

| Service | URL | Port |
|---------|-----|------|
| **Web API** | `http://localhost:8005` | 8005 |
| **Nginx (HTTP)** | `http://localhost` | 80 |
| **Nginx (HTTPS)** | `https://localhost` | 443 |
| **Swagger Docs** | `http://localhost/swagger/` | 80 |
| **API Base** | `http://localhost/api/` | 80 |
| **Database** | `localhost:5432` | 5432 |

---

## 🔧 Service Configuration

### **Database (PostgreSQL)**
```yaml
Service:  db
Image:    postgres:15
Port:     5432
Database: eagleeyeau
User:     postgres
Password: postgres123
Volume:   postgres_data:/var/lib/postgresql/data
```

### **Web Application (Django)**
```yaml
Service:      web
Image:        eagleeyeau-app
Port:         8005
Framework:    Django 5.2
Database:     PostgreSQL
Environment:  Development
Volume:       Source code mounted for development
```

### **Nginx (Reverse Proxy)**
```yaml
Service:      nginx
Image:        eagleeyeau-nginx
Ports:        80 (HTTP), 443 (HTTPS)
SSL:          Enabled (certificates required)
Proxy:        Routes to Django web service
Static Files: Serves static and media files
```

---

## 📝 Docker Compose Commands

### **Start Services**
```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d

# Start specific service
docker-compose up -d web
```

### **Stop Services**
```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop web

# Remove all containers and volumes
docker-compose down
docker-compose down -v  # Remove volumes too
```

### **View Logs**
```bash
# View all logs
docker-compose logs

# Follow web service logs
docker-compose logs -f web

# View nginx logs
docker-compose logs -f nginx

# View database logs
docker-compose logs -f db

# Show last 50 lines
docker-compose logs --tail=50 web
```

### **Execute Commands in Container**
```bash
# Run Django migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Install package
docker-compose exec web pip install package_name

# Run shell
docker-compose exec web python manage.py shell

# Check database connection
docker-compose exec web python manage.py dbshell
```

### **Rebuild Services**
```bash
# Rebuild images after code changes
docker-compose build

# Rebuild and start
docker-compose up -d --build

# Rebuild specific service
docker-compose build web
```

---

## 🔌 Network Configuration

### **Docker Network: `eagleeyeau-network`**

All services communicate via a custom bridge network:

```
                    ┌─────────────────────────────────┐
                    │      eagleeyeau-network         │
                    │  (Custom Bridge Network)        │
                    ├─────────────────────────────────┤
                    │                                 │
    ┌───────────────┤ ┌──────────────┐               │
    │               │ │  nginx       │               │
    │               │ │  :80, :443   │               │
    │               │ └──────────────┘               │
    │               │         ↓                      │
    │               │ ┌──────────────┐               │
    │               │ │  web         │               │
    │               │ │  :8005       │               │
    │               │ └──────────────┘               │
    │               │         ↓                      │
    │               │ ┌──────────────┐               │
    │               │ │  db          │               │
    │               │ │  :5432       │               │
    │               │ └──────────────┘               │
    │               │                                 │
    └───────────────┤ Host Machine Access            │
                    │ (via exposed ports)            │
                    └─────────────────────────────────┘
```

### **Service Discovery**
- Services can communicate using service name as hostname
- Example: `postgres://postgres:postgres123@db:5432/eagleeyeau`

---

## 🆕 Employee Assigned Tasks API - Docker Integration

### **Access the API**

```bash
# Get Employee Assigned Tasks (with Pagination)
curl -X GET "http://localhost/api/employee/assigned-tasks/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With pagination
curl -X GET "http://localhost/api/employee/assigned-tasks/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With search and pagination
curl -X GET "http://localhost/api/employee/assigned-tasks/?search=kitchen&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# With filters, search, and pagination
curl -X GET "http://localhost/api/employee/assigned-tasks/?status=in_progress&priority=high&search=kitchen&page=1&page_size=15" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **API Features (in Docker)**

| Feature | Status | Query Parameter |
|---------|--------|-----------------|
| Pagination | ✅ | `?page=1&page_size=10` |
| Search (Enhanced) | ✅ | `?search=keyword` |
| Filter by Status | ✅ | `?status=in_progress` |
| Filter by Priority | ✅ | `?priority=high` |
| Filter by Project | ✅ | `?project_id=1` |
| Combine Filters | ✅ | `?status=...&priority=...&page=...` |

### **Response with Pagination**

```json
{
  "success": true,
  "message": "Retrieved 10 assigned tasks for employee...",
  "data": {
    "employee": {...},
    "statistics": {...},
    "pagination": {
      "count": 25,
      "page_size": 10,
      "total_pages": 3,
      "current_page": 1,
      "next": "http://localhost/api/employee/assigned-tasks/?page=2",
      "previous": null
    },
    "tasks": [...]
  }
}
```

---

## 📊 Database Management

### **Access Database**
```bash
# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d eagleeyeau

# List tables
\dt

# View data
SELECT * FROM project_manager_task LIMIT 5;

# Exit
\q
```

### **Backup Database**
```bash
# Backup to file
docker-compose exec db pg_dump -U postgres eagleeyeau > backup.sql

# Restore from file
cat backup.sql | docker-compose exec -T db psql -U postgres -d eagleeyeau
```

### **Reset Database**
```bash
# WARNING: This deletes all data!
docker-compose exec web python manage.py flush
docker-compose exec web python manage.py migrate
```

---

## 🔒 SSL/HTTPS Configuration

### **Prerequisites**
1. SSL certificates generated using Certbot:
   ```bash
   certbot certonly --standalone -d app.lignaflow.com
   ```

2. Certificates placed in `./certs/`:
   - `fullchain.pem` (copy from `/etc/letsencrypt/live/app.lignaflow.com/`)
   - `privkey.pem` (copy from `/etc/letsencrypt/live/app.lignaflow.com/`)

### **Testing HTTPS**
```bash
# Test with self-signed certificate (ignore warnings)
curl -k https://localhost/api/employee/assigned-tasks/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Test Swagger UI
curl -k https://localhost/swagger/ | head -100
```

---

## 🐛 Troubleshooting

### **Issue: "Connection refused" when accessing services**

**Solution:**
```bash
# Check if services are running
docker-compose ps

# Check service logs
docker-compose logs web

# Verify network
docker network ls
docker network inspect eagleeyeau_eagleeyeau-network
```

### **Issue: Database connection error**

**Solution:**
```bash
# Check database status
docker-compose logs db

# Test database connection
docker-compose exec web python manage.py dbshell

# Verify database is running
docker-compose exec db psql -U postgres -c "SELECT version();"
```

### **Issue: 502 Bad Gateway from Nginx**

**Solution:**
```bash
# Check web service is running and healthy
docker-compose logs web

# Verify services are on the same network
docker-compose exec nginx ping web

# Check Nginx configuration
docker-compose logs nginx
```

### **Issue: Swagger/API docs not loading**

**Solution:**
```bash
# Clear cache and rebuild
docker-compose down -v
docker-compose up -d --build

# Verify Django static files
docker-compose exec web python manage.py collectstatic --noinput

# Check Swagger configuration
docker-compose exec web grep -r "swagger" eagleeyeau/settings.py
```

### **Issue: Pagination not working**

**Solution:**
```bash
# Verify Django REST Framework settings
docker-compose exec web python -c \
  "from django.conf import settings; print(settings.REST_FRAMEWORK['DEFAULT_PAGINATION_CLASS'])"

# Check Python packages
docker-compose exec web pip list | grep djangorestframework
```

---

## 📈 Performance Tips

### **Database Optimization**
```bash
# Create indexes
docker-compose exec web python manage.py sqlsequencereset app_name | \
  docker-compose exec -T db psql -U postgres eagleeyeau
```

### **Reduce Docker Image Size**
```bash
# Build without cache
docker-compose build --no-cache

# Use .dockerignore to exclude files
# .dockerignore:
# __pycache__
# *.pyc
# .git
# .env
```

### **Enable Docker Compose Caching**
```bash
# Use BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker-compose build
```

---

## 🚢 Production Deployment

### **Update docker-compose for production:**

```yaml
version: '3.8'

services:
  web:
    build: .
    restart: always
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=app.lignaflow.com,www.app.lignaflow.com
    healthcheck:
      test: curl -f http://localhost:8005/api/health/ || exit 1
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    restart: always
    ports:
      - "80:80"
      - "443:443"
    environment:
      - SERVER_NAME=app.lignaflow.com
```

### **Start in Production**
```bash
# Build and start
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitor services
docker-compose logs -f web

# Scale services
docker-compose up -d --scale worker=3
```

---

## 📚 Related Documentation

- **Employee API Details**: See `README_EMPLOYEE_API.md`
- **Testing Guide**: See `EMPLOYEE_TASKS_TESTING.md`
- **Swagger Docs**: Access at `http://localhost/swagger/`
- **Deployment**: See `DEPLOYMENT_CHECKLIST.md`

---

## ✅ Verification Checklist

- [ ] Docker and Docker Compose installed
- [ ] SSL certificates in `./certs/` (if using HTTPS)
- [ ] Services started: `docker-compose up -d`
- [ ] All services healthy: `docker-compose ps`
- [ ] Web API accessible: `http://localhost:8005`
- [ ] Nginx proxy working: `http://localhost/api/`
- [ ] Swagger docs loaded: `http://localhost/swagger/`
- [ ] Employee API works: `http://localhost/api/employee/assigned-tasks/`
- [ ] Pagination working: `?page=1&page_size=10`
- [ ] Search working: `?search=keyword`
- [ ] Database connected: `docker-compose exec web python manage.py dbshell`

---

## 🎯 Quick Reference

```bash
# Start all services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f web

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Remove all (including volumes)
docker-compose down -v

# Execute command in container
docker-compose exec web <command>

# Access shell
docker-compose exec web bash
```

---

**Documentation Updated:** February 4, 2026
**API Version:** 1.0 with Pagination & Enhanced Search
**Docker Status:** ✅ Production Ready

