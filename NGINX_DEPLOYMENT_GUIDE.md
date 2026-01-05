# NGINX + HTTPS DEPLOYMENT GUIDE

## Overview
This guide covers deploying your Django application with Nginx reverse proxy, HTTPS/SSL support, and Swagger documentation on app.lignaflow.com

## Quick Start

### 1. Generate SSL Certificates
```bash
# On your server, run:
bash setup-ssl.sh
```

### 2. Build and Run with Docker Compose
```bash
# Build all services
docker-compose build

# Start services in background
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Access Your Application
- **Main App**: https://app.lignaflow.com
- **API**: https://app.lignaflow.com/api/
- **Swagger Docs**: https://app.lignaflow.com/swagger/
- **Admin Panel**: https://app.lignaflow.com/admin/

---

## GIT WORKFLOW

### Initial Setup
```bash
# Clone repository
git clone <your-repo-url>
cd eagleeyeau

# Create and switch to development branch
git checkout -b develop
```

### Daily Workflow - Push Changes
```bash
# 1. Check status
git status

# 2. Stage changes
git add .
# Or add specific files
git add nginx/
git add docker-compose.yml

# 3. Commit with descriptive message
git commit -m "feat: Add Nginx reverse proxy with HTTPS support"

# 4. Push to remote
git push origin develop
```

### Pull Latest Changes
```bash
# Fetch latest from remote
git fetch origin

# Pull changes to current branch
git pull origin develop

# If on main branch
git pull origin main
```

### Deploy to Server (Production)
```bash
# 1. SSH into your server
ssh user@server.ip

# 2. Navigate to project directory
cd /path/to/eagleeyeau

# 3. Pull latest code
git pull origin main

# 4. Build and restart services
docker-compose down
docker-compose build
docker-compose up -d

# 5. Check logs
docker-compose logs -f
```

### Useful Git Commands
```bash
# See commit history
git log --oneline

# See branches
git branch -a

# Switch branches
git checkout main
git checkout develop

# Create new feature branch
git checkout -b feature/your-feature-name

# Merge feature to develop
git checkout develop
git merge feature/your-feature-name

# Delete branch
git branch -d feature/your-feature-name
```

---

## HTTPS/SSL Configuration

### For Testing (Self-Signed)
Certificates are auto-generated. Browser will show security warning - this is normal.

### For Production (Let's Encrypt)
```bash
# 1. Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 2. Generate certificate (stop Nginx first)
docker-compose down
sudo certbot certonly --standalone -d app.lignaflow.com

# 3. Copy certificates
mkdir -p ssl
sudo cp /etc/letsencrypt/live/app.lignaflow.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.lignaflow.com/privkey.pem ssl/key.pem
sudo chown $USER:$USER ssl/*

# 4. Restart services
docker-compose up -d

# 5. Auto-renewal setup
sudo certbot renew --dry-run
```

---

## Docker Commands

### Container Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f                 # All logs
docker-compose logs -f web             # Just Django app
docker-compose logs -f nginx           # Just Nginx
docker-compose logs -f db              # Just Database

# Access container shell
docker-compose exec web bash           # Django app
docker-compose exec db psql -U postgres eagleeyeau  # Database
```

### Monitoring
```bash
# Check service status
docker-compose ps

# View resource usage
docker stats

# Health check
curl http://localhost/health
curl https://app.lignaflow.com/health -k
```

---

## Common Issues & Solutions

### Issue: Connection Refused
```bash
# Solution: Check if services are running
docker-compose ps

# Restart services
docker-compose restart
```

### Issue: SSL Certificate Error
```bash
# Solution: Generate new certificates
bash setup-ssl.sh
docker-compose restart nginx
```

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :80
lsof -i :443

# Kill process (if needed)
kill -9 <PID>
```

### Issue: Database Connection Error
```bash
# Check database logs
docker-compose logs db

# Reset database (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

---

## Environment Variables

Update in `docker-compose.yml`:
- `ALLOWED_HOSTS`: Add your domain here
- `DATABASE_URL`: Database connection string
- `DEBUG`: Set to False in production

```yaml
environment:
  - ALLOWED_HOSTS=app.lignaflow.com,localhost
  - DEBUG=False
  - SECRET_KEY=your-secret-key-here
```

---

## Monitoring & Maintenance

### Regular Tasks
- Check Nginx logs: `docker-compose logs nginx`
- Monitor disk space: `docker system df`
- Clean up unused images: `docker system prune`
- Backup database: See database backup guide

### Health Endpoints
- Nginx health: `curl https://app.lignaflow.com/health -k`
- Django status: `curl https://app.lignaflow.com/api/health -k`

---

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify services: `docker-compose ps`
3. Test connectivity: `curl -v https://app.lignaflow.com -k`
