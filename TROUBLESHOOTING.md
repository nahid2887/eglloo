# 🆘 TROUBLESHOOTING GUIDE

## Quick Diagnostics

### Step 1: Check All Services Are Running
```bash
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND             STATUS              PORTS
eagleeyeau-db      "docker-entrypoint…" Up (healthy)        5432/tcp
eagleeyeau-app    "/bin/bash -c '/app…" Up                  0.0.0.0:8005->8005/tcp
eagleeyeau-nginx  "nginx -g 'daemon…"  Up (healthy)         0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

If any show "Exited":
```bash
docker-compose logs <service-name>
# Example: docker-compose logs web
```

---

## Problem: Services Not Starting

### Error: "docker: command not found"
```bash
# Docker not installed
# Install from: https://www.docker.com/products/docker-desktop
```

### Error: "Port 80 already in use"
```bash
# Find what's using port 80
lsof -i :80
# On Windows
netstat -ano | findstr :80

# Kill the process
kill -9 <PID>
# Or change port in docker-compose.yml
```

### Error: "Cannot connect to Docker daemon"
```bash
# Docker daemon not running
# On Windows: Start Docker Desktop
# On Linux: sudo systemctl start docker

# Verify
docker ps
```

---

## Problem: SSL/TLS Certificates

### Issue: "SSL: CERTIFICATE_VERIFY_FAILED"
```bash
# Expected behavior with self-signed certificates
# Solutions:

# 1. Use -k flag with curl
curl -k https://localhost

# 2. Ignore warning in browser (click "Advanced")

# 3. For production, use Let's Encrypt
bash setup-ssl.sh  # Regenerate certificates
```

### Issue: Certificate expired
```bash
# Check expiration date
openssl x509 -in ssl/cert.pem -text -noout | grep -A 2 "Validity"

# Regenerate if needed
bash setup-ssl.sh

# Restart nginx
docker-compose restart nginx
```

### Issue: Certificate not found
```bash
# Check if files exist
ls -la ssl/

# Should see:
# cert.pem
# key.pem

# If missing, generate
bash setup-ssl.sh
```

---

## Problem: Port Already in Use

### Port 80 (HTTP)
```bash
# Find what's using it
lsof -i :80
netstat -ano | findstr :80

# Kill process
kill -9 <PID>

# Or change in docker-compose.yml
# Change:   "80:80"
# To:       "8080:80"
# Then: docker-compose restart
```

### Port 443 (HTTPS)
```bash
# Find what's using it
lsof -i :443
netstat -ano | findstr :443

# Kill process
kill -9 <PID>
```

### Port 5432 (Database)
```bash
# Check if PostgreSQL is running
lsof -i :5432

# Stop local PostgreSQL
# On Windows: Services → PostgreSQL → Stop
# On Linux: sudo systemctl stop postgresql

# Or change port in docker-compose.yml:
# Change:   "5432:5432"
# To:       "5433:5432"
```

### Port 8005 (Django)
```bash
# Find and kill
lsof -i :8005
kill -9 <PID>
```

---

## Problem: Database Connection Error

### Error: "Connection refused" to PostgreSQL
```bash
# Check database logs
docker-compose logs db

# Common causes:
# 1. Database not started
docker-compose start db

# 2. Database not healthy yet (wait 10 seconds)
docker-compose ps db

# 3. Wrong credentials in docker-compose.yml
# Verify: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

# 4. Test connection
docker-compose exec db psql -U postgres eagleeyeau
# Type: \q to exit
```

### Error: "FATAL: database "eagleeyeau" does not exist"
```bash
# Database wasn't created. Solutions:

# Option 1: Reset everything (deletes data!)
docker-compose down -v
docker-compose up -d
docker-compose logs web  # Check migrations run

# Option 2: Create database manually
docker-compose exec db psql -U postgres
# In psql:
CREATE DATABASE eagleeyeau;
\q
```

### Error: "relation \"admindashboard_something\" does not exist"
```bash
# Migrations haven't run. Solutions:

# Option 1: Run migrations manually
docker-compose exec web python manage.py migrate

# Option 2: Check if migrations are in migrations folder
ls -la eagleeyeau/admindashboard/migrations/

# Option 3: Re-create migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## Problem: Django App Issues

### Error: "ModuleNotFoundError"
```bash
# Missing Python package. Solutions:

# Option 1: Install via requirements.txt
docker-compose exec web pip install -r requirements.txt

# Option 2: Add to requirements.txt and rebuild
# Edit requirements.txt, add package
docker-compose build
docker-compose up -d web
```

