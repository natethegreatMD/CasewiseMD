# Devnet Setup Guide

This guide explains how to set up and run the development environment (devnet) alongside production.

## Overview

- **Production**: Runs on ports 8000/8042 at casewisemd.org domains
- **Development**: Runs on ports 8001/8043 at dev-*.casewisemd.org domains
- **Both environments run simultaneously** on the same VPS

## Prerequisites

1. DNS records for dev-*.casewisemd.org (already created)
2. Access to the VPS (143.244.154.89)
3. Nginx configuration (needs to be updated on VPS)

## Local Setup Steps

### 1. Create Development Environment File

```bash
# Copy the example file
cp .env.example .env.dev

# Edit .env.dev and update:
# - Set ENVIRONMENT=development
# - Update all URLs to use dev-* domains
# - Use ports 8001/8043
# - Keep the same OPENAI_API_KEY
```

### 2. Create Frontend Development Environment

```bash
# Copy the frontend example
cp frontend/.env.example frontend/.env.dev

# Update all VITE_ variables to use dev-* domains
```

### 3. Test Locally

```bash
# Start development backend
docker-compose -f docker-compose.dev.yml up -d

# Check services
docker ps

# View logs
docker logs mcp-dev
docker logs casewise_orthanc-dev

# Test endpoints
curl http://localhost:8001/health
curl http://localhost:8043/system
```

## VPS Deployment Steps

### 1. SSH to VPS

```bash
ssh root@143.244.154.89
cd /root/casewise-vps
```

### 2. Pull Latest Code

```bash
git pull origin main
```

### 3. Set Up Environment Files

```bash
# Create .env.dev from example
cp .env.example .env.dev
nano .env.dev

# Update with development values:
ENVIRONMENT=development
MCP_PORT=8001
ORTHANC_PORT=8043
# ... (see .env.example for all variables)
```

### 4. Deploy Development Environment

```bash
# Use the deployment script
./scripts/deploy-dev.sh

# Or manually:
docker-compose -f docker-compose.dev.yml up -d
```

### 5. Update Nginx Configuration (One-time setup)

Create new nginx configuration files for dev domains:

```bash
# API configuration
sudo nano /etc/nginx/sites-available/dev-api.casewisemd.org

# Add:
upstream mcp_backend_dev {
    server localhost:8001;
}

server {
    server_name dev-api.casewisemd.org;
    
    location / {
        proxy_pass http://mcp_backend_dev;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /orthanc/ {
        proxy_pass http://localhost:8043/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Frontend configuration
sudo nano /etc/nginx/sites-available/dev-app.casewisemd.org

# Add:
server {
    server_name dev-app.casewisemd.org;
    root /var/www/frontend-dev;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 6. Enable Nginx Sites

```bash
# Create symbolic links
sudo ln -s /etc/nginx/sites-available/dev-api.casewisemd.org /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/dev-app.casewisemd.org /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 7. Set Up SSL Certificates

```bash
# Get certificates for all dev domains
sudo certbot --nginx -d dev-app.casewisemd.org -d dev-api.casewisemd.org -d dev-viewer.casewisemd.org -d dev-dicom.casewisemd.org
```

### 8. Deploy Frontend

```bash
# Create frontend dev directory
sudo mkdir -p /var/www/frontend-dev

# Deploy using script
./deploy-frontend-dev.sh
```

## Verification

### Check Services

```bash
# Docker containers
docker ps

# Should see:
# - mcp (production on port 8000)
# - casewise_orthanc (production on port 8042)
# - mcp-dev (development on port 8001)
# - casewise_orthanc-dev (development on port 8043)
```

### Test Endpoints

```bash
# Production
curl https://api.casewisemd.org/health

# Development
curl https://dev-api.casewisemd.org/health
```

### Access Applications

- Production: https://app.casewisemd.org
- Development: https://dev-app.casewisemd.org

## Common Commands

### View Logs

```bash
# Production
docker logs mcp --follow
docker logs casewise_orthanc --follow

# Development
docker logs mcp-dev --follow
docker logs casewise_orthanc-dev --follow
```

### Restart Services

```bash
# Production
docker-compose restart

# Development
docker-compose -f docker-compose.dev.yml restart
```

### Stop Services

```bash
# Stop development only
docker-compose -f docker-compose.dev.yml down

# Stop production only
docker-compose down
```

## Troubleshooting

### Port Conflicts

If you get port conflicts:
1. Check what's using the ports: `sudo lsof -i :8001`
2. Make sure no other services are using 8001/8043

### CORS Issues

If you get CORS errors:
1. Check that ALLOWED_ORIGINS in .env.dev includes your frontend URL
2. Restart the mcp-dev container after changes

### Frontend Not Loading

1. Check that frontend was built with correct env vars: `cd frontend && cat .env.dev`
2. Verify files were copied: `ls -la /var/www/frontend-dev/`
3. Check nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### Database Issues

Currently using the same demo_cases for both environments. In the future, you may want to:
- Use separate Orthanc volumes for complete isolation
- Set up different case sets for dev testing

## Best Practices

1. **Always test in devnet first** before deploying to production
2. **Keep .env.dev updated** with the latest environment variables
3. **Monitor both environments** - they share the same VPS resources
4. **Use the deployment scripts** for consistency
5. **Document any nginx changes** for future reference

## Quick Reference

| Component | Production | Development |
|-----------|------------|-------------|
| MCP Port | 8000 | 8001 |
| Orthanc Port | 8042 | 8043 |
| Frontend URL | app.casewisemd.org | dev-app.casewisemd.org |
| API URL | api.casewisemd.org | dev-api.casewisemd.org |
| Container Prefix | casewise_ | casewise_dev_ |
| Env File | .env | .env.dev |
| Docker Compose | docker-compose.yml | docker-compose.dev.yml |
| Deploy Script | scripts/deploy-prod.sh | scripts/deploy-dev.sh |