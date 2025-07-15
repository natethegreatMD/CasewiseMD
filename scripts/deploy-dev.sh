#!/bin/bash

echo "🚀 Deploying CasewiseMD Development Environment..."

# Change to project root
cd /root/casewise-dev

# Check if .env.dev exists
if [ ! -f ".env.dev" ]; then
    echo "❌ Error: .env.dev not found!"
    echo "📝 Please create .env.dev from .env.example"
    exit 1
fi

# Deploy backend
echo "🐳 Deploying development backend services..."
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d

# Check if Docker services are running
if docker ps | grep -q "mcp-dev"; then
    echo "✅ Development backend services deployed successfully!"
else
    echo "❌ Development backend deployment failed!"
    exit 1
fi

# Deploy frontend
echo "🎨 Deploying development frontend..."
cd frontend

# Source development environment variables
echo "📋 Loading development environment variables..."
export $(cat ../.env.dev | grep -E '^VITE_' | xargs)

# Build frontend
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build successful!"
    
    # Create dev directory if needed
    sudo mkdir -p /var/www/frontend-dev
    
    # Copy to nginx
    sudo cp -r dist/* /var/www/frontend-dev/
    
    echo "🎉 Development deployment complete!"
    echo "📍 Development URLs:"
    echo "   - Frontend: https://dev-app.casewisemd.org"
    echo "   - API: https://dev-api.casewisemd.org"
    echo "   - Viewer: https://dev-viewer.casewisemd.org"
else
    echo "❌ Frontend build failed!"
    exit 1
fi