#!/bin/bash

# ============================================
# Secret Generation Script
# ============================================
# Generates all required secrets for the platform
# Usage: bash scripts/generate_secrets.sh

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Unified Codegen Platform - Secret Generator           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Generated on: $(date)"
echo ""
echo "⚠️  IMPORTANT: Save these secrets securely!"
echo "⚠️  These values are shown only once!"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

# Application Secrets
echo "# ============================================"
echo "# APPLICATION SECRETS"
echo "# ============================================"
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32)"
echo "JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))' 2>/dev/null || openssl rand -base64 32)"
echo ""

# Redis
echo "# ============================================"
echo "# REDIS"
echo "# ============================================"
REDIS_PASS=$(openssl rand -hex 16)
echo "REDIS_PASSWORD=${REDIS_PASS}"
echo "REDIS_URL=redis://:${REDIS_PASS}@redis:6379/0"
echo ""

# LiteLLM
echo "# ============================================"
echo "# LITELLM PROXY"
echo "# ============================================"
echo "LITELLM_MASTER_KEY=sk-$(openssl rand -hex 16)"
echo ""

# Langfuse
echo "# ============================================"
echo "# LANGFUSE"
echo "# ============================================"
LANGFUSE_DB_PASS=$(openssl rand -hex 16)
echo "LANGFUSE_DB_PASSWORD=${LANGFUSE_DB_PASS}"
echo "LANGFUSE_NEXTAUTH_SECRET=$(openssl rand -base64 32)"
echo "LANGFUSE_SALT=$(openssl rand -base64 32)"
echo "DATABASE_URL=postgresql://langfuse:${LANGFUSE_DB_PASS}@langfuse_db:5432/langfuse"
echo ""

# Grafana
echo "# ============================================"
echo "# MONITORING"
echo "# ============================================"
echo "GRAFANA_PASSWORD=$(openssl rand -hex 12)"
echo ""

echo "════════════════════════════════════════════════════════════"
echo ""
echo "✅ All secrets generated successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Copy the secrets above"
echo "   2. Update your .env files (config/.env.production, etc.)"
echo "   3. Update service .env files (infrastructure/litellm/.env, etc.)"
echo "   4. Never commit these values to git!"
echo ""
echo "💡 Tip: Run this script and redirect output to a secure file:"
echo "   bash scripts/generate_secrets.sh > secrets.txt"
echo "   Then copy values to your .env files and delete secrets.txt"
echo ""