### Error: Django page blank or 500 error
```bash
# Check logs
docker-compose logs web

# Common causes:
# 1. Database error (check above)
# 2. Missing migrations (run: python manage.py migrate)
# 3. Missing static files (run: python manage.py collectstatic)
# 4. Wrong ALLOWED_HOSTS (update in docker-compose.yml)
```

### Error: "Invalid HTTP_HOST header"
```bash
# Update ALLOWED_HOSTS in docker-compose.yml:

# For localhost:
- ALLOWED_HOSTS=localhost,127.0.0.1

# For production:
- ALLOWED_HOSTS=app.lignaflow.com

# Then restart:
docker-compose restart web
```

### Static files not loading (CSS/JS 404)
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check if folder exists
ls -la eagleeyeau/staticfiles/

# Restart nginx
docker-compose restart nginx

# Clear browser cache (Ctrl+Shift+Delete)
```

---

## Problem: Nginx Issues

### Error: "Connection refused" at localhost
```bash
# Check if nginx running
docker-compose ps nginx

# If not running, check logs
docker-compose logs nginx

# Try restart
docker-compose restart nginx

# Verify port 80 available
lsof -i :80
```

### Error: "502 Bad Gateway"
```bash
# Nginx can't reach Django app. Solutions:

# 1. Check web service running
docker-compose ps web

# 2. Verify network configuration
docker network ls
docker network inspect eagleeyeau_eagleeyeau-network

# 3. Check logs
docker-compose logs nginx
docker-compose logs web

# 4. Restart both
docker-compose restart nginx web

# 5. Verify web is responding
docker-compose exec web python manage.py shell -c "print('OK')"
```

### Error: "403 Forbidden" on /swagger/
```bash
# Check Swagger configuration in Django

# 1. Verify Swagger package installed
docker-compose exec web pip list | grep swagger

# 2. Check Django settings for Swagger
docker-compose exec web grep -r "swagger" eagleeyeau/eagleeyeau/settings.py

# 3. Restart web service
docker-compose restart web

# 4. Clear cache
docker-compose exec web python manage.py clear_cache
```

### Error: "301 redirect loop"
```bash
# Nginx is redirecting HTTP→HTTPS infinitely

# 1. Check nginx.conf
cat nginx/nginx.conf | grep -A 5 "redirect"

# 2. Verify HTTPS working
curl -k https://localhost

# 3. If HTTPS works but loop continues:
docker-compose restart nginx
# Wait 10 seconds
curl https://localhost
```

---

## Problem: Git Issues

### Error: "fatal: not a git repository"
```bash
# Not in a git project directory

# Initialize git
git init
git add .
git commit -m "Initial commit"
```

### Error: "Authentication failed" when pushing
```bash
# Generate personal access token
# 1. Go to GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token with 'repo' scope
# 3. Use as password when prompted

# Or setup SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
# Add public key to GitHub
cat ~/.ssh/id_ed25519.pub  # Copy this
# GitHub → Settings → SSH keys → Add key
```

### Error: "merge conflict"
```bash
# When pulling code with conflicts

# 1. See conflicts
git status

# 2. Edit conflicted files (remove <<<, ===, >>>)
# Or use merge tool
git mergetool

# 3. Mark as resolved
git add <resolved-file>

# 4. Complete merge
git commit -m "Resolve conflicts"
```

### Error: "Permission denied (publickey)"
```bash
# SSH key issue

# 1. Generate SSH key
ssh-keygen -t ed25519

# 2. Add to GitHub
# GitHub → Settings → SSH keys

# 3. Test connection
ssh -T git@github.com

# 4. Use SSH URL for clone/remote
git remote add origin git@github.com:username/eagleeyeau.git
```

---

## Problem: Deployment to Server

### Error: "connection timeout" to server
```bash
# Can't reach server

# 1. Check server IP is correct
ping your-server-ip

# 2. Check SSH port open
ssh -p 22 user@server-ip
# If fails, server might be down

# 3. Check firewall
sudo ufw status
sudo ufw allow 22  # SSH
sudo ufw allow 80  # HTTP
sudo ufw allow 443 # HTTPS
```

### Error: "git: command not found" on server
```bash
# Git not installed on server

sudo apt-get update
sudo apt-get install git
```

### Error: "docker: command not found" on server
```bash
# Docker not installed

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/latest/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Error: "port 80/443 not accessible" from internet
```bash
# Firewall blocking traffic

# 1. Check firewall
sudo ufw status

# 2. Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 3. Check cloud provider firewall
# AWS/Azure/DigitalOcean → Security Groups → Inbound Rules
# Allow ports 80 and 443

# 4. Test externally
curl https://app.lignaflow.com
```

