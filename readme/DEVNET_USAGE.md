# Casewise Devnet Usage Guide

## Overview
This guide explains how to use the development environment (devnet) alongside production. Both environments run simultaneously on the same VPS with no switching required.

## Architecture
- **Production**: Runs on standard ports (8000, 8042) at casewisemd.org domains
- **Devnet**: Runs on alternate ports (8001, 8043) at dev-*.casewisemd.org domains
- **Both environments are completely independent**

## Accessing the Environments

### Production
- Frontend: https://app.casewisemd.org
- API: https://api.casewisemd.org
- Viewer: https://viewer.casewisemd.org

### Devnet
- Frontend: https://dev-app.casewisemd.org
- API: https://dev-api.casewisemd.org
- Viewer: https://dev-viewer.casewisemd.org

## Starting the Environments

### Production Backend
```bash
# SSH to VPS
ssh root@143.244.154.89

# Start production
docker-compose up -d
```

### Devnet Backend
```bash
# SSH to VPS
ssh root@143.244.154.89

# Start devnet (uses different compose file)
docker-compose -f docker-compose.dev.yml up -d
```

### Check What's Running
```bash
docker ps
```
You should see both sets of containers running with -dev suffix for devnet.

## Deploying Frontend

### Production Frontend
```bash
# On VPS
cd /root/casewise-vps
./deploy-frontend.sh
```
This builds with production URLs and deploys to `/var/www/frontend/`

### Devnet Frontend
```bash
# On VPS
cd /root/casewise-vps
./deploy-frontend-dev.sh
```
This builds with dev URLs and deploys to `/var/www/frontend-dev/`

## Environment Files

### Production
- Backend: `/root/casewise-vps/.env`
- Frontend: `/root/casewise-vps/frontend/.env.production`

### Devnet
- Backend: `/root/casewise-vps/.env.dev`
- Frontend: `/root/casewise-vps/frontend/.env.dev`

## Common Workflows

### Testing a New Feature
1. Develop locally
2. Push to git
3. Pull on VPS
4. Deploy to devnet first
5. Test at https://dev-app.casewisemd.org
6. If working correctly, deploy to production

### Viewing Logs
```bash
# Production logs
docker logs mcp -f

# Devnet logs
docker logs mcp-dev -f
```

### Stopping Services
```bash
# Stop production (users will be affected!)
docker-compose down

# Stop devnet (safe to do anytime)
docker-compose -f docker-compose.dev.yml down
```

## Important Notes
1. **Frontend builds are environment-specific** - You must build separately for each environment
2. **Both environments share the same codebase** - Only configuration differs
3. **Devnet is safe for testing** - Breaking devnet won't affect production users
4. **Check `commands.md` for detailed commands** - Full command reference available

## Quick Status Check
Visit these URLs to verify services are running:
- Production API: https://api.casewisemd.org/health
- Devnet API: https://dev-api.casewisemd.org/health

## Troubleshooting
- If devnet frontend shows wrong API URL: Check frontend was built with `.env.dev`
- If services won't start: Check ports 8001/8043 are free
- If nginx errors: Ensure `/var/www/frontend-dev/` exists
- See `commands.md` for more troubleshooting commands