#!/bin/bash

echo "🚀 Deploying CasewiseMD Frontend (Development)..."

# Change to frontend directory
cd /root/casewise-vps/frontend

# Source the development environment variables
if [ -f "../.env.dev" ]; then
    echo "📋 Loading development environment variables..."
    export $(cat ../.env.dev | grep -E '^VITE_' | xargs)
else
    echo "⚠️  Warning: .env.dev not found, using defaults"
fi

# Build the frontend with dev environment
echo "📦 Building frontend for development..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Create dev directory if it doesn't exist
    echo "📂 Creating development directory..."
    sudo mkdir -p /var/www/frontend-dev
    
    # Copy files to nginx dev directory
    echo "📂 Copying files to nginx development directory..."
    sudo cp -r dist/* /var/www/frontend-dev/
    
    echo "🎉 Development frontend deployed successfully!"
    echo "🌐 Changes are now live at https://dev-app.casewisemd.org"
else
    echo "❌ Build failed! Deployment aborted."
    exit 1
fi