# Environment Files - Complete Setup Guide

## 📍 Total Environment Files: **9 files**

---

## File Structure Overview

```
project-root/
├── config/
│   ├── .env.example          ✅ Template (committed to git)
│   ├── .env.development      ❌ Dev settings (gitignored)
│   ├── .env.production       ❌ Prod settings (gitignored)
│   ├── .env.test             ❌ Test settings (gitignored)
│   └── .env.local            ❌ Local overrides (gitignored)
│
└── infrastructure/
    ├── litellm/
    │   ├── .env.example      ✅ Template (committed)
    │   └── .env              ❌ Config (gitignored)
    │
    └── langfuse/
        ├── .env.example      ✅ Template (committed)
        └── .env              ❌ Config (gitignored)
```

---

## 🔧 Quick Setup

### Step 1: Create Environment Files

```bash
# Create config directory
mkdir -p config

# Copy templates for root environment files
cp config/.env.example config/.env.development
cp config/.env.example config/.env.production
cp config/.env.example config/.env.test

# Copy templates for service environment files
cp infrastructure/litellm/.env.example infrastructure/litellm/.env
cp infrastructure/langfuse/.env.example infrastructure/langfuse/.env
```

### Step 2: Generate Secure Secrets

```bash
# Generate SECRET_KEY (Python)
python -c "import secrets; print(f'SECRET_KEY={secrets.token_urlsafe(32)}')"

# Generate JWT_SECRET_KEY (Python)
python -c "import secrets; print(f'JWT_SECRET_KEY={secrets.token_urlsafe(32)}')"

# Generate NEXTAUTH_SECRET (OpenSSL)
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)"

# Generate SALT (OpenSSL)
echo "SALT=$(openssl rand -base64 32)"

# Generate Redis password (OpenSSL)
echo "REDIS_PASSWORD=$(openssl rand -hex 16)"

# Generate LiteLLM Master Key (OpenSSL)
echo "LITELLM_MASTER_KEY=sk-$(openssl rand -hex 16)"
```

### Step 3: Update API Keys

Edit the environment files and add your actual API keys:

**`config/.env.development`:**
```bash
GEMINI_API_KEY=your-actual-gemini-api-key
```

**`infrastructure/litellm/.env`:**
```bash
GEMINI_API_KEY=your-actual-gemini-api-key
LITELLM_MASTER_KEY=sk-your-generated-master-key
REDIS_PASSWORD=your-generated-redis-password
```

**`infrastructure/langfuse/.env`:**
```bash
DATABASE_URL=postgresql://langfuse:your-strong-password@langfuse_db:5432/langfuse
NEXTAUTH_SECRET=your-generated-nextauth-secret
SALT=your-generated-salt
```

### Step 4: Update .gitignore

Add to your `.gitignore`:

```bash
# Environment Files
config/.env.development
config/.env.production
config/.env.test
config/.env.local
infrastructure/litellm/.env
infrastructure/langfuse/.env
*.env
!.env.example
!**/.env.example

# Storage
storage/generated/*
storage/temp/*
storage/cache/*
storage/logs/*
!storage/.gitkeep
```

---

## 📋 Environment File Loading Priority

The application loads environment files in this order (later overrides earlier):

1. `config/.env.example` (base defaults)
2. `config/.env.{ENVIRONMENT}` (environment-specific)
3. `config/.env.local` (local overrides)
4. System environment variables (highest priority)

---

## 🔑 Required Secrets Checklist

### For Development

- [ ] `GEMINI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] `SECRET_KEY` - Generate with Python secrets
- [ ] `REDIS_PASSWORD` - Generate with OpenSSL
- [ ] `LITELLM_MASTER_KEY` - Generate with OpenSSL

### For Production (Additional)

- [ ] `JWT_SECRET_KEY` - Generate with Python secrets
- [ ] `LANGFUSE_NEXTAUTH_SECRET` - Generate with OpenSSL
- [ ] `LANGFUSE_SALT` - Generate with OpenSSL
- [ ] `LANGFUSE_DB_PASSWORD` - Strong unique password
- [ ] All keys from development (with production values)

---

## 🚀 Usage with Docker Compose

### Development Mode

```bash
# Use development environment
docker-compose --env-file config/.env.development up

# Or use make command
make dev
```

### Production Mode

```bash
# Use production environment
docker-compose --env-file config/.env.production up -d

# Or use make command
make prod
```

### Test Mode

```bash
# Use test environment
docker-compose --env-file config/.env.test -f docker-compose.test.yml up

# Or use make command
make test
```

---

## 🔐 Security Best Practices

### 1. Never Commit Secrets
```bash
# Check what would be committed
git status

