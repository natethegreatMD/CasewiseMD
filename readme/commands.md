# Casewise VPS - Command Reference

## Docker Commands

### Production Environment
```bash
# Start production containers
docker-compose up -d

# Stop production containers
docker-compose down

# View production logs
docker-compose logs -f
docker logs mcp --follow
docker logs casewise_orthanc --follow

# Restart production services
docker-compose restart
docker-compose restart mcp
```

### Development Environment (Devnet)
```bash
# Start devnet containers
docker-compose -f docker-compose.dev.yml up -d

# Stop devnet containers
docker-compose -f docker-compose.dev.yml down

# View devnet logs
docker-compose -f docker-compose.dev.yml logs -f
docker logs mcp-dev --follow
docker logs casewise_orthanc-dev --follow

# Restart devnet services
docker-compose -f docker-compose.dev.yml restart
docker-compose -f docker-compose.dev.yml restart mcp-dev
```

### General Docker Commands
```bash
# View all running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Remove unused containers and images
docker system prune -a

# Check container resource usage
docker stats
```

## Development Commands

### Frontend Development
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server (localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Backend Development
```bash
# Navigate to backend
cd mcp

# Run development server
python main.py

# Run with specific env file
python main.py --env .env.dev
```

## Deployment Commands

### Deploy Frontend to Production
```bash
# SSH to VPS first
ssh root@143.244.154.89

# Navigate to project
cd /root/casewise-vps

# Run deployment script
./deploy-frontend.sh

# What it does:
# 1. Builds frontend with production env vars
# 2. Copies dist/* to /var/www/frontend/
# 3. Live at https://app.casewisemd.org
```

### Deploy Frontend to Devnet (after env refactor)
```bash
# SSH to VPS first
ssh root@143.244.154.89

# Navigate to project
cd /root/casewise-vps

# Run dev deployment script (to be created)
./deploy-frontend-dev.sh

# What it will do:
# 1. Source .env.dev for dev URLs
# 2. Build frontend with dev env vars
# 3. Copy dist/* to /var/www/frontend-dev/
# 4. Live at https://dev-app.casewisemd.org
```

## Nginx Commands (VPS Only)

```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx (after config changes)
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# View nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# View nginx status
sudo systemctl status nginx
```

## SSL Certificate Commands (VPS Only)

```bash
# Create certificates for devnet domains
sudo certbot --nginx -d dev-app.casewisemd.org -d dev-api.casewisemd.org -d dev-viewer.casewisemd.org -d dev-dicom.casewisemd.org

# Renew all certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

## Testing Commands

### API Health Checks
```bash
# Production
curl https://api.casewisemd.org/health
curl https://api.casewisemd.org/api/v1/config/available-cases

# Devnet (after setup)
curl https://dev-api.casewisemd.org/health
curl https://dev-api.casewisemd.org/api/v1/config/available-cases

# Test diagnostic endpoint
curl "https://api.casewisemd.org/api/v1/diagnostic-session?case_id=case001"
```

### Check Services
```bash
# Check if ports are in use
sudo lsof -i :8000  # Production MCP
sudo lsof -i :8042  # Production Orthanc
sudo lsof -i :8001  # Devnet MCP
sudo lsof -i :8043  # Devnet Orthanc

# Check Docker networks
docker network ls
```

## Environment Management

### Switch Between Environments
```bash
# No switching needed! Both run simultaneously
# Access production: https://app.casewisemd.org
# Access devnet: https://dev-app.casewisemd.org
```

### View Environment Variables
```bash
# Production
docker exec mcp env | grep -E "API|OHIF|DICOM"

# Devnet (after setup)
docker exec mcp-dev env | grep -E "API|OHIF|DICOM"
```

## Git Commands

### Common Workflow
```bash
# Check status
git status

# Create new branch for feature
git checkout -b feature/env-variable-refactor

# Add and commit changes
git add .
git commit -m "Add environment variable support"

# Push to remote
git push origin feature/env-variable-refactor
```

## SSH Commands

### Connect to VPS
```bash
# Replace 'user' with your actual username
ssh user@143.244.154.89

# Copy files to VPS
scp local-file.txt user@143.244.154.89:/path/to/destination

# Copy files from VPS
scp user@143.244.154.89:/path/to/file.txt ./local-destination
```

## Troubleshooting Commands

### Debug Container Issues
```bash
# Enter running container
docker exec -it mcp /bin/bash
docker exec -it mcp-dev /bin/bash

# View container details
docker inspect mcp
docker inspect mcp-dev

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Check Disk Space
```bash
# General disk usage
df -h

# Docker disk usage
docker system df
```

### Memory and CPU
```bash
# System resources
htop  # Interactive
top   # Classic

# Docker resource usage
docker stats --no-stream
```

## Quick Reference

| Task | Production | Devnet |
|------|------------|---------|
| Start | `docker-compose up -d` | `docker-compose -f docker-compose.dev.yml up -d` |
| Stop | `docker-compose down` | `docker-compose -f docker-compose.dev.yml down` |
| Logs | `docker logs mcp -f` | `docker logs mcp-dev -f` |
| URL | https://app.casewisemd.org | https://dev-app.casewisemd.org |
| API Port | 8000 | 8001 |
| Orthanc Port | 8042 | 8043 |

## Notes
- Production and devnet run simultaneously on the same VPS
- No switching required - access different URLs for each environment
- Always test on devnet before deploying to production
- Use `docker ps` to see what's currently running