### Error: "DNS not resolving" for app.lignaflow.com
```bash
# DNS not configured yet

# 1. Wait 5-30 minutes after setting DNS record

# 2. Check DNS propagation
nslookup app.lignaflow.com
dig app.lignaflow.com

# 3. Verify DNS record in registrar
# Go to domain registrar
# Check A record for 'app' points to server IP

# 4. Test after propagation
curl https://app.lignaflow.com/health
```

---

## Common Solutions

### "Nothing works, start fresh"
```bash
# Complete reset (deletes all data!)
docker-compose down -v
docker system prune -af
docker volume prune -f

# Start over
bash setup-ssl.sh
docker-compose build
docker-compose up -d

# Check
docker-compose ps
docker-compose logs -f
```

### "Want to clear all data but keep services"
```bash
# Delete database volume only
docker-compose down
docker volume rm eagleeyeau_postgres_data

# Restart
docker-compose up -d
```

### "Services running but app not responding"
```bash
# Check all logs at once
docker-compose logs

# Check specific service in detail
docker-compose logs --tail=100 web

# Real-time monitoring
docker-compose logs -f

# Exit with: Ctrl+C
```

---

## Health Check Commands

### System Health
```bash
# Services running?
docker-compose ps

# Resources used?
docker stats

# Network working?
docker-compose exec web ping db

# Database responsive?
docker-compose exec db psql -U postgres -c "SELECT NOW();"

# Ports listening?
netstat -tuln | grep -E ":(80|443|5432|8005)"
```

### Application Health
```bash
# Django health check
curl -k https://localhost/health

# Nginx responding
curl -k -v https://localhost

# Swagger loading
curl -k https://localhost/swagger/ | head -20

# API working
curl -k https://localhost/api/

# Database accessible
docker-compose exec web python manage.py dbshell -c "SELECT 1;"
```

### Security Check
```bash
# SSL certificate valid?
openssl s_client -connect localhost:443 | head -20

# Headers present?
curl -k -I https://localhost | grep -E "Strict|X-Frame"

# No errors in logs?
docker-compose logs | grep -i error
```

---

## When All Else Fails

### 1. Check Documentation
- [NGINX_SETUP_README.md](NGINX_SETUP_README.md)
- [NGINX_DEPLOYMENT_GUIDE.md](NGINX_DEPLOYMENT_GUIDE.md)
- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)

### 2. Review Logs Thoroughly
```bash
docker-compose logs web 2>&1 | tail -200
docker-compose logs nginx 2>&1 | tail -200
docker-compose logs db 2>&1 | tail -200
```

### 3. Search Error Message
Google the exact error message in quotes

### 4. Test Each Component Separately
```bash
# Test Nginx
docker-compose exec nginx nginx -t

# Test Django
docker-compose exec web python manage.py check

# Test Database
docker-compose exec db pg_isready
```

### 5. Compare with Working State
```bash
# Save current state
docker-compose ps > status.txt
docker-compose logs > logs.txt

# Compare with git history
git log --oneline
git diff HEAD
```

---

## Performance Issues

### Slow Response Time
```bash
# Check resource usage
docker stats

# If high CPU/Memory:
docker-compose logs web  # Check for errors
docker system prune  # Clean up

# Restart services
docker-compose restart
```

### High Disk Usage
```bash
# Check Docker disk usage
docker system df

# Clean up unused images/volumes
docker system prune -a
docker volume prune

# Check database size
docker-compose exec db psql -U postgres eagleeyeau -c "SELECT pg_size_pretty(pg_database_size('eagleeyeau'));"
```

### Slow Database Queries
```bash
# Enable Django debug logging
# Add to settings.py:
# LOGGING = { 'version': 1, 'handlers': {...}, 'loggers': {'django.db.backends': {...}}}

# Or use Django Query Inspector
pip install django-debug-toolbar

# Check PostgreSQL logs
docker-compose logs db | grep slow
```

---

## Security Checklist

- [ ] HTTPS enabled (curl -k https://localhost)
- [ ] Security headers present (curl -I https://localhost)
- [ ] SSL certificate valid (not self-signed in production)
- [ ] Database credentials not in git (.env added to .gitignore)
- [ ] ALLOWED_HOSTS configured correctly
- [ ] DEBUG=False in production
- [ ] Secret keys not exposed
- [ ] Regular backups scheduled
- [ ] Logs monitored for errors
- [ ] Updates applied regularly

---

**Still stuck? Check the full guides or ask in GitHub issues.**