# If you accidentally staged .env files
git reset config/.env.production
git reset infrastructure/*/.env
```

### 2. Use Strong Passwords

❌ Weak:
```bash
REDIS_PASSWORD=password123
```

✅ Strong:
```bash
REDIS_PASSWORD=8a7f6e5d4c3b2a1f9e8d7c6b5a4f3e2d
```

### 3. Rotate Secrets Regularly

Create a reminder to rotate production secrets:
- Every 90 days for API keys
- Every 30 days for database passwords
- Immediately if compromised

### 4. Use Different Keys Per Environment

```bash
# Development
GEMINI_API_KEY=dev-key-with-quota-limits

# Production
GEMINI_API_KEY=prod-key-with-monitoring
```

---

## 🧪 Testing Your Configuration

### Verify Environment Loading

```python
# test_env.py
import os
from dotenv import load_dotenv

load_dotenv('config/.env.development')

required_vars = [
    'GEMINI_API_KEY',
    'REDIS_PASSWORD',
    'LITELLM_MASTER_KEY',
    'SECRET_KEY'
]

for var in required_vars:
    value = os.getenv(var)
    if value and value != f'your-{var.lower().replace("_", "-")}':
        print(f'✅ {var}: Configured')
    else:
        print(f'❌ {var}: Missing or using placeholder')
```

Run it:
```bash
python test_env.py
```

### Verify Services Can Connect

```bash
# Check if services can read their configs
docker-compose config

# Start services and check health
docker-compose up -d
docker-compose ps
curl http://localhost:6000/health
```

---

## 🐛 Troubleshooting

### Problem: Environment variables not loading

**Solution:**
```bash
# Check file exists
ls -la config/.env.development

# Check file has correct format (no spaces around =)
cat config/.env.development | grep "GEMINI"

# Verify Docker Compose is using the right file
docker-compose --env-file config/.env.development config | grep GEMINI
```

### Problem: Redis connection failed

**Solution:**
```bash
# Check password matches in both files
grep REDIS_PASSWORD config/.env.development
grep REDIS_PASSWORD infrastructure/litellm/.env

# Test Redis connection
docker exec -it codegen_redis redis-cli -a your-password ping
```

### Problem: LiteLLM can't find API key

**Solution:**
```bash
# Check LiteLLM container environment
docker exec codegen_litellm env | grep GEMINI

# Verify .env file is being loaded
docker-compose logs litellm | grep "API key"
```

---

## 📊 Environment Variables Reference

### Critical Variables

| Variable | Required | Example | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | `AIza...` | Google Gemini API key |
| `SECRET_KEY` | Yes | `random32chars` | App secret for sessions |
| `REDIS_PASSWORD` | Yes | `random16chars` | Redis authentication |
| `LITELLM_MASTER_KEY` | Yes | `sk-random16` | LiteLLM proxy key |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `WORKERS` | `4` | Uvicorn workers |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit |
| `LANGFUSE_ENABLED` | `false` | Enable observability |

---

## 🔄 Migration from Old Setup

If you have existing `.env` files in the root:

```bash
# Backup existing
cp .env .env.backup
cp .env.production .env.production.backup

# Move to new structure
mkdir -p config
mv .env.production config/.env.production
mv .env.development config/.env.development

# Update docker-compose references
# Change: env_file: .env.production
# To: env_file: config/.env.production
```

---

## ✅ Final Verification Checklist

Before deploying:

- [ ] All `.env.example` files exist and are up to date
- [ ] All actual `.env` files are in `.gitignore`
- [ ] All secrets are unique and randomly generated
- [ ] API keys are valid and have proper permissions
- [ ] Redis password matches across all config files
- [ ] Database credentials are strong and match
- [ ] File paths are correct for your environment
- [ ] Ports don't conflict with other services
- [ ] `docker-compose config` runs without errors
- [ ] Health check endpoint returns 200 OK

---

## 🆘 Getting Help

If you encounter issues:

1. Check the logs:
   ```bash
   docker-compose logs -f
   ```

2. Verify configuration:
   ```bash
   docker-compose config
   ```

3. Test individual services:
   ```bash
   curl http://localhost:6000/health
   curl http://localhost:4000/health
   ```

4. Review documentation:
   - [Deployment Guide](DEPLOYMENT.md)
   - [Architecture](ARCHITECTURE.md)
   - [API Documentation](API.md)

---

**Need to generate all secrets at once?** Run this script:

```bash
#!/bin/bash
echo "# Generated Secrets - $(date)"
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "JWT_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "REDIS_PASSWORD=$(openssl rand -hex 16)"
echo "LITELLM_MASTER_KEY=sk-$(openssl rand -hex 16)"
echo "NEXTAUTH_SECRET=$(openssl rand -base64 32)"
echo "SALT=$(openssl rand -base64 32)"
echo "LANGFUSE_DB_PASSWORD=$(openssl rand -hex 16)"
```

Save it as `scripts/generate_secrets.sh` and run with `bash scripts/generate_secrets.sh`

