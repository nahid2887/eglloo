# NGINX + HTTPS + GIT - QUICK REFERENCE

## 🚀 START APPLICATION
```bash
# Generate SSL certificates
bash setup-ssl.sh

# Build and start all services
docker-compose up -d

# Verify running
docker-compose ps
```

---

## 📊 URLS
| Service | URL |
|---------|-----|
| Main App | https://app.lignaflow.com |
| API | https://app.lignaflow.com/api/ |
| Swagger Docs | https://app.lignaflow.com/swagger/ |
| Admin Panel | https://app.lignaflow.com/admin/ |
| Health Check | https://app.lignaflow.com/health |

---

## 📝 GIT PUSH (Upload Your Changes)
```bash
git add .
git commit -m "your message here"
git push origin develop
```

## ⬇️ GIT PULL (Download Latest Changes)
```bash
git pull origin develop
```

## 🔄 GIT WORKFLOW (Simple)
```bash
# Start work on new feature
git checkout -b feature/your-name

# Make changes and commit
git add .
git commit -m "description"

# Push to server
git push origin feature/your-name

# Merge back to develop (on GitHub)
# Then update local
git checkout develop
git pull origin develop
```

---

## 🐳 DOCKER COMMANDS
```bash
# View logs
docker-compose logs -f              # All logs
docker-compose logs -f web          # Just Django
docker-compose logs -f nginx        # Just Nginx
docker-compose logs -f db           # Just Database

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Remove everything and start fresh
docker-compose down
docker-compose up -d

# SSH into container
docker-compose exec web bash        # Django app
```

---

## 🔍 TROUBLESHOOTING
```bash
# Check if services running
docker-compose ps

# View error logs
docker-compose logs --tail=50 nginx

# Test connection
curl https://app.lignaflow.com/health -k

# Test specific container
docker-compose exec web python manage.py shell
```

---

## 🌐 NGINX CONFIGURATION
- **Config File**: `nginx/nginx.conf`
- **Dockerfile**: `nginx/Dockerfile`
- **Certificates**: `ssl/cert.pem` and `ssl/key.pem`
- **Ports**: 80 (HTTP) → 443 (HTTPS)

---

## 📂 FILE STRUCTURE
```
eagleeyeau/
├── nginx/
│   ├── nginx.conf        ← Configuration
│   └── Dockerfile        ← Build image
├── ssl/                  ← SSL certificates (auto-generated)
├── docker-compose.yml    ← Services definition
├── setup-ssl.sh          ← Generate certificates
└── [other files...]
```

---

## 🔐 HTTPS SETUP
### Development (Self-Signed)
```bash
bash setup-ssl.sh
```

### Production (Let's Encrypt)
```bash
sudo certbot certonly --standalone -d app.lignaflow.com
sudo cp /etc/letsencrypt/live/app.lignaflow.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.lignaflow.com/privkey.pem ssl/key.pem
docker-compose restart nginx
```

---

## 🆘 COMMON ISSUES

**Port 80/443 in use?**
```bash
sudo lsof -i :80
sudo lsof -i :443
sudo kill -9 <PID>
```

**Certificate error?**
```bash
rm -rf ssl/
bash setup-ssl.sh
docker-compose restart nginx
```

**Database error?**
```bash
docker-compose logs -f db
docker-compose exec db psql -U postgres eagleeyeau
```

---

## 📞 SUPPORT
See full guide: `NGINX_DEPLOYMENT_GUIDE.md`
