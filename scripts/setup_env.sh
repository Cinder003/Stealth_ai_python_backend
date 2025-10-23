#!/bin/bash

# ============================================
# Environment Setup Script
# ============================================
# Sets up all environment files from templates
# Usage: bash scripts/setup_env.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Unified Codegen Platform - Environment Setup          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create directories
echo "📁 Creating directories..."
mkdir -p config
mkdir -p infrastructure/litellm
mkdir -p infrastructure/langfuse
mkdir -p storage/generated
mkdir -p storage/temp
mkdir -p storage/cache
mkdir -p storage/logs
echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Copy environment templates
echo "📄 Setting up environment files..."

# Root environment files
if [ ! -f "config/.env.development" ]; then
    cp config/.env.example config/.env.development
    echo -e "${GREEN}✓${NC} Created config/.env.development"
else
    echo -e "${YELLOW}⚠${NC} config/.env.development already exists, skipping"
fi

if [ ! -f "config/.env.production" ]; then
    cp config/.env.example config/.env.production
    echo -e "${GREEN}✓${NC} Created config/.env.production"
else
    echo -e "${YELLOW}⚠${NC} config/.env.production already exists, skipping"
fi

if [ ! -f "config/.env.test" ]; then
    cp config/.env.example config/.env.test
    echo -e "${GREEN}✓${NC} Created config/.env.test"
else
    echo -e "${YELLOW}⚠${NC} config/.env.test already exists, skipping"
fi

# Service environment files
if [ ! -f "infrastructure/litellm/.env" ]; then
    cp infrastructure/litellm/.env.example infrastructure/litellm/.env
    echo -e "${GREEN}✓${NC} Created infrastructure/litellm/.env"
else
    echo -e "${YELLOW}⚠${NC} infrastructure/litellm/.env already exists, skipping"
fi

if [ ! -f "infrastructure/langfuse/.env" ]; then
    cp infrastructure/langfuse/.env.example infrastructure/langfuse/.env
    echo -e "${GREEN}✓${NC} Created infrastructure/langfuse/.env"
else
    echo -e "${YELLOW}⚠${NC} infrastructure/langfuse/.env already exists, skipping"
fi

echo ""
echo "🔐 Generating secrets..."

# Generate secrets
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32)
REDIS_PASS=$(openssl rand -hex 16)
LITELLM_KEY="sk-$(openssl rand -hex 16)"
LANGFUSE_SECRET=$(openssl rand -base64 32)
LANGFUSE_SALT=$(openssl rand -base64 32)
LANGFUSE_DB_PASS=$(openssl rand -hex 16)

echo -e "${GREEN}✓${NC} Secrets generated"
echo ""

# Update development environment
echo "🔧 Updating config/.env.development..."
sed -i.bak "s/change-this-in-production-use-openssl-rand-hex-32/${SECRET_KEY}/" config/.env.development
sed -i.bak "s/dev-password/${REDIS_PASS}/" config/.env.development
sed -i.bak "s/your-redis-password-change-me/${REDIS_PASS}/g" config/.env.development
rm config/.env.development.bak 2>/dev/null || true
echo -e "${GREEN}✓${NC} Development environment configured"
echo ""

# Update LiteLLM environment
echo "🔧 Updating infrastructure/litellm/.env..."
sed -i.bak "s/sk-1234567890abcdef/${LITELLM_KEY}/" infrastructure/litellm/.env
sed -i.bak "s/your-redis-password/${REDIS_PASS}/" infrastructure/litellm/.env
rm infrastructure/litellm/.env.bak 2>/dev/null || true
echo -e "${GREEN}✓${NC} LiteLLM environment configured"
echo ""

# Update Langfuse environment
echo "🔧 Updating infrastructure/langfuse/.env..."
sed -i.bak "s/change-this-strong-password/${LANGFUSE_DB_PASS}/g" infrastructure/langfuse/.env
sed -i.bak "s/your-nextauth-secret-here-use-openssl-rand/${LANGFUSE_SECRET}/" infrastructure/langfuse/.env
sed -i.bak "s/your-salt-value-here-use-openssl-rand/${LANGFUSE_SALT}/" infrastructure/langfuse/.env
rm infrastructure/langfuse/.env.bak 2>/dev/null || true
echo -e "${GREEN}✓${NC} Langfuse environment configured"
echo ""

echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ Environment setup complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "   1. Add your Gemini API key to the environment files:"
echo "      - config/.env.development"
echo "      - infrastructure/litellm/.env"
echo ""
echo "   2. Get your Gemini API key from:"
echo "      https://makersuite.google.com/app/apikey"
echo ""
echo "   3. Update the GEMINI_API_KEY in:"
echo "      ${YELLOW}config/.env.development${NC}"
echo "      ${YELLOW}infrastructure/litellm/.env${NC}"
echo ""
echo "   4. Start the platform:"
echo "      ${GREEN}make prod${NC}"
echo ""
echo "⚠️  IMPORTANT: The following secrets were generated:"
echo "   - SECRET_KEY (saved to config/.env.development)"
echo "   - REDIS_PASSWORD (saved to all env files)"
echo "   - LITELLM_MASTER_KEY (saved to infrastructure/litellm/.env)"
echo "   - LANGFUSE secrets (saved to infrastructure/langfuse/.env)"
echo ""
echo "   These are saved in your .env files but NOT shown here for security."
echo "   Make sure these files are in .gitignore!"
echo ""

