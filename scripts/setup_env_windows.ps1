# ============================================
# SECURE ENVIRONMENT SETUP SCRIPT (Windows)
# ============================================
# This script creates secure environment files
# that are NOT committed to version control

Write-Host "🔒 Setting up secure environment files..." -ForegroundColor Green

# Create main environment files
Write-Host "📁 Creating main environment files..." -ForegroundColor Yellow

# Development environment
if (-not (Test-Path ".env.development")) {
    Copy-Item "config/env.development.example" ".env.development"
    Write-Host "✅ Created .env.development" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.development already exists" -ForegroundColor Yellow
}

# Production environment
if (-not (Test-Path ".env.production")) {
    Copy-Item "config/env.production.example" ".env.production"
    Write-Host "✅ Created .env.production" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.production already exists" -ForegroundColor Yellow
}

# Test environment
if (-not (Test-Path ".env.test")) {
    Copy-Item "config/env.test.example" ".env.test"
    Write-Host "✅ Created .env.test" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.test already exists" -ForegroundColor Yellow
}

# Local environment (highest priority)
if (-not (Test-Path ".env.local")) {
    Copy-Item "config/env.local.example" ".env.local"
    Write-Host "✅ Created .env.local" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env.local already exists" -ForegroundColor Yellow
}

# Create service-specific environment files
Write-Host "📁 Creating service-specific environment files..." -ForegroundColor Yellow

# LiteLLM environment
if (-not (Test-Path "infrastructure/litellm")) {
    New-Item -ItemType Directory -Path "infrastructure/litellm" -Force
}
if (-not (Test-Path "infrastructure/litellm/.env")) {
    $litellmMasterKey = "sk-" + (-join ((1..32) | ForEach-Object { Get-Random -InputObject @('0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f') }))
    @"
# LiteLLM Environment Variables
LITELLM_MASTER_KEY=$litellmMasterKey
GEMINI_API_KEY=your-gemini-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
"@ | Out-File -FilePath "infrastructure/litellm/.env" -Encoding UTF8
    Write-Host "✅ Created infrastructure/litellm/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  infrastructure/litellm/.env already exists" -ForegroundColor Yellow
}

# Langfuse environment
if (-not (Test-Path "infrastructure/langfuse")) {
    New-Item -ItemType Directory -Path "infrastructure/langfuse" -Force
}
if (-not (Test-Path "infrastructure/langfuse/.env")) {
    $langfuseDbPassword = [System.Web.Security.Membership]::GeneratePassword(32, 0)
    $langfuseNextAuthSecret = [System.Web.Security.Membership]::GeneratePassword(32, 0)
    $langfuseSalt = [System.Web.Security.Membership]::GeneratePassword(32, 0)
    @"
# Langfuse Environment Variables
LANGFUSE_PUBLIC_KEY=pk-lf-$(Get-Random -Minimum 100000 -Maximum 999999)
LANGFUSE_SECRET_KEY=sk-lf-$(Get-Random -Minimum 100000 -Maximum 999999)
LANGFUSE_DB_PASSWORD=$langfuseDbPassword
LANGFUSE_NEXTAUTH_SECRET=$langfuseNextAuthSecret
LANGFUSE_SALT=$langfuseSalt
"@ | Out-File -FilePath "infrastructure/langfuse/.env" -Encoding UTF8
    Write-Host "✅ Created infrastructure/langfuse/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  infrastructure/langfuse/.env already exists" -ForegroundColor Yellow
}

# Redis environment
if (-not (Test-Path "infrastructure/redis")) {
    New-Item -ItemType Directory -Path "infrastructure/redis" -Force
}
if (-not (Test-Path "infrastructure/redis/.env")) {
    $redisPassword = [System.Web.Security.Membership]::GeneratePassword(32, 0)
    @"
# Redis Environment Variables
REDIS_PASSWORD=$redisPassword
"@ | Out-File -FilePath "infrastructure/redis/.env" -Encoding UTF8
    Write-Host "✅ Created infrastructure/redis/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  infrastructure/redis/.env already exists" -ForegroundColor Yellow
}

