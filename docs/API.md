# API Documentation

## Base URL

```
http://localhost:6000/api/v1
```

## Authentication

API key authentication (optional):
```
X-API-Key: your-api-key
```

---

## Endpoints

### 1. Generate Code

Generate code based on natural language description.

**Endpoint:** `POST /generate_code`

**Request Body:**

```json
{
  "prompt": "Create a React todo app with dark mode toggle",
  "code_type": "frontend",
  "framework": "react",
  "model": "gemini/gemini-1.5-flash-latest",
  "include_tests": false,
  "include_documentation": false,
  "production_ready": true,
  "styling": "tailwindcss",
  "output_format": "json",
  "async_generation": false,
  "additional_context": {}
}
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | Natural language description (10-10000 chars) |
| `code_type` | enum | No | `frontend` | `frontend`, `backend`, `fullstack`, `component`, `api`, `utility` |
| `framework` | enum | No | Auto-detect | See frameworks list below |
| `model` | enum | No | `gemini-1.5-flash` | LLM model to use |
| `include_tests` | boolean | No | `false` | Include test files |
| `include_documentation` | boolean | No | `false` | Include README and docs |
| `production_ready` | boolean | No | `false` | Add production features |
| `styling` | string | No | `tailwindcss` | CSS framework/approach |
| `output_format` | enum | No | `json` | `json`, `zip`, `tar`, `files` |
| `async_generation` | boolean | No | `false` | Generate asynchronously |

**Supported Frameworks:**

Frontend: `react`, `react-typescript`, `vue`, `angular`, `svelte`, `nextjs`
Backend: `nodejs`, `express`, `fastapi`, `flask`, `django`, `nestjs`

**Response:**

```json
{
  "success": true,
  "files": [
    {
      "path": "src/App.jsx",
      "content": "// React code here...",
      "language": "jsx",
      "size_bytes": 1234
    }
  ],
  "framework_detected": "react",
  "total_files": 5,
  "total_lines": 250,
  "generation_time_seconds": 3.45,
  "model_used": "gemini/gemini-1.5-flash-latest",
  "tokens_used": 1500,
  "message": "Code generated successfully"
}
```

---

### 2. Health Check

Check service health.

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "llm": "healthy",
    "cache": "healthy"
  }
}
```

---

### 3. Metrics

Get Prometheus metrics.

**Endpoint:** `GET /metrics`

**Response:** Prometheus format metrics

---

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "details": {}
  }
}
```

**Status Codes:**

- `200` - Success
- `400` - Bad Request (validation error)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `502` - Bad Gateway (LLM service error)
- `503` - Service Unavailable

---

## Rate Limits

- 60 requests per minute
- 1000 requests per hour

Rate limit headers are included in responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

---

## Examples

### Example 1: React Frontend

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a modern login page with email and password fields",
    "code_type": "frontend",
    "framework": "react",
    "production_ready": true,
    "styling": "tailwindcss"
  }'
```

### Example 2: Node.js Backend

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a REST API for a blog with posts and comments",
    "code_type": "backend",
    "framework": "express",
    "production_ready": true,
    "include_tests": true
  }'
```

### Example 3: Fullstack App

```bash
curl -X POST http://localhost:6000/api/v1/generate_code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a task management app with user authentication",
    "code_type": "fullstack",
    "production_ready": true
  }'
```

