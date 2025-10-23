# Quick Start Guide

Get up and running with the Unified Code Generation Platform in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Step 1: Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd stealth_ai

# Run setup
make setup
```

## Step 2: Configure

Add your Gemini API key to `.env.production`:

```bash
# Open in your editor
nano .env.production

# Or use sed to replace
sed -i 's/your-gemini-api-key-here/YOUR_ACTUAL_KEY/' .env.production
```

## Step 3: Start Services

```bash
make prod
```

Wait 30-60 seconds for all services to start.

## Step 4: Test the API

### Option A: Using curl

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a button component with loading state",
    "code_type": "component",
    "framework": "react",
    "styling": "tailwindcss"
  }'
```

### Option B: Using the test script

```bash
chmod +x examples/test_api.sh
./examples/test_api.sh
```

### Option C: Using Python

```bash
python examples/generate_code.py
```

## Step 5: View Results

Check the generated code in the API response or saved files.

## Next Steps

- 📚 Read the [API Documentation](docs/API.md)
- 🎯 See [Usage Guide](docs/USAGE_GUIDE.md) for examples
- 📊 View dashboards at http://localhost:3001 (admin/admin)
- 🔍 Explore API docs at http://localhost:6000/docs

## Useful Commands

```bash
# View logs
docker-compose logs -f app

# Stop services
make clean

# Restart
docker-compose restart app

# Check health
curl http://localhost:6000/health
```

## Troubleshooting

### Services won't start
```bash
# Check what's running on port 6000
lsof -i :6000

# View all logs
docker-compose logs
```

### LLM errors
- Verify your Gemini API key is correct
- Check LiteLLM logs: `docker-compose logs litellm`

### Need help?
- Check [Deployment Guide](docs/DEPLOYMENT.md)
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub

---

## Example Request

```json
{
  "prompt": "Create a modern landing page with hero section, features, and contact form",
  "code_type": "frontend",
  "framework": "nextjs",
  "production_ready": true,
  "styling": "tailwindcss"
}
```

**Response includes:**
- Complete, working code files
- Package.json with dependencies
- README with setup instructions
- Responsive, accessible components

---

**Ready to generate code? Start with the examples in `examples/` directory!** 🚀

