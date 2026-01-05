# DEPLOYMENT CHECKLIST - NGINX + HTTPS + GIT

## ✅ Pre-Deployment

### Local Development Setup
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Navigate to project: `cd eagleeyeau`
- [ ] Check structure: `ls -la` (should see `nginx/`, `docker-compose.yml`, `setup-ssl.sh`)
- [ ] Review files created:
  - [ ] `nginx/nginx.conf` - Reverse proxy configuration
  - [ ] `nginx/Dockerfile` - Nginx image build
  - [ ] `setup-ssl.sh` - Certificate generation script
  - [ ] `NGINX_DEPLOYMENT_GUIDE.md` - Full documentation
  - [ ] `NGINX_QUICK_REFERENCE.md` - Quick commands

### Git Configuration
```bash
# Configure git (if first time)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## ✅ Step 1: Generate SSL Certificates

### Local Machine
```bash
# Generate self-signed certificates (for testing)
bash setup-ssl.sh

# Verify certificates created
ls -la ssl/
```

Should see:
- `ssl/cert.pem`
- `ssl/key.pem`

### Production Server
For Let's Encrypt (automatic HTTPS):
```bash
sudo certbot certonly --standalone -d app.lignaflow.com
sudo cp /etc/letsencrypt/live/app.lignaflow.com/fullchain.pem /path/to/project/ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.lignaflow.com/privkey.pem /path/to/project/ssl/key.pem
sudo chown $USER:$USER /path/to/project/ssl/*
```

---

## ✅ Step 2: Build Docker Images

```bash
# Build all services
docker-compose build

# Watch for build completion
# Expected output: "Successfully tagged eagleeyeau-web:latest" etc.
```

---

## ✅ Step 3: Start Services

```bash
# Start in background
docker-compose up -d

# Wait 30 seconds for services to initialize

# Check all services running
docker-compose ps

# Expected output:
# NAME                 STATUS              PORTS
# eagleeyeau-db       Up (healthy)         5432->5432
# eagleeyeau-app     Up                    8005->8005
# eagleeyeau-nginx   Up (healthy)          0.0.0.0:80->80, 0.0.0.0:443->443
```

---

## ✅ Step 4: Verify Application

```bash
# Test HTTP redirect
curl -v http://localhost
# Should show: 301 redirect to https

# Test HTTPS (ignore self-signed warning)
curl -k https://localhost/health
# Should return: "healthy"

# Test API endpoint
curl -k https://localhost/api/
# Should return: API response

# Test Swagger docs
curl -k https://localhost/swagger/
# Should return: Swagger UI HTML
```

### Test in Browser
- Open: https://localhost (ignore SSL warning)
- Should see: API response or admin page
- Swagger: https://localhost/swagger/

---

## ✅ Step 5: Git Setup & Push

### Initialize Git (if not already done)
```bash
git init
git add .
git commit -m "Initial commit: Add Nginx reverse proxy with HTTPS support"
```

### Add Remote Repository
```bash
git remote add origin https://github.com/YOUR-USERNAME/eagleeyeau.git
git remote -v  # Verify
```

### Push to GitHub
```bash
# Create main branch
git branch -M main

# Push to GitHub
git push -u origin main

# Verify on GitHub.com
```

### Setup Development Branch
```bash
git checkout -b develop
git push -u origin develop
```

---

## ✅ Step 6: Deploy to Server

### SSH into Production Server
```bash
ssh user@your-server-ip
cd /path/to/project
```

### Pull Code
```bash
# First time setup
git clone https://github.com/YOUR-USERNAME/eagleeyeau.git
cd eagleeyeau

# Subsequent updates
git pull origin main
```

### Setup SSL (Production)
```bash
bash setup-ssl.sh  # This will create self-signed

# OR use Let's Encrypt for production
sudo certbot certonly --standalone -d app.lignaflow.com
sudo cp /etc/letsencrypt/live/app.lignaflow.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.lignaflow.com/privkey.pem ssl/key.pem
```

### Start Services
```bash
docker-compose up -d
```

### Verify Deployment
```bash
docker-compose ps
docker-compose logs -f  # Monitor logs for 30 seconds, then Ctrl+C
```

---

## ✅ Step 7: DNS & Domain Setup

### Update DNS Records
In your domain registrar (where you registered lignaflow.com):

1. Create A record:
   - Name: `app`
   - Type: `A`
   - Value: `YOUR-SERVER-IP`

Wait 5-30 minutes for DNS to propagate.

### Test Domain
```bash
# After DNS updated
curl -k https://app.lignaflow.com/health
# Should return: "healthy"
```

---

## ✅ Step 8: Monitor & Maintain

### Daily Checks
```bash
# Check if services running
docker-compose ps

# View logs
docker-compose logs -f nginx  # Last 50 lines

# Check disk usage
docker system df
```

### Weekly Tasks
```bash
# Clean up unused images
docker system prune -f

# Check SSL certificate expiration (Let's Encrypt auto-renews)
sudo certbot certificates
```

### Monthly Tasks
```bash
# Backup database
docker-compose exec db pg_dump -U postgres eagleeyeau > backup-$(date +%Y%m%d).sql

# Update packages
git pull origin main
docker-compose build
docker-compose restart
```

---

## 📋 GIT WORKFLOW (For Teams)

### Push Your Changes
```bash
# 1. Check what changed
git status

# 2. Stage changes
git add .

# 3. Commit with message
git commit -m "feat: description of changes"

# 4. Push
git push origin develop
```

### Pull Team's Changes
```bash
# Before starting work each day
git pull origin develop

# Resolve conflicts if any
# Then continue working
```

### Create Feature Branch
```bash
# For new features
git checkout -b feature/user-authentication

# Make changes...
git add .
git commit -m "feat: add user login"
git push origin feature/user-authentication

# On GitHub, create Pull Request to develop
```

---

## 🆘 Troubleshooting

### Services Not Starting
```bash
docker-compose logs
# Check error messages
docker-compose down
docker-compose up -d
```

### SSL Certificate Error
```bash
rm -rf ssl/cert.pem ssl/key.pem
bash setup-ssl.sh
docker-compose restart nginx
```

### Can't Connect to app.lignaflow.com
```bash
# Check DNS
nslookup app.lignaflow.com

# Check firewall (allow ports 80, 443)
sudo ufw allow 80
sudo ufw allow 443

# Check if Nginx running
docker-compose ps nginx
```

### Database Connection Error
```bash
docker-compose logs db
docker-compose exec db psql -U postgres eagleeyeau
```

---

## 📞 Quick Links

- Full Guide: [NGINX_DEPLOYMENT_GUIDE.md](NGINX_DEPLOYMENT_GUIDE.md)
- Quick Ref: [NGINX_QUICK_REFERENCE.md](NGINX_QUICK_REFERENCE.md)
- Docker Compose: [docker-compose.yml](docker-compose.yml)
- Nginx Config: [nginx/nginx.conf](nginx/nginx.conf)

---

## ✅ Final Checklist

- [ ] SSL certificates generated (`ssl/` folder has files)
- [ ] Docker images built successfully
- [ ] All services running (`docker-compose ps`)
- [ ] Health endpoint responds (`curl -k https://localhost/health`)
- [ ] Swagger accessible (`https://localhost/swagger/`)
- [ ] Code pushed to GitHub
- [ ] DNS configured for `app.lignaflow.com`
- [ ] Server deployment complete
- [ ] HTTPS working on domain
- [ ] Logs monitored and clean

**Status**: 🚀 Ready for Production!
