#!/bin/bash

echo "🚀 Deploying CasewiseMD Frontend..."

# Change to frontend directory
cd /root/casewise-vps/frontend

# Build the frontend
echo "📦 Building frontend..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    # Copy files to nginx directory
    echo "📂 Copying files to nginx..."
    sudo cp -r dist/* /var/www/frontend/
    
    echo "🎉 Frontend deployed successfully!"
    echo "🌐 Changes are now live at https://casewisemd.org"
else
    echo "❌ Build failed! Deployment aborted."
    exit 1
fi 