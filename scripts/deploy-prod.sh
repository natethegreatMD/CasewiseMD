#!/bin/bash

echo "🚀 Deploying CasewiseMD Production Environment..."

# Change to project root
cd /root/CasewiseMD-workspace/production

# Deploy backend
echo "🐳 Deploying backend services..."
docker-compose down
docker-compose build
docker-compose up -d

# Check if Docker services are running
if docker ps | grep -q "mcp"; then
    echo "✅ Backend services deployed successfully!"
else
    echo "❌ Backend deployment failed!"
    exit 1
fi

# Deploy frontend
echo "🎨 Deploying frontend..."
cd frontend

# Source production environment variables
if [ -f "../.env" ]; then
    echo "📋 Loading production environment variables..."
    export $(cat ../.env | grep -E '^VITE_' | xargs)
fi

# Build frontend
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
    
    # Copy to nginx
    sudo cp -r dist/* /var/www/frontend/
    
    echo "🎉 Production deployment complete!"
    echo "📍 Production URLs:"
    echo "   - Frontend: https://app.casewisemd.org"
    echo "   - API: https://api.casewisemd.org"
    echo "   - Viewer: https://viewer.casewisemd.org"
else
    echo "❌ Frontend build failed!"
    exit 1
fi