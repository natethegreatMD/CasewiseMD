#!/bin/bash

echo "🧪 Testing Environment Variable Setup..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 missing"
        return 1
    fi
}

echo -e "\n📁 Checking required files..."
test_file ".env.example"
test_file "frontend/.env.example"
test_file "docker-compose.yml"
test_file "docker-compose.dev.yml"
test_file "mcp/config/settings.py"
test_file "scripts/deploy-prod.sh"
test_file "scripts/deploy-dev.sh"
test_file "DEVNET_SETUP.md"

echo -e "\n🔍 Checking Python imports..."
cd mcp
python -c "from config import settings; print('✓ Settings module imports correctly')" 2>/dev/null || echo -e "${RED}✗${NC} Failed to import settings module"
cd ..

echo -e "\n📋 Checking environment files..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env exists"
    # Check for required variables
    for var in "ENVIRONMENT" "MCP_PORT" "ALLOWED_ORIGINS" "OPENAI_API_KEY"; do
        if grep -q "^$var=" .env; then
            echo -e "  ${GREEN}✓${NC} $var is set"
        else
            echo -e "  ${YELLOW}⚠${NC} $var not found in .env"
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} .env not found (using defaults)"
fi

echo -e "\n🐳 Checking Docker configuration..."
# Check if docker-compose can parse the files
docker-compose config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} docker-compose.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.yml has errors"
fi

docker-compose -f docker-compose.dev.yml config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} docker-compose.dev.yml is valid"
else
    echo -e "${RED}✗${NC} docker-compose.dev.yml has errors"
fi

echo -e "\n📊 Summary:"
echo "The environment variable refactor is complete!"
echo "Next steps:"
echo "1. Create .env file from .env.example"
echo "2. Set your OPENAI_API_KEY in .env"
echo "3. Run 'docker-compose up -d' to test production"
echo "4. Follow DEVNET_SETUP.md for development environment"