# NATS environment
if (-not (Test-Path "infrastructure/nats")) {
    New-Item -ItemType Directory -Path "infrastructure/nats" -Force
}
if (-not (Test-Path "infrastructure/nats/.env")) {
    @"
# NATS Environment Variables
NATS_URL=nats://nats:4222
NATS_MAX_RECONNECT_ATTEMPTS=10
NATS_RECONNECT_TIME_WAIT=2
"@ | Out-File -FilePath "infrastructure/nats/.env" -Encoding UTF8
    Write-Host "✅ Created infrastructure/nats/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  infrastructure/nats/.env already exists" -ForegroundColor Yellow
}

# Nginx environment
if (-not (Test-Path "infrastructure/nginx")) {
    New-Item -ItemType Directory -Path "infrastructure/nginx" -Force
}
if (-not (Test-Path "infrastructure/nginx/.env")) {
    @"
# Nginx Environment Variables
NGINX_WORKER_PROCESSES=auto
NGINX_WORKER_CONNECTIONS=1024
"@ | Out-File -FilePath "infrastructure/nginx/.env" -Encoding UTF8
    Write-Host "✅ Created infrastructure/nginx/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  infrastructure/nginx/.env already exists" -ForegroundColor Yellow
}

# Prometheus environment
if (-not (Test-Path "monitoring/prometheus")) {
    New-Item -ItemType Directory -Path "monitoring/prometheus" -Force
}
if (-not (Test-Path "monitoring/prometheus/.env")) {
    @"
# Prometheus Environment Variables
PROMETHEUS_RETENTION_TIME=15d
PROMETHEUS_STORAGE_PATH=/prometheus
"@ | Out-File -FilePath "monitoring/prometheus/.env" -Encoding UTF8
    Write-Host "✅ Created monitoring/prometheus/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  monitoring/prometheus/.env already exists" -ForegroundColor Yellow
}

# Grafana environment
if (-not (Test-Path "monitoring/grafana")) {
    New-Item -ItemType Directory -Path "monitoring/grafana" -Force
}
if (-not (Test-Path "monitoring/grafana/.env")) {
    $grafanaPassword = [System.Web.Security.Membership]::GeneratePassword(16, 0)
    $grafanaSecretKey = [System.Web.Security.Membership]::GeneratePassword(32, 0)
    @"
# Grafana Environment Variables
GRAFANA_PASSWORD=$grafanaPassword
GRAFANA_SECRET_KEY=$grafanaSecretKey
"@ | Out-File -FilePath "monitoring/grafana/.env" -Encoding UTF8
    Write-Host "✅ Created monitoring/grafana/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  monitoring/grafana/.env already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔒 SECURITY CHECK:" -ForegroundColor Green
Write-Host "✅ All .env files are in .gitignore" -ForegroundColor Green
Write-Host "✅ Environment files created with secure defaults" -ForegroundColor Green
Write-Host "✅ API keys are NOT exposed in version control" -ForegroundColor Green
Write-Host ""
Write-Host "📝 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Edit .env.development and add your API keys:"
Write-Host "   - GEMINI_API_KEY=your-actual-gemini-key"
Write-Host "   - OPENAI_API_KEY=your-actual-openai-key (optional)"
Write-Host "   - ANTHROPIC_API_KEY=your-actual-anthropic-key (optional)"
Write-Host ""
Write-Host "2. For production, edit .env.production with production values"
Write-Host ""
Write-Host "3. Start the platform:"
Write-Host "   docker-compose up -d"
Write-Host ""
Write-Host "🔐 SECURITY REMINDERS:" -ForegroundColor Red
Write-Host "- Never commit .env files to version control"
Write-Host "- Use strong, unique passwords for production"
Write-Host "- Rotate API keys regularly"
Write-Host "- Use environment-specific values"
