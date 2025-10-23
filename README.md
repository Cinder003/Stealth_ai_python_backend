# Unified Code Generation Platform

A production-ready AI-powered code generation platform using Gemini LLM to generate React frontends and Node.js backends.

## Features

- 🚀 **FastAPI Backend** - High-performance async Python API
- 🤖 **Gemini LLM Integration** - Powered by Google's Gemini AI
- ⚛️ **React Frontend Generation** - Modern React applications
- 🟢 **Node.js Backend Generation** - Express.js and other frameworks
- 📦 **LiteLLM Proxy** - Unified interface for multiple LLM providers
- 💾 **Redis Caching** - Fast response caching
- 📨 **NATS Message Queue** - Async job processing
- 📊 **Langfuse Observability** - LLM call tracing and monitoring
- 🔍 **Prometheus & Grafana** - Metrics and visualization
- 🔒 **Production Security** - Rate limiting, authentication
- 🐳 **Docker Compose** - Easy deployment

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Gemini API Key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd stealth_ai
```

2. Setup environment:
```bash
make setup
```

3. Configure your Gemini API key in `.env.production`:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

4. Start the platform:
```bash
make prod
```

The API will be available at: **http://localhost:6000/api/v1/generate_code**

## API Endpoints

### Generate Code
```bash
POST http://localhost:6000/api/v1/generate_code
Content-Type: application/json

{
  "prompt": "Create a React todo app with dark mode",
  "code_type": "frontend",
  "framework": "react",
  "include_tests": true,
  "production_ready": true
}
```

### Health Check
```bash
GET http://localhost:6000/health
```

### Metrics
```bash
GET http://localhost:6000/metrics
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI App │────▶│   LiteLLM   │
│             │     │  (Port 6000) │     │  (Port 4000)│
└─────────────┘     └──────────────┘     └─────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐      ┌─────────────┐
                    │    Redis     │      │   Gemini    │
                    │  (Port 6379) │      │     LLM     │
                    └──────────────┘      └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     NATS     │
                    │  (Port 4222) │
                    └──────────────┘
```

## Project Structure

- `app/` - Main FastAPI application
  - `api/` - API routes and endpoints
  - `core/` - Core configuration and utilities
  - `models/` - Data models and schemas
  - `services/` - Business logic layer
  - `helpers/` - Utility functions
- `infrastructure/` - Docker and infrastructure configs
- `prompts/` - LLM prompt templates
- `storage/` - Generated code output
- `tests/` - Test suite

## Development

```bash
# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint

# Clean up
make clean
```

## Monitoring

- **Langfuse**: http://localhost:3000 - LLM observability
- **Prometheus**: http://localhost:9090 - Metrics
- **Grafana**: http://localhost:3001 - Dashboards (admin/admin)
- **NATS Monitor**: http://localhost:8222 - Queue monitoring

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

