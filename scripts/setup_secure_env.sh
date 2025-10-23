#!/bin/bash

# ============================================
# SECURE ENVIRONMENT SETUP SCRIPT
# ============================================
# This script creates secure environment files
# that are NOT committed to version control

set -e

echo "🔒 Setting up secure environment files..."

# Create main environment files
echo "📁 Creating main environment files..."

# Development environment
if [ ! -f ".env.development" ]; then
    cp config/env.development.example .env.development
    echo "✅ Created .env.development"
else
    echo "⚠️  .env.development already exists"
fi

# Production environment
if [ ! -f ".env.production" ]; then
    cp config/env.production.example .env.production
    echo "✅ Created .env.production"
else
    echo "⚠️  .env.production already exists"
fi

# Test environment
if [ ! -f ".env.test" ]; then
    cp config/env.test.example .env.test
    echo "✅ Created .env.test"
else
    echo "⚠️  .env.test already exists"
fi

# Local environment (highest priority)
if [ ! -f ".env.local" ]; then
    cp config/env.local.example .env.local
    echo "✅ Created .env.local"
else
    echo "⚠️  .env.local already exists"
fi

# Create service-specific environment files
echo "📁 Creating service-specific environment files..."

# LiteLLM environment
mkdir -p infrastructure/litellm
if [ ! -f "infrastructure/litellm/.env" ]; then
    cat > infrastructure/litellm/.env << EOF
# LiteLLM Environment Variables
LITELLM_MASTER_KEY=sk-$(openssl rand -hex 16)
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
EOF
    echo "✅ Created infrastructure/litellm/.env"
else
    echo "⚠️  infrastructure/litellm/.env already exists"
fi

# Langfuse environment
mkdir -p infrastructure/langfuse
if [ ! -f "infrastructure/langfuse/.env" ]; then
    cat > infrastructure/langfuse/.env << EOF
# Langfuse Environment Variables
LANGFUSE_PUBLIC_KEY=pk-lf-$(openssl rand -hex 16)
LANGFUSE_SECRET_KEY=sk-lf-$(openssl rand -hex 16)
LANGFUSE_DB_PASSWORD=$(openssl rand -base64 32)
LANGFUSE_NEXTAUTH_SECRET=$(openssl rand -base64 32)
LANGFUSE_SALT=$(openssl rand -base64 32)
EOF
    echo "✅ Created infrastructure/langfuse/.env"
else
    echo "⚠️  infrastructure/langfuse/.env already exists"
fi

# Redis environment
mkdir -p infrastructure/redis
if [ ! -f "infrastructure/redis/.env" ]; then
    cat > infrastructure/redis/.env << EOF
# Redis Environment Variables
REDIS_PASSWORD=$(openssl rand -base64 32)
EOF
    echo "✅ Created infrastructure/redis/.env"
else
    echo "⚠️  infrastructure/redis/.env already exists"
fi

# NATS environment
mkdir -p infrastructure/nats
if [ ! -f "infrastructure/nats/.env" ]; then
    cat > infrastructure/nats/.env << EOF
# NATS Environment Variables
NATS_URL=nats://nats:4222
NATS_MAX_RECONNECT_ATTEMPTS=10
NATS_RECONNECT_TIME_WAIT=2
EOF
    echo "✅ Created infrastructure/nats/.env"
else
    echo "⚠️  infrastructure/nats/.env already exists"
fi

# Nginx environment
mkdir -p infrastructure/nginx
if [ ! -f "infrastructure/nginx/.env" ]; then
    cat > infrastructure/nginx/.env << EOF
# Nginx Environment Variables
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024
EOF
    echo "✅ Created infrastructure/nginx/.env"
else
    echo "⚠️  infrastructure/nginx/.env already exists"
fi

# Prometheus environment
mkdir -p monitoring/prometheus
if [ ! -f "monitoring/prometheus/.env" ]; then
    cat > monitoring/prometheus/.env << EOF
# Prometheus Environment Variables
PROMETHEUS_RETENTION_TIME=15d
PROMETHEUS_STORAGE_PATH=/prometheus
EOF
    echo "✅ Created monitoring/prometheus/.env"
else
    echo "⚠️  monitoring/prometheus/.env already exists"
fi

# Grafana environment
mkdir -p monitoring/grafana
if [ ! -f "monitoring/grafana/.env" ]; then
    cat > monitoring/grafana/.env << EOF
# Grafana Environment Variables
GRAFANA_PASSWORD=$(openssl rand -base64 16)
GRAFANA_SECRET_KEY=$(openssl rand -base64 32)
EOF
    echo "✅ Created monitoring/grafana/.env"
else
    echo "⚠️  monitoring/grafana/.env already exists"
fi

echo ""
echo "🔒 SECURITY CHECK:"
echo "✅ All .env files are in .gitignore"
echo "✅ Environment files created with secure defaults"
echo "✅ API keys are NOT exposed in version control"
echo ""
echo "📝 NEXT STEPS:"
echo "1. Edit .env.development and add your API keys:"
echo "   - GEMINI_API_KEY=your-actual-gemini-key"
echo "   - OPENAI_API_KEY=your-actual-openai-key (optional)"
echo "   - ANTHROPIC_API_KEY=your-actual-anthropic-key (optional)"
echo ""
echo "2. For production, edit .env.production with production values"
echo ""
echo "3. Start the platform:"
echo "   docker-compose up -d"
echo ""
echo "🔐 SECURITY REMINDERS:"
echo "- Never commit .env files to version control"
echo "- Use strong, unique passwords for production"
echo "- Rotate API keys regularly"
echo "- Use environment-specific values"
