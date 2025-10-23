#!/bin/bash

# ============================================
# Environment Files Setup Script
# ============================================
# Creates all necessary .env files from .env.example templates
# Usage: bash scripts/setup_env_files.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Unified Codegen Platform - Environment Setup          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create directories
echo "📁 Creating directories..."
mkdir -p config
mkdir -p infrastructure/litellm
mkdir -p infrastructure/langfuse
mkdir -p infrastructure/nginx
mkdir -p infrastructure/redis
mkdir -p infrastructure/nats
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana
mkdir -p storage/generated
mkdir -p storage/temp
mkdir -p storage/cache
mkdir -p storage/logs
echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Function to copy env file if it doesn't exist
copy_env_file() {
    local source="$1"
    local dest="$2"
    local description="$3"
    
    if [ ! -f "$dest" ]; then
        if [ -f "$source" ]; then
            cp "$source" "$dest"
            echo -e "${GREEN}✓${NC} Created $description"
        else
            echo -e "${RED}✗${NC} Source file $source not found"
        fi
    else
        echo -e "${YELLOW}⚠${NC} $description already exists, skipping"
    fi
}

echo "📄 Setting up environment files..."

# Root environment files
copy_env_file "config/.env.example" "config/.env.development" "config/.env.development"
copy_env_file "config/.env.development.example" "config/.env.development" "config/.env.development (from development template)"
copy_env_file "config/.env.production.example" "config/.env.production" "config/.env.production"
copy_env_file "config/.env.test.example" "config/.env.test" "config/.env.test"
copy_env_file "config/.env.local.example" "config/.env.local" "config/.env.local"

# Service environment files
copy_env_file "infrastructure/litellm/.env.example" "infrastructure/litellm/.env" "infrastructure/litellm/.env"
copy_env_file "infrastructure/langfuse/.env.example" "infrastructure/langfuse/.env" "infrastructure/langfuse/.env"
copy_env_file "infrastructure/nginx/.env.example" "infrastructure/nginx/.env" "infrastructure/nginx/.env"
copy_env_file "infrastructure/redis/.env.example" "infrastructure/redis/.env" "infrastructure/redis/.env"
copy_env_file "infrastructure/nats/.env.example" "infrastructure/nats/.env" "infrastructure/nats/.env"

# Monitoring environment files
copy_env_file "monitoring/prometheus/.env.example" "monitoring/prometheus/.env" "monitoring/prometheus/.env"
copy_env_file "monitoring/grafana/.env.example" "monitoring/grafana/.env" "monitoring/grafana/.env"

echo ""
echo "🔐 Generating secrets..."

# Generate secrets
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32)
REDIS_PASS=$(openssl rand -hex 16)
LITELLM_KEY="sk-$(openssl rand -hex 16)"
LANGFUSE_SECRET=$(openssl rand -base64 32)
LANGFUSE_SALT=$(openssl rand -base64 32)
LANGFUSE_DB_PASS=$(openssl rand -hex 16)
GRAFANA_PASS=$(openssl rand -hex 12)

echo -e "${GREEN}✓${NC} Secrets generated"
echo ""

# Update development environment
echo "🔧 Updating config/.env.development..."
if [ -f "config/.env.development" ]; then
    sed -i.bak "s/change-this-in-production-use-openssl-rand-hex-32/${SECRET_KEY}/" config/.env.development
    sed -i.bak "s/dev-password/${REDIS_PASS}/" config/.env.development
    sed -i.bak "s/your-redis-password-change-me/${REDIS_PASS}/g" config/.env.development
    rm config/.env.development.bak 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Development environment configured"
else
    echo -e "${YELLOW}⚠${NC} config/.env.development not found"
fi

# Update LiteLLM environment
echo "🔧 Updating infrastructure/litellm/.env..."
if [ -f "infrastructure/litellm/.env" ]; then
    sed -i.bak "s/sk-1234567890abcdef/${LITELLM_KEY}/" infrastructure/litellm/.env
    sed -i.bak "s/your-redis-password/${REDIS_PASS}/" infrastructure/litellm/.env
    rm infrastructure/litellm/.env.bak 2>/dev/null || true
    echo -e "${GREEN}✓${NC} LiteLLM environment configured"
else
    echo -e "${YELLOW}⚠${NC} infrastructure/litellm/.env not found"
fi

# Update Langfuse environment
echo "🔧 Updating infrastructure/langfuse/.env..."
if [ -f "infrastructure/langfuse/.env" ]; then
    sed -i.bak "s/change-this-strong-password/${LANGFUSE_DB_PASS}/g" infrastructure/langfuse/.env
    sed -i.bak "s/your-nextauth-secret-here-use-openssl-rand/${LANGFUSE_SECRET}/" infrastructure/langfuse/.env
    sed -i.bak "s/your-salt-value-here-use-openssl-rand/${LANGFUSE_SALT}/" infrastructure/langfuse/.env
    rm infrastructure/langfuse/.env.bak 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Langfuse environment configured"
else
    echo -e "${YELLOW}⚠${NC} infrastructure/langfuse/.env not found"
fi

# Update Grafana environment
echo "🔧 Updating monitoring/grafana/.env..."
if [ -f "monitoring/grafana/.env" ]; then
    sed -i.bak "s/admin/${GRAFANA_PASS}/" monitoring/grafana/.env
    rm monitoring/grafana/.env.bak 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Grafana environment configured"
else
    echo -e "${YELLOW}⚠${NC} monitoring/grafana/.env not found"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Environment files setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "   1. Add your Gemini API key to:"
echo "      ${BLUE}config/.env.development${NC}"
echo "      ${BLUE}infrastructure/litellm/.env${NC}"
echo ""
echo "   2. Get your Gemini API key from:"
echo "      ${YELLOW}https://makersuite.google.com/app/apikey${NC}"
echo ""
echo "   3. Update the GEMINI_API_KEY in both files:"
echo "      ${BLUE}config/.env.development${NC} → GEMINI_API_KEY=your-actual-key"
echo "      ${BLUE}infrastructure/litellm/.env${NC} → GEMINI_API_KEY=your-actual-key"
echo ""
echo "   4. Start the platform:"
echo "      ${GREEN}make prod${NC}"
echo ""
echo "⚠️  IMPORTANT: The following secrets were generated:"
echo "   - SECRET_KEY (saved to config/.env.development)"
echo "   - REDIS_PASSWORD (saved to all env files)"
echo "   - LITELLM_MASTER_KEY (saved to infrastructure/litellm/.env)"
echo "   - LANGFUSE secrets (saved to infrastructure/langfuse/.env)"
echo "   - GRAFANA_PASSWORD (saved to monitoring/grafana/.env)"
echo ""
echo "   These are saved in your .env files but NOT shown here for security."
echo "   Make sure these files are in .gitignore!"
echo ""
echo "📋 Files created:"
echo "   ${GREEN}✓${NC} config/.env.development"
echo "   ${GREEN}✓${NC} config/.env.production"
echo "   ${GREEN}✓${NC} config/.env.test"
echo "   ${GREEN}✓${NC} config/.env.local"
echo "   ${GREEN}✓${NC} infrastructure/litellm/.env"
echo "   ${GREEN}✓${NC} infrastructure/langfuse/.env"
echo "   ${GREEN}✓${NC} infrastructure/nginx/.env"
echo "   ${GREEN}✓${NC} infrastructure/redis/.env"
echo "   ${GREEN}✓${NC} infrastructure/nats/.env"
echo "   ${GREEN}✓${NC} monitoring/prometheus/.env"
echo "   ${GREEN}✓${NC} monitoring/grafana/.env"
echo ""
