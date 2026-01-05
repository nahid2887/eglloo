# 🚀 EagleEyeau - Complete Nginx + HTTPS + Git Setup

## What Was Created

This setup provides:
- ✅ **Nginx Reverse Proxy** - Route traffic to your Django app
- ✅ **HTTPS/SSL Support** - Secure encryption for app.lignaflow.com
- ✅ **Swagger Documentation** - API docs at `/swagger/`
- ✅ **Docker Integration** - Easy deployment and scaling
- ✅ **Git Workflow** - Version control and team collaboration

---

## 📁 New Files Created

```
nginx/
  ├── nginx.conf         # Reverse proxy configuration
  └── Dockerfile         # Build Nginx Docker image
  
ssl/                     # SSL certificates (will be generated)
  ├── cert.pem
  └── key.pem

setup-ssl.sh            # Script to generate SSL certificates
git-helper.sh           # Helper script for git commands

NGINX_DEPLOYMENT_GUIDE.md      # Full documentation
NGINX_QUICK_REFERENCE.md       # Quick command reference
DEPLOYMENT_CHECKLIST.md        # Step-by-step deployment guide
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Generate SSL Certificates
```bash
bash setup-ssl.sh
```

### Step 2: Build and Start Services
```bash
docker-compose build
docker-compose up -d
```

### Step 3: Verify It's Working
```bash
curl -k https://localhost/health
```

Expected response: `healthy`

---

## 🌐 Access Points

Once running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Main App** | https://localhost | Django app/admin |
| **API** | https://localhost/api/ | REST API |
| **Swagger** | https://localhost/swagger/ | API Documentation |
| **Admin** | https://localhost/admin/ | Django Admin |
| **Health** | https://localhost/health | Status check |

For **production** (app.lignaflow.com), replace `localhost` with `app.lignaflow.com`

---

## 📊 Architecture

```
┌─────────────────┐
│  Browser/Client │
└────────┬────────┘
         │ HTTPS (443)
         │ HTTP (80)
         ▼
    ┌─────────┐
    │  Nginx  │
    │ Reverse │
    │  Proxy  │
    └────┬────┘
         │ Port 8005
         ▼
    ┌─────────────────┐
    │  Django App     │
    │ (web service)   │
    └────┬────────────┘
         │
         ▼
    ┌─────────────────┐
    │  PostgreSQL     │
    │  Database       │
    └─────────────────┘
```

---

## 🐳 Docker Services

**docker-compose.yml** defines 3 services:

### 1. **db** (PostgreSQL Database)
- Container: `eagleeyeau-db`
- Port: 5432
- Status: Automatically checks health

### 2. **web** (Django Application)
- Container: `eagleeyeau-app`
- Port: 8005
- Handles: API, Admin, Logic

### 3. **nginx** (Web Server)
- Container: `eagleeyeau-nginx`
- Ports: 80 (HTTP), 443 (HTTPS)
- Routes traffic to Django app

---

## 🔐 SSL/HTTPS Configuration

### Development (Self-Signed)
Self-signed certificates are auto-generated:
- Valid for 365 days
- Browser will show warning - **normal for testing**
- Use `-k` flag with curl to ignore: `curl -k https://localhost`

### Production (Let's Encrypt)
For real HTTPS on app.lignaflow.com:
```bash
# 1. On your server:
sudo certbot certonly --standalone -d app.lignaflow.com

# 2. Copy certificates:
sudo cp /etc/letsencrypt/live/app.lignaflow.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.lignaflow.com/privkey.pem ssl/key.pem

# 3. Restart Nginx:
docker-compose restart nginx
```

---

## 📝 GIT - Version Control & Deployment

### Initial Setup
```bash
# Configure git (first time)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Initialize repository
git init
git add .
git commit -m "Initial commit: Nginx + HTTPS setup"
```

### Push Your Code to GitHub
```bash
# 1. Create repository on GitHub.com

# 2. Add remote
git remote add origin https://github.com/YOUR-USERNAME/eagleeyeau.git

# 3. Push to GitHub
git branch -M main
git push -u origin main

# 4. Create develop branch
git checkout -b develop
git push -u origin develop
```

### Daily Workflow - Push Changes
```bash
# Check what changed
git status

# Stage all changes
git add .

# Commit with message
git commit -m "feat: description of what you changed"

# Push to remote
git push origin develop
```

### Pull Latest Changes
```bash
# Get latest code from team
git pull origin develop
```

### Using Git Helper Script
```bash
# Interactive helper for common commands
bash git-helper.sh

# Examples:
bash git-helper.sh setup              # Initial setup
bash git-helper.sh status             # Show status
bash git-helper.sh push "Your message" # Commit & push
bash git-helper.sh pull               # Pull latest
bash git-helper.sh feature "auth"     # Create feature branch
```

---

## 🚢 Deployment to Server

### Deploy to Production Server

```bash
# 1. SSH into server
ssh user@your-server-ip

# 2. Clone project
cd /opt
git clone https://github.com/YOUR-USERNAME/eagleeyeau.git
cd eagleeyeau

# 3. Generate SSL certificates
bash setup-ssl.sh

# 4. Start services
docker-compose build
docker-compose up -d

# 5. Verify
docker-compose ps
docker-compose logs -f

# 6. Update DNS to point app.lignaflow.com to server IP
```

### Update Deployment
```bash
# When code changes on GitHub:

# 1. Pull latest code
git pull origin main

# 2. Rebuild and restart
docker-compose build
docker-compose restart

# 3. Check logs
docker-compose logs -f
```

---

## 🔧 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f              # All services
docker-compose logs -f nginx        # Just Nginx
docker-compose logs -f web          # Just Django
docker-compose logs -f db           # Just Database

# Access container shell
docker-compose exec web bash        # Django container
docker-compose exec db psql -U postgres  # Database

# View service status
docker-compose ps

# Restart services
docker-compose restart
```

---

## 🧪 Testing

### Test Locally
```bash
# Check Nginx is running
curl -v http://localhost
# Should redirect to HTTPS

# Test HTTPS
curl -k https://localhost/health
# Should return: "healthy"

# Test API
curl -k https://localhost/api/
# Should return: API response

# Test Swagger
curl -k https://localhost/swagger/
# Should return: HTML page
```

### Test on Production
```bash
# After deploying to server
curl -k https://app.lignaflow.com/health

# Open in browser
https://app.lignaflow.com
https://app.lignaflow.com/swagger/
```

---

## 📋 Nginx Configuration Details

**File**: `nginx/nginx.conf`

**Routes configured**:
- `/api/` → Django API
- `/admin/` → Django Admin
- `/swagger/` → Swagger Documentation
- `/static/` → Static files (CSS, JS, images)
- `/media/` → User uploaded files
- `/health` → Health check endpoint

**Features**:
- Automatic HTTP → HTTPS redirect
- GZIP compression
- Security headers (HSTS, X-Frame-Options, etc.)
- Load balancing ready
- WebSocket support (for real-time features)

---

## 🆘 Troubleshooting

### Services not starting?
```bash
docker-compose logs
# Check the error messages
docker-compose down
docker-compose up -d
```

### Port already in use?
```bash
# Find process using port
lsof -i :80
lsof -i :443
# Kill if needed
kill -9 <PID>
```

### SSL Certificate error?
```bash
# Regenerate certificates
bash setup-ssl.sh
docker-compose restart nginx
```

### Can't connect to app.lignaflow.com?
```bash
# Check DNS is configured
nslookup app.lignaflow.com

# Check firewall allows ports
sudo ufw allow 80
sudo ufw allow 443

# Check service is running
docker-compose ps nginx
```

### Database issues?
```bash
# Check database logs
docker-compose logs db

# Access database
docker-compose exec db psql -U postgres eagleeyeau
```

---

## 📚 Complete Guides

1. **[NGINX_DEPLOYMENT_GUIDE.md](NGINX_DEPLOYMENT_GUIDE.md)** - Full deployment guide
2. **[NGINX_QUICK_REFERENCE.md](NGINX_QUICK_REFERENCE.md)** - Quick command reference
3. **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist

---

## 🎯 Next Steps

1. ✅ Generate SSL certificates: `bash setup-ssl.sh`
2. ✅ Build services: `docker-compose build`
3. ✅ Start services: `docker-compose up -d`
4. ✅ Verify: `docker-compose ps`
5. ✅ Test endpoints: `curl -k https://localhost/health`
6. ✅ Push to GitHub (see Git section)
7. ✅ Deploy to server (see Deployment section)
8. ✅ Configure DNS for app.lignaflow.com
9. ✅ Monitor logs: `docker-compose logs -f`

---

## 📞 Support

For detailed information:
- Full Deployment: See `NGINX_DEPLOYMENT_GUIDE.md`
- Quick Reference: See `NGINX_QUICK_REFERENCE.md`
- Checklist: See `DEPLOYMENT_CHECKLIST.md`
- Git Help: Run `bash git-helper.sh`

---

**Status**: 🚀 **Ready to Deploy!